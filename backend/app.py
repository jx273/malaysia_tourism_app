import base64
import os
from io import BytesIO
from html import escape
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from pathlib import Path
from dotenv import load_dotenv

from ai_service import (
    DEFAULT_GEMINI_MODEL,
    GeminiAssistantError,
    generate_contextual_answer,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")
APP_BUILD = "2026.09.21.8"

TRAINING_YEARS = (2017, 2018, 2019, 2023)
HOLDOUT_YEARS = (2024, 2025)
NEUTRAL_GAP_LIMIT = 5.0

LOW_RELIABILITY_STATES = {
    "Perlis",
    "W.P. Putrajaya",
}

NATIONAL_2025_CONTEXT = {
    "tourism_expenditure_rm_billion": 121.3,
    "tourism_expenditure_growth_pct": 13.6,
    "domestic_trips_million": 332.2,
    "trips_per_visitor": 1.15,
}

NATIONAL_2025_SPENDING = {
    "Shopping": 36.9,
    "Food & beverages": 16.1,
    "Automotive fuel": 13.5,
    "Other categories": 33.5,
}


def get_gemini_settings():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv(
        "GEMINI_MODEL",
        DEFAULT_GEMINI_MODEL,
    ).strip()

    return api_key, model or DEFAULT_GEMINI_MODEL

FEATURE_REQUIRED_COLUMNS = {
    "state",
    "year",
    "visitors_000",
    "log_gdp_per_capita",
    "rooms_per_1k_residents",
}

ML_REQUIRED_COLUMNS = {
    "state",
    "year",
    "visitors_000",
    "expected_visitors_000",
    "actual_share_pct",
    "expected_share_pct",
    "opportunity_gap_pp",
    "opportunity_gap_pct",
    "is_holdout_year",
}


def validate_columns(dataframe, required_columns, dataset_name):
    missing_columns = required_columns.difference(dataframe.columns)

    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))
        raise ValueError(
            f"{dataset_name} is missing required columns: {missing_text}"
        )


def validate_unique_state_year(dataframe, dataset_name):
    duplicate_rows = dataframe.duplicated(
        subset=["state", "year"],
        keep=False,
    )

    if duplicate_rows.any():
        duplicate_keys = (
            dataframe.loc[duplicate_rows, ["state", "year"]]
            .drop_duplicates()
            .sort_values(["year", "state"])
            .to_dict("records")
        )
        raise ValueError(
            f"{dataset_name} contains duplicate state-year rows: "
            f"{duplicate_keys}"
        )


def classify_opportunity_gap(gap_value):
    if pd.isna(gap_value):
        return {
            "label": "Data unavailable",
            "short_label": "Data unavailable",
            "category": "unavailable",
            "delta_color": "off",
        }

    if gap_value > NEUTRAL_GAP_LIMIT:
        return {
            "label": "Positive relative opportunity gap",
            "short_label": "Positive gap",
            "category": "positive_gap",
            "delta_color": "normal",
        }

    if gap_value < -NEUTRAL_GAP_LIMIT:
        return {
            "label": "Above model-expected share",
            "short_label": "Above benchmark",
            "category": "above_expected",
            "delta_color": "inverse",
        }

    return {
        "label": "Close to model expectation",
        "short_label": "Near benchmark",
        "category": "neutral",
        "delta_color": "off",
    }
    
def get_reliability_notes(state, year):
    notes = []

    if year in TRAINING_YEARS:
        notes.append(
            f"{year} is a model training year. This is an in-sample "
            "structural benchmark, not an independent validation result."
        )

    if year in HOLDOUT_YEARS:
        notes.append(
            f"{year} is part of the untouched holdout period used for "
            "out-of-sample evaluation."
        )

    if state in LOW_RELIABILITY_STATES:
        notes.append(
            f"{state} has higher-than-median holdout error. Interpret its "
            "opportunity gap as indicative rather than conclusive."
        )

    return notes


def build_deterministic_context(
    selected_region,
    selected_year,
    features,
    predictions,
):
    year_features = features[
        features["year"] == selected_year
    ].copy()
    year_predictions = predictions[
        predictions["year"] == selected_year
    ].copy()

    context = {
        "scope": selected_region,
        "year": int(selected_year),
        "is_holdout_year": selected_year in HOLDOUT_YEARS,
        "training_years": list(TRAINING_YEARS),
        "holdout_years": list(HOLDOUT_YEARS),
        "neutral_gap_limit_pct": NEUTRAL_GAP_LIMIT,
        "source": "DOSM official Malaysian tourism and socioeconomic data",
        "model": "Gradient Boosting structural expected-demand model",
        "limitations": [
            "The opportunity gap is a structural benchmark, not a forecast.",
            "The analysis does not establish the cause of a state's gap.",
            "Scenario calculations are illustrative and not estimated policy effects.",
        ],
        "decision_lenses": [
            "Prioritization should consider opportunity alignment, delivery readiness and downside risk together.",
            "A gap signal should trigger investigation before it triggers intervention.",
        ],
    }

    if selected_region == "Malaysia":
        meaningful_opportunities = (
            year_predictions[
                year_predictions["opportunity_gap_pct"]
                > NEUTRAL_GAP_LIMIT
            ]
            .sort_values(
                "opportunity_gap_pct",
                ascending=False,
            )
            .copy()
        )

        context["national_visitors_million"] = round(
            year_features["visitors_000"].sum() / 1000,
            4,
        )
        top_three_visitors = year_features.nlargest(3, "visitors_000")[
            "visitors_000"
        ].sum()
        national_visitors = year_features["visitors_000"].sum()
        context["top_three_visitor_concentration_pct"] = round(
            float(top_three_visitors / national_visitors * 100),
            2,
        )
        context["meaningful_opportunities"] = (
            meaningful_opportunities[
                [
                    "state",
                    "actual_share_pct",
                    "expected_share_pct",
                    "opportunity_gap_pct",
                ]
            ]
            .head(5)
            .to_dict("records")
        )

        if not meaningful_opportunities.empty:
            focus_row = meaningful_opportunities.iloc[0]
            context["focus_state"] = focus_row["state"]
            context["actual_share_pct"] = float(
                focus_row["actual_share_pct"]
            )
            context["expected_share_pct"] = float(
                focus_row["expected_share_pct"]
            )
            context["opportunity_gap_pct"] = float(
                focus_row["opportunity_gap_pct"]
            )
            context["gap_status"] = classify_opportunity_gap(
                focus_row["opportunity_gap_pct"]
            )
            context["reliability_notes"] = get_reliability_notes(
                focus_row["state"],
                selected_year,
            )
            focus_features = year_features[
                year_features["state"] == focus_row["state"]
            ]
            if not focus_features.empty:
                focus_feature_row = focus_features.iloc[0]
                context["focus_state_readiness_proxies"] = {
                    "rooms_per_1k_residents": round(
                        float(focus_feature_row["rooms_per_1k_residents"]),
                        4,
                    ),
                    "rooms_relative_to_state_median": (
                        "above"
                        if focus_feature_row["rooms_per_1k_residents"]
                        >= year_features["rooms_per_1k_residents"].median()
                        else "below"
                    ),
                    "economic_strength_relative_to_state_median": (
                        "above"
                        if focus_feature_row["log_gdp_per_capita"]
                        >= year_features["log_gdp_per_capita"].median()
                        else "below"
                    ),
                }
        else:
            context["focus_state"] = None
            context["reliability_notes"] = get_reliability_notes(
                None,
                selected_year,
            )

        return context

    selected_rows = year_predictions[
        year_predictions["state"] == selected_region
    ]

    if selected_rows.empty:
        context["data_available"] = False
        context["reliability_notes"] = [
            "No model output is available for this state-year selection."
        ]
        return context

    selected_row = selected_rows.iloc[0]
    selected_features = year_features[
        year_features["state"] == selected_region
    ]
    selected_history = features[
        (features["state"] == selected_region)
        & (features["year"] <= selected_year)
    ].sort_values("year")
    context.update(
        {
            "data_available": True,
            "focus_state": selected_region,
            "actual_visitors_million": round(
                float(selected_row["visitors_000"]) / 1000,
                4,
            ),
            "expected_visitors_million": round(
                float(selected_row["expected_visitors_000"]) / 1000,
                4,
            ),
            "actual_share_pct": float(
                selected_row["actual_share_pct"]
            ),
            "expected_share_pct": float(
                selected_row["expected_share_pct"]
            ),
            "opportunity_gap_pp": float(
                selected_row["opportunity_gap_pp"]
            ),
            "opportunity_gap_pct": float(
                selected_row["opportunity_gap_pct"]
            ),
            "gap_status": classify_opportunity_gap(
                selected_row["opportunity_gap_pct"]
            ),
            "reliability_notes": get_reliability_notes(
                selected_region,
                selected_year,
            ),
            "visitor_history": dataframe_records(
                selected_history.assign(
                    visitors_million=selected_history["visitors_000"] / 1000
                ),
                ["year", "visitors_million"],
            ),
        }
    )

    if not selected_features.empty:
        feature_row = selected_features.iloc[0]
        context["readiness_proxies"] = {
            "rooms_per_1k_residents": round(
                float(feature_row["rooms_per_1k_residents"]),
                4,
            ),
            "rooms_relative_to_state_median": (
                "above"
                if feature_row["rooms_per_1k_residents"]
                >= year_features["rooms_per_1k_residents"].median()
                else "below"
            ),
            "economic_strength_relative_to_state_median": (
                "above"
                if feature_row["log_gdp_per_capita"]
                >= year_features["log_gdp_per_capita"].median()
                else "below"
            ),
        }

    return context


def dataframe_records(dataframe, columns, digits=4):
    records = dataframe[columns].copy()
    numeric_columns = records.select_dtypes(include="number").columns
    records[numeric_columns] = records[numeric_columns].round(digits)
    return records.to_dict("records")


def build_visitor_flows_context(selected_year):
    observed = df[df["year"] <= selected_year].copy()
    selected = df[df["year"] == selected_year].copy()
    top_states = selected.nlargest(3, "visitors_M")["state"].tolist()
    trajectories = observed[observed["state"].isin(top_states)]
    trajectory_summaries = []
    for state in top_states:
        state_history = observed[observed["state"] == state].sort_values("year")
        if state_history.empty:
            continue

        first_row = state_history.iloc[0]
        last_row = state_history.iloc[-1]
        summary = {
            "state": state,
            "first_observed_year": int(first_row["year"]),
            "first_observed_visitors_million": round(
                float(first_row["visitors_M"]), 4
            ),
            "latest_observed_year": int(last_row["year"]),
            "latest_observed_visitors_million": round(
                float(last_row["visitors_M"]), 4
            ),
        }
        if len(state_history) >= 2:
            prior_row = state_history.iloc[-2]
            summary["prior_observed_year"] = int(prior_row["year"])
            summary["change_since_prior_observation_pct"] = round(
                (
                    (float(last_row["visitors_M"]) - float(prior_row["visitors_M"]))
                    / float(prior_row["visitors_M"])
                    * 100
                ),
                2,
            )
        trajectory_summaries.append(summary)

    national_total = selected["visitors_M"].sum()
    top_three_total = selected.nlargest(3, "visitors_M")["visitors_M"].sum()
    return {
        "page": "Visitor flows",
        "selected_year": int(selected_year),
        "observed_years": sorted(observed["year"].unique().tolist()),
        "missing_years": [2020, 2021, 2022],
        "top_states_by_visitors": dataframe_records(
            selected.nlargest(5, "visitors_M"),
            ["state", "year", "visitors_M"],
        ),
        "highlighted_trajectories": dataframe_records(
            trajectories.sort_values(["state", "year"]),
            ["state", "year", "visitors_M"],
        ),
        "trajectory_summaries": trajectory_summaries,
        "top_three_visitor_concentration_pct": round(
            float(top_three_total / national_total * 100), 2
        ),
        "decision_lenses": [
            "Distinguish persistent concentration from a temporary change between observations.",
            "Investigate whether growth is supported by destination capacity and visitor value, not volume alone.",
        ],
        "source": "DOSM official Malaysian tourism data",
        "limitations": [
            "No observations are available for 2020 to 2022.",
            "Lines are intentionally disconnected across missing years.",
            "Observed patterns do not establish causal drivers.",
        ],
    }


def build_sustainability_context(selected_year):
    selected = df[df["year"] == selected_year].copy()
    median_gdp = float(selected["log_gdp_per_capita"].median())
    median_rooms = float(selected["rooms_per_1k_residents"].median())
    median_visitors = float(selected["visitors_M"].median())
    selected["economic_position"] = selected["log_gdp_per_capita"].apply(
        lambda value: "above median" if value >= median_gdp else "below median"
    )
    selected["capacity_position"] = selected["rooms_per_1k_residents"].apply(
        lambda value: "above median" if value >= median_rooms else "below median"
    )
    selected["visitor_volume_position"] = selected["visitors_M"].apply(
        lambda value: "above median" if value >= median_visitors else "below median"
    )
    pressure_candidates = selected[
        (selected["visitors_M"] >= median_visitors)
        & (selected["rooms_per_1k_residents"] < median_rooms)
    ].sort_values("visitors_M", ascending=False)
    return {
        "page": "Sustainability",
        "selected_year": int(selected_year),
        "median_log_gdp_per_capita": round(median_gdp, 4),
        "median_rooms_per_1k_residents": round(median_rooms, 4),
        "median_visitors_million": round(median_visitors, 4),
        "state_capacity_evidence": dataframe_records(
            selected.sort_values("visitors_M", ascending=False),
            [
                "state",
                "log_gdp_per_capita",
                "rooms_per_1k_residents",
                "visitors_M",
                "economic_position",
                "capacity_position",
                "visitor_volume_position",
            ],
        ),
        "high_volume_below_median_room_supply": dataframe_records(
            pressure_candidates,
            ["state", "visitors_M", "rooms_per_1k_residents"],
        ),
        "decision_lenses": [
            "Use the chart to identify where readiness checks are most urgent, not to declare carrying-capacity limits.",
            "Validate accommodation occupancy, transport pressure, seasonality and resident impact before drawing a sustainability conclusion.",
        ],
        "source": "DOSM official Malaysian tourism and socioeconomic data",
        "limitations": [
            "The chart is descriptive and does not measure tourism carrying capacity.",
            "Bubble size shows visitor volume, not environmental impact.",
            "Median reference lines are analytical guides, not policy thresholds.",
        ],
    }


def build_scenario_context(
    selected_year,
    source_state,
    target_state,
    shift_pct,
    source_volume,
    target_volume,
    source_scenario_volume,
    target_scenario_volume,
    national_before,
    national_after,
):
    selected_features = df[df["year"] == selected_year].copy()
    selected_predictions = df_ml[df_ml["year"] == selected_year].copy()
    median_rooms = float(selected_features["rooms_per_1k_residents"].median())
    median_gdp = float(selected_features["log_gdp_per_capita"].median())

    def state_context(state, observed_volume, scenario_volume):
        feature_row = selected_features[
            selected_features["state"] == state
        ].iloc[0]
        prediction_row = selected_predictions[
            selected_predictions["state"] == state
        ].iloc[0]
        return {
            "state": state,
            "observed_visitors_million": round(observed_volume, 4),
            "scenario_visitors_million": round(scenario_volume, 4),
            "scenario_change_pct": round(
                (scenario_volume - observed_volume) / observed_volume * 100,
                2,
            ),
            "actual_visitor_share_pct": round(
                float(prediction_row["actual_share_pct"]), 4
            ),
            "model_expected_share_pct": round(
                float(prediction_row["expected_share_pct"]), 4
            ),
            "relative_opportunity_gap_pct": round(
                float(prediction_row["opportunity_gap_pct"]), 4
            ),
            "gap_interpretation": classify_opportunity_gap(
                prediction_row["opportunity_gap_pct"]
            )["label"],
            "rooms_per_1k_residents": round(
                float(feature_row["rooms_per_1k_residents"]), 4
            ),
            "room_supply_relative_to_state_median": (
                "above"
                if feature_row["rooms_per_1k_residents"] >= median_rooms
                else "below"
            ),
            "economic_strength_relative_to_state_median": (
                "above"
                if feature_row["log_gdp_per_capita"] >= median_gdp
                else "below"
            ),
            "reliability_notes": get_reliability_notes(state, selected_year),
        }

    return {
        "page": "Scenario lab",
        "selected_year": int(selected_year),
        "source_state_evidence": state_context(
            source_state,
            source_volume,
            source_scenario_volume,
        ),
        "target_state_evidence": state_context(
            target_state,
            target_volume,
            target_scenario_volume,
        ),
        "illustrative_shift_pct": int(shift_pct),
        "illustrative_transfer_million": round(
            source_volume - source_scenario_volume, 4
        ),
        "national_before_million": round(float(national_before), 4),
        "national_after_million": round(float(national_after), 4),
        "decision_lenses": [
            "Does the target's structural opportunity signal align with the direction of the scenario?",
            "Could the target absorb additional volume without creating a readiness bottleneck?",
            "What visitor behavior, cost, seasonality and local-impact evidence is missing?",
            "What downside would the source state face if demand were displaced rather than expanded?",
        ],
        "source": "Arithmetic transformation of DOSM observed visitor volumes",
        "limitations": [
            "This is an illustrative arithmetic scenario, not a forecast.",
            "It does not estimate behavioral responses, costs or policy feasibility.",
            "The national visitor total is held constant by construction.",
        ],
    }


def build_evidence_context(selected_year):
    selected_predictions = df_ml[df_ml["year"] == selected_year].copy()
    return {
        "page": "Evidence",
        "selected_year": int(selected_year),
        "training_years": list(TRAINING_YEARS),
        "holdout_years": list(HOLDOUT_YEARS),
        "total_records": int(len(df)),
        "total_states": int(df["state"].nunique()),
        "observed_years": sorted(df["year"].unique().tolist()),
        "selected_year_model_output": dataframe_records(
            selected_predictions.sort_values(
                "opportunity_gap_pct", ascending=False
            ),
            [
                "state",
                "actual_share_pct",
                "expected_share_pct",
                "opportunity_gap_pct",
                "is_holdout_year",
            ],
        ),
        "model": "Gradient Boosting structural expected-demand model",
        "source": "DOSM official Malaysian tourism and socioeconomic data",
        "limitations": [
            "The expected value is a structural benchmark, not a forecast.",
            "The model does not establish causes for observed gaps.",
            "Perlis and W.P. Putrajaya require additional reliability caution.",
        ],
    }


# --- 1. Page Configuration ---
st.set_page_config(
    page_title="LestariLens Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
        #MainMenu {
            visibility: hidden;
        }

        :root {
            color-scheme: light only;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

OLLIE_CHAT_HTML = """
<div class="ollie-chat-shell">
  <div class="ollie-chat-frame">
    <div class="ollie-chat-toolbar">
      <span>Conversation</span>
      <button id="ollie-clear" class="ollie-clear" type="button">Clear</button>
    </div>
    <div id="ollie-messages" class="ollie-messages" aria-live="polite"></div>
  </div>
  <div id="ollie-suggestions" class="ollie-suggestions"></div>
  <div class="ollie-composer">
    <textarea
      id="ollie-input"
      rows="2"
      placeholder="Ask Ollie about this page"
      aria-label="Ask Ollie about this page"
    ></textarea>
    <div class="ollie-actions">
      <button
        id="ollie-mic"
        class="ollie-icon-button"
        type="button"
        aria-label="Start voice input"
        title="Start voice input"
      >
        <span class="ollie-mic-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" focusable="false">
            <rect x="9" y="3" width="6" height="11" rx="3"></rect>
            <path d="M6.5 11.5a5.5 5.5 0 0 0 11 0"></path>
            <path d="M12 17v4"></path>
            <path d="M9 21h6"></path>
          </svg>
        </span>
        <span class="ollie-stop-icon" aria-hidden="true"></span>
      </button>
      <button
        id="ollie-send"
        class="ollie-icon-button ollie-send"
        type="button"
        aria-label="Send question"
        title="Send question"
      >
        <span class="ollie-send-icon">&#8593;</span>
        <span class="ollie-spinner" aria-hidden="true"></span>
      </button>
    </div>
  </div>
  <div id="ollie-status" class="ollie-status" role="status"></div>
</div>
"""

OLLIE_CHAT_CSS = """
.ollie-chat-shell {
  box-sizing: border-box;
  color: var(--st-text-color, #2d3142);
  font-family: var(--st-font, "Inter", sans-serif);
  overflow: hidden;
  width: 100%;
}

.ollie-chat-frame {
  background: rgba(255, 255, 255, 0.48);
  border: 1px solid rgba(45, 49, 66, 0.16);
  border-radius: 12px;
  overflow: hidden;
}

.ollie-chat-toolbar {
  align-items: center;
  border-bottom: 1px solid rgba(45, 49, 66, 0.09);
  color: #737780;
  display: flex;
  font-size: 0.72rem;
  justify-content: space-between;
  min-height: 32px;
  padding: 0 10px;
}

.ollie-clear {
  background: transparent;
  border: 0;
  color: #69706d;
  cursor: pointer;
  font: inherit;
  padding: 4px 2px;
}

.ollie-clear:hover {
  color: #2d3142;
}

.ollie-messages {
  box-sizing: border-box;
  overflow-y: auto;
  padding: 10px;
  scroll-behavior: smooth;
}

.ollie-empty {
  color: #737780;
  font-size: 0.78rem;
  line-height: 1.45;
  margin: 4px 2px 10px;
}

.ollie-message {
  display: flex;
  gap: 7px;
  margin-bottom: 10px;
  scroll-margin-top: 8px;
}

.ollie-message.user {
  justify-content: flex-end;
}

.ollie-bubble {
  background: #ffffff;
  border: 1px solid rgba(45, 49, 66, 0.08);
  border-radius: 10px;
  box-sizing: border-box;
  font-size: 0.78rem;
  line-height: 1.43;
  max-width: calc(100% - 35px);
  overflow-wrap: anywhere;
  padding: 8px 9px;
  white-space: pre-wrap;
}

.ollie-message.user .ollie-bubble {
  background: #3b3c54;
  color: #ffffff;
  max-width: 88%;
}

.ollie-message.assistant {
  display: block;
}

.ollie-message.assistant .ollie-bubble {
  background: transparent;
  border: 0;
  max-width: 100%;
  padding: 2px 4px 8px;
}

.ollie-thinking-row {
  align-items: center;
  display: flex;
}

.ollie-thinking-avatar {
  flex: 0 0 24px;
  height: 24px;
  image-rendering: pixelated;
  object-fit: contain;
  width: 24px;
}

.ollie-thinking-label {
  animation: ollie-shimmer 1.35s linear infinite;
  background: linear-gradient(
    90deg,
    #777b84 10%,
    #d9a078 42%,
    #ffffff 50%,
    #d9a078 58%,
    #777b84 90%
  );
  background-clip: text;
  background-size: 220% 100%;
  color: transparent;
  font-size: 0.76rem;
  font-weight: 600;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.ollie-implications {
  border-top: 1px solid rgba(45, 49, 66, 0.08);
  margin-top: 7px;
  padding-top: 6px;
}

.ollie-implications-title {
  font-size: 0.7rem;
  font-weight: 700;
  margin-bottom: 3px;
}

.ollie-implications ul {
  margin: 0;
  padding-left: 16px;
}

.ollie-caveat {
  color: #737780;
  font-size: 0.67rem;
  line-height: 1.35;
  margin-top: 7px;
}

.ollie-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 8px 0;
}

.ollie-suggestion-label {
  color: #737780;
  flex-basis: 100%;
  font-size: 0.68rem;
  margin-bottom: -1px;
}

.ollie-chip {
  background: rgba(133, 168, 143, 0.16);
  border: 1px solid rgba(78, 111, 88, 0.28);
  border-radius: 999px;
  color: #405d48;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.69rem;
  line-height: 1.25;
  padding: 6px 9px;
  text-align: left;
}

.ollie-chip:hover {
  background: rgba(133, 168, 143, 0.28);
  border-color: rgba(78, 111, 88, 0.5);
}

.ollie-composer {
  align-items: flex-end;
  background: #ffffff;
  border: 1px solid #c9cec7;
  border-radius: 12px;
  box-sizing: border-box;
  display: flex;
  gap: 7px;
  padding: 7px;
  width: 100%;
}

.ollie-composer:focus-within {
  border-color: #85a88f;
  box-shadow: 0 0 0 2px rgba(133, 168, 143, 0.18);
}

#ollie-input {
  background: transparent;
  border: 0;
  box-sizing: border-box;
  color: #2d3142;
  flex: 1;
  font-family: inherit;
  font-size: 0.78rem;
  line-height: 1.4;
  max-height: 108px;
  min-height: 50px;
  outline: 0;
  overflow-y: auto;
  padding: 5px 4px;
  resize: none;
}

#ollie-input::placeholder {
  color: #8a8d95;
}

.ollie-actions {
  display: flex;
  flex: 0 0 auto;
  gap: 5px;
}

.ollie-icon-button {
  align-items: center;
  background: #85a88f;
  border: 0;
  border-radius: 999px;
  color: #ffffff;
  cursor: pointer;
  display: inline-flex;
  height: 36px;
  justify-content: center;
  padding: 0;
  width: 36px;
}

.ollie-icon-button:hover {
  background: #72967c;
}

.ollie-icon-button:disabled {
  background: #dfe3df;
  color: #9ca19d;
  cursor: default;
}

.ollie-icon-button.recording {
  background: #85a88f;
}

.ollie-mic-icon {
  display: inline-flex;
  height: 19px;
  width: 19px;
}

.ollie-mic-icon svg {
  fill: none;
  height: 100%;
  stroke: #ffffff;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
  width: 100%;
}

.ollie-mic-icon svg rect {
  fill: #ffffff;
  stroke: none;
}

.ollie-stop-icon {
  background: #ffffff;
  border-radius: 2px;
  display: none;
  height: 12px;
  width: 12px;
}

.ollie-icon-button.recording .ollie-mic-icon {
  display: none;
}

.ollie-icon-button.recording .ollie-stop-icon {
  display: block;
}

.ollie-send {
  background: #e27d60;
  font-size: 1.25rem;
  font-weight: 700;
}

.ollie-send:hover {
  background: #d36c4f;
}

.ollie-spinner {
  animation: ollie-spin 0.8s linear infinite;
  border: 2px solid rgba(255, 255, 255, 0.42);
  border-radius: 50%;
  border-top-color: #ffffff;
  display: none;
  height: 14px;
  width: 14px;
}

.ollie-send.sending .ollie-send-icon {
  display: none;
}

.ollie-send.sending .ollie-spinner {
  display: block;
}

.ollie-status {
  color: #9b5b49;
  font-size: 0.67rem;
  line-height: 1.35;
  min-height: 0;
  padding: 5px 2px 0;
}

@keyframes ollie-spin {
  to { transform: rotate(360deg); }
}

@keyframes ollie-shimmer {
  from { background-position: 120% 0; }
  to { background-position: -120% 0; }
}
"""

OLLIE_CHAT_JS = """
const ollieInstances = new WeakMap()

function createElement(tagName, className, text) {
  const element = document.createElement(tagName)
  if (className) element.className = className
  if (typeof text === "string") element.textContent = text
  return element
}

export default function (component) {
  const { data, parentElement, setTriggerValue } = component
  const messagesElement = parentElement.querySelector("#ollie-messages")
  const suggestionsElement = parentElement.querySelector("#ollie-suggestions")
  const inputElement = parentElement.querySelector("#ollie-input")
  const microphoneButton = parentElement.querySelector("#ollie-mic")
  const sendButton = parentElement.querySelector("#ollie-send")
  const clearButton = parentElement.querySelector("#ollie-clear")
  const statusElement = parentElement.querySelector("#ollie-status")

  if (
    !messagesElement ||
    !suggestionsElement ||
    !inputElement ||
    !microphoneButton ||
    !sendButton ||
    !clearButton ||
    !statusElement
  ) return

  const componentHost = parentElement.host || parentElement
  if (componentHost && componentHost.style) {
    componentHost.style.overflow = "hidden"
  }
  messagesElement.style.height = `${data.conversation_height || 90}px`

  let instance = ollieInstances.get(parentElement)
  if (!instance) {
    instance = {
      recognition: null,
      recording: false,
      wantsRecording: false,
      baseText: "",
      finalTranscript: "",
      messageSignature: "",
      pendingQuestion: "",
    }
    ollieInstances.set(parentElement, instance)
  }

  const setSending = isSending => {
    sendButton.classList.toggle("sending", isSending)
    sendButton.disabled = isSending
    microphoneButton.disabled = isSending
  }

  const resizeInput = () => {
    inputElement.style.height = "auto"
    inputElement.style.height = `${Math.min(inputElement.scrollHeight, 108)}px`
  }

  const submitQuestion = question => {
    const cleanedQuestion = String(question || "").trim()
    if (!cleanedQuestion || sendButton.disabled) return
    if (instance.recording && instance.recognition) {
      instance.wantsRecording = false
      instance.recognition.stop()
    }
    statusElement.textContent = ""
    instance.pendingQuestion = cleanedQuestion
    const chatFrame = parentElement.querySelector(".ollie-chat-frame")
    chatFrame.style.display = "block"

    const pendingUserRow = createElement("div", "ollie-message user")
    pendingUserRow.dataset.role = "user"
    pendingUserRow.appendChild(
      createElement("div", "ollie-bubble", cleanedQuestion)
    )
    messagesElement.appendChild(pendingUserRow)

    const thinkingRow = createElement(
      "div",
      "ollie-message assistant ollie-thinking-row"
    )
    thinkingRow.dataset.role = "thinking"
    if (data.thinking_avatar_url) {
      const walkingTiger = createElement("img", "ollie-thinking-avatar")
      walkingTiger.src = data.thinking_avatar_url
      walkingTiger.alt = ""
      thinkingRow.appendChild(walkingTiger)
    }
    thinkingRow.appendChild(
      createElement("span", "ollie-thinking-label", "Thinking...")
    )
    messagesElement.appendChild(thinkingRow)

    inputElement.value = ""
    resizeInput()
    suggestionsElement.replaceChildren()
    setSending(true)
    requestAnimationFrame(() => {
      messagesElement.scrollTop = Math.max(0, pendingUserRow.offsetTop - 42)
    })
    setTriggerValue("submitted", cleanedQuestion)
  }

  const renderChip = (label, question) => {
    const button = createElement("button", "ollie-chip", label)
    button.type = "button"
    button.onclick = () => submitQuestion(question)
    suggestionsElement.appendChild(button)
  }

  const renderMessages = messages => {
    const chatFrame = parentElement.querySelector(".ollie-chat-frame")
    messagesElement.replaceChildren()

    if (!messages.length) {
      chatFrame.style.display = "none"
      return
    }
    chatFrame.style.display = "block"

    messages.forEach(message => {
      const row = createElement("div", `ollie-message ${message.role}`)
      row.dataset.role = message.role

      const bubble = createElement("div", "ollie-bubble", message.content || "")

      if (message.role === "assistant" && message.planning_implications?.length) {
        const implications = createElement("div", "ollie-implications")
        implications.appendChild(
          createElement("div", "ollie-implications-title", "What this could mean")
        )
        const list = createElement("ul")
        message.planning_implications.forEach(item => {
          list.appendChild(createElement("li", "", item))
        })
        implications.appendChild(list)
        bubble.appendChild(implications)
      }

      if (message.role === "assistant" && message.caveat) {
        bubble.appendChild(
          createElement("div", "ollie-caveat", `Limit: ${message.caveat}`)
        )
      }

      row.appendChild(bubble)
      messagesElement.appendChild(row)
    })
  }

  const messages = Array.isArray(data.messages) ? data.messages : []
  const messageSignature = JSON.stringify(
    messages.map(message => [message.role, message.content, message.caveat])
  )

  if (messageSignature !== instance.messageSignature) {
    instance.messageSignature = messageSignature
    renderMessages(messages)
    inputElement.value = ""
    instance.pendingQuestion = ""
    setSending(false)
    requestAnimationFrame(() => {
      const assistantMessages = messagesElement.querySelectorAll(
        '[data-role="assistant"]'
      )
      const target = assistantMessages[assistantMessages.length - 1]
      if (target) {
        messagesElement.scrollTop = Math.max(0, target.offsetTop - 42)
      } else {
        messagesElement.scrollTop = messagesElement.scrollHeight
      }
    })
  }

  suggestionsElement.replaceChildren()
  const followUps = messages.length
    ? messages[messages.length - 1]?.follow_up_prompts || []
    : data.initial_suggestions || []
  if (followUps.length) {
    suggestionsElement.appendChild(
      createElement(
        "div",
        "ollie-suggestion-label",
        messages.length ? "Ask next" : "Try asking"
      )
    )
    followUps.forEach(prompt => renderChip(prompt, prompt))
  }

  clearButton.style.visibility = messages.length ? "visible" : "hidden"
  statusElement.textContent = data.error || ""
  if (data.error) {
    renderMessages(messages)
    inputElement.value = instance.pendingQuestion
    instance.pendingQuestion = ""
    setSending(false)
    resizeInput()
  }

  inputElement.oninput = () => {
    statusElement.textContent = ""
    resizeInput()
  }
  inputElement.onkeydown = event => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault()
      submitQuestion(inputElement.value)
    }
  }
  sendButton.onclick = () => submitQuestion(inputElement.value)
  clearButton.onclick = () => {
    statusElement.textContent = ""
    setTriggerValue("cleared", Date.now())
  }

  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition

  if (!SpeechRecognition) {
    microphoneButton.disabled = true
    microphoneButton.title = "Voice input is unavailable in this browser"
  } else if (!instance.recognition) {
    const recognition = new SpeechRecognition()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = data.speech_language || "en-MY"

    recognition.onstart = () => {
      instance.recording = true
      instance.baseText = inputElement.value.trim()
      instance.finalTranscript = ""
      microphoneButton.classList.add("recording")
      microphoneButton.setAttribute("aria-label", "Stop voice input")
      microphoneButton.title = "Stop voice input"
      statusElement.textContent = ""
    }

    recognition.onresult = event => {
      let interimTranscript = ""
      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        const transcript = event.results[index][0].transcript.trim()
        if (event.results[index].isFinal) {
          instance.finalTranscript = `${instance.finalTranscript} ${transcript}`.trim()
        } else {
          interimTranscript = `${interimTranscript} ${transcript}`.trim()
        }
      }
      inputElement.value = [
        instance.baseText,
        instance.finalTranscript,
        interimTranscript,
      ].filter(Boolean).join(" ")
      resizeInput()
      inputElement.focus()
    }

    recognition.onerror = event => {
      instance.wantsRecording = false
      statusElement.textContent =
        event.error === "not-allowed"
          ? "Microphone access was not allowed."
          : "Voice input could not continue."
    }

    recognition.onend = () => {
      instance.recording = false
      if (instance.wantsRecording && !sendButton.disabled) {
        try {
          recognition.start()
          return
        } catch (error) {
          instance.wantsRecording = false
        }
      }
      microphoneButton.classList.remove("recording")
      microphoneButton.setAttribute("aria-label", "Start voice input")
      microphoneButton.title = "Start voice input"
    }

    instance.recognition = recognition
  }

  microphoneButton.onclick = () => {
    if (!instance.recognition) return
    if (instance.recording) {
      instance.wantsRecording = false
      instance.recognition.stop()
    } else {
      try {
        instance.wantsRecording = true
        instance.recognition.start()
      } catch (error) {
        instance.wantsRecording = false
        statusElement.textContent = "Voice input could not start."
      }
    }
  }
}
"""

OLLIE_CHAT_COMPONENT = st.components.v2.component(
    "lestari_ollie_chat",
    html=OLLIE_CHAT_HTML,
    css=OLLIE_CHAT_CSS,
    js=OLLIE_CHAT_JS,
)

# --- 2. Safe Global CSS for Premium UI ---
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #F7F5F0 !important; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #EBE8DE !important; border-right: 1px solid #DEDAD0; }
    [data-testid="stHeader"] { background-color: transparent !important; }
    [data-testid="stSidebarHeader"] {
        height: 3.25rem !important;
        min-height: 3.25rem !important;
        padding: 0.45rem 0.75rem !important;
    }
    [data-testid="stSidebarUserContent"] {
        margin-top: -3.25rem !important;
        padding-top: 0 !important;
    }
    [data-testid="stSidebarContent"] { padding-top: 0 !important; }
    
    .block-container { padding-top: 2.5rem !important; max-width: 1400px !important; }
    h1, h2, h3 { color: #2D3142 !important; font-weight: 600 !important; margin-top:0; padding-top:0;}
    .sub-header { color: #E27D60; font-size: 0.85rem; text-transform: uppercase; font-weight: 700; margin-bottom: -15px; letter-spacing: 1px;}

    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03) !important;
        border: 1px solid #EAE6DB !important;
    }

    /* Fixed Metric wrapping for long state names */
    [data-testid="stMetricValue"] { color: #2D3142 !important; font-weight: 700 !important; white-space: normal !important; line-height: 1.1 !important; font-size: 1.6rem !important;}
    [data-testid="stMetricValue"] > div { white-space: normal !important; }
    [data-testid="stMetricLabel"] { color: #888C95 !important; font-weight: 600 !important; white-space: normal !important; }

    .stButton>button { border-radius: 8px !important; font-weight: bold !important; transition: 0.2s; border: none !important; }
    button[kind="primary"] { background-color: #E27D60 !important; color: white !important; }
    button[kind="secondary"] { background-color: #85A88F !important; color: white !important; border-radius: 20px !important; }
    button[kind="primary"]:hover { background-color: #D36C4F !important; }
    button[kind="secondary"]:hover { background-color: #72967C !important; }
    
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { display: none; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        padding: 10px 15px; border-radius: 8px; margin-bottom: 5px; background-color: transparent; transition: 0.2s all; cursor: pointer;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover { background-color: rgba(0,0,0,0.05); }
    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #FFFFFF; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] p {
        color: #E27D60 !important; font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. Data Loading (Dynamic Relative Paths) ---
@st.cache_data
def load_data():
    project_root = Path(__file__).resolve().parents[1]

    features_path = (
        project_root
        / "ml"
        / "handoff"
        / "for_hongyik"
        / "state_features.csv"
    )
    predictions_path = (
        project_root
        / "ml"
        / "handoff"
        / "for_hongyik"
        / "sample_predictions.csv"
    )

    if not features_path.exists():
        raise FileNotFoundError(
            f"State features file was not found: {features_path}"
        )

    if not predictions_path.exists():
        raise FileNotFoundError(
            f"Prediction file was not found: {predictions_path}"
        )

    features = pd.read_csv(features_path)
    predictions = pd.read_csv(predictions_path)

    validate_columns(
        features,
        FEATURE_REQUIRED_COLUMNS,
        "state_features.csv",
    )
    validate_columns(
        predictions,
        ML_REQUIRED_COLUMNS,
        "sample_predictions.csv",
    )

    features["year"] = pd.to_numeric(
        features["year"],
        errors="raise",
    ).astype(int)
    predictions["year"] = pd.to_numeric(
        predictions["year"],
        errors="raise",
    ).astype(int)

    validate_unique_state_year(
        features,
        "state_features.csv",
    )
    validate_unique_state_year(
        predictions,
        "sample_predictions.csv",
    )

    feature_keys = set(
        features[["state", "year"]].itertuples(
            index=False,
            name=None,
        )
    )
    prediction_keys = set(
        predictions[["state", "year"]].itertuples(
            index=False,
            name=None,
        )
    )

    if feature_keys != prediction_keys:
        missing_predictions = sorted(feature_keys - prediction_keys)
        missing_features = sorted(prediction_keys - feature_keys)

        raise ValueError(
            "The feature and prediction datasets do not contain the same "
            f"state-year keys. Missing predictions: {missing_predictions}. "
            f"Missing features: {missing_features}."
        )

    features["visitors_M"] = features["visitors_000"] / 1000

    available_years = set(features["year"].unique())
    expected_years = set(TRAINING_YEARS + HOLDOUT_YEARS)

    if available_years != expected_years:
        raise ValueError(
            "Unexpected analytical years. "
            f"Expected {sorted(expected_years)}, "
            f"received {sorted(available_years)}."
        )

    return features, predictions


try:
    df, df_ml = load_data()
except Exception as error:
    st.error(
        "The dashboard could not validate its analytical data. "
        "Check the files in ml/handoff/for_hongyik/."
    )
    st.exception(error)
    st.stop()


# --- 4. Sidebar Navigation & Global Filters ---
with st.sidebar:
    st.markdown("<h2 style='color:#E27D60; margin:0; padding-right:3.25rem; font-size:1.8rem; line-height:3.25rem;'>🎯 LestariLens</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.75rem; color:#737373; font-weight:bold; letter-spacing:1px; margin-top:-5px; margin-bottom:12px;'>MALAYSIA TOURISM<br>INTELLIGENCE</p>", unsafe_allow_html=True)
    
    selected_page = st.radio("Navigation", ["Overview", "Visitor flows", "Sustainability", "Scenario lab", "Evidence"], label_visibility="collapsed")
    
    st.markdown("<p style='font-size:0.85rem; color:#2D3142; font-weight:bold; margin:8px 0 -5px;'>📅 Global Year Filter</p>", unsafe_allow_html=True)
    
    available_years = sorted(df['year'].unique().tolist(), reverse=True)
    selected_year = st.selectbox("Year", available_years, label_visibility="collapsed")

    st.markdown("""
    <div style="background-color: #DDE2DA; padding: 12px 14px; margin-top: 14px; border-radius: 8px; font-size: 0.78rem; color: #555; line-height: 1.45;">
        <b>DOSM official data first</b><br><br>Every insight shows its source, year and analytical limitation.
    </div>
    """, unsafe_allow_html=True)

    ollie_sidebar_slot = st.container()


@st.cache_data
def load_ollie_assets():
    sprite_path = PROJECT_ROOT / "assets" / "images" / "tiger_sheet.png"
    if not sprite_path.exists():
        return None, None

    sprite = Image.open(sprite_path).convert("RGBA")
    frame_size = 64
    def build_animation(row_index, duration):
        frames = [
            sprite.crop(
                (
                    column_index * frame_size,
                    row_index * frame_size,
                    (column_index + 1) * frame_size,
                    (row_index + 1) * frame_size,
                )
            )
            for column_index in range(4)
        ]
        animation_buffer = BytesIO()
        frames[0].save(
            animation_buffer,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=0,
            disposal=2,
        )
        return animation_buffer.getvalue()

    status_animation = build_animation(
        row_index=7,
        duration=180,
    )
    thinking_animation = build_animation(
        row_index=5,
        duration=135,
    )
    return status_animation, thinking_animation


def render_ollie_status(image_placeholder, copy_placeholder, title, subtitle):
    animation_bytes, _ = load_ollie_assets()
    if animation_bytes:
        image_placeholder.image(animation_bytes, width=64)
    else:
        image_placeholder.markdown("## 🐯")
    copy_placeholder.markdown(f"**{title}**  \n{subtitle}")


def get_ollie_suggestions(page_name):
    suggestions = {
        "Overview": [
            "Why does this gap matter?",
            "What should planners compare?",
        ],
        "Visitor flows": [
            "Is this growth concentrated?",
            "What risk could follow?",
        ],
        "Sustainability": [
            "Where could capacity tighten?",
            "What should be validated?",
        ],
        "Scenario lab": [
            "What trade-offs emerge?",
            "Is the target ready?",
        ],
        "Evidence": [
            "How reliable is this gap?",
            "What can this model not prove?",
        ],
    }
    return suggestions.get(page_name, [])


def render_ollie_assistant(context, page_name, year, sidebar_slot):
    api_key, model = get_gemini_settings()
    st.session_state.setdefault("ollie_messages", [])
    error_key = f"ollie_error::{page_name}::{year}"

    with sidebar_slot:
        st.divider()
        status_image_column, status_copy_column = st.columns([1, 3])
        status_image_placeholder = status_image_column.empty()
        status_copy_placeholder = status_copy_column.empty()
        render_ollie_status(
            image_placeholder=status_image_placeholder,
            copy_placeholder=status_copy_placeholder,
            title="Ask Ollie",
            subtitle="Ask follow-ups grounded in this page's validated data",
        )

        current_messages = [
            message
            for message in st.session_state["ollie_messages"]
            if message["page"] == page_name and message["year"] == year
        ]
        _, thinking_animation_bytes = load_ollie_assets()
        thinking_avatar_url = ""
        if thinking_animation_bytes:
            encoded_thinking_icon = base64.b64encode(
                thinking_animation_bytes
            ).decode("ascii")
            thinking_avatar_url = (
                f"data:image/gif;base64,{encoded_thinking_icon}"
            )

        component_messages = [
            {
                "role": message["role"],
                "content": message["content"],
                "planning_implications": message.get(
                    "planning_implications", []
                ),
                "follow_up_prompts": message.get("follow_up_prompts", []),
                "caveat": message.get("caveat", ""),
            }
            for message in current_messages
        ]

        has_conversation = bool(current_messages)
        conversation_height = 360 if has_conversation else 90
        component_height = 555 if has_conversation else 205

        chat_result = OLLIE_CHAT_COMPONENT(
            key=f"ollie_chat::{page_name}::{year}",
            data={
                "messages": component_messages,
                "initial_suggestions": get_ollie_suggestions(page_name),
                "thinking_avatar_url": thinking_avatar_url,
                "conversation_height": conversation_height,
                "speech_language": "en-MY",
                "error": st.session_state.get(error_key, ""),
            },
            on_submitted_change=lambda: None,
            on_cleared_change=lambda: None,
            width="stretch",
            height=component_height,
        )

        if getattr(chat_result, "cleared", None):
            st.session_state["ollie_messages"] = [
                message
                for message in st.session_state["ollie_messages"]
                if not (
                    message["page"] == page_name
                    and message["year"] == year
                )
            ]
            st.session_state.pop(error_key, None)
            st.rerun()

        submitted_question = (
            getattr(chat_result, "submitted", None) or ""
        ).strip()
        if submitted_question:
            question = submitted_question

            if not api_key:
                st.session_state[error_key] = (
                    "Ollie is unavailable because GEMINI_API_KEY is not "
                    "configured in the project .env file."
                )
                st.rerun()

            model_history = [
                {
                    "role": message["role"],
                    "content": message["content"],
                }
                for message in current_messages[-6:]
            ]
            st.session_state.pop(error_key, None)

            try:
                answer = generate_contextual_answer(
                    api_key=api_key,
                    context=context,
                    question=question,
                    history=model_history,
                    model=model,
                )

                st.session_state["ollie_messages"].extend(
                    [
                        {
                            "role": "user",
                            "content": question,
                            "page": page_name,
                            "year": year,
                        },
                        {
                            "role": "assistant",
                            "content": answer.direct_answer,
                            "planning_implications": answer.planning_implications,
                            "follow_up_prompts": answer.follow_up_prompts,
                            "caveat": answer.caveat,
                            "page": page_name,
                            "year": year,
                        },
                    ]
                )
                st.session_state["ollie_messages"] = st.session_state[
                    "ollie_messages"
                ][-30:]
                st.session_state.pop(error_key, None)
                st.rerun()
            except GeminiAssistantError:
                st.session_state[error_key] = (
                    "That request was not completed because Ollie could not "
                    "validate the response against this page. Your previous "
                    "answer, if any, is still shown above."
                )
                st.rerun()


# ==========================================
# PAGE 1: OVERVIEW DASHBOARD
# ==========================================
def render_overview():
    col_head1, col_head2 = st.columns([2.5, 1.5])
    states_list = ["Malaysia"] + sorted(df['state'].unique().tolist())

    with col_head1:
        st.markdown(f'<p class="sub-header">NATIONAL PULSE · {selected_year} OVERVIEW</p>', unsafe_allow_html=True)
        st.markdown('<h1>Grow tourism value.<br>Protect what makes Malaysia special.</h1>', unsafe_allow_html=True)

    with col_head2:
        st.markdown("<br>", unsafe_allow_html=True)
        selected_region = st.selectbox("Region", states_list, label_visibility="collapsed")
        st.caption(
            "Use Ollie in the sidebar to explore implications and follow-up "
            "questions for this selection."
        )

    # Time calculations
    all_years_sorted = sorted(df['year'].unique().tolist())
    curr_idx = all_years_sorted.index(selected_year)
    prev_year = all_years_sorted[curr_idx - 1] if curr_idx > 0 else None

    # Sync ML Data with Selected Year
    ml_selected_year = df_ml[df_ml['year'] == selected_year].copy()

    # Filtering Logic
    if selected_region == "Malaysia":
        df_current = df[df['year'] == selected_year]
        df_prev = df[df['year'] == prev_year] if prev_year else pd.DataFrame()
        
        # Sort ONLY the selected year's ML data
        chart_data = ml_selected_year.sort_values(by='opportunity_gap_pct', ascending=False).head(5).copy()
        chart_title = f"Top Untapped Potential (ML Opportunity Gap %, {selected_year})"
        y_axis = 'state'
        x_axis = 'opportunity_gap_pct'
        
        # Safe extraction
        if not chart_data.empty:
            top_ml_state = chart_data.iloc[0]['state']
            top_ml_gap = chart_data.iloc[0]['opportunity_gap_pct']
            top2_ml_state = chart_data.iloc[1]['state'] if len(chart_data) > 1 else ""
        else:
            top_ml_state, top_ml_gap, top2_ml_state = "N/A", 0, ""
            
    else:
        df_current = df[(df['year'] == selected_year) & (df['state'] == selected_region)]
        df_prev = df[(df['year'] == prev_year) & (df['state'] == selected_region)] if prev_year else pd.DataFrame()
        
        chart_data = df[(df['state'] == selected_region) & (df['year'] <= selected_year)].sort_values(by='year', ascending=True).tail(5).copy()
        chart_data['year'] = chart_data['year'].astype(str)
        chart_title = f"Historical Visitor Trend ({selected_region})"
        y_axis = 'year'
        x_axis = 'visitors_M'
        
        top_ml_state = selected_region
        ml_filter = ml_selected_year[ml_selected_year['state'] == selected_region]
        top_ml_gap = ml_filter['opportunity_gap_pct'].values[0] if not ml_filter.empty else 0

    v_current = df_current['visitors_M'].sum() if not df_current.empty else 0
    v_prev = df_prev['visitors_M'].sum() if not df_prev.empty else 0
    v_growth = ((v_current - v_prev) / v_prev) * 100 if v_prev > 0 else 0
    insight_context = build_deterministic_context(
        selected_region=selected_region,
        selected_year=selected_year,
        features=df,
        predictions=df_ml,
    )

    if prev_year:
        delta_label = f"↑ {v_growth:.1f}% vs {prev_year}" if v_growth >= 0 else f"↓ {abs(v_growth):.1f}% vs {prev_year}"
    else:
        delta_label = None

    st.markdown("<br>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)

    with k1.container(border=True):
        st.metric(
            label=f"Domestic visitors ({selected_year})",
            value=f"{v_current:.1f}M",
            delta=delta_label,
        )

    with k2.container(border=True):
        if selected_region == "Malaysia":
            if selected_year == 2025:
                expenditure = NATIONAL_2025_CONTEXT[
                    "tourism_expenditure_rm_billion"
                ]
                expenditure_growth = NATIONAL_2025_CONTEXT[
                    "tourism_expenditure_growth_pct"
                ]
                st.metric(
                    label="Tourism expenditure (2025)",
                    value=f"RM{expenditure:.1f}B",
                    delta=f"+{expenditure_growth:.1f}% year-on-year",
                )
            else:
                st.metric(
                    label="Tourism expenditure",
                    value="Not available",
                    delta="2025 only",
                    delta_color="off",
                )
                st.caption(
                    "The current dashboard source provides national tourism "
                    "expenditure for 2025 only."
                )
        else:
            actual_share = insight_context.get("actual_share_pct")

            st.metric(
                label="Actual national visitor share",
                value=(
                    f"{actual_share:.2f}%"
                    if actual_share is not None
                    else "Not available"
                ),
                delta=f"Observed in {selected_year}",
                delta_color="off",
            )

    with k3.container(border=True):
        if selected_region == "Malaysia":
            if selected_year == 2025:
                domestic_trips = NATIONAL_2025_CONTEXT[
                    "domestic_trips_million"
                ]
                trips_per_visitor = NATIONAL_2025_CONTEXT[
                    "trips_per_visitor"
                ]
                st.metric(
                    label="Domestic trips (2025)",
                    value=f"{domestic_trips:.1f}M",
                    delta=f"{trips_per_visitor:.2f} trips per visitor",
                    delta_color="off",
                )
            else:
                st.metric(
                    label="Domestic trips",
                    value="Not available",
                    delta="2025 only",
                    delta_color="off",
                )
                st.caption(
                    "The current dashboard source provides national domestic "
                    "trip totals for 2025 only."
                )
        else:
            expected_share = insight_context.get("expected_share_pct")

            st.metric(
                label="Model-expected visitor share",
                value=(
                    f"{expected_share:.2f}%"
                    if expected_share is not None
                    else "Not available"
                ),
                delta="Structural benchmark",
                delta_color="off",
            )

    with k4.container(border=True):
        gap_status = classify_opportunity_gap(top_ml_gap)
        gap_prefix = "+" if top_ml_gap > 0 else ""

        st.metric(
            label=f"Relative Gap ({top_ml_state})",
            value=f"{gap_prefix}{top_ml_gap:.1f}%",
            delta=gap_status["short_label"],
            delta_color=gap_status["delta_color"],
        )

    st.markdown("<br>", unsafe_allow_html=True)
    mid_col1, mid_col2 = st.columns([2.3, 1])

    with mid_col1:
        with st.container(border=True):
            st.subheader("Market Analysis")
            st.caption(chart_title)
            
            if selected_region == "Malaysia":
                colors = ['#E5E2D9', '#E8B87B', '#85A88F', '#E27D60', '#D36C4F']
                chart_data['Color'] = colors[-len(chart_data):] if not chart_data.empty else []
                fig_bar = px.bar(chart_data.iloc[::-1], x=x_axis, y=y_axis, orientation='h', text=x_axis)
                fig_bar.update_traces(marker_color=chart_data.iloc[::-1]['Color'] if not chart_data.empty else [], marker_line_width=0, texttemplate='+%{text:.1f}%', textposition='outside', textfont=dict(color='#2D3142', size=11))
            else:
                fig_bar = px.bar(chart_data, x=y_axis, y=x_axis, orientation='v', text=x_axis)
                fig_bar.update_traces(marker_color='#E8B87B', marker_line_width=0, texttemplate='%{text:.1f}M', textposition='outside', textfont=dict(color='#2D3142', size=11))
                fig_bar.update_xaxes(type='category')

            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=40, t=10, b=0), height=280, xaxis=dict(showgrid=False, showticklabels=False, title=""), yaxis=dict(showgrid=False, title=""))
            st.plotly_chart(fig_bar, width="stretch")

    with mid_col2:
        focus_state = insight_context.get(
            "focus_state",
            selected_region,
        )
        focus_gap = insight_context.get(
            "opportunity_gap_pct",
            top_ml_gap,
        )
        focus_status = classify_opportunity_gap(focus_gap)
        reliability_notes = insight_context.get(
            "reliability_notes",
            [],
        )

        if selected_region == "Malaysia":
            opportunity_rows = insight_context.get(
                "meaningful_opportunities",
                [],
            )
            opportunity_names = [
                row["state"]
                for row in opportunity_rows[:2]
            ]

            if opportunity_names:
                highlighted_states = " and ".join(opportunity_names)
                insight_body = (
                    f"<b>{highlighted_states}</b> record the largest positive "
                    f"relative opportunity gaps in {selected_year}. These gaps "
                    "show differences between actual and model-expected visitor "
                    "shares; they do not identify the cause."
                )
            else:
                insight_body = (
                    f"No state exceeds the +{NEUTRAL_GAP_LIMIT:.0f}% "
                    f"meaningful-gap threshold in {selected_year}."
                )
        else:
            if focus_status["category"] == "positive_gap":
                insight_body = (
                    f"<b>{selected_region}</b> received a smaller share of "
                    "national visitors than its structural benchmark in "
                    f"{selected_year}. This is a relative opportunity signal, "
                    "not a forecast or causal finding."
                )
            elif focus_status["category"] == "above_expected":
                insight_body = (
                    f"<b>{selected_region}</b> received a larger share of "
                    "national visitors than its structural benchmark in "
                    f"{selected_year}. This does not by itself indicate "
                    "sustainability pressure."
                )
            else:
                insight_body = (
                    f"<b>{selected_region}</b> remained within the ±"
                    f"{NEUTRAL_GAP_LIMIT:.0f}% neutral band in "
                    f"{selected_year}. The difference is not promoted as a "
                    "meaningful opportunity finding."
                )

        actual_share = insight_context.get("actual_share_pct")
        expected_share = insight_context.get("expected_share_pct")

        if actual_share is not None and expected_share is not None:
            evidence_text = (
                f"Actual share: {actual_share:.2f}% · "
                f"Expected share: {expected_share:.2f}% · "
                f"Relative gap: {focus_gap:+.1f}%"
            )
        else:
            evidence_text = (
                f"Leading relative gap: {focus_gap:+.1f}% "
                f"({focus_state}, {selected_year})"
            )

        panel_title = "Evidence Brief"
        panel_body = insight_body

        st.markdown(
            f"""
            <div style="
                background-color: #3B3C54;
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                margin-bottom: 10px;
                min-height: 320px;
            ">
                <div style="
                    color: white;
                    font-family: sans-serif;
                    font-size: 1.4rem;
                    font-weight: 600;
                    margin-bottom: 15px;
                ">
                    {panel_title}
                </div>
                <div style="
                    color: #F3F4F6;
                    font-family: sans-serif;
                    font-size: 0.95rem;
                    line-height: 1.5;
                    margin-bottom: 20px;
                ">
                    {panel_body}
                </div>
                <div style="
                    background-color: rgba(255,255,255,0.08);
                    padding: 15px;
                    border-radius: 8px;
                    font-family: sans-serif;
                    font-size: 0.85rem;
                    color: #D1D5DB;
                ">
                    {evidence_text}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("Method, reliability and sources"):
            st.write(
                "**Source:** DOSM official Malaysian tourism and "
                "socioeconomic data."
            )
            st.write(
                "**Method:** Gradient Boosting structural expected-demand "
                "benchmark."
            )
            st.write(
                "**Interpretation:** Values inside ±5% are treated as close "
                "to expectation."
            )

            for note in reliability_notes:
                st.warning(note)

            st.caption(
                "This evidence brief is generated deterministically from "
                "the selected dashboard data."
            )

    st.markdown("<br>", unsafe_allow_html=True)
    bot_col1, bot_col2 = st.columns([1.5, 1.5])

    with bot_col1:
        with st.container(border=True):
            st.subheader("National tourism spending mix")

            if selected_year == 2025:
                st.caption(
                    "Share of domestic tourism expenditure, Malaysia, 2025"
                )

                spending_data = pd.DataFrame(
                    {
                        "Category": list(
                            NATIONAL_2025_SPENDING.keys()
                        ),
                        "Share": list(
                            NATIONAL_2025_SPENDING.values()
                        ),
                        "Color": [
                            "#E27D60",
                            "#85A88F",
                            "#E8B87B",
                            "#E4E4E4",
                        ],
                    }
                )

                spending_figure = go.Figure(
                    data=[
                        go.Pie(
                            labels=spending_data["Category"],
                            values=spending_data["Share"],
                            hole=0.6,
                            marker={
                                "colors": spending_data["Color"],
                            },
                            textinfo="none",
                            sort=False,
                            direction="clockwise",
                            hovertemplate=(
                                "%{label}<br>%{value:.1f}%"
                                "<extra></extra>"
                            ),
                        )
                    ]
                )

                spending_figure.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin={
                        "l": 0,
                        "r": 0,
                        "t": 10,
                        "b": 0,
                    },
                    height=250,
                    showlegend=True,
                    annotations=[
                        {
                            "text": "2025",
                            "x": 0.5,
                            "y": 0.5,
                            "font_size": 18,
                            "font_color": "#2D3142",
                            "showarrow": False,
                        }
                    ],
                )

                st.plotly_chart(
                    spending_figure,
                    width="stretch",
                )
                st.caption(
                    "Source: DOSM Domestic Tourism Survey 2025. "
                    "This is a national spending distribution and does not "
                    "change with the selected state."
                )
            else:
                st.info(
                    "The current dashboard source contains the national "
                    "spending-category breakdown for 2025 only. No value is "
                    "shown for the selected year."
                )

    with bot_col2:
        with st.container(border=True):
            if selected_region == "Malaysia":
                st.subheader("Top Opportunity Snapshot")
                st.caption(
                    f"Highest positive relative gap in {selected_year}"
                )
            else:
                st.subheader("Model Evidence Snapshot")
                st.caption(
                    f"Selected state evidence for {selected_year}"
                )

            focus_state = insight_context.get("focus_state")

            if focus_state is None:
                st.info(
                    "No state exceeds the meaningful positive-gap threshold "
                    "for this selection."
                )
            else:
                actual_share = insight_context.get("actual_share_pct")
                expected_share = insight_context.get("expected_share_pct")
                relative_gap = insight_context.get(
                    "opportunity_gap_pct"
                )
                gap_status = classify_opportunity_gap(relative_gap)

                st.markdown(f"### {focus_state}")

                if selected_region == "Malaysia":
                    st.caption(
                        "Ranked #1 by relative opportunity gap for the "
                        "selected year. This state is selected "
                        "automatically, not randomly."
                    )

                evidence_col1, evidence_col2 = st.columns(2)

                evidence_col1.metric(
                    "Actual visitor share",
                    f"{actual_share:.2f}%",
                )
                evidence_col2.metric(
                    "Expected visitor share",
                    f"{expected_share:.2f}%",
                )

                gap_prefix = "+" if relative_gap > 0 else ""

                st.metric(
                    "Relative opportunity gap",
                    f"{gap_prefix}{relative_gap:.1f}%",
                    gap_status["short_label"],
                    delta_color=gap_status["delta_color"],
                )

                for note in insight_context.get(
                    "reliability_notes",
                    [],
                ):
                    st.caption(note)

    return insight_context


# ==========================================
# PAGE 2: VISITOR FLOWS
# ==========================================
def render_visitor_flows():
    page_context = build_visitor_flows_context(selected_year)
    st.markdown(
        (
            f'<p class="sub-header">'
            f'ANALYTICS · HISTORICAL TRENDS ({selected_year})'
            f'</p>'
        ),
        unsafe_allow_html=True,
    )
    st.header("Visitor Trends & Growth Trajectories")
    st.markdown(
        "Compare domestic visitor trajectories across states using the "
        "available DOSM observation years."
    )

    observed_data = (
        df[df["year"] <= selected_year]
        .groupby(["year", "state"], as_index=False)["visitors_M"]
        .sum()
    )

    selected_year_data = df[df["year"] == selected_year]
    top_states = (
        selected_year_data
        .sort_values("visitors_M", ascending=False)
        .head(3)["state"]
        .tolist()
    )

    if observed_data.empty:
        st.warning(
            "No visitor trend data is available for the selected year."
        )
        return page_context

    first_year = int(observed_data["year"].min())
    display_years = list(range(first_year, selected_year + 1))
    states = sorted(observed_data["state"].unique())

    complete_index = pd.MultiIndex.from_product(
        [display_years, states],
        names=["year", "state"],
    ).to_frame(index=False)

    trend_data = complete_index.merge(
        observed_data,
        on=["year", "state"],
        how="left",
    )

    trend_data["Highlight"] = trend_data["state"].apply(
        lambda state: state if state in top_states else "Other States"
    )

    highlight_colors = [
        "#E27D60",
        "#85A88F",
        "#E8B87B",
    ]
    color_map = {
        state: color
        for state, color in zip(top_states, highlight_colors)
    }
    color_map["Other States"] = "#DEDAD0"

    figure = px.line(
        trend_data,
        x="year",
        y="visitors_M",
        color="Highlight",
        line_group="state",
        hover_name="state",
        markers=True,
        color_discrete_map=color_map,
        labels={
            "year": "Year",
            "visitors_M": "Visitors (Millions)",
            "Highlight": "Highlighted states",
        },
    )

    figure.update_traces(connectgaps=False)

    if selected_year >= 2023:
        figure.add_vrect(
            x0=2019.5,
            x1=2022.5,
            fillcolor="#F3EFE7",
            opacity=0.65,
            line_width=0,
            layer="below",
        )
        figure.add_annotation(
            x=2021,
            y=1.04,
            xref="x",
            yref="paper",
            text="No observations for 2020–2022 · lines intentionally disconnected",
            showarrow=False,
            font={
                "size": 11,
                "color": "#6B7280",
            },
        )

    figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=540,
        margin={
            "l": 20,
            "r": 20,
            "t": 65,
            "b": 20,
        },
        xaxis={
            "showgrid": False,
            "title": "Year",
            "tickmode": "linear",
            "dtick": 1,
        },
        yaxis={
            "showgrid": True,
            "gridcolor": "#E5E2D9",
            "title": "Visitors (Millions)",
        },
        legend_title_text="Highlighted states",
        hovermode="closest",
    )

    st.plotly_chart(
        figure,
        width="stretch",
    )

    st.caption(
        "Observed years: 2017–2019 and 2023–2025. "
        "No observations are available for 2020–2022, so lines are "
        "intentionally disconnected across this gap."
    )

    return page_context


# ==========================================
# PAGE 3: SUSTAINABILITY
# ==========================================
def render_sustainability():
    st.markdown(f'<p class="sub-header">INFRASTRUCTURE · CAPACITY ({selected_year})</p>', unsafe_allow_html=True)
    st.header("Sustainability & Tourism Strain")
    st.markdown(f"Analyze local infrastructure capacity versus economic output based on the **{selected_year}** global filter.")
    
    df_yr = df[df['year'] == selected_year].copy()
    page_context = build_sustainability_context(selected_year)
    
    fig_scatter = px.scatter(df_yr, x="log_gdp_per_capita", y="rooms_per_1k_residents", 
                             size="visitors_M", color="visitors_M", hover_name="state",
                             color_continuous_scale=["#85A88F", "#E8B87B", "#E27D60"],
                             labels={"log_gdp_per_capita": "Economic Strength (Log GDP per Capita)", 
                                     "rooms_per_1k_residents": "Infrastructure Capacity (Rooms per 1k Residents)"})
    
    if not df_yr.empty:
        fig_scatter.add_vline(x=df_yr['log_gdp_per_capita'].median(), line_width=1, line_dash="dash", line_color="gray")
        fig_scatter.add_hline(y=df_yr['rooms_per_1k_residents'].median(), line_width=1, line_dash="dash", line_color="gray")
    
    fig_scatter.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=500)
    st.plotly_chart(fig_scatter, width="stretch")

    return page_context


# ==========================================
# PAGE 4: SCENARIO LAB
# ==========================================
def render_scenario_lab():
    st.markdown(
        (
            f'<p class="sub-header">'
            f'POLICY · ILLUSTRATIVE SCENARIO ({selected_year})'
            f'</p>'
        ),
        unsafe_allow_html=True,
    )
    st.header("Scenario Lab: Visitor Redistribution")
    st.markdown(
        "Explore a transparent arithmetic redistribution between two "
        f"states using observed {selected_year} visitor volumes."
    )

    st.warning(
        "This is an illustrative arithmetic scenario. It is not a "
        "forecast, causal estimate or predicted policy outcome."
    )

    year_data = (
        df[df["year"] == selected_year]
        .sort_values("visitors_M", ascending=False)
        .copy()
    )

    if year_data.empty:
        st.error(
            "No visitor data is available for the selected year."
        )
        return {
            "page": "Scenario lab",
            "selected_year": int(selected_year),
            "data_available": False,
        }

    state_options = year_data["state"].tolist()

    control_col1, control_col2, control_col3 = st.columns(
        [1, 1, 1.5]
    )

    with control_col1:
        source_state = st.selectbox(
            "Source state",
            state_options,
            key="scenario_source_state",
        )

    target_options = [
        state
        for state in state_options
        if state != source_state
    ]

    with control_col2:
        target_state = st.selectbox(
            "Target state",
            target_options,
            key="scenario_target_state",
        )

    with control_col3:
        shift_pct = st.slider(
            "Illustrative share of source visitors to reallocate",
            min_value=0,
            max_value=30,
            value=5,
            format="%d%%",
            key="scenario_shift_pct",
        )

    source_volume = float(
        year_data.loc[
            year_data["state"] == source_state,
            "visitors_M",
        ].iloc[0]
    )
    target_volume = float(
        year_data.loc[
            year_data["state"] == target_state,
            "visitors_M",
        ].iloc[0]
    )

    shift_amount = source_volume * (shift_pct / 100)
    source_scenario_volume = source_volume - shift_amount
    target_scenario_volume = target_volume + shift_amount

    st.markdown("<br>", unsafe_allow_html=True)

    result_col1, result_col2 = st.columns(2)

    with result_col1.container(border=True):
        st.subheader(f"{source_state} · Source")
        st.metric(
            "Illustrative visitor volume",
            f"{source_scenario_volume:.1f}M",
            f"-{shift_amount:.1f}M arithmetic reallocation",
            delta_color="inverse",
        )
        st.caption(
            f"Observed baseline: {source_volume:.1f}M visitors."
        )

    with result_col2.container(border=True):
        st.subheader(f"{target_state} · Target")
        st.metric(
            "Illustrative visitor volume",
            f"{target_scenario_volume:.1f}M",
            f"+{shift_amount:.1f}M arithmetic reallocation",
        )
        st.caption(
            f"Observed baseline: {target_volume:.1f}M visitors."
        )

    national_before = year_data["visitors_M"].sum()
    national_after = (
        national_before
        - source_volume
        - target_volume
        + source_scenario_volume
        + target_scenario_volume
    )

    st.caption(
        f"National total is preserved: {national_before:.1f}M before "
        f"and {national_after:.1f}M after the illustrative transfer."
    )

    page_context = build_scenario_context(
        selected_year=selected_year,
        source_state=source_state,
        target_state=target_state,
        shift_pct=shift_pct,
        source_volume=source_volume,
        target_volume=target_volume,
        source_scenario_volume=source_scenario_volume,
        target_scenario_volume=target_scenario_volume,
        national_before=national_before,
        national_after=national_after,
    )
    return page_context

# ==========================================
# PAGE 5: EVIDENCE & LIMITATIONS
# ==========================================
def render_evidence():
    page_context = build_evidence_context(selected_year)
    st.markdown('<p class="sub-header">DATA · TRANSPARENCY</p>', unsafe_allow_html=True)
    st.header("Evidence & Methodology")
    st.markdown("Direct access to the underlying DOSM dataset, ML Predictions, and project limitations.")
    
    # Critical Model Limitations section requested in Code Review
    with st.expander(
        "ML Methodology & Limitations",
        expanded=True,
    ):
        st.markdown(
            """
            - **Training years:** 2017, 2018, 2019 and 2023.
            - **Untouched holdout years:** 2024 and 2025.
            - **Model:** Gradient Boosting structural expected-demand model.
            - **Headline metric:** The Tourism Opportunity Gap compares a state's
            actual share of national visitors with its model-expected share for
            the same year.
            - **Interpretation threshold:** Values between -5% and +5% are treated
            as close to the model expectation and are not promoted as a
            meaningful opportunity finding.
            - **Not a forecast:** The expected value is a structural benchmark,
            not a prediction of future visitor volume.
            - **No causal claim:** The result does not prove that marketing,
            discoverability, transport or any single factor caused the gap.
            - **Reliability warning:** Results for Perlis and W.P. Putrajaya
            require additional caution because their holdout errors are higher
            than the median state.
            """
        )
            
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Records", len(df))
        col2.metric("Total States", df['state'].nunique())
        col3.metric(
            "Observed Years",
            "2017–2019, 2023–2025",
        )
    
    st.subheader("Historical Data (DOSM)")
    st.dataframe(df, width="stretch", height=300)
    
    st.subheader("Machine Learning Output (Opportunity Gap)")
    st.dataframe(df_ml, width="stretch")
    return page_context


# --- 9. Execution Engine ---
if selected_page == "Overview":
    current_page_context = render_overview()
elif selected_page == "Visitor flows":
    current_page_context = render_visitor_flows()
elif selected_page == "Sustainability":
    current_page_context = render_sustainability()
elif selected_page == "Scenario lab":
    current_page_context = render_scenario_lab()
elif selected_page == "Evidence":
    current_page_context = render_evidence()

render_ollie_assistant(
    context=current_page_context,
    page_name=selected_page,
    year=int(selected_year),
    sidebar_slot=ollie_sidebar_slot,
)
