# API contract — Tourism Opportunity Gap model

**For:** HongYik (Backend & Dashboard)
**From:** YiYu (Data & AI)
**Date:** 2026-09-16
**Model:** `ml/models/a2_gap_model.joblib` — gradient boosting, trained on 58 DOSM state-year
rows. Holdout MAE_log 0.2648 against a baseline of 0.4467, a 40.7% reduction
(`ml/reports/09_evaluation.md`).

> ### ⚠️ Changed on 2026-09-18 — re-pull before you build
> `expected_visitors_000` **now means something different**, and two fields were added.
>
> Before, it was the model's raw output, which is anchored on the model's training years
> and runs systematically low for later ones. Put beside an actual it produced a visible
> contradiction: Johor 2025 showed expected 17.7m against actual 18.2m while the gap said
> +27% below expectation. **In 2025 that happened for 8 of the 16 states.**
>
> `expected_visitors_000` is now the expected **share** applied to that year's national
> total, so it sits on the same scale as the actual. Across all 90 rows the level and the
> gap now agree in direction, with **zero** contradictions. The raw output is still
> available as `model_raw_expected_000`, for diagnostics only.
>
> Nothing about the model or its accuracy changed. No number in the evaluation moved.

---

## 1. You may not need the API at all

`sample_predictions.csv` in this folder already contains **every prediction the model can
make** — 90 rows, all 16 states, 2017–2019 and 2023–2025. If the dashboard only shows stored
results, load that CSV and you are done. No Python, no service, nothing for the judges to
install.

That matters for scoring: the booklet requires a dashboard that works "without external
dependencies that cannot be accessed by the judges" (`ml/reports/00_brief.md` §3.1). **A live
API that only runs on your laptop is a risk; the CSV is not.** Use `predict()` only if you
want interactive scenarios ("what if Kedah adds 5,000 hotel rooms").

## 2. Importing

```python
import sys
sys.path.insert(0, "ml")            # or wherever ml/ sits relative to your app
from src.predict import predict, available, PredictionError
```

Importing loads nothing and **trains nothing**. The model file opens lazily on the first call
and is cached. All paths resolve relative to `ml/`, so the working directory does not matter
and there are no Windows-specific paths.

Requires `pandas`, `numpy`, `scikit-learn` and `joblib` — all pinned in
`ml/requirements.txt`.

## 3. `predict(payload: dict) -> dict`

### Input

| Field | Type | Required | Units / values |
|---|---|---|---|
| `state` | string | **yes** | one of the 16 DOSM labels, exactly: `Johor`, `Kedah`, `Kelantan`, `Melaka`, `Negeri Sembilan`, `Pahang`, `Pulau Pinang`, `Perak`, `Perlis`, `Selangor`, `Terengganu`, `Sabah`, `Sarawak`, `W.P. Kuala Lumpur`, `W.P. Labuan`, `W.P. Putrajaya` |
| `year` | int | **yes** | one of `2017, 2018, 2019, 2023, 2024, 2025` |
| `features` | object | no | `{feature_name: float}` overrides for scenario analysis |

**2020, 2021 and 2022 are deliberately unavailable.** Movement controls broke the
relationship the model is built on, so it was never trained to explain those years and
raises `PredictionError` for them rather than returning a misleading number.

Call `available()` for the live lists:

```python
available()
# {"states": ["Johor", "Kedah", ...], "years": [2017, 2018, 2019, 2023, 2024, 2025]}
```

### Example request

```python
predict({"state": "Johor", "year": 2025})
```

### Example response

```json
{
  "state": "Johor",
  "year": 2025,
  "expected_visitors_000": 23118.9,
  "actual_visitors_000": 18197.0,
  "gap_visitors_000": 4921.9,
  "model_raw_expected_000": 17712.1,
  "expected_share_pct": 7.9702,
  "actual_share_pct": 6.2734,
  "opportunity_gap_pct": 27.0,
  "opportunity_gap_pp": 1.6968,
  "interpretation": "receives a smaller share of national visitors than its population, economy and accommodation capacity imply",
  "basis": "share of the national total for the same year",
  "model": {
    "family": "GradientBoosting",
    "trained_on_years": [2017, 2018, 2019, 2023],
    "holdout_MAE_log": 0.2648,
    "baseline_MAE_log": 0.4467
  },
  "warnings": []
}
```

### Response fields

| Field | Type | Units | Meaning |
|---|---|---|---|
| `state`, `year` | string, int | — | echoed back |
| `expected_visitors_000` | float \| null | **thousands of visitors** | **the one to display.** The expected share applied to that year's national total, so it is directly comparable with `actual_visitors_000` |
| `actual_visitors_000` | float \| null | thousands | what DOSM published |
| **`gap_visitors_000`** | float \| null | thousands | `expected_visitors_000 − actual_visitors_000`. Positive = a shortfall. Johor 2025 is **+4,922**, i.e. 4.9m visitors below its benchmark |
| `model_raw_expected_000` | float | thousands | **diagnostic only, never display beside an actual.** The unscaled model output, anchored on the training years |
| `expected_share_pct` | float | **percent** | expected share of that year's national total |
| `actual_share_pct` | float \| null | percent | actual share |
| **`opportunity_gap_pct`** | float \| null | **percent** | **the headline number.** `expected_share / actual_share − 1`. Positive = the state receives a *smaller* share than its fundamentals imply |
| `opportunity_gap_pp` | float \| null | percentage points | `expected_share − actual_share`, for stacked or map shading |
| `interpretation` | string | — | a plain-English sentence, safe to show a user. The wording switches at **±5%**: above +5% "receives a smaller share…", below −5% "receives a larger share…", and in between "receives about the share…". Treat anything inside ±5% as no finding |
| `basis` | string | — | always "share of the national total for the same year" |
| `model` | object | — | provenance to display in an "about" panel |
| `warnings` | array of strings | — | **show these.** See below |

### Why there are two expected columns

The model has no time term: it estimates the level implied by a state's fundamentals.
National visitors grew from 213.7m in 2023 to 290.1m in 2025 while population and hotel
stock barely moved, so the **raw** model output runs low for every state in recent years —
91% of holdout rows. Two consequences:

1. A gap in raw visitors would measure **national growth**, not state performance. It would
   have marked 15 of 16 states as "opportunities", which is meaningless.
2. Showing the raw level beside an actual reads as a contradiction. Johor 2025: raw expected
   17.7m, actual 18.2m, yet the gap says the state is 27% below expectation. In 2025 that
   affected 8 of 16 states.

The fix is to rescale: `expected_visitors_000 = expected_share × the year's national total`.
Both sides then carry the same national total, so

    expected_visitors_000 / actual_visitors_000 − 1  ==  opportunity_gap_pct

holds exactly, and `gap_visitors_000` always has the same sign as `opportunity_gap_pct`.
Verified across all 90 rows.

**`expected_visitors_000` is a benchmark, not a forecast.** It uses the national total of a
year that has already been published, so it answers "given what the country did that year,
what share should this state have taken", never "what will happen next year".

**Do not display `model_raw_expected_000` next to an actual**, and do not build your own gap
from it.

### Warnings you should surface

Two kinds appear, and both belong on screen:

- `"Perlis had a holdout error of 0.708 MAE_log, well above the median state; treat this gap
  as indicative only"` — also fires for W.P. Putrajaya. Small states are volatile and the
  model is much less reliable for them.
- `"2023 is one of the model's training years, so this is an in-sample figure, not a test of
  the model"` — fires for 2017, 2018, 2019 and 2023.

Years **2024 and 2025 carry no warning**: they are the untouched holdout, and they are the
figures to lead with.

### Scenario analysis (optional)

```python
predict({"state": "Kedah", "year": 2025, "features": {"log_rooms": 9.8}})
```

Feature values are on the model's own scale, which is mostly **natural logs**. To set hotel
rooms to 18,000: `math.log(18000)`. Valid names are in `models/a2_gap_model_metadata.json`
under `features`; an unknown name raises `PredictionError`. The response adds a warning
naming the overridden features.

### Errors

Everything raises `PredictionError` (a subclass of `ValueError`) with a message that is safe
to show a user:

| Cause | Message |
|---|---|
| unknown state | `state 'Atlantis' is not available for 2025; valid states are [...]` |
| unavailable year | `year 2021 is not available; available years are [2017, 2018, 2019, 2023, 2024, 2025]` |
| missing field | `payload must contain 'state' and 'year'` |
| unknown override | `unknown feature(s) ['foo']; valid features are [...]` |
| model file absent | `model file not found at models/a2_gap_model.joblib; run python src/tune.py from the ml/ folder` |

```python
try:
    result = predict(payload)
except PredictionError as exc:
    return {"error": str(exc)}, 400
```

## 4. `sample_predictions.csv`

90 rows, one per state-year.

| Column | Units | Notes |
|---|---|---|
| `state`, `year` | — | key |
| `visitors_000` | thousands | actual, from DOSM |
| `expected_visitors_000` | thousands | benchmarked expectation, comparable with the actual |
| **`gap_visitors_000`** | thousands | shortfall in visitors; positive = below benchmark |
| `actual_share_pct`, `expected_share_pct` | percent | within that year |
| `opportunity_gap_pp` | percentage points | expected share − actual share |
| **`opportunity_gap_pct`** | percent | the headline number |
| `model_raw_expected_000` | thousands | diagnostic only; do not display beside an actual |
| `is_holdout_year` | bool | `true` for 2024 and 2025 — **lead with these** |
| `naive_forecast_next_year_000` | thousands | only on 2025 rows; see §5 |

Sorted by year then gap descending, so the first rows of each year are the biggest
opportunities.

## 5. The forecast layer is deliberately naive

Four models were tested for year-ahead forecasting against a naive "last value" baseline.
**None beat it** across rolling-origin folds — baseline 0.6835 MAE_log against Ridge at
0.7981 (`ml/reports/07_model_comparison.md` §1). So the forecast shipped is the naive method:

**forecast for next year = this year's actual.**

That is what `naive_forecast_next_year_000` holds. If the dashboard shows a forecast, label it
"naive baseline" and say the ML model is the *expected-demand* model, not the forecaster. This
is an honest negative result and it is defensible under questioning; claiming an ML forecast
that does not beat naive is not.

## 6. `state_features.csv`

The 12 model inputs per state-year, 90 rows. `predict()` falls back to this file when
`data/processed/features.parquet` is absent, so **a fresh clone can call `predict()` without
running the pipeline**. Both sources give identical answers; that is asserted in testing.

## 7. Suggested dashboard fields

| Panel | Field |
|---|---|
| Map shading | `opportunity_gap_pct` for the selected year, diverging scale centred on 0 |
| State drill-down | `actual_visitors_000` against `expected_visitors_000` (both on the same scale), the shortfall `gap_visitors_000`, plus `interpretation` |
| Ranked table | states sorted by `opportunity_gap_pct`, 2025 |
| Reliability | show `warnings`; grey out or footnote Perlis and W.P. Putrajaya |
| About | `model.family`, `trained_on_years`, `holdout_MAE_log` against `baseline_MAE_log` |

**One thing to avoid.** The gap says a state receives less than its fundamentals imply. It
does **not** say why, and nothing in this analysis identifies a cause. Label it
"Opportunity Gap", never "underserved" or "lacks promotion".

## 8. Questions

Ask me before 20 September. I am unavailable 21–25 September, so anything after 20 September
has to be answered from these files.
