# `ml/` — Data & AI track, DOSM Datathon 2026

Python workspace for the Data & AI workstream. **Everything in this track lives under
`ml/`** so that it never collides with the Flutter project in the repository root.

> **Status: Phase 0 of 10 complete.** Setup and reproduction instructions are filled in as
> the phases land; the complete end-to-end instructions are written in Phase 10. Do not
> expect the pipeline below to run yet.

## Folder map

```
ml/
├── data/
│   ├── raw/          # write-once downloads from OpenDOSM etc. NOT tracked by git.
│   │                 # Reproduce with src/download.py. Only SOURCES.md is tracked.
│   └── processed/    # Parquet outputs of src/clean.py and src/features.py. Not tracked.
├── notebooks/        # exploratory analysis (03_eda.ipynb, ...)
├── src/              # all reusable code: download.py, clean.py, features.py, predict.py, ...
├── models/           # trained model artefacts (small scikit-learn files only)
├── reports/          # written findings, one file per phase
│   └── figures/      # PNG figures referenced by the reports
├── handoff/
│   ├── for_hongyik/  # API contract + sample predictions for the backend/dashboard
│   └── for_yihui/    # plain-English findings + figures for the report
├── requirements.txt  # pinned dependencies
└── README.md         # this file
```

## Reports so far

| Phase | File | Contents |
|---|---|---|
| 0 | [`reports/00_brief.md`](reports/00_brief.md) | Digest of the competition brief, booklet, official site and both scoring rubrics: theme, timeline, data rules, the three deliverables, full rubric weights, and the conflicts between sources. |
| 1 | [`data/raw/SOURCES.md`](data/raw/SOURCES.md) | Every raw dataset: catalogue URL, file URL, granularity, measured time range, last-updated date, and a file manifest with hashes. |
| 2 | [`reports/02_cleaning.md`](reports/02_cleaning.md) | Cleaning rules, joins with row counts, three validation checks, and the completeness of the analysis panel. |
| 3 | [`notebooks/03_eda.ipynb`](notebooks/03_eda.ipynb) | Exploratory analysis; ten figures in [`reports/figures/`](reports/figures/), each with a takeaway. |
| 4 | [`reports/04_problem_candidates.md`](reports/04_problem_candidates.md) | Three problem candidates with evidence, data sufficiency and risks, and a recommendation scored against the rubric. |
| 5 | [`reports/05_features.md`](reports/05_features.md) | Every feature with its definition, source column and rationale; the leakage rules; and the rows lost at each stage. |

## Setup

*(Written in full at Phase 10.)* The intended setup is a virtual environment at `ml/.venv`
with dependencies pinned in `ml/requirements.txt`:

```bash
cd ml
python -m venv .venv
.venv/Scripts/activate      # Windows;  source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
```

## Reproducing the pipeline

*(Written in full at Phase 10.)* The order will be: `download.py` → `clean.py` →
`features.py` → train → evaluate. All paths in `ml/src/` are relative and built with
`pathlib`, so the scripts run from any machine and any operating system.

## Conventions

- `random_state=42` everywhere.
- Temporal data uses time-based splits only — train on earlier periods, test on later.
  Nothing is shuffled across time; scalers and encoders are fit on training data only.
- `data/raw/` is write-once. Downloaded files are never edited or overwritten; every
  transform is a script that writes to `data/processed/`.
- Every number that appears in a report comes from code that actually ran, and cites the
  script or notebook cell it came from.
