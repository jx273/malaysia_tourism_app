# 05 — Feature engineering

**Phase:** 5
**Script:** `ml/src/features.py` → `data/processed/features.parquet` (160 rows × 49 columns)
**Run:** 2026-09-16, from `ml/`: `python src/features.py`
**Problem:** Candidate A, Tourism Opportunity Gap (`reports/04_problem_candidates.md`).
**Dimension:** Technology & Governance primary, Social secondary (team decision, 2026-09-16).

**Target:** `log_visitors = log(visitors_000)` — domestic visitors by state visited,
thousands. Logged because Phase 3 showed the structural relationships are near-linear in
logs (`figures/06_loglog_structure.png`: population r = 0.907, employment 0.906, rooms 0.859,
GDP 0.844) and because state sizes span two orders of magnitude, from W.P. Labuan at 604k to
Selangor at 36,376k in 2025.

---

## Two feature sets, on purpose

| | Model A1 — Forecast | Model A2 — Structural |
|---|---|---|
| Question | what will this state receive next year? | how many visitors *should* this state receive, given what it is? |
| Lag of target | **yes, that is the point** | **never** |
| Purpose | prove predictive accuracy against a baseline | produce the opportunity gap |
| Sample | 2018–2025, **118 rows** | 2017–2019 and 2023–2025, **90 rows** |

If a lagged target entered A2, the gap would collapse into an autoregressive residual: it
would measure "more or less than last year's trend", not "more or less than this state's
potential", and a *better* accuracy score would make the gap *less* meaningful.

---

## A2 — structural features (12)

All contemporaneous with the target. That is the design: A2 asks what a state's size,
capacity and price level imply for its visitor volume in the same year.

| Feature | Definition | Source column | Rationale |
|---|---|---|---|
| `log_population` | log of resident population ('000) | `population_000` (D6) | Strongest single correlate in logs (r = 0.907). Domestic tourism is largely intra-national travel, so resident base scales both origin and destination potential. |
| `log_gdp_total` | log of real GDP, RM million, constant 2015 prices | `gdp_total_rm_mn` (D7) | Economic size; r = 0.844 in logs. |
| `log_gdp_services` | log of services-sector real GDP | `gdp_services_rm_mn` (D7) | Tourism sits inside services; a state with a large services base has the businesses visitors spend at. |
| `services_share` | `gdp_services_rm_mn / gdp_total_rm_mn` | D7 | Distinguishes a services economy from a resource or manufacturing one at the same GDP. |
| `log_gdp_per_capita` | log of GDP per resident (RM) | D7 ÷ D6 | Separates *rich* from *big*; without it GDP and population carry the same information. |
| `log_rooms` | log of hotel rooms | `rooms` (D4 Table 14) | The only accommodation-supply measure in open DOSM data; r = 0.859 in logs. Capacity is a precondition for overnight visitors. |
| `rooms_per_1k_residents` | `rooms / population_000` | D4 ÷ D6 | Tourism capacity relative to local size — high in Melaka and Pahang, low in Selangor and Johor. |
| `log_lf_employed` | log of employed persons ('000), annual mean of quarters | `lf_employed_000` (D8) | Labour available to tourism-facing businesses; r = 0.906 in logs. |
| `u_rate` | unemployment rate, annual mean of quarters | `u_rate` (D8) | Local economic slack. Weak on its own (r = −0.121) but cheap to carry. |
| `p_rate` | labour-force participation rate | `p_rate` (D8) | Same. |
| `cpi_accom_food_rel` | state CPI division 11 ÷ the mean of all states that year | `cpi_accom_food` (D5) | **Relative, not absolute.** Every state's index is base 2010 = 100, so the level mostly encodes national inflation; the ratio is what says whether a state is expensive *for its year*. Price is the affordability channel for a domestic visitor. |
| `cpi_recreation_rel` | state CPI division 09 ÷ the same-year mean | `cpi_recreation` (D5) | Cost of things visitors actually do — recreation, sport and culture. |

**Collinearity is expected and handled downstream.** Phase 3 measured pairwise correlations
of 0.541 to 0.992 among the size variables (`figures/07_correlation_matrix.png`), so Phase 7
compares regularised and tree-based models rather than plain OLS, and no coefficient will be
read as an independent effect.

---

## A1 — forecasting features (14)

Everything here is knowable before year *t* begins.

| Feature | Definition | Source | Rationale |
|---|---|---|---|
| `log_visitors_lag1` | log visitors in *t−1* | target, shifted | Tourism volumes are highly persistent; this is the main signal. |
| `log_visitors_lag2` | log visitors in *t−2* | target, shifted | Lets the model see direction, not just level. |
| `visitors_growth_lag1` | `visitors(t−1) / visitors(t−2) − 1` | target, shifted | Momentum, which matters across the recovery. |
| `log_visitors_ma2_lag1` | log of the mean of *t−1* and *t−2* | target, shifted | A smoother level than a single year; small states are volatile (Perlis σ = 28.0). |
| `log_national_visitors_lag1` | log of the national total in *t−1* | target, summed then shifted | National conditions a state moves with. **Lagged**, because the year-*t* national total would require every other state's year-*t* value. |
| `state_share_lag1` | state's share of the national total in *t−1* | target, shifted | Position in the national market. Same leakage reasoning. |
| `log_population`, `log_rooms`, `log_gdp_total` | as above | D6, D4, D7 | Size anchors, carried over from A2. |
| `u_rate_lag1` | unemployment rate in *t−1* | D8, shifted | Lagged: the year-*t* labour survey is not published when year *t* is forecast. |
| `cpi_accom_food_rel_lag1` | relative accommodation CPI in *t−1* | D5, shifted | Same reasoning. |
| `years_since_2016` | `year − 2016` | calendar | Linear trend term. |
| `is_pandemic_year` | 2020 or 2021 | calendar | A calendar fact, known in advance, not leakage. Keeps the movement-control years usable instead of discarded. |
| `is_recovery_year` | 2022 | calendar | 2022's median state growth was +213.8%; without a flag it would distort every coefficient. |

---

## OD features (3) — built, but they cost half the sample

The team asked on 2026-09-16 for the origin-destination matrix to feed Model A2. The
features were built and the cost was measured rather than assumed.

| Feature | Definition | Rationale |
|---|---|---|
| `log_od_inbound_external` | log of tourists arriving from *other* states | Market access: how much of the country actually travels to this state. |
| `od_klang_share` | tourists from Selangor + W.P. Kuala Lumpur ÷ all external inbound | Phase 3 found all ten largest inter-state flows start in the Klang Valley (`figures/09_od_flows.png`); this measures dependence on that one source market. |
| `od_self_share` | own-state tourists ÷ all inbound | How much of a state's tourism is its own residents. |

**Measured cost.** `od_flows.parquet` covers 2023–2025 only, so:

| Sample | Rows | Train | Holdout |
|---|---:|---:|---:|
| A2 without OD | **90** | 58 (2017–2019, 2023) | 32 (2024–2025) |
| A2 with OD | **48** | **16** (2023 only) | 32 (2024–2025) |

Adding the OD features **removes 42 rows, 47% of the structural sample**, and leaves 16
training rows. A time-based split on 16 rows is not a model, it is a coincidence.

**Decision:** the OD columns stay in `features.parquet` and Phase 7 reports an A2+OD variant
as a **cross-sectional comparison on 2023–2025 only**, alongside the main A2. The headline
gap comes from the 90-row model. If the OD variant turns out to agree with it, that is worth
a sentence in the report; it cannot carry the result on its own.

---

## Leakage checks that ran

`features.py` asserts both of these and exits non-zero if either fails:

1. **`visitors_lag1` never equals the same year's value** — 0 rows.
2. **Every `visitors_lag1` equals the previous year's actual value**, recomputed independently
   — 0 mismatches.

Two further guarantees by construction:

- All lags use `groupby("state").shift(k)`. The panel is complete for all 16 states from 2016
  to 2025, so shifting one row is exactly shifting one year — there are no gaps that would
  silently turn a lag into a two-year lag.
- **Nothing is scaled or encoded here.** Scalers are fitted inside a scikit-learn pipeline on
  the training split only, in Phases 6–7, so no test-set statistic reaches a fitted transform.

## Rows lost, and why

| Sample | Rows | Lost against the panel | Reason |
|---|---:|---:|---|
| Full panel | 160 | — | 16 states × 2016–2025 |
| A1 forecasting | **118** | 42 | 32 rows have no two-year history (2016, 2017); the rest lack a lagged predictor |
| A2 structural | **90** | 70 | 2020–2022 excluded by the team decision (48 rows); 2016 has no labour-force data (16); W.P. Putrajaya has no GDP before 2023 (3 remaining rows); Selangor has no 2022-edition hotel file, the HTTP 404 (3 rows) |
| A2 + OD | **48** | 112 | OD matrix starts in 2023 |
