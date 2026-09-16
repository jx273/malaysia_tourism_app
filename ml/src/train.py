"""Phases 6-7 - baselines and model comparison, on identical splits and metrics.

Run from the ml/ folder:   python src/train.py
Input:   data/processed/features.parquet
Output:  printed tables, consumed by reports/06_baseline.md and reports/07_model_comparison.md

**The 2024-2025 holdout is not touched here.** Model selection uses 2023 as the validation
year; Phase 9 is the first and only time the holdout is scored. Every split is by time: the
training years always precede the validation year, and nothing is shuffled across time.

Scalers live inside a scikit-learn Pipeline, so they are fitted on the training fold only.
random_state=42 everywhere a model accepts one.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent))
from features import FORECAST_FEATURES, OD_FEATURES, STRUCTURAL_FEATURES, TARGET  # noqa: E402

ML_DIR = Path(__file__).resolve().parents[1]
PROCESSED = ML_DIR / "data" / "processed"
RANDOM_STATE = 42

# Time-based splits. Holdout is declared here only so it can be excluded.
A1_TRAIN_YEARS = [2018, 2019, 2020, 2021, 2022]
A1_VALID_YEARS = [2023]
A2_TRAIN_YEARS = [2017, 2018, 2019]
A2_VALID_YEARS = [2023]
HOLDOUT_YEARS = [2024, 2025]


def log(message: str = "") -> None:
    print(message, flush=True)


def head(title: str) -> None:
    log(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def metrics(actual_log: np.ndarray, predicted_log: np.ndarray) -> dict[str, float]:
    """Errors in log space and, after exponentiating, in thousands of visitors.

    Exponentiating a prediction of a log target returns a median rather than a mean, so the
    level metrics carry a small retransformation bias. Both are reported rather than one
    being quietly preferred.
    """
    actual = np.exp(actual_log)
    predicted = np.exp(predicted_log)
    error = predicted - actual
    return {
        "MAE_log": float(np.mean(np.abs(predicted_log - actual_log))),
        "MAE_000": float(np.mean(np.abs(error))),
        "RMSE_000": float(np.sqrt(np.mean(error ** 2))),
        "MAPE_%": float(np.mean(np.abs(error / actual)) * 100),
    }


def show(title: str, rows: list[dict]) -> pd.DataFrame:
    frame = pd.DataFrame(rows).set_index("model")
    log(f"\n{title}")
    log(frame.round(4).to_string())
    return frame


# --------------------------------------------------------------------------
# Phase 6 - baselines
# --------------------------------------------------------------------------
def baselines(df: pd.DataFrame) -> pd.DataFrame:
    head("PHASE 6 - baselines (validation year 2023)")
    rows = []

    # A1 baseline 1: last value. The standard naive forecast for an annual series.
    a1 = df.dropna(subset=FORECAST_FEATURES + [TARGET])
    valid = a1[a1.year.isin(A1_VALID_YEARS)]
    rows.append({"model": "A1 naive: last value", "n_valid": len(valid),
                 **metrics(valid[TARGET].to_numpy(), valid["log_visitors_lag1"].to_numpy())})

    # A1 baseline 2: last value carried forward by the national growth rate observed
    # between t-2 and t-1, which is information available before year t.
    train = a1[a1.year.isin(A1_TRAIN_YEARS)]
    drift = float(np.mean(train[TARGET] - train["log_visitors_lag1"]))
    log(f"  drift estimated on the training years only: {drift:+.4f} in log space "
        f"({np.expm1(drift):+.1%} per year)")
    rows.append({"model": "A1 naive + drift", "n_valid": len(valid),
                 **metrics(valid[TARGET].to_numpy(),
                           valid["log_visitors_lag1"].to_numpy() + drift)})

    # A2 baseline: national average visitors per resident, applied to each state's
    # population. This is the simplest credible "expected demand" a stakeholder could
    # compute without a model, so it is what A2 has to beat.
    a2 = df[df.in_structural_sample & (df.year >= 2017)].dropna(subset=STRUCTURAL_FEATURES + [TARGET])
    a2_train = a2[a2.year.isin(A2_TRAIN_YEARS)]
    a2_valid = a2[a2.year.isin(A2_VALID_YEARS)]
    intensity = float((np.exp(a2_train[TARGET]) / a2_train["population_000"]).mean())
    log(f"  mean visitors per resident on the training years only: {intensity:.2f}")
    predicted = np.log(intensity * a2_valid["population_000"].to_numpy())
    rows.append({"model": "A2 baseline: national mean intensity x population",
                 "n_valid": len(a2_valid),
                 **metrics(a2_valid[TARGET].to_numpy(), predicted)})

    return show("baseline metrics", rows)


# --------------------------------------------------------------------------
# Phase 7 - model comparison
# --------------------------------------------------------------------------
def candidates() -> dict[str, Pipeline]:
    """Four models of increasing complexity, all behind the same interface."""
    return {
        "Linear regression": Pipeline([("scale", StandardScaler()),
                                       ("model", LinearRegression())]),
        "Ridge (alpha=1.0)": Pipeline([("scale", StandardScaler()),
                                       ("model", Ridge(alpha=1.0, random_state=RANDOM_STATE))]),
        "Random forest": Pipeline([("model", RandomForestRegressor(
            n_estimators=300, min_samples_leaf=2, random_state=RANDOM_STATE, n_jobs=-1))]),
        "Gradient boosting": Pipeline([("model", GradientBoostingRegressor(
            n_estimators=200, max_depth=2, learning_rate=0.05, random_state=RANDOM_STATE))]),
    }


def compare(df: pd.DataFrame, features: list[str], train_years: list[int],
            valid_years: list[int], label: str) -> pd.DataFrame:
    head(f"PHASE 7 - {label}")
    usable = df.dropna(subset=features + [TARGET])
    if label.startswith("Model A2"):
        usable = usable[usable.in_structural_sample & (usable.year >= 2017)]
    train = usable[usable.year.isin(train_years)]
    valid = usable[usable.year.isin(valid_years)]
    log(f"  features: {len(features)}")
    log(f"  train years {train_years} -> {len(train)} rows")
    log(f"  validation years {valid_years} -> {len(valid)} rows")
    log(f"  holdout {HOLDOUT_YEARS} is untouched: "
        f"{len(usable[usable.year.isin(HOLDOUT_YEARS)])} rows reserved for Phase 9")
    if len(train) < 2 or len(valid) < 1:
        log("  not enough rows to compare models on this sample")
        return pd.DataFrame()

    x_train, y_train = train[features].to_numpy(), train[TARGET].to_numpy()
    x_valid, y_valid = valid[features].to_numpy(), valid[TARGET].to_numpy()

    rows = []
    for name, pipeline in candidates().items():
        started = time.perf_counter()
        pipeline.fit(x_train, y_train)
        fit_seconds = time.perf_counter() - started
        predicted = pipeline.predict(x_valid)
        in_sample = pipeline.predict(x_train)
        rows.append({"model": name, "n_train": len(train), "n_valid": len(valid),
                     **metrics(y_valid, predicted),
                     "train_MAE_log": float(np.mean(np.abs(in_sample - y_train))),
                     "fit_seconds": fit_seconds})
    return show(f"{label}: validation metrics", rows)


def rolling_origin(df: pd.DataFrame, features: list[str], fold_years: list[int],
                   label: str, structural: bool) -> pd.DataFrame:
    """Expanding-window validation: train on every year before v, validate on v.

    A single validation year is 16 rows, which is too few to rank four models on. This
    repeats the comparison across several origins so the ranking rests on more than one
    year. The 2024-2025 holdout is never a fold.
    """
    head(f"PHASE 7 - {label}: rolling-origin validation")
    usable = df.dropna(subset=features + [TARGET])
    if structural:
        usable = usable[usable.in_structural_sample & (usable.year >= 2017)]
    usable = usable[~usable.year.isin(HOLDOUT_YEARS)]

    scores: dict[str, list[float]] = {name: [] for name in candidates()}
    scores["BASELINE"] = []
    for v in fold_years:
        train = usable[usable.year < v]
        valid = usable[usable.year == v]
        if len(train) < 10 or len(valid) == 0:
            log(f"  fold {v}: skipped ({len(train)} train, {len(valid)} valid)")
            continue
        # The same baseline, refitted per fold, so every comparison is like for like.
        if structural:
            intensity = float((np.exp(train[TARGET]) / train["population_000"]).mean())
            base_pred = np.log(intensity * valid["population_000"].to_numpy())
        else:
            base_pred = valid["log_visitors_lag1"].to_numpy()
        scores["BASELINE"].append(metrics(valid[TARGET].to_numpy(), base_pred)["MAE_log"])
        line = [f"  fold {v}: train {len(train):3d} rows, valid {len(valid):2d} rows",
                f"BASELINE {scores['BASELINE'][-1]:.4f}"]
        for name, pipeline in candidates().items():
            pipeline.fit(train[features].to_numpy(), train[TARGET].to_numpy())
            score = metrics(valid[TARGET].to_numpy(),
                            pipeline.predict(valid[features].to_numpy()))["MAE_log"]
            scores[name].append(score)
            line.append(f"{name} {score:.4f}")
        log("  |  ".join(line))

    rows = [{"model": name, "folds": len(values),
             "mean_MAE_log": float(np.mean(values)) if values else np.nan,
             "worst_fold_MAE_log": float(np.max(values)) if values else np.nan}
            for name, values in scores.items()]
    return show(f"{label}: mean across folds", rows)


def main() -> int:
    df = pd.read_parquet(PROCESSED / "features.parquet")
    df["state"] = df["state"].astype(str)
    log(f"features.parquet {df.shape}")

    base = baselines(df)

    a1 = compare(df, FORECAST_FEATURES, A1_TRAIN_YEARS, A1_VALID_YEARS,
                 "Model A1 (forecast, lags allowed)")
    a2 = compare(df, STRUCTURAL_FEATURES, A2_TRAIN_YEARS, A2_VALID_YEARS,
                 "Model A2 (structural, no lag of the target)")
    a2_od = compare(df, STRUCTURAL_FEATURES + OD_FEATURES, [2023], [2024],
                    "Model A2 + OD (cross-sectional only, OD starts in 2023)")

    a1_cv = rolling_origin(df, FORECAST_FEATURES, [2020, 2021, 2022, 2023],
                           "Model A1", structural=False)
    a2_cv = rolling_origin(df, STRUCTURAL_FEATURES, [2018, 2019, 2023],
                           "Model A2", structural=True)

    head("does anything beat its baseline on the validation year?")
    naive = base.loc["A1 naive: last value", "MAE_log"]
    drift = base.loc["A1 naive + drift", "MAE_log"]
    a2_base = base.loc["A2 baseline: national mean intensity x population", "MAE_log"]
    log(f"  A1 baselines: last value MAE_log {naive:.4f}, with drift {drift:.4f}")
    if not a1.empty:
        best = a1["MAE_log"].idxmin()
        log(f"  A1 best model: {best} at {a1.loc[best, 'MAE_log']:.4f} -> "
            f"{'BEATS' if a1.loc[best, 'MAE_log'] < min(naive, drift) else 'DOES NOT BEAT'} "
            f"the better baseline")
    log(f"\n  A2 baseline MAE_log {a2_base:.4f}")
    if not a2.empty:
        best = a2["MAE_log"].idxmin()
        log(f"  A2 best model: {best} at {a2.loc[best, 'MAE_log']:.4f} -> "
            f"{'BEATS' if a2.loc[best, 'MAE_log'] < a2_base else 'DOES NOT BEAT'} the baseline")
    if not a2_od.empty:
        best = a2_od["MAE_log"].idxmin()
        log(f"\n  A2+OD best model: {best} at {a2_od.loc[best, 'MAE_log']:.4f} "
            f"(different sample, not comparable to the above)")

    head("selection on the rolling-origin means (this is what Phase 8 should tune)")
    for name, frame in [("A1", a1_cv), ("A2", a2_cv)]:
        if frame.empty:
            continue
        ranked = frame.sort_values("mean_MAE_log")
        log(f"  {name}: " + ", ".join(
            f"{model} {row.mean_MAE_log:.4f}" for model, row in ranked.iterrows()))
        log(f"      -> lowest mean fold error: {ranked.index[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
