"""Phase 10 - the one function the backend calls.

    from src.predict import predict
    predict({"state": "Johor", "year": 2025})

Importing this module loads nothing and trains nothing. The model file is opened lazily on
the first call and cached afterwards. Every path is resolved relative to the ml/ folder, so
it works from any working directory and on any operating system.

Contract, examples and error shapes: handoff/for_hongyik/API_CONTRACT.md
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

ML_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = ML_DIR / "models" / "a2_gap_model.joblib"
METADATA_PATH = ML_DIR / "models" / "a2_gap_model_metadata.json"
# Preferred source, produced by the pipeline; the CSV is the tracked fallback so that a
# fresh clone can call predict() without running the whole pipeline first.
FEATURES_PARQUET = ML_DIR / "data" / "processed" / "features.parquet"
FEATURES_CSV = ML_DIR / "handoff" / "for_hongyik" / "state_features.csv"

# States whose holdout error was more than twice the median; see reports/09_evaluation.md.
HIGH_ERROR_STATES = {"Perlis": 0.708, "W.P. Putrajaya": 0.408}


class PredictionError(ValueError):
    """Raised for an input the model cannot answer. Message is safe to show a user."""


@lru_cache(maxsize=1)
def _model():
    import joblib  # imported here so that merely importing this module stays cheap
    if not MODEL_PATH.exists():
        raise PredictionError(
            f"model file not found at {MODEL_PATH.relative_to(ML_DIR).as_posix()}; "
            "run `python src/tune.py` from the ml/ folder")
    return joblib.load(MODEL_PATH)


@lru_cache(maxsize=1)
def _metadata() -> dict:
    return json.loads(METADATA_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _table() -> pd.DataFrame:
    """State-year features, from the pipeline output or the tracked CSV fallback."""
    columns = ["state", "year", "visitors_000"] + _metadata()["features"]
    if FEATURES_PARQUET.exists():
        frame = pd.read_parquet(FEATURES_PARQUET)
        # The CSV fallback holds only the structural sample, so apply the same filter here.
        # Without it predict() would answer differently depending on which file is present,
        # and would answer for 2020-2022, which the model was never trained to explain.
        frame = frame[frame["in_structural_sample"] & (frame["year"] >= 2017)]
    elif FEATURES_CSV.exists():
        frame = pd.read_csv(FEATURES_CSV)
    else:
        raise PredictionError(
            "no feature table found; expected "
            f"{FEATURES_PARQUET.relative_to(ML_DIR).as_posix()} or "
            f"{FEATURES_CSV.relative_to(ML_DIR).as_posix()}")
    frame["state"] = frame["state"].astype(str)
    frame = frame[[c for c in columns if c in frame.columns]].dropna(
        subset=_metadata()["features"])
    return frame


def available() -> dict:
    """What predict() can answer: the valid states and years."""
    table = _table()
    return {"states": sorted(table["state"].unique()),
            "years": sorted(int(y) for y in table["year"].unique())}


def _expected_for_year(year: int) -> pd.DataFrame:
    """Model-expected visitors for every state in one year, needed to form shares."""
    rows = _table()[_table()["year"] == year].copy()
    if rows.empty:
        raise PredictionError(
            f"year {year} is not available; available years are {available()['years']}")
    features = _metadata()["features"]
    rows["expected_000"] = np.exp(_model().predict(rows[features].to_numpy()))
    return rows


def predict(payload: dict) -> dict:
    """Expected domestic visitors for one state-year, and its opportunity gap.

    payload
      state     required, one of the 16 DOSM state labels
      year      required, int
      features  optional {feature: value} overrides, for scenario analysis

    expected_visitors_000 is the expected share applied to that year's national total,
    so it is directly comparable with actual_visitors_000. model_raw_expected_000 is the
    unscaled model output, kept for diagnostics only - do not display it beside an
    actual.

    Returns a JSON-serialisable dict; see the API contract for the full shape.
    """
    if not isinstance(payload, dict):
        raise PredictionError("payload must be a dict")
    state = payload.get("state")
    year = payload.get("year")
    if state is None or year is None:
        raise PredictionError("payload must contain 'state' and 'year'")
    try:
        year = int(year)
    except (TypeError, ValueError):
        raise PredictionError(f"year must be an integer, got {year!r}") from None

    rows = _expected_for_year(year)
    if state not in set(rows["state"]):
        raise PredictionError(
            f"state {state!r} is not available for {year}; "
            f"valid states are {available()['states']}")

    features = _metadata()["features"]
    overrides = payload.get("features") or {}
    unknown = sorted(set(overrides) - set(features))
    if unknown:
        raise PredictionError(f"unknown feature(s) {unknown}; valid features are {features}")

    warnings: list[str] = []
    if overrides:
        target_row = rows[rows["state"] == state].copy()
        for key, value in overrides.items():
            target_row[key] = float(value)
        new_expected = float(np.exp(_model().predict(target_row[features].to_numpy()))[0])
        rows.loc[rows["state"] == state, "expected_000"] = new_expected
        warnings.append("scenario: expected demand recomputed with overridden features "
                        f"{sorted(overrides)}")

    row = rows[rows["state"] == state].iloc[0]
    expected = float(row["expected_000"])
    expected_share = expected / float(rows["expected_000"].sum())

    actual = row.get("visitors_000")
    actual = None if actual is None or pd.isna(actual) else float(actual)
    actual_share = gap_pct = gap_pp = benchmarked = gap_visitors = None
    if actual is not None and rows["visitors_000"].notna().all():
        national_actual = float(rows["visitors_000"].sum())
        actual_share = actual / national_actual
        gap_pct = (expected_share / actual_share - 1.0) * 100.0
        gap_pp = (expected_share - actual_share) * 100.0
        # The model's raw level is anchored on its training years and runs
        # systematically low for later ones, so showing it beside an actual invites the
        # question "how can actual exceed expected while the gap says the state is
        # below expectation?". Rescaling the expected share to the year's own national
        # total puts both on one scale; the level gap then agrees with the share gap by
        # construction, since both sides carry the same national total.
        # This uses the year's published national total, so it is a benchmark for a year
        # already observed, never a forecast.
        benchmarked = expected_share * national_actual
        gap_visitors = benchmarked - actual

    if state in HIGH_ERROR_STATES:
        warnings.append(
            f"{state} had a holdout error of {HIGH_ERROR_STATES[state]:.3f} MAE_log, "
            "well above the median state; treat this gap as indicative only")
    if year not in _metadata()["holdout_years"] and year in _metadata()["trained_on_years"]:
        warnings.append(f"{year} is one of the model's training years, so this is an "
                        "in-sample figure, not a test of the model")

    meta = _metadata()
    return {
        "state": state,
        "year": year,
        "expected_visitors_000": None if benchmarked is None else round(benchmarked, 1),
        "actual_visitors_000": None if actual is None else round(actual, 1),
        "gap_visitors_000": None if gap_visitors is None else round(gap_visitors, 1),
        "model_raw_expected_000": round(expected, 1),
        "expected_share_pct": round(expected_share * 100, 4),
        "actual_share_pct": None if actual_share is None else round(actual_share * 100, 4),
        "opportunity_gap_pct": None if gap_pct is None else round(gap_pct, 1),
        "opportunity_gap_pp": None if gap_pp is None else round(gap_pp, 4),
        "interpretation": _interpret(gap_pct),
        "basis": "share of the national total for the same year",
        "model": {"family": meta["family"], "trained_on_years": meta["trained_on_years"],
                  "holdout_MAE_log": 0.2648, "baseline_MAE_log": 0.4467},
        "warnings": warnings,
    }


def _interpret(gap_pct: float | None) -> str:
    if gap_pct is None:
        return "no actual figure published for this year, so no gap can be computed"
    if gap_pct > 5:
        return ("receives a smaller share of national visitors than its population, economy "
                "and accommodation capacity imply")
    if gap_pct < -5:
        return ("receives a larger share of national visitors than its population, economy "
                "and accommodation capacity imply")
    return "receives about the share its population, economy and capacity imply"


if __name__ == "__main__":
    example = {"state": "Johor", "year": 2025}
    print(json.dumps(predict(example), indent=2))
