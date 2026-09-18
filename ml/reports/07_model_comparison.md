# 07 — Model comparison

**Phase:** 7 — decision point.
**Script:** `ml/src/train.py`
**Run:** 2026-09-16, from `ml/`: `python src/train.py`
**Baselines to beat:** `reports/06_baseline.md`

**The 2024–2025 holdout has not been touched.** Selection uses 2023 as the validation year
plus rolling-origin folds over earlier years. Phase 9 is the first and only time the holdout
is scored.

Four models of increasing complexity, identical features, identical splits, identical
metrics, `random_state=42` throughout. Scalers sit inside a `Pipeline`, so they are fitted on
each training fold only and no validation statistic reaches a fitted transform.

| Model | Specification |
|---|---|
| Linear regression | ordinary least squares, standardised inputs |
| Ridge | L2, `alpha=1.0`, standardised inputs |
| Random forest | 300 trees, `min_samples_leaf=2` |
| Gradient boosting | 200 stages, `max_depth=2`, `learning_rate=0.05` |

---

## 1. Model A1 — forecasting (lags allowed)

14 features, 70 training rows (2018–2022), 16 validation rows (2023), 32 holdout rows
reserved.

### On the single validation year, 2023

| Model | MAE_log | MAE ('000) | RMSE ('000) | MAPE % | train MAE_log | fit (s) |
|---|---:|---:|---:|---:|---:|---:|
| Linear regression | 1.6574 | 163,036.1 | 525,849.5 | 7514.4 | 0.1297 | 0.016 |
| Ridge | 0.3840 | 4,316.6 | 5,479.4 | 51.2 | 0.1403 | 0.001 |
| Random forest | 0.3347 | 3,881.4 | 4,780.3 | 27.4 | 0.1228 | 0.185 |
| **Gradient boosting** | **0.1833** | 1,807.6 | 2,820.7 | 20.0 | 0.0503 | 0.051 |
| *B1 baseline (last value)* | *0.2266* | *2,633.8* | *3,077.4* | *20.1* | — | — |

On this one year, gradient boosting beats the naive baseline. **That conclusion does not
survive contact with more folds.**

### Across rolling-origin folds

Train on every year before *v*, validate on *v*. The holdout is never a fold.

| Fold | Baseline | Linear | Ridge | Random forest | Gradient boosting |
|---|---:|---:|---:|---:|---:|
| 2020 | **0.6689** | 0.7624 | 0.7561 | 0.7089 | 0.7119 |
| 2021 | 0.7562 | 4.3506 | **0.5806** | 0.9874 | 0.9151 |
| 2022 | **1.0822** | 1.3978 | 1.4716 | 1.2986 | 1.6035 |
| 2023 | 0.2266 | 1.6574 | 0.3840 | 0.3347 | **0.1833** |
| **mean** | **0.6835** | 2.0421 | 0.7981 | 0.8324 | 0.8534 |
| worst fold | 1.0822 | 4.3506 | 1.4716 | 1.2986 | 1.6035 |

### ⚠️ Finding: no A1 model beats the naive baseline

Mean fold error: **baseline 0.6835**, best model **Ridge 0.7981**. Gradient boosting, the
winner on the single 2023 fold, comes fourth across folds at 0.8534.

Three things are going on, and all three are worth saying out loud:

1. **2020–2022 are not forecastable.** Every method, baseline included, produces errors three
   to five times its 2023 error on those folds. A model cannot anticipate a border closure
   from the state's population and hotel stock.
2. **The single-year result was misleading.** Ranking four models on 16 rows of one year
   picked gradient boosting; four folds put it last. This is why the rolling-origin check was
   added rather than reporting the 2023 column alone.
3. **Gradient boosting is overfitting.** Training error 0.0503 against validation 0.1833 on
   the 2023 split — a factor of 3.6 — on 70 rows.

**Linear regression is unusable**, with a MAPE of 7,514% on 2023 and 4.35 MAE_log on the 2021
fold. That is the collinearity Phase 3 measured (pairwise correlations to 0.992,
`figures/07_correlation_matrix.png`) doing exactly what collinearity does to an unregularised
fit on 70 rows. It is kept in the table as evidence for the modelling choice, not as a
contender.

---

## 2. Model A2 — structural expectation (no lag of the target)

12 features, 42 training rows (2017–2019), 16 validation rows (2023), 32 holdout rows
reserved.

### On the single validation year, 2023

| Model | MAE_log | MAE ('000) | RMSE ('000) | MAPE % | train MAE_log | fit (s) |
|---|---:|---:|---:|---:|---:|---:|
| Linear regression | 1.5811 | 23,858.1 | 37,441.2 | 239.5 | 0.1658 | 0.001 |
| Ridge | 0.3432 | 3,161.9 | 3,888.3 | 36.2 | 0.2050 | 0.001 |
| Random forest | 0.2289 | 2,133.0 | 2,989.8 | 26.0 | 0.0836 | 0.161 |
| **Gradient boosting** | **0.2058** | 1,987.9 | 2,461.0 | 22.2 | 0.0182 | 0.047 |
| *B3 baseline (intensity × population)* | *0.4370* | *6,664.1* | *10,286.8* | *52.7* | — | — |

### Across rolling-origin folds

| Fold | Baseline | Linear | Ridge | Random forest | Gradient boosting |
|---|---:|---:|---:|---:|---:|
| 2018 | 0.3153 | 0.3310 | 0.1939 | 0.2767 | **0.1636** |
| 2019 | 0.3185 | 0.1998 | 0.2341 | 0.1781 | **0.0959** |
| 2023 | 0.4370 | 1.5811 | 0.3432 | 0.2289 | **0.2058** |
| **mean** | 0.3569 | 0.7040 | 0.2571 | 0.2279 | **0.1551** |
| worst fold | 0.4370 | 1.5811 | 0.3432 | 0.2767 | **0.2058** |

### ✅ Finding: A2 gradient boosting beats its baseline on every fold

Mean fold error **0.1551 against the baseline's 0.3569 — a 57% reduction** — and it is the
best model on all three folds, not on average only. Its worst fold (0.2058) is still better
than the baseline's best fold (0.3153).

This is the model that produces the Opportunity Gap, so this is the result that matters for
the product. Ridge and random forest also beat the baseline, so the conclusion does not rest
on one model family.

**Caveat, stated plainly:** gradient boosting's training error on the 2023 split is 0.0182
against 0.2058 on validation, a factor of 11. On 42 training rows it is partly memorising.
Random forest at 0.2279 mean is close behind with a much smaller train/validation gap, and is
the safer choice if Phase 8 tuning cannot close that gap.

---

## 3. Model A2 + OD features — cross-sectional only

15 features. The origin-destination matrix starts in 2023, so this variant has **16 training
rows (2023) and 16 validation rows (2024)**. It is reported for completeness because the team
asked for the OD features on 2026-09-16; it is not a candidate for selection.

| Model | MAE_log | MAE ('000) | MAPE % | train MAE_log |
|---|---:|---:|---:|---:|
| Linear regression | 1.5455 | 137,653.4 | 2382.1 | 0.0461 |
| Ridge | 0.2937 | 4,120.0 | 26.0 | 0.2117 |
| Random forest | 0.3643 | 4,442.3 | 40.5 | 0.1949 |
| Gradient boosting | 0.2822 | 3,105.0 | 23.0 | 0.0030 |

**Not comparable to section 2** — different sample, different years, one training year. A
gradient boosting training error of 0.0030 on 16 rows is memorisation, not learning.

**Conclusion on OD:** the features are built, documented and available in
`features.parquet`, and their descriptive value is real — Phase 3's finding that within-state
tourism fell from 36.4% to 22.6% and that every large flow starts in the Klang Valley is a
strong dashboard and report story. But they cannot enter the model that produces the
headline gap without cutting its sample in half. **Recommendation: keep OD as a dashboard and
narrative layer, not as a model input.**

---

## 4. Recommendation for Phase 8

| | Recommendation |
|---|---|
| **A2 (the gap model)** | Tune **gradient boosting**, with **random forest as the fallback** if the train/validation gap does not close. Both beat the baseline on every fold. |
| **A1 (the forecast)** | **Do not present a tuned ML forecaster as beating the baseline, because it does not.** Two honest options below — this needs a decision. |

### The A1 decision

**Option 1 — ship the naive baseline as the forecast component.** It is the most accurate
method tested across folds (0.6835), it is trivially explainable to judges, and the report
says so directly: "we tested four models against a naive baseline for year-ahead forecasting
and none beat it, so the forecast layer uses the naive method." This is an honest negative
result and rubric criterion `ANL4` rewards explaining analytical decisions.

**Option 2 — restrict A1's claim to non-pandemic years.** On the 2023 fold gradient boosting
does beat the baseline (0.1833 against 0.2266). The claim becomes "in a normal year the model
improves on naive by 19%", with the pandemic folds shown as the limit of the method. Weaker
evidence — one fold — but it keeps an ML forecaster in the story.

**My recommendation is Option 1**, with the 2023 result shown as supporting detail. The
project's ML contribution is A2, which is strong and survives every fold; A1's job was to
test whether a forecast adds anything, and the honest answer is that it does not beat naive
across the period we have. Claiming otherwise on one fold is exactly what a judge asking
"how do you know your AI works" is looking for.

## 5. What Phase 9 will do

Score the tuned A2 on the **2024–2025 holdout**, untouched until then, and report: metrics
against the baseline, error broken down by state and by year, feature importance, and the
gap rankings with their limitations.
