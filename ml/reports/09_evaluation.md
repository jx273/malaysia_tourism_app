# 09 — Evaluation on the untouched holdout

**Phase:** 9
**Script:** `ml/src/evaluate.py`
**Run:** 2026-09-16, from `ml/`: `python src/evaluate.py`
**Model:** `models/a2_gap_model.joblib` — gradient boosting, `n_estimators=400`,
`max_depth=2`, `learning_rate=0.03`, `min_samples_leaf=3`, `subsample=1.0`,
`random_state=42`. Trained on 58 rows (2017–2019 and 2023).

**The 2024–2025 holdout was read for the first time by this script.** Hyperparameters were
fixed in Phase 8 using rolling-origin folds over 2018, 2019 and 2023 only.

---

## 1. Headline: the model beats its baseline

32 holdout rows, 16 states, 2024 and 2025.

| Model | MAE_log | MAE ('000) | RMSE ('000) | MAPE % |
|---|---:|---:|---:|---:|
| Baseline — national mean intensity × population | 0.4467 | 7,071.5 | 9,715.2 | 41.4 |
| **Final model — gradient boosting, tuned** | **0.2648** | **3,772.9** | **4,814.0** | **22.5** |
| Random forest — diagnostic, **not** selected | 0.2584 | 3,691.2 | 5,100.2 | 21.3 |

**The model reduces holdout error by 40.7% against the baseline**, and halves MAPE from
41.4% to 22.5%.

Two things must be said alongside that number:

- **The holdout error is nearly double the selection-time estimate** — 0.2648 against 0.1373
  from the rolling-origin folds. That is what out-of-period generalisation costs: the folds
  sat inside the training period, while the holdout is one and two years past the last
  training year and after two years of strong national growth. The selection estimate was
  optimistic, and reporting only it would have been misleading.
- **The random forest scores marginally better on the holdout** (0.2584 against 0.2648).
  It was not selected: the decision was made in Phase 8 on the validation folds, before this
  file was ever run. Swapping now because a second model looks better *on the holdout* would
  turn the holdout into a selection set and destroy the honesty of every number above. The
  difference is 0.006 MAE_log, well inside the noise of 32 rows. It is reported because
  hiding it would be worse.

## 2. Error by year and by state

| Year | Rows | MAE_log |
|---|---:|---:|
| 2024 | 16 | 0.2405 |
| 2025 | 16 | 0.2891 |

Error grows with distance from the training period, as expected.

**By state**, mean over both holdout years:

| State | MAE_log | Mean actual ('000) |
|---|---:|---:|
| Perlis | 0.708 | 3,491 |
| W.P. Putrajaya | 0.408 | 2,852 |
| Perak | 0.350 | 22,709 |
| W.P. Kuala Lumpur | 0.327 | 31,021 |
| Melaka | 0.325 | 19,980 |
| Pahang | 0.309 | 21,668 |
| Selangor | 0.296 | 35,419 |
| Sabah | 0.257 | 21,476 |
| Kelantan | 0.246 | 11,288 |
| Sarawak | 0.189 | 21,174 |
| Negeri Sembilan | 0.176 | 18,571 |
| Pulau Pinang | 0.174 | 17,161 |
| Terengganu | 0.170 | 14,962 |
| W.P. Labuan | 0.145 | 527 |
| Kedah | 0.120 | 15,130 |
| Johor | 0.036 | 17,668 |

- **States under 5m visitors: mean error 0.421** (3 states) against **0.288 for states over
  20m** (6 states). Phase 3 predicted this — small states are the volatile ones (Perlis
  year-on-year σ = 28.0 against Sarawak 5.1) — and it is why absolute error is reported
  beside percentage error.
- **Perlis is the worst state by a wide margin at 0.708.** Any statement the dashboard makes
  about Perlis should carry a warning.

`figures/11_holdout_actual_vs_expected.png`

## 3. A systematic bias, and what was done about it

| Year | Mean signed error (log) |
|---|---:|
| 2024 | −0.2063 |
| 2025 | −0.2781 |

**91% of holdout rows are under-predicted.** This is not random error, and it has a clear
cause: the structural model has **no time term by design** — it estimates the level implied
by a state's population, economy and capacity. National visitors grew from 213.7m in 2023 to
290.1m in 2025 while those fundamentals barely moved, so the model under-predicts everywhere
in the holdout years.

**Consequence: a gap measured in levels would have been measuring national growth, not state
performance.** In the first run of this script, 15 of 16 states showed a "positive
opportunity" in 2025 — which is meaningless.

**The gap is therefore expressed in shares**: each state's share of national visitors against
the share its fundamentals imply. Normalising removes the national level entirely, which is
what makes a comparison between states meaningful. No retraining was needed; this is a
change in how the model's output is read, and it is the number the dashboard and the report
should use.

## 4. The Tourism Opportunity Gap, 2025

Positive = the state receives a **smaller** share of national visitors than its population,
economy and accommodation capacity imply.

| State | Actual ('000) | Benchmark ('000) | Shortfall ('000) | Gap (pp) | **Gap (%)** |
|---|---:|---:|---:|---:|---:|
| Kedah | 15,608 | 22,258 | +6,650 | +2.29 | **+42.6** |
| Johor | 18,197 | 23,119 | +4,922 | +1.70 | **+27.0** |
| Terengganu | 15,462 | 17,984 | +2,522 | +0.87 | +16.3 |
| W.P. Labuan | 604 | 667 | +62 | +0.02 | +10.3 |
| Pulau Pinang | 17,718 | 19,411 | +1,693 | +0.58 | +9.6 |
| Sabah | 22,361 | 23,577 | +1,216 | +0.42 | +5.4 |
| Negeri Sembilan | 19,357 | 20,309 | +953 | +0.33 | +4.9 |
| Kelantan | 12,062 | 12,357 | +295 | +0.10 | +2.4 |
| Sarawak | 22,722 | 22,815 | +94 | +0.03 | +0.4 |
| Selangor | 36,376 | 33,430 | −2,946 | −1.02 | −8.1 |
| Melaka | 20,832 | 18,744 | −2,088 | −0.72 | −10.0 |
| Pahang | 23,161 | 20,659 | −2,502 | −0.86 | −10.8 |
| Perak | 23,642 | 20,800 | −2,842 | −0.98 | −12.0 |
| W.P. Kuala Lumpur | 35,060 | 28,903 | −6,157 | −2.12 | −17.6 |
| W.P. Putrajaya | 3,146 | 2,462 | −684 | −0.24 | −21.7 |
| Perlis | 3,756 | 2,569 | −1,187 | −0.41 | −31.6 |

**Benchmark** is the state's expected share applied to the year's national total. It exists
because the raw model level cannot be shown beside an actual: anchored on the training
years, it runs low for 2024–2025, and for **8 of the 16 states in 2025 it sat on the opposite
side of the actual from where the gap says the state stands**. Rescaling removes that; the
level, the shortfall and the percentage now agree in direction on all 90 published rows.
The accuracy figures in §1 are unchanged — they are computed on the raw output, since the
benchmark uses the year's own national total and would flatter the model.

`figures/12_opportunity_gap_2025.png`

**Is the ranking stable?** Across the two holdout years, **81% of states keep the same sign**
and the **Spearman correlation of the rankings is 0.732**. The gap is a persistent property
of a state, not a one-year artefact — but 81% is not 100%, and the states near zero
(Sarawak +0.4%, Kelantan +2.4%) should not be presented as findings.

## 5. What the model is actually using

Permutation importance on the holdout, 30 repeats:

| Feature | Permutation mean | SD | Impurity |
|---|---:|---:|---:|
| `log_population` | 0.1749 | 0.0326 | 0.4391 |
| `log_gdp_total` | 0.0830 | 0.0169 | 0.1236 |
| `log_lf_employed` | 0.0714 | 0.0165 | 0.2365 |
| `log_rooms` | 0.0612 | 0.0159 | 0.0887 |
| `log_gdp_services` | 0.0308 | 0.0092 | 0.0581 |
| `rooms_per_1k_residents` | 0.0054 | 0.0098 | 0.0233 |
| `u_rate` | 0.0023 | 0.0092 | 0.0236 |
| `p_rate` | 0.0007 | 0.0012 | 0.0004 |
| `log_gdp_per_capita` | 0.0004 | 0.0002 | 0.0006 |
| `cpi_recreation_rel` | 0.0000 | 0.0015 | 0.0007 |
| `cpi_accom_food_rel` | −0.0010 | 0.0034 | 0.0020 |
| `services_share` | −0.0068 | 0.0049 | 0.0035 |

`figures/13_feature_importance.png`

- **Five size variables carry the model**: population, GDP, employment, rooms, services GDP.
  Population alone is more than twice the next feature.
- **The two CPI features contributed close to zero** (0.0000 and −0.0010, both inside their
  own standard deviation). This is a statement about *this model and this feature set*, not
  about price in general: CPI divisions 09 and 11 are **resident** consumer price indices for
  each state, not measures of tourism prices, so nothing here shows that price is irrelevant
  to an individual traveller's decision. Worth one carefully worded line in the report.
- **Importance is shared, not attributed.** Phase 3 measured pairwise correlations to 0.992
  among these size variables, so permutation importance spreads credit among substitutes.
  No single coefficient should be quoted as "population causes X% of visits".

## 6. Limitations

1. **58 training rows.** Everything here rests on a sample smaller than most spreadsheets.
2. **The gap has no ground truth.** The model's prediction error is measurable; "which state
   has the most untapped potential" is not verifiable against anything. The model identifies
   **underperformance relative to its own expectation**, and nothing in this analysis
   identifies a *cause* — not discoverability, not marketing, not access.
3. **A level gap would have been wrong** (§3). The share formulation is a correction, and the
   report must state that the gap is relative, not absolute.
4. **Small states are unreliable.** Perlis at 0.708 MAE_log is four times the median state.
5. **Hotel capacity is carried back.** `rooms` exists for 2022 and 2023 only, so 2017–2019
   rows use the 2022 figure (`reports/02_cleaning.md` §2.6). Capacity is assumed roughly
   constant within the period.
6. **Annual, state-level, 16 units.** No seasonality, no district detail, no visitor segments.
7. **Excursionists and tourists are mixed.** The target counts domestic *visitors*, most of
   whom are day-trippers; a state weak in overnight tourism can still look strong here.
8. **Domestic only.** Inbound foreign arrivals are not in the model
   (`reports/02_cleaning.md` §7 explains why `arrivals_soe` was excluded).

## 7. Verdict against the acceptance criteria

> *The final model beats the baseline on the holdout set, OR the report states plainly that
> it does not.*

**It beats it: 0.2648 against 0.4467 MAE_log, a 40.7% reduction, on data the model had never
seen.** The forecasting model A1 does **not** beat its naive baseline, which is stated in
`reports/07_model_comparison.md` and is why the forecast layer ships as the naive method.
