# 04 — Problem candidates

**Phase:** 4 — decision point. YiYu chooses one; Phases 5–10 build only that one.
**Date:** 2026-09-16
**Evidence base:** `reports/figures/` (Phase 3) and `data/processed/` (Phase 2).
Every row count below is printed by `src/clean.py` or by a cell of `notebooks/03_eda.ipynb`.

A note on where this sits. The team already leaned towards Candidate A in the WhatsApp
discussion of 2026-09-16. This document does not rubber-stamp that: B and C are set out with
their real numbers so the choice is made against evidence, and C turns out to have more
training rows than A, which is worth seeing before deciding.

---

## Candidate A — Tourism Opportunity Gap

**Problem statement.** Malaysian domestic tourism is concentrated and has stayed that way:
the top three states held 32.7% of national visitors in 2019 and 32.8% in 2025
(`figures/03_concentration.png`). Which states attract fewer domestic visitors than their
population, economy and accommodation capacity would imply, and how large is that shortfall?

**Who would act on it.** MOTAC and the state tourism boards, when deciding where to direct
promotion budget and which states to prioritise in a national campaign. The output is a
ranked list of states with a quantified shortfall, which is the form a budget argument takes.

**EDA evidence.**
- `figures/06_loglog_structure.png` — in logs, visitors track structural size closely:
  population r = 0.907, employment 0.906, hotel rooms 0.859, GDP 0.844. This is what makes an
  "expected demand" estimate defensible rather than arbitrary.
- `figures/04_volume_vs_intensity.png` — volume and intensity are different rankings.
  W.P. Putrajaya sees 26.1 visitors per resident and Melaka 19.8, against Selangor 4.9 and
  Johor 4.3: a 6.0x spread invisible in a volume ranking.
- `figures/03_concentration.png` — the top-three share returned to almost the same level in
  2025 (32.8%) as in 2019 (32.7%), which suggests the gap is persistent rather than a
  one-year artefact. Only those two endpoints were compared.
- `figures/07_correlation_matrix.png` — the size predictors are collinear (0.541 to 0.992),
  which constrains the model family.

**ML task and target.** Two supervised regressions, deliberately separated:

| | Purpose | Target | Features | Evaluated by |
|---|---|---|---|---|
| **Model A1** Forecast | Show the model predicts | `log(visitors_000)` | lags, trend, national total, pandemic flags, state effect | time holdout, MAE / RMSE / MAPE against a naive baseline |
| **Model A2** Structural | Produce the gap | `log(visitors_000)` | **no lags**: population, GDP, services GDP, rooms, employment, participation rate, CPI accommodation and recreation | same holdout; gap = expected − actual |

Keeping lags out of A2 is the whole point. With lagged visitors in the features the residual
would be an autoregressive error term, and a high accuracy score would make the gap *less*
meaningful, not more.

**Data sufficiency.** 16 states; `state_year_panel.parquet`.
- Model A1 (forecasting sample, 2017–2025): **138 rows** — train 2017–2022 **90**, validate
  2023 **16**, holdout 2024–2025 **32**.
- Model A2 (structural sample, 2017–2019 and 2023–2025, pandemic and rebound years excluded
  per the decision of 2026-09-16): **96 state-years, of which 93 have every core predictor**.
- Target has **0% missing** across all 160 state-years and was cross-checked twice: 128
  overlapping cells across editions agree to 0.0000%, and 111 of 112 cells match a separate
  DOSM publication exactly (`reports/02_cleaning.md` §4).

**What the dashboard shows.** A Malaysia map shaded by opportunity gap; per-state drill-down
with actual against expected over time; a ranked table of states by shortfall; and a filter
for which structural factor drives each state's expectation.

**Main risk.** **The gap itself has no ground truth.** A2's prediction error can be measured;
"which state has the most untapped potential" cannot be validated against anything. The
report must say that the model identifies underperformance relative to its own expectation,
and must not claim to have identified the cause. Secondary risk: 90 training rows with
collinear predictors — a regularised linear model is likely to beat gradient boosting, and
the baseline may beat both.

---

## Candidate B — Accommodation capacity pressure

**Problem statement.** Visitor load per unit of accommodation varies by a factor of eight
across states, from 3,017 visitors per hotel room in Perlis and 2,767 in Kelantan down to 584
in Johor and 356 in W.P. Labuan (`figures/05_accommodation_pressure.png`). Which states are
carrying visitor volumes out of proportion to their accommodation stock?

**Who would act on it.** MIDA and state investment arms assessing where new accommodation
investment is warranted; state planning units managing seasonal strain.

**EDA evidence.** `figures/05_accommodation_pressure.png`;
`figures/04_volume_vs_intensity.png`.

**ML task and target.** Regression on rooms required given visitors, or classification of
states into pressure tiers.

**Data sufficiency — this is where it fails.** Hotel and room counts exist for **2022 and
2023 only** (D4 Table 14), and the 2022 Selangor workbook returns HTTP 404, so the table is
**31 state-years in total**. A target observed at two time points cannot support a time-based
split, and with 16 states a classification into tiers would have roughly five examples per
class. There is also a definitional problem: most domestic visitors are excursionists, not
overnight tourists, so visitors per room measures load against capacity, not occupancy.
DOSM publishes no occupancy-rate series in open data.

**What the dashboard shows.** Pressure map, capacity-versus-demand scatter, investment
shortlist.

**Main risk.** Fatal on data sufficiency. **Not recommended**, and it is included here so the
reason is on record rather than because it is viable.

---

## Candidate C — Inter-state flow (gravity) model

**Problem statement.** Domestic tourism is becoming less local: the share of tourists staying
within their own state fell from 36.4% in 2023 to 22.6% in 2025, and every one of the ten
largest inter-state flows originates in Selangor or W.P. Kuala Lumpur
(`figures/09_od_flows.png`). Which origin–destination pairs carry less traffic than the two
states' characteristics imply, and where is the Klang Valley market under-served?

**Who would act on it.** Transport and tourism-corridor planners; state boards targeting a
specific source market rather than the whole country.

**EDA evidence.** `figures/09_od_flows.png`; `figures/03_concentration.png`.

**ML task and target.** Regression on `log(tourists_000)` per origin–destination pair, in the
style of a gravity model: origin size, destination attractiveness, and a resistance term.

**Data sufficiency.** `od_flows.parquet` — **768 rows** (3 years × 16 origins × 16
destinations), **0 nulls**. Time split: train 2023–2024 **512 rows**, holdout 2025 **256
rows**. **This is 5.7x the training data of Candidate A**, which is the strongest argument
for it.

**What the dashboard shows.** A flow map with origin selection, a matrix of actual against
expected flows, and a ranked list of under-connected pairs.

**Main risk.** **The resistance term is missing.** A gravity model needs distance, and
neither the OpenDOSM nor the data.gov.my catalogue index lists a geojson, centroid or
boundary file — I searched both and got zero hits (`reports/02_cleaning.md` §8). Without
distance the model reduces to origin size × destination size, which is a weak specification
and easy for a judge to challenge. Adding a coordinates source needs approval and new
cleaning work. Secondary risk: only three years, so the holdout is a single year, and the
flows are not independent observations — each origin's row sums to that state's outbound
total.

---

## Recommendation: Candidate A

Scored against the preliminary rubric (`reports/00_brief.md` §5.1):

| Criterion | Weight | Why A |
|---|---:|---|
| **C2 Data Quality & Analysis** | **25%** | A joins **six** DOSM sources on `state × year` — domestic tourism, population, GDP, labour force, CPI, hotel supply — plus the OD matrix as a feature. `QLT3` rewards combining dataset types and `QLT4` rewards integration producing new insight; the gap is an insight that exists in none of the inputs alone. `QLT1`/`QLT2`: all sources official and current to 2025, with the cross-edition agreement in §4 of the cleaning report as evidence of `QLT5`. |
| **C4 Impact & Commercial Potential** | **25%** | `KOM5` asks the team to explain the implementation model. A's output is a ranked budget-allocation list for a named stakeholder, which is the most directly actionable of the three. |
| **C3 Dashboard** | **20%** | A map plus a per-state drill-down is a natural interactive dashboard, which is what `PRS1`/`PRS2` reward. |
| **C1 Methodology** | **15%** | `KDH3` asks whether the method suits the data. The A1/A2 split is defensible under questioning: one model proves predictive accuracy, the other produces the insight, and neither is asked to do both. |
| **C5 Creativity** | **15%** | `KRE2` covers innovation in applying data science. Expected-versus-actual is a recognised technique, not a novel one, so this is A's weakest criterion — C would score higher here. |

**SDG:** SDG 8 (decent work and economic growth) as primary, through inclusive regional
tourism growth; SDG 12 as secondary. Both rubrics score SDG relevance (`KDH4`, `IMP5`).

**Why not C, given it has more rows.** The missing distance variable is not a detail. Without
it the specification is origin size × destination size, which a judge can challenge in one
question, and fixing it means sourcing and cleaning geographic data with four days left
before handover. C's OD data is better used **inside** A: an inbound-flow feature summarising
how much traffic each state receives from the Klang Valley is computable today from
`od_flows.parquet` and needs no new source.

**Why not B.** 31 state-years, a target observed at two points, and no occupancy series. It
cannot be evaluated honestly.

**Honest expectation for A.** With 90 training rows and collinear predictors, a regularised
linear model may not beat a seasonal-naive baseline on the holdout. Phase 9 will report that
outcome plainly if it happens; per the acceptance criteria, a model that does not beat its
baseline is an acceptable result provided it is stated, not hidden.

---

## Decision needed

1. **Confirm Candidate A**, or pick B or C.
2. **Should the OD inbound-flow feature go into Model A2?** It is free to compute and
   strengthens `QLT3`, but it is derived from the target's own publication, so it needs a
   sentence in the methodology explaining that it is a separate table (tourists by
   origin–destination) and not a transform of the target.
3. **Primary dimension**: I suggest **Technology & Governance** as primary with **Social**
   secondary, matching the captain's reasoning — a decision-support tool for smarter tourism
   management. Confirm so Phase 10's `FINDINGS.md` frames it that way for YiHui.
