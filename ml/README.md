# `ml/` — Data & AI track, DOSM Datathon 2026

Python workspace for the Data & AI workstream. **Everything in this track lives under
`ml/`** so that it never collides with the Flutter project in the repository root.

**What it does.** Turns nine OpenDOSM datasets into a model that estimates how many
domestic visitors each Malaysian state *should* receive given its population, economy and
hotel capacity, and reports the difference from what it actually receives — measured in
**shares of the national total**, which is what makes it comparable between states. That is
the **relative Tourism Opportunity Gap**.

**Headline result.** On two years the model had never seen, it reduces error by **40.7%**
against a sensible baseline: MAE_log 0.2648 against 0.4467, MAPE 22.5% against 41.4%. Details
in [`reports/09_evaluation.md`](reports/09_evaluation.md).

---

## Setup

Requires **Python 3.13** (built and tested on 3.13.14, Windows 11).

```bash
cd ml
python -m venv .venv
```

Activate it — Windows:

```bash
.venv/Scripts/activate
```

macOS or Linux:

```bash
source .venv/bin/activate
```

Then install the dependencies:

```bash
pip install -r requirements.txt
```

The file includes the ML packages (pandas, numpy, pyarrow, matplotlib,
scikit-learn, jupyter and joblib) and the dashboard and optional AI dependencies.
The Excel reader for DOSM's formatted reports uses the standard library.
To launch the dashboard from the repository root, follow the root README and
install the same file with `pip install -r ml/requirements.txt`.

## Reproducing everything from scratch

Run these in order from the `ml/` folder. The whole chain takes a few minutes, most of it the
download.

```bash
python src/download.py
```

Fetches 62 files (~36 MB) into `data/raw/`. **Write-once**: a file that already exists is
never re-fetched or overwritten, so re-running is safe. Prints a SHA-256 per file; if one
differs from [`data/raw/SOURCES.md`](data/raw/SOURCES.md), DOSM has revised that file.

```bash
python src/clean.py
```

Parses the DOSM Excel reports and CSVs into four tidy Parquet tables in `data/processed/`.
Logs every rule and every join with row counts, and runs three data-quality checks.

```bash
python src/features.py
```

Builds `data/processed/features.parquet`. Asserts two leakage checks and exits non-zero if
either fails.

```bash
python src/train.py
```

Phases 6–7: baselines and four models on identical splits, single-year and rolling-origin.
Prints the tables behind `reports/06_baseline.md` and `reports/07_model_comparison.md`.
**Does not touch the 2024–2025 holdout.**

```bash
python src/tune.py
```

Tunes the structural model and writes `models/a2_gap_model.joblib` and its metadata.
`random_state=42`, so this is deterministic: the same command reproduces the same model file.

```bash
python src/evaluate.py
```

Scores the tuned model on the 2024–2025 holdout, writes three figures and
`data/processed/opportunity_gap.parquet`. This is the only script that reads the holdout.

```bash
python src/handoff.py
```

Writes the files in `handoff/` for HongYik and YiHui.

Optionally, the exploratory notebook, which regenerates the ten Phase-3 figures:

```bash
python -m jupyter nbconvert --to notebook --execute --inplace notebooks/03_eda.ipynb
```

## Using the model

```python
import sys
sys.path.insert(0, "ml")
from src.predict import predict

predict({"state": "Johor", "year": 2025})
# {"state": "Johor", "year": 2025, "expected_visitors_000": 17712.1,
#  "opportunity_gap_pct": 27.0, ...}
```

Importing trains nothing and loads nothing; the model file opens lazily on the first call.
Full contract, response fields and error shapes:
[`handoff/for_hongyik/API_CONTRACT.md`](handoff/for_hongyik/API_CONTRACT.md).

`predict()` works on a fresh clone **without running the pipeline**, because
`handoff/for_hongyik/state_features.csv` is tracked and used as a fallback. Both sources give
identical answers.

## Folder map

```
ml/
├── data/
│   ├── raw/           # write-once downloads. NOT tracked. Only SOURCES.md is.
│   └── processed/     # Parquet from clean.py / features.py / evaluate.py. NOT tracked.
├── notebooks/
│   └── 03_eda.ipynb   # exploratory analysis, executed, ten figures
├── src/
│   ├── download.py    # phase 1   raw data, write-once
│   ├── xlsx_reader.py #           stdlib .xlsx reader for DOSM's formatted reports
│   ├── clean.py       # phase 2   raw -> four tidy Parquet tables
│   ├── features.py    # phase 5   model features, with leakage assertions
│   ├── train.py       # phase 6-7 baselines and model comparison
│   ├── tune.py        # phase 8   hyperparameter search, saves the model
│   ├── evaluate.py    # phase 9   holdout evaluation, gap table, figures
│   ├── predict.py     # phase 10  the one function the backend calls
│   └── handoff.py     # phase 10  generates the handoff files
├── models/
│   ├── a2_gap_model.joblib        # 0.28 MB, tracked
│   └── a2_gap_model_metadata.json # family, params, features, training years, scores
├── reports/           # one per phase, plus figures/
├── handoff/
│   ├── for_hongyik/   # API_CONTRACT.md, sample_predictions.csv, state_features.csv
│   └── for_yihui/     # FINDINGS.md and the figures it cites
├── requirements.txt
└── README.md
```

## Reports

| Phase | File | Contents |
|---|---|---|
| 0 | [`reports/00_brief.md`](reports/00_brief.md) | Digest of the competition brief, booklet, official site and both scoring rubrics: theme, timeline, data rules, the three deliverables, full rubric weights, and the conflicts between sources. |
| 1 | [`data/raw/SOURCES.md`](data/raw/SOURCES.md) | Every raw dataset: catalogue URL, file URL, granularity, measured time range, last-updated date, and a file manifest with hashes. |
| 2 | [`reports/02_cleaning.md`](reports/02_cleaning.md) | Cleaning rules, joins with row counts, three validation checks, and the completeness of the analysis panel. |
| 3 | [`notebooks/03_eda.ipynb`](notebooks/03_eda.ipynb) | Exploratory analysis; ten figures in [`reports/figures/`](reports/figures/), each with a takeaway. |
| 4 | [`reports/04_problem_candidates.md`](reports/04_problem_candidates.md) | Three problem candidates with evidence, data sufficiency and risks, and a recommendation scored against the rubric. |
| 5 | [`reports/05_features.md`](reports/05_features.md) | Every feature with its definition, source column and rationale; the leakage rules; and the rows lost at each stage. |
| 6 | [`reports/06_baseline.md`](reports/06_baseline.md) | The three baselines, how each is fitted, and their error on the validation year and every rolling-origin fold. |
| 7 | [`reports/07_model_comparison.md`](reports/07_model_comparison.md) | Four models on identical splits and metrics, single-year and rolling-origin, with training times and a recommendation. |
| 8 | [`models/a2_gap_model_metadata.json`](models/a2_gap_model_metadata.json) | The tuned model's family, hyperparameters, features, training years and selection scores. |
| 9 | [`reports/09_evaluation.md`](reports/09_evaluation.md) | Holdout results against the baseline, error by year and state, the systematic bias and the share-based gap, feature importance, limitations. |
| 10 | [`handoff/`](handoff/) | `for_hongyik/API_CONTRACT.md` and `sample_predictions.csv`; `for_yihui/FINDINGS.md` and its figures. |

## Conventions

- `random_state=42` everywhere.
- **Time-based splits only.** Training years always precede validation and holdout years;
  nothing is shuffled across time. Scalers are fitted inside a scikit-learn `Pipeline` on the
  training fold only.
- **The 2024–2025 holdout was read exactly once**, by `evaluate.py`, after the model and its
  hyperparameters were fixed.
- `data/raw/` is write-once. Downloaded files are never edited or overwritten; every
  transform is a script that writes to `data/processed/`.
- **Nothing is imputed.** Gaps stay null and are located exactly in the reports.
- Every number that appears in a report comes from code that actually ran, and the report
  names the script or notebook cell it came from.
- All paths are relative and built with `pathlib`, so the scripts run from any working
  directory on any operating system.

## Known limitations

In full in [`reports/09_evaluation.md`](reports/09_evaluation.md) §6, summarised for the
report in [`handoff/for_yihui/FINDINGS.md`](handoff/for_yihui/FINDINGS.md) §6. The two that
matter most:

- **The gap identifies underperformance, not its cause.** It says a state receives a smaller
  share of national visitors than its fundamentals imply. It does not say why.
- **58 training rows.** DOSM publishes this at state-year resolution, so a decade of data for
  the whole country is a small table.
