"""Phase 8 - tune the A2 structural model and save it.

Run from the ml/ folder:   python src/tune.py
Input:   data/processed/features.parquet
Output:  models/a2_gap_model.joblib, models/a2_gap_model_metadata.json

Scope, per the decisions of 2026-09-16:
- Tune gradient boosting, with random forest as the fallback if the train/validation gap
  does not close.
- The forecast layer is the naive last-value baseline. Phase 7 found no model beat it
  across folds, so there is nothing to tune there; predict.py implements it as a formula.
- The origin-destination features are a dashboard and narrative layer, not model inputs.
- No LLM or NLP component: the project holds no text to model and none could be evaluated.

**The 2024-2025 holdout is never read here.** Selection uses the same rolling-origin folds
as Phase 7. The chosen configuration is then refitted on every non-holdout structural row.
"""
from __future__ import annotations

import json
import sys
import time
from itertools import product
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.pipeline import Pipeline

sys.path.insert(0, str(Path(__file__).resolve().parent))
from features import STRUCTURAL_FEATURES, TARGET  # noqa: E402

ML_DIR = Path(__file__).resolve().parents[1]
PROCESSED = ML_DIR / "data" / "processed"
MODELS = ML_DIR / "models"
RANDOM_STATE = 42

FOLD_YEARS = [2018, 2019, 2023]
HOLDOUT_YEARS = [2024, 2025]


def log(message: str = "") -> None:
    print(message, flush=True)


def head(title: str) -> None:
    log(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def mae_log(actual: np.ndarray, predicted: np.ndarray) -> float:
    return float(np.mean(np.abs(predicted - actual)))


def structural_rows(df: pd.DataFrame) -> pd.DataFrame:
    rows = df[df.in_structural_sample & (df.year >= 2017)]
    return rows.dropna(subset=STRUCTURAL_FEATURES + [TARGET])


def score(pipeline_factory, usable: pd.DataFrame) -> dict[str, float]:
    """Mean error across rolling-origin folds, plus the train/validation gap."""
    valid_scores, train_scores = [], []
    for year in FOLD_YEARS:
        train = usable[usable.year < year]
        valid = usable[usable.year == year]
        if len(train) < 10 or valid.empty:
            continue
        pipeline = pipeline_factory()
        pipeline.fit(train[STRUCTURAL_FEATURES].to_numpy(), train[TARGET].to_numpy())
        valid_scores.append(mae_log(valid[TARGET].to_numpy(),
                                    pipeline.predict(valid[STRUCTURAL_FEATURES].to_numpy())))
        train_scores.append(mae_log(train[TARGET].to_numpy(),
                                    pipeline.predict(train[STRUCTURAL_FEATURES].to_numpy())))
    return {"folds": len(valid_scores),
            "mean_MAE_log": float(np.mean(valid_scores)),
            "worst_fold": float(np.max(valid_scores)),
            "mean_train_MAE_log": float(np.mean(train_scores)),
            "overfit_ratio": float(np.mean(valid_scores) / max(np.mean(train_scores), 1e-9))}


def gradient_boosting_grid() -> list[dict]:
    """Deliberately small. With 42 training rows a large grid tunes to noise."""
    grid = []
    for n, depth, rate, leaf, sub in product(
            [100, 200, 400], [1, 2, 3], [0.03, 0.05, 0.1], [1, 3], [0.8, 1.0]):
        grid.append({"n_estimators": n, "max_depth": depth, "learning_rate": rate,
                     "min_samples_leaf": leaf, "subsample": sub})
    return grid


def random_forest_grid() -> list[dict]:
    return [{"n_estimators": n, "max_depth": depth, "min_samples_leaf": leaf}
            for n, depth, leaf in product([300, 600], [None, 3, 5], [1, 2, 3])]


def main() -> int:
    df = pd.read_parquet(PROCESSED / "features.parquet")
    df["state"] = df["state"].astype(str)
    usable = structural_rows(df)
    fit_pool = usable[~usable.year.isin(HOLDOUT_YEARS)]

    head("sample")
    log(f"  structural rows (excluding holdout): {len(fit_pool)}, "
        f"years {sorted(fit_pool.year.unique())}")
    log(f"  holdout rows reserved and not read here: "
        f"{len(usable[usable.year.isin(HOLDOUT_YEARS)])}")
    log(f"  features: {len(STRUCTURAL_FEATURES)}")

    head("tuning gradient boosting")
    started = time.perf_counter()
    results = []
    for params in gradient_boosting_grid():
        factory = lambda p=params: Pipeline([("model", GradientBoostingRegressor(
            random_state=RANDOM_STATE, **p))])
        results.append({**params, "family": "GradientBoosting", **score(factory, fit_pool)})
    gb = pd.DataFrame(results).sort_values("mean_MAE_log")
    log(f"  {len(gb)} configurations in {time.perf_counter() - started:.1f}s")
    log("\n  top 8 by mean fold error:")
    log(gb.head(8).round(4).to_string(index=False))

    head("tuning random forest (fallback)")
    started = time.perf_counter()
    results = []
    for params in random_forest_grid():
        factory = lambda p=params: Pipeline([("model", RandomForestRegressor(
            random_state=RANDOM_STATE, n_jobs=-1, **p))])
        results.append({**params, "family": "RandomForest", **score(factory, fit_pool)})
    rf = pd.DataFrame(results).sort_values("mean_MAE_log")
    log(f"  {len(rf)} configurations in {time.perf_counter() - started:.1f}s")
    log("\n  top 5 by mean fold error:")
    log(rf.head(5).round(4).to_string(index=False))

    head("selection")
    best_gb, best_rf = gb.iloc[0], rf.iloc[0]
    log(f"  best gradient boosting: mean {best_gb.mean_MAE_log:.4f}, "
        f"worst fold {best_gb.worst_fold:.4f}, train {best_gb.mean_train_MAE_log:.4f}, "
        f"valid/train ratio {best_gb.overfit_ratio:.1f}")
    log(f"  best random forest    : mean {best_rf.mean_MAE_log:.4f}, "
        f"worst fold {best_rf.worst_fold:.4f}, train {best_rf.mean_train_MAE_log:.4f}, "
        f"valid/train ratio {best_rf.overfit_ratio:.1f}")
    log(f"  Phase 7 untuned gradient boosting was 0.1551 mean, ratio 8.5")
    log(f"  Phase 6 baseline (intensity x population) was 0.3569 mean")

    if best_gb.mean_MAE_log <= best_rf.mean_MAE_log:
        chosen, family = best_gb, "GradientBoosting"
        keys = ["n_estimators", "max_depth", "learning_rate", "min_samples_leaf", "subsample"]
        params = {k: chosen[k] for k in keys}
        params["max_depth"] = int(params["max_depth"])
        params["n_estimators"] = int(params["n_estimators"])
        params["min_samples_leaf"] = int(params["min_samples_leaf"])
        estimator = GradientBoostingRegressor(random_state=RANDOM_STATE, **params)
    else:
        chosen, family = best_rf, "RandomForest"
        params = {"n_estimators": int(chosen["n_estimators"]),
                  "max_depth": None if pd.isna(chosen["max_depth"]) else int(chosen["max_depth"]),
                  "min_samples_leaf": int(chosen["min_samples_leaf"])}
        estimator = RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1, **params)
    log(f"\n  chosen: {family} {params}")

    head("refit on every non-holdout structural row")
    final = Pipeline([("model", estimator)])
    final.fit(fit_pool[STRUCTURAL_FEATURES].to_numpy(), fit_pool[TARGET].to_numpy())
    log(f"  fitted on {len(fit_pool)} rows, years {sorted(fit_pool.year.unique())}")
    log(f"  in-sample MAE_log: "
        f"{mae_log(fit_pool[TARGET].to_numpy(), final.predict(fit_pool[STRUCTURAL_FEATURES].to_numpy())):.4f}")

    MODELS.mkdir(parents=True, exist_ok=True)
    model_path = MODELS / "a2_gap_model.joblib"
    joblib.dump(final, model_path)
    metadata = {
        "created": "2026-09-16",
        "phase": 8,
        "purpose": "Model A2 - structural expected demand; the opportunity gap is expected minus actual",
        "family": family,
        "params": {k: (None if v is None else (int(v) if isinstance(v, (int, np.integer)) else float(v)))
                   for k, v in params.items()},
        "features": STRUCTURAL_FEATURES,
        "target": TARGET,
        "target_units": "log of domestic visitors in thousands",
        "trained_on_years": sorted(int(y) for y in fit_pool.year.unique()),
        "n_training_rows": int(len(fit_pool)),
        "holdout_years": HOLDOUT_YEARS,
        "selection": {"method": "rolling-origin folds", "folds": FOLD_YEARS,
                      "mean_MAE_log": float(chosen.mean_MAE_log),
                      "worst_fold_MAE_log": float(chosen.worst_fold),
                      "mean_train_MAE_log": float(chosen.mean_train_MAE_log)},
        "baseline_mean_MAE_log": 0.3569,
        "random_state": RANDOM_STATE,
        "sklearn_version": __import__("sklearn").__version__,
    }
    meta_path = MODELS / "a2_gap_model_metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    head("saved")
    log(f"  {model_path.relative_to(ML_DIR).as_posix()}  "
        f"({model_path.stat().st_size / 1e6:.3f} MB)")
    log(f"  {meta_path.relative_to(ML_DIR).as_posix()}")

    gb.to_csv(PROCESSED / "tuning_gradient_boosting.csv", index=False)
    rf.to_csv(PROCESSED / "tuning_random_forest.csv", index=False)
    log(f"  full grids written to data/processed/tuning_*.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
