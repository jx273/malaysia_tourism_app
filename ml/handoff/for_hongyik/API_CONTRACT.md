# API contract — Tourism Opportunity Gap model

**For:** HongYik (Backend & Dashboard)
**From:** YiYu (Data & AI)
**Date:** 2026-09-16
**Model:** `ml/models/a2_gap_model.joblib` — gradient boosting, trained on 58 DOSM state-year
rows. Holdout MAE_log 0.2648 against a baseline of 0.4467, a 40.7% reduction
(`ml/reports/09_evaluation.md`).

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

Requires `pandas`, `numpy`, `scikit-learn` and `joblib` — see `ml/requirements.txt`.

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
  "expected_visitors_000": 17712.1,
  "actual_visitors_000": 18197.0,
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
| `expected_visitors_000` | float | **thousands of visitors** | what the model expects from this state's population, economy and capacity |
| `actual_visitors_000` | float \| null | thousands | what DOSM published |
| `expected_share_pct` | float | **percent** | expected share of that year's national total |
| `actual_share_pct` | float \| null | percent | actual share |
| **`opportunity_gap_pct`** | float \| null | **percent** | **the headline number.** `expected_share / actual_share − 1`. Positive = the state receives a *smaller* share than its fundamentals imply |
| `opportunity_gap_pp` | float \| null | percentage points | `expected_share − actual_share`, for stacked or map shading |
| `interpretation` | string | — | a plain-English sentence, safe to show a user |
| `basis` | string | — | always "share of the national total for the same year" |
| `model` | object | — | provenance to display in an "about" panel |
| `warnings` | array of strings | — | **show these.** See below |

### Why the gap is a share, not a difference in visitors

The model has no time term: it estimates the level implied by a state's fundamentals. National
visitors grew from 213.7m in 2023 to 290.1m in 2025 while population and hotel stock barely
moved, so the model under-predicts every state in recent years — 91% of holdout rows. A gap
in raw visitors would therefore measure **national growth**, not state performance, and would
have shown 15 of 16 states as "opportunities". Normalising to shares removes that entirely.

**Do not compute your own gap as `expected_visitors_000 − actual_visitors_000`.** It will be
negative almost everywhere and it will not mean what it looks like.

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
| `expected_visitors_000` | thousands | model output |
| `actual_share_pct`, `expected_share_pct` | percent | within that year |
| `opportunity_gap_pp` | percentage points | expected share − actual share |
| **`opportunity_gap_pct`** | percent | the headline number |
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
| State drill-down | `actual_visitors_000` and `expected_visitors_000`, plus `interpretation` |
| Ranked table | states sorted by `opportunity_gap_pct`, 2025 |
| Reliability | show `warnings`; grey out or footnote Perlis and W.P. Putrajaya |
| About | `model.family`, `trained_on_years`, `holdout_MAE_log` against `baseline_MAE_log` |

**One thing to avoid.** The gap says a state receives less than its fundamentals imply. It
does **not** say why, and nothing in this analysis identifies a cause. Label it
"Opportunity Gap", never "underserved" or "lacks promotion".

## 8. Questions

Ask me before 20 September. I am unavailable 21–25 September, so anything after 20 September
has to be answered from these files.
