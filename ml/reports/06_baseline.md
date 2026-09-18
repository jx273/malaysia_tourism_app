# 06 — Baselines

**Phase:** 6
**Script:** `ml/src/train.py` → `baselines()` and the per-fold baseline inside `rolling_origin()`
**Run:** 2026-09-16, from `ml/`: `python src/train.py`

A baseline is what the model has to beat to be worth building. Three are defined, one per
model plus a drift variant, and all are fitted on training years only.

---

## The baselines

### A1 — forecasting

**B1. Last value (naive).** Predict this year's visitors as last year's:
`log_visitors(t) = log_visitors(t−1)`. For an annual series with no seasonality this is the
standard naive forecast, and Phase 3 showed the series is highly persistent.

**B2. Last value plus drift.** `log_visitors(t) = log_visitors(t−1) + d`, where `d` is the
mean year-on-year log change **measured on the training years only**.

The estimated drift is **−0.0359 in log space, i.e. −3.5% per year**. It is negative because
the training window 2018–2022 contains the two collapse years, so a drift term fitted there
carries the pandemic forward into a normal year. This is why B2 is *worse* than B1 on 2023,
and it is a useful illustration of how a sensible-looking correction can be harmful when the
training window spans a structural break.

### A2 — structural expectation

**B3. National mean intensity × population.** Compute mean visitors per resident across the
training years, then predict `visitors = intensity × population`. Measured on the training
years: **8.16 visitors per resident**.

This is the baseline that matters most. It is exactly what a stakeholder could work out on
the back of an envelope — "a state should get visitors in proportion to its population" — so
if the structural model cannot beat it, the model adds nothing.

---

## Metrics on the 2023 validation year

The 2024–2025 holdout is untouched. `MAE_log` is the mean absolute error of
`log(visitors_000)`; the level metrics come from exponentiating, which returns a median
rather than a mean, so both are reported.

| Baseline | n | MAE_log | MAE ('000) | RMSE ('000) | MAPE % |
|---|---:|---:|---:|---:|---:|
| **B1** A1 naive: last value | 16 | **0.2266** | 2,633.8 | 3,077.4 | 20.1 |
| B2 A1 naive + drift | 16 | 0.2625 | 3,012.2 | 3,495.3 | 22.9 |
| **B3** A2 national mean intensity × population | 16 | **0.4370** | 6,664.1 | 10,286.8 | 52.7 |

## The same baselines across rolling-origin folds

A single validation year is 16 rows, so each baseline was also refitted and scored on every
fold used in Phase 7.

| Fold | B1 (A1 naive) | B3 (A2 intensity) |
|---|---:|---:|
| 2018 | — | 0.3153 |
| 2019 | — | 0.3185 |
| 2020 | 0.6689 | — |
| 2021 | 0.7562 | — |
| 2022 | 1.0822 | — |
| 2023 | 0.2266 | 0.4370 |
| **mean** | **0.6835** | **0.3569** |

The A1 baseline's error is three to five times larger in 2020–2022 than in 2023, which is the
pandemic showing up as unforecastable. The A2 baseline is stable across its folds because the
structural sample excludes those years by design.

**Reading for Phase 7:** any model claiming to forecast must beat **0.6835** across folds, not
just 0.2266 on the one easy year. Any structural model must beat **0.3569**.
