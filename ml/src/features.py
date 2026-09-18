"""Phase 5 - build model features from the cleaned panel.

Run from the ml/ folder:   python src/features.py
Input:   data/processed/state_year_panel.parquet, data/processed/od_flows.parquet
Output:  data/processed/features.parquet

Two feature sets are built, for the two models agreed in reports/04_problem_candidates.md:

  FORECAST_FEATURES  (Model A1)  proves the model predicts. Lags allowed.
  STRUCTURAL_FEATURES(Model A2)  produces the opportunity gap. NO lag of the target,
                                 because a lagged target would turn the gap into an
                                 autoregressive residual.

Leakage rules enforced here
---------------------------
1. Every lag is built with ``groupby("state").shift(k)``, so a row for year t only ever
   sees years < t. The panel is complete for all 16 states from 2016 to 2025, so a shift
   of one row is exactly a shift of one year.
2. National aggregates are lagged too. A state's share of the national total in year t
   would require knowing every other state's year-t value, which is not available when
   predicting year t.
3. Nothing is scaled or encoded in this file. Scalers are fitted inside a scikit-learn
   pipeline on the training split only (Phases 6-7).
4. Hotel capacity was already attached in clean.py with a carry-back rule; see
   reports/02_cleaning.md section 2.6.
5. Calendar flags (pandemic, recovery) are known in advance and are not leakage.

Every feature is documented in reports/05_features.md with its definition, source column
and rationale.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ML_DIR = Path(__file__).resolve().parents[1]
PROCESSED = ML_DIR / "data" / "processed"

KLANG_VALLEY = ["Selangor", "W.P. Kuala Lumpur"]

# Model A2 - structural expectation. No lag of the target appears here.
STRUCTURAL_FEATURES = [
    "log_population",
    "log_gdp_total",
    "log_gdp_services",
    "services_share",
    "log_gdp_per_capita",
    "log_rooms",
    "rooms_per_1k_residents",
    "log_lf_employed",
    "u_rate",
    "p_rate",
    "cpi_accom_food_rel",
    "cpi_recreation_rel",
]

# Optional additions for A2, available only from 2023 (see od_features below).
OD_FEATURES = ["log_od_inbound_external", "od_klang_share", "od_self_share"]

# Model A1 - forecasting. Lags of the target are the point.
FORECAST_FEATURES = [
    "log_visitors_lag1",
    "log_visitors_lag2",
    "visitors_growth_lag1",
    "log_visitors_ma2_lag1",
    "log_national_visitors_lag1",
    "state_share_lag1",
    "log_population",
    "log_rooms",
    "log_gdp_total",
    "u_rate_lag1",
    "cpi_accom_food_rel_lag1",
    "years_since_2016",
    "is_pandemic_year",
    "is_recovery_year",
]

TARGET = "log_visitors"


def log(message: str = "") -> None:
    print(message, flush=True)


def head(title: str) -> None:
    log(f"\n{'=' * 72}\n{title}\n{'=' * 72}")


def structural_features(panel: pd.DataFrame) -> pd.DataFrame:
    """State size, capacity and price level in the same year as the target.

    These are contemporaneous by design: the question A2 asks is "given what this state
    *is*, how many visitors should it receive", not "what will happen next year".
    """
    df = panel.copy()
    df["log_population"] = np.log(df["population_000"])
    df["log_gdp_total"] = np.log(df["gdp_total_rm_mn"])
    df["log_gdp_services"] = np.log(df["gdp_services_rm_mn"])
    df["services_share"] = df["gdp_services_rm_mn"] / df["gdp_total_rm_mn"]
    # GDP is RM million, population is thousands, so this is RM per resident.
    df["log_gdp_per_capita"] = np.log(df["gdp_total_rm_mn"] * 1000.0 / df["population_000"])
    df["log_rooms"] = np.log(df["rooms"])
    df["rooms_per_1k_residents"] = df["rooms"] / df["population_000"]
    df["log_lf_employed"] = np.log(df["lf_employed_000"])

    # Price level relative to the national mean of the same year. The absolute index is
    # base 2010 = 100 for every state, so the level alone mostly encodes national
    # inflation; the ratio is what says whether a state is expensive for its year.
    for column, name in [("cpi_accom_food", "cpi_accom_food_rel"),
                         ("cpi_recreation", "cpi_recreation_rel")]:
        national = df.groupby("year")[column].transform("mean")
        df[name] = df[column] / national
    return df


def lag_features(panel: pd.DataFrame) -> pd.DataFrame:
    """Everything a forecaster could know before year t begins."""
    df = panel.sort_values(["state", "year"]).copy()
    grouped = df.groupby("state", observed=True)["visitors_000"]

    df["visitors_lag1"] = grouped.shift(1)
    df["visitors_lag2"] = grouped.shift(2)
    df["log_visitors_lag1"] = np.log(df["visitors_lag1"])
    df["log_visitors_lag2"] = np.log(df["visitors_lag2"])
    df["visitors_growth_lag1"] = df["visitors_lag1"] / df["visitors_lag2"] - 1.0
    # Mean of the two previous years, so still past-only.
    df["log_visitors_ma2_lag1"] = np.log((df["visitors_lag1"] + df["visitors_lag2"]) / 2.0)

    national = df.groupby("year")["visitors_000"].transform("sum")
    df["national_visitors"] = national
    df["state_share"] = df["visitors_000"] / national
    for source, target in [("national_visitors", "log_national_visitors_lag1"),
                           ("state_share", "state_share_lag1")]:
        shifted = df.groupby("state", observed=True)[source].shift(1)
        df[target] = np.log(shifted) if target.startswith("log_") else shifted
    # The un-lagged helpers would leak year t; drop them.
    df = df.drop(columns=["national_visitors", "state_share"])

    for source, target in [("u_rate", "u_rate_lag1"),
                           ("cpi_accom_food_rel", "cpi_accom_food_rel_lag1")]:
        df[target] = df.groupby("state", observed=True)[source].shift(1)

    df["years_since_2016"] = df["year"] - 2016
    return df


def od_features(panel: pd.DataFrame, flows: pd.DataFrame) -> pd.DataFrame:
    """Market access, from the origin-destination tourist matrix.

    Available for 2023-2025 only, so these columns are null for earlier years. They are
    contemporaneous, matching the rest of the A2 feature set.
    """
    inbound = []
    for (year, destination), group in flows.groupby(["year", "destination"]):
        total = group["tourists_000"].sum()
        self_flow = group.loc[group["origin"] == destination, "tourists_000"].sum()
        external = total - self_flow
        klang = group.loc[group["origin"].isin(KLANG_VALLEY)
                          & (group["origin"] != destination), "tourists_000"].sum()
        inbound.append({
            "year": year, "state": destination,
            "od_inbound_total": total,
            "od_inbound_external": external,
            "od_inbound_klang": klang,
            "od_klang_share": klang / external if external else np.nan,
            "od_self_share": self_flow / total if total else np.nan,
        })
    frame = pd.DataFrame.from_records(inbound)
    frame["log_od_inbound_external"] = np.log(frame["od_inbound_external"])
    frame["year"] = frame["year"].astype(panel["year"].dtype)
    log(f"  origin-destination features built for {frame['year'].nunique()} years "
        f"({sorted(frame['year'].unique())}), {len(frame)} state-years")
    merged = panel.merge(frame, on=["state", "year"], how="left")
    assert len(merged) == len(panel), "OD merge changed the row count"
    return merged


def build() -> pd.DataFrame:
    panel = pd.read_parquet(PROCESSED / "state_year_panel.parquet")
    panel["state"] = panel["state"].astype(str)
    flows = pd.read_parquet(PROCESSED / "od_flows.parquet")
    log(f"  panel {panel.shape}, flows {flows.shape}")

    head("structural features (Model A2)")
    df = structural_features(panel)
    log(f"  built {len(STRUCTURAL_FEATURES)} columns")

    head("lag features (Model A1)")
    df = lag_features(df)
    log(f"  built lag columns; rows without a 2-year history: "
        f"{int(df['log_visitors_lag2'].isna().sum())} (expected 32 = 16 states x 2016-2017)")

    head("origin-destination features")
    df = od_features(df, flows)

    df[TARGET] = np.log(df["visitors_000"])

    head("leakage self-checks")
    # A lag column must never equal the same-year value it is derived from.
    same = int((df["visitors_lag1"] == df["visitors_000"]).sum())
    log(f"  rows where visitors_lag1 equals the current year's value: {same} (must be 0)")
    # Each lag must match the previous year's actual value.
    check = df.sort_values(["state", "year"]).copy()
    check["expected_lag1"] = check.groupby("state", observed=True)["visitors_000"].shift(1)
    mismatch = int((check["visitors_lag1"].round(6) != check["expected_lag1"].round(6)).sum()
                   - check["expected_lag1"].isna().sum())
    log(f"  lag1 values not matching the previous year: {mismatch} (must be 0)")
    assert same == 0 and mismatch == 0, "lag construction is wrong"

    head("sample sizes")
    forecast_ready = df.dropna(subset=FORECAST_FEATURES + [TARGET])
    log(f"  Model A1 forecasting sample: {len(forecast_ready)} rows, "
        f"years {forecast_ready['year'].min()}-{forecast_ready['year'].max()}")
    for name, years in [("train 2018-2022", range(2018, 2023)), ("validate 2023", [2023]),
                        ("holdout 2024-2025", [2024, 2025])]:
        log(f"    {name:20s} {len(forecast_ready[forecast_ready.year.isin(years)]):4d} rows")

    structural_ready = df[df["in_structural_sample"] & (df["year"] >= 2017)].dropna(
        subset=STRUCTURAL_FEATURES + [TARGET])
    log(f"\n  Model A2 structural sample (no OD): {len(structural_ready)} rows, "
        f"years {sorted(structural_ready['year'].unique())}")
    for name, years in [("train 2017-2019+2023", [2017, 2018, 2019, 2023]),
                        ("holdout 2024-2025", [2024, 2025])]:
        log(f"    {name:24s} {len(structural_ready[structural_ready.year.isin(years)]):4d} rows")

    with_od = structural_ready.dropna(subset=OD_FEATURES)
    log(f"\n  Model A2 + OD features: {len(with_od)} rows, "
        f"years {sorted(with_od['year'].unique())}")
    log(f"    -> adding the OD features costs {len(structural_ready) - len(with_od)} rows "
        f"({(len(structural_ready) - len(with_od)) / len(structural_ready):.0%} of the sample), "
        f"because the origin-destination matrix starts in 2023")
    log(f"    -> a time split on that subset leaves "
        f"{len(with_od[with_od.year == 2023])} training rows, which is not workable; "
        f"Phase 7 will report the OD variant as a cross-sectional comparison only")

    return df


def main() -> int:
    df = build()
    path = PROCESSED / "features.parquet"
    df.to_parquet(path, index=False)
    head("output")
    log(f"  {path.relative_to(ML_DIR).as_posix()}  {df.shape[0]} rows x {df.shape[1]} cols "
        f"({path.stat().st_size / 1e6:.2f} MB)")
    log(f"  target: {TARGET}")
    log(f"  forecast features ({len(FORECAST_FEATURES)}): {FORECAST_FEATURES}")
    log(f"  structural features ({len(STRUCTURAL_FEATURES)}): {STRUCTURAL_FEATURES}")
    log(f"  optional OD features ({len(OD_FEATURES)}): {OD_FEATURES}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
