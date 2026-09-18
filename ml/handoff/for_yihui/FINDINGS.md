# Findings — Tourism Opportunity Gap

**For:** YiHui (Product / Report / Pitch)
**From:** YiYu (Data & AI)
**Date:** 2026-09-16
**Figures:** `figures/` in this folder, all high-resolution PNG.

Plain English throughout. Every number here was produced by code that ran, and the file that
produced it is named so you can cite it. Nothing is rounded up for effect.

---

## 1. The problem, in one paragraph

Malaysian domestic tourism is concentrated in a few states and has stayed that way through a
pandemic. We built a model that estimates how many visitors each state *should* receive given
its population, economy and hotel capacity, then compared that with what it actually
receives.

**That comparison is made in shares of the national total, not in raw visitor numbers.** The
model deliberately has no time element, and national visitors grew by roughly a third between
2023 and 2025, so an absolute difference would measure national growth rather than each
state's own performance. The result is a **relative, share-based Tourism Opportunity Gap**:
it points to states whose *share* of national visitors sits below what their own structural
conditions imply. Keep the word "relative" or "share-based" attached to it wherever it is
defined — see the wording table in §8.

**Dimension:** Technology & Governance (primary), Social (secondary).
**SDG:** SDG 8, decent work and economic growth, through inclusive regional tourism growth.

## 2. The data

Everything is official Malaysian statistics. **Nine OpenDOSM datasets** feed the model, and
all ten datasets we downloaded (62 files) are listed with their catalogue links in
`ml/data/raw/SOURCES.md` — that file is your References section. The tenth, monthly foreign
arrivals, comes from data.gov.my rather than OpenDOSM; we profiled it and left it out, for
the reasons in §6.

| What | Source | Coverage |
|---|---|---|
| Domestic visitors by state | DOSM Domestic Tourism Survey | 16 states, 2016–2025 |
| State tourism receipts and trips | DOSM Domestic Tourism by State | 2017–2023 |
| Hotels and rooms by star rating | DOSM Domestic Tourism by State | 2022, 2023 |
| Origin → destination tourist flows | DOSM Domestic Tourism Survey | 2023–2025 |
| Population, GDP, labour force, CPI | OpenDOSM data catalogue | to 2025/2026 |

One thing worth putting in the report: **the tourism data is not in the OpenDOSM data
catalogue.** We searched all 183 catalogue datasets and found no tourism series; it lives in
OpenDOSM *Publications* as Excel reports. Finding it was real work and it shows we went
past the obvious.

**Data quality, verified three ways** (`ml/reports/02_cleaning.md` §4):
- 128 state-year figures published in more than one edition agree to **0.0000%**.
- Checked against a second DOSM publication: **111 of 112 figures match exactly**; the one
  difference is rounding (W.P. Labuan 2020, 107.0 against 107.53).
- Quarterly figures sum to the annual totals printed in the same table, **5 of 5 years**.

## 3. The method, in words

Two models, kept deliberately separate:

**Model A1 — forecasting.** Can we predict next year's visitors? We tested four models
against a naive "same as last year" baseline. **None beat it.** So the forecast layer ships
as the naive method, and we say so.

**Model A2 — expected demand.** Given a state's population, economy, employment and hotel
capacity — *and no history of its own visitor numbers* — how many visitors should it receive?
This is the model that produces the gap. Leaving visitor history out is the whole point: if
the model knew last year's figure, the gap would just say "more or less than last year",
not "more or less than this state's potential".

**How we tested it honestly.** Training used 2017–2019 and 2023. **2024 and 2025 were locked
away and opened once, at the end.** Splits are by time, never random, so the model is always
predicting a later year from earlier ones.

## 4. The results

**The model works.** On the two years it had never seen:

| | Error (MAE_log) | Average error | MAPE |
|---|---|---|---|
| Simple baseline (visitors in proportion to population) | 0.4467 | 7.07m visitors | 41.4% |
| **Our model** | **0.2648** | **3.77m visitors** | **22.5%** |

**A 40.7% reduction in error, and MAPE almost halved.** `figures/11_holdout_actual_vs_expected.png`

Source: `ml/reports/09_evaluation.md` §1.

## 5. Five key insights

### Insight 1 — Tourism concentration returned to almost the same level in 2025 as in 2019
`figures/03_concentration.png`

The top three states held **32.7%** of national domestic visitors in 2019 and **32.8%** in
2025. Between those two points total visitors collapsed from 239.1m to 66.0m and recovered to
290.1m, so the national level moved enormously while the top-three share came back to where
it started.

**Careful with the claim.** We compared two endpoints. This says 2025 resembles 2019; it does
not say the share was unchanged in every year in between.

### Insight 2 — Visitor volume and tourism intensity reveal very different state profiles
`figures/04_volume_vs_intensity.png`

W.P. Putrajaya records **26.1 visitors per resident** and Melaka **19.8**, while Selangor and
Johor — first and fourth by raw volume — sit last at **4.9 and 4.3**, a **6.0x spread** that a
visitor-count ranking hides completely. This is the argument for looking at tourism relative
to a state's own size, which is what our model does.

**Read W.P. Putrajaya with care.** It is a small administrative territory: the denominator is
only **120.7 thousand residents**, and much of its footfall is administrative and commuter
movement rather than leisure tourism. A high visitors-per-resident figure is not the same
thing as the strongest tourism performance, and should not be presented as a ranking win.

### Insight 3 — Kedah, Johor and Terengganu recorded the largest positive Tourism Opportunity Gaps in 2025
`figures/12_opportunity_gap_2025.png`

For 2025, the states furthest below their model-expected share:

| State | Actual | Benchmark | Shortfall | Gap |
|---|---:|---:|---:|---:|
| **Kedah** | 15.6m | 22.3m | **6.7m** | **+42.6%** |
| **Johor** | 18.2m | 23.1m | **4.9m** | **+27.0%** |
| Terengganu | 15.5m | 18.0m | 2.5m | +16.3% |
| W.P. Labuan | 0.6m | 0.7m | 0.06m | +10.3% |
| Pulau Pinang | 17.7m | 19.4m | 1.7m | +9.6% |

And furthest above: Perlis −31.6%, W.P. Putrajaya −21.7%, W.P. Kuala Lumpur −17.6%.

**"Benchmark" is the state's expected share applied to that year's national total**, which
is what makes it comparable with the actual. The shortfall column is the difference. Both
say the same thing as the percentage — they are the same number on three scales, so quote
whichever suits the sentence. "Kedah received 6.7 million fewer domestic visitors in 2025
than its population, economy and accommodation capacity imply" is the plainest form.

**These gaps indicate lower-than-expected visitor shares given the modelled structural
conditions. They do not identify the cause.** That sentence should follow the finding every
time it is used, in the report and in the pitch.

**The ranking is stable**: across both holdout years **81% of states keep the same sign** and
the rank correlation is **0.732**. Do not quote the states near zero (Sarawak +0.4%,
Kelantan +2.4%) as findings — they are inside the noise.

### Insight 4 — Domestic travel became more interstate-oriented between 2023 and 2025
`figures/09_od_flows.png`

The share of tourists holidaying inside their own state fell from **36.4% in 2023 to 22.6% in
2025**. Malaysians are travelling further from home.

**Selangor and W.P. Kuala Lumpur dominate the largest interstate origin flows**: all ten of
the largest inter-state flows in 2025 start in one of the two. Other states clearly generate
outbound travel as well — they simply do not appear in the top ten, which is all our data
shows. Do not write that the Klang Valley is the country's only source market.

### Insight 5 — Structural scale indicators contributed more predictive information than the two CPI-based price indicators
`figures/13_feature_importance.png`

**Within our model and this feature set**, population contributed the most predictive
information (permutation importance 0.175), followed by GDP (0.083), employment (0.071) and
hotel rooms (0.061). The two CPI-based indicators contributed close to zero: **0.0000** for
recreation, sport and culture and **−0.0010** for restaurants and accommodation, both inside
their own error bars.

**This is a statement about our model, not about price.** CPI divisions 09 and 11 are
*resident* consumer price indices for each state. They are not a measure of tourism prices,
and nothing here shows that price is irrelevant to an individual traveller's decision. Write
"contributed less predictive information", never "price does not matter".

## 6. Limitations — please include these

The judges will ask. Having them written down is worth more than hiding them.

1. **The gap identifies underperformance, not its cause.** The model says a state receives
   less than its fundamentals imply. It does **not** say why — not discoverability, not
   marketing, not access. Our platform addresses one plausible cause; the data does not prove
   that cause.
2. **58 training rows.** DOSM publishes this at state-year resolution, so the whole country
   for a decade is a small table. Everything rests on that.
3. **The gap is relative, not absolute.** It compares each state's share of national visitors
   with its expected share. A gap in raw visitor numbers would have measured national growth
   instead — see §7.
4. **Small states are unreliable.** Perlis has four times the median error. Treat Perlis and
   W.P. Putrajaya as indicative only.
5. **Hotel capacity is only published for 2022 and 2023**, so earlier years reuse the 2022
   figure and capacity is assumed roughly constant.
6. **Annual and state-level.** No seasons, no districts, no visitor segments.
7. **Most domestic visitors are day-trippers**, not overnight tourists, so a state weak in
   overnight tourism can still look strong on this measure.
8. **Domestic only.** Foreign arrivals are excluded: the one open dataset records where
   visitors *entered* the country, not where they went, and it stopped updating in 2024.

## 7. One methodological point worth a paragraph in the report

Our first version measured the gap in visitor numbers, and **15 of 16 states came out as
"opportunities"** — obviously wrong. The cause: the model deliberately has no time element,
so as national visitors grew from 213.7m to 290.1m it under-predicted everyone. We switched
the gap to **shares of the national total**, which removes the national level entirely.

This is a good paragraph for Methodology. It shows we checked our own output instead of
shipping the first plausible-looking number, which is exactly what the "critical thinking"
criterion is looking for.

## 8. Wording to avoid

| Do not write | Write instead |
|---|---|
| "ML proves poor discoverability causes low tourism" | "the state's visitor share is below what its fundamentals imply; discoverability is one possible explanation we propose to address" |
| "underserved states" | "states with a tourism opportunity gap" |
| "the model predicts 2026 visitors" | "the expected-demand model estimates the share implied by fundamentals; the forecast layer is a naive baseline" |
| "our AI is 40% accurate" | "our model reduces error by 40.7% against the baseline, from 41.4% to 22.5% MAPE" |
| "size determines where Malaysians go, price does not matter" | "within our model, structural scale variables such as population and GDP contributed more predictive information than the two CPI-based price indicators" |
| "the Klang Valley is the country's only source market" | "Selangor and Kuala Lumpur dominate the largest interstate origin flows" |
| "six years and a pandemic did not change tourism concentration" | "tourism concentration among the top three states returned to almost the same level in 2025 as in 2019" |
| "the Opportunity Gap" (unqualified) | "the relative, share-based Tourism Opportunity Gap" — and define it as a share the first time it appears |
| "Putrajaya has the strongest tourism performance" | "Putrajaya records the highest visitors per resident, on a very small resident base that also carries administrative and commuter movement" |

## 9. Where each number lives

| Section of your report | File |
|---|---|
| Background, problem statement | `ml/reports/04_problem_candidates.md` |
| Data sources, References | `ml/data/raw/SOURCES.md` |
| Methodology — cleaning | `ml/reports/02_cleaning.md` |
| Methodology — features | `ml/reports/05_features.md` |
| Methodology — model choice | `ml/reports/06_baseline.md`, `ml/reports/07_model_comparison.md` |
| Findings, limitations | `ml/reports/09_evaluation.md` |
| Output / dashboard | `ml/handoff/for_hongyik/API_CONTRACT.md` |

## 10. Timing

I am unavailable **21–25 September**, and the submission deadline is **22 September, 5:00 pm**.
Ask me anything before **20 September**. After that, these files are the answer.
