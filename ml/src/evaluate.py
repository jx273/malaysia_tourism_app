"""Phase 9 - score the final model on the untouched 2024-2025 holdout.

Run from the ml/ folder:   python src/evaluate.py
Input:   data/processed/features.parquet, models/a2_gap_model.joblib
Output:  data/processed/opportunity_gap.parquet
         reports/figures/11_holdout_actual_vs_expected.png
         reports/figures/12_opportunity_gap_2025.png
         reports/figures/13_feature_importance.png

This is the first and only time the holdout is read. The model and its hyperparameters were
fixed in Phase 8 using rolling-origin folds over 2018, 2019 and 2023 only.

A random forest is also scored here. It is a **diagnostic, not a selection**: the choice was
made before the holdout was opened, and reporting a second model afterwards would be using
the holdout to choose if it changed the decision. It does not.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.pipeline import Pipeline

sys.path.insert(0, str(Path(__file__).resolve().parent))
from features import STRUCTURAL_FEATURES, TARGET  # noqa: E402

ML_DIR = Path(__file__).resolve().parents[1]
PROCESSED = ML_DIR / "data" / "processed"
MODELS = ML_DIR / "models"
FIGURES = ML_DIR / "reports" / "figures"
RANDOM_STATE = 42
HOLDOUT_YEARS = [2024, 2025]


def log(message: str = "") -> None:
    print(message, flush=True)


def head(title: str) -> None:
    log(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def metrics(actual_log: np.ndarray, predicted_log: np.ndarray) -> dict[str, float]:
    actual, predicted = np.exp(actual_log), np.exp(predicted_log)
    error = predicted - actual
    return {"MAE_log": float(np.mean(np.abs(predicted_log - actual_log))),
            "MAE_000": float(np.mean(np.abs(error))),
            "RMSE_000": float(np.sqrt(np.mean(error ** 2))),
            "MAPE_%": float(np.mean(np.abs(error / actual)) * 100)}


def main() -> int:
    FIGURES.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(PROCESSED / "features.parquet")
    df["state"] = df["state"].astype(str)
    usable = df[df.in_structural_sample & (df.year >= 2017)].dropna(
        subset=STRUCTURAL_FEATURES + [TARGET])
    fit_pool = usable[~usable.year.isin(HOLDOUT_YEARS)]
    holdout = usable[usable.year.isin(HOLDOUT_YEARS)]

    model = joblib.load(MODELS / "a2_gap_model.joblib")
    metadata = json.loads((MODELS / "a2_gap_model_metadata.json").read_text(encoding="utf-8"))

    head("holdout")
    log(f"  model: {metadata['family']} {metadata['params']}")
    log(f"  trained on {metadata['n_training_rows']} rows, years {metadata['trained_on_years']}")
    log(f"  holdout: {len(holdout)} rows, years {sorted(holdout.year.unique())}, "
        f"{holdout.state.nunique()} states")

    x_hold = holdout[STRUCTURAL_FEATURES].to_numpy()
    y_hold = holdout[TARGET].to_numpy()
    predicted = model.predict(x_hold)

    head("headline: model against baseline on the holdout")
    intensity = float((np.exp(fit_pool[TARGET]) / fit_pool["population_000"]).mean())
    base_pred = np.log(intensity * holdout["population_000"].to_numpy())
    rows = [{"model": "Baseline: national mean intensity x population", **metrics(y_hold, base_pred)},
            {"model": f"Final model ({metadata['family']}, tuned)", **metrics(y_hold, predicted)}]

    # Diagnostic only - the selection was made in Phase 8, before this file was run.
    rf = Pipeline([("model", RandomForestRegressor(n_estimators=300, min_samples_leaf=1,
                                                   random_state=RANDOM_STATE, n_jobs=-1))])
    rf.fit(fit_pool[STRUCTURAL_FEATURES].to_numpy(), fit_pool[TARGET].to_numpy())
    rows.append({"model": "Random forest (diagnostic, not selected)",
                 **metrics(y_hold, rf.predict(x_hold))})
    table = pd.DataFrame(rows).set_index("model")
    log(table.round(4).to_string())

    improvement = 1 - table.loc[f"Final model ({metadata['family']}, tuned)", "MAE_log"] / \
        table.loc["Baseline: national mean intensity x population", "MAE_log"]
    log(f"\n  model vs baseline on MAE_log: {improvement:+.1%}")
    log(f"  selection-time estimate was {metadata['selection']['mean_MAE_log']:.4f}; "
        f"holdout is {table.iloc[1]['MAE_log']:.4f}")

    head("error by year")
    holdout = holdout.copy()
    holdout["predicted_log"] = predicted
    holdout["expected_000"] = np.exp(predicted)
    holdout["actual_000"] = np.exp(y_hold)
    holdout["abs_error_log"] = np.abs(predicted - y_hold)
    holdout["gap_000"] = holdout["expected_000"] - holdout["actual_000"]
    holdout["gap_pct"] = holdout["gap_000"] / holdout["actual_000"] * 100
    by_year = holdout.groupby("year").agg(rows=("state", "size"),
                                          MAE_log=("abs_error_log", "mean"))
    log(by_year.round(4).to_string())

    head("error by state (holdout, both years)")
    by_state = (holdout.groupby("state")
                .agg(MAE_log=("abs_error_log", "mean"),
                     mean_actual_000=("actual_000", "mean"))
                .sort_values("MAE_log", ascending=False))
    log(by_state.round(3).to_string())
    log(f"\n  worst state {by_state.index[0]} at {by_state.iloc[0]['MAE_log']:.3f}, "
        f"best {by_state.index[-1]} at {by_state.iloc[-1]['MAE_log']:.3f}")
    small = by_state[by_state.mean_actual_000 < 5000]
    large = by_state[by_state.mean_actual_000 >= 20000]
    log(f"  mean error for states under 5m visitors: {small['MAE_log'].mean():.3f} "
        f"({len(small)} states)")
    log(f"  mean error for states over 20m visitors: {large['MAE_log'].mean():.3f} "
        f"({len(large)} states)")

    head("feature importance")
    perm = permutation_importance(model, x_hold, y_hold, n_repeats=30,
                                  random_state=RANDOM_STATE, scoring="neg_mean_absolute_error")
    importance = (pd.DataFrame({"feature": STRUCTURAL_FEATURES,
                                "permutation_mean": perm.importances_mean,
                                "permutation_sd": perm.importances_std,
                                "impurity": model.named_steps["model"].feature_importances_})
                  .sort_values("permutation_mean", ascending=False))
    log(importance.round(4).to_string(index=False))

    head("systematic bias check")
    holdout["signed_error_log"] = holdout["predicted_log"] - holdout[TARGET]
    bias = holdout.groupby("year")["signed_error_log"].mean()
    log("  mean signed error in log space, by year (negative = model under-predicts):")
    log(bias.round(4).to_string())
    log(f"  share of holdout rows under-predicted: "
        f"{(holdout.signed_error_log < 0).mean():.0%}")
    log("")
    log("  The structural model has no time term, by design: it estimates the level implied")
    log("  by a state's population, economy and capacity. National visitor numbers grew from")
    log("  213.7m in 2023 to 290.1m in 2025 while those fundamentals barely moved, so the")
    log("  model under-predicts every state in the holdout years. A gap measured in levels")
    log("  would therefore be measuring national growth, not state performance.")

    head("opportunity gap, expressed in shares")
    # Normalising to shares removes the national level entirely, which is what makes the
    # comparison between states meaningful. Positive gap = the state takes a smaller share
    # of national visitors than its fundamentals imply.
    for year, group in holdout.groupby("year"):
        holdout.loc[group.index, "expected_share"] = group.expected_000 / group.expected_000.sum()
        holdout.loc[group.index, "actual_share"] = group.actual_000 / group.actual_000.sum()
    holdout["gap_share_pp"] = (holdout.expected_share - holdout.actual_share) * 100
    holdout["gap_share_rel_pct"] = (holdout.expected_share / holdout.actual_share - 1) * 100
    # Expected share applied to the year's own national total, so the level and the gap
    # sit on one scale and cannot contradict each other on screen.
    for year, group in holdout.groupby("year"):
        national = group.actual_000.sum()
        holdout.loc[group.index, "expected_benchmarked_000"] = group.expected_share * national
    holdout["gap_visitors_000"] = holdout.expected_benchmarked_000 - holdout.actual_000

    head("opportunity gap, 2025")
    latest = holdout[holdout.year == 2025].sort_values("gap_share_rel_pct", ascending=False)
    log(latest[["state", "actual_000", "expected_000", "actual_share", "expected_share",
                "gap_share_pp", "gap_share_rel_pct"]].round(4).to_string(index=False))
    log("")
    log("  positive = the state receives a smaller share of national visitors than its")
    log("  population, economy and accommodation capacity imply")

    stability = holdout.pivot(index="state", columns="year", values="gap_share_rel_pct")
    agreement = ((stability[2024] > 0) == (stability[2025] > 0)).mean()
    log("")
    log(f"  states with the same sign of gap in both holdout years: {agreement:.0%}")
    log(f"  correlation of the 2024 and 2025 gap rankings: "
        f"{stability[2024].corr(stability[2025], method='spearman'):.3f}")

    gap_table = holdout[["state", "year", "actual_000", "expected_benchmarked_000",
                         "gap_visitors_000", "actual_share", "expected_share",
                         "gap_share_pp", "gap_share_rel_pct", "expected_000", "gap_000",
                         "gap_pct", "population_000", "rooms"]].copy()
    gap_table.to_parquet(PROCESSED / "opportunity_gap.parquet", index=False)
    log(f"\n  written: data/processed/opportunity_gap.parquet ({len(gap_table)} rows)")

    # ---------------- figures ----------------
    fig, ax = plt.subplots(figsize=(5.6, 5.4))
    limits = [holdout.actual_000.min() * 0.7, holdout.actual_000.max() * 1.3]
    ax.plot(limits, limits, color="0.6", linestyle="--", linewidth=1)
    for year, colour in [(2024, "#1f4e79"), (2025, "#c0392b")]:
        subset = holdout[holdout.year == year]
        ax.scatter(subset.actual_000, subset.expected_000, s=30, color=colour, label=str(year))
    for _, row in holdout[holdout.year == 2025].iterrows():
        if abs(row.gap_pct) > 25:
            ax.annotate(row.state, (row.actual_000, row.expected_000), fontsize=6,
                        xytext=(3, 3), textcoords="offset points")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Actual visitors ('000)")
    ax.set_ylabel("Raw model output ('000)")
    ax.set_title("Holdout 2024-2025: raw model output against actual (accuracy view)")
    ax.legend(frameon=False, fontsize=8)
    fig.savefig(FIGURES / "11_holdout_actual_vs_expected.png", bbox_inches="tight", dpi=130)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4.6))
    ordered = latest.sort_values("gap_share_rel_pct")
    colours = ["#c0392b" if v > 0 else "#1f4e79" for v in ordered.gap_share_rel_pct]
    ax.barh(ordered.state, ordered.gap_share_rel_pct, color=colours)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Opportunity gap: expected share vs actual share, %  (positive = under-performing)")
    ax.set_title("Tourism Opportunity Gap by state, 2025")
    fig.savefig(FIGURES / "12_opportunity_gap_2025.png", bbox_inches="tight", dpi=130)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    top = importance.head(10).iloc[::-1]
    ax.barh(top.feature, top.permutation_mean, xerr=top.permutation_sd,
            color="#1f4e79", error_kw={"linewidth": 0.8})
    ax.set_xlabel("Permutation importance (increase in MAE when shuffled)")
    ax.set_title("What drives the expected-demand model")
    fig.savefig(FIGURES / "13_feature_importance.png", bbox_inches="tight", dpi=130)
    plt.close(fig)
    log("  figures written: 11, 12, 13")
    return 0


if __name__ == "__main__":
    sys.exit(main())
