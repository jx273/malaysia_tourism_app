"""Phase 10 - generate the handoff files for HongYik and YiHui.

Run from the ml/ folder:   python src/handoff.py

Writes
  handoff/for_hongyik/state_features.csv     inputs predict() needs, tracked so a fresh
                                             clone can call it without running the pipeline
  handoff/for_hongyik/sample_predictions.csv every state-year the model can answer, for
                                             mocking the dashboard before any API exists
  handoff/for_yihui/figures/*.png            the figures referenced by FINDINGS.md

These are small, tracked files on purpose: the competition booklet requires a dashboard that
works "without external dependencies that cannot be accessed by the judges", so the dashboard
must be able to stand up without a live service.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from predict import _metadata, _model  # noqa: E402

ML_DIR = Path(__file__).resolve().parents[1]
PROCESSED = ML_DIR / "data" / "processed"
FIGURES = ML_DIR / "reports" / "figures"
FOR_HONGYIK = ML_DIR / "handoff" / "for_hongyik"
FOR_YIHUI = ML_DIR / "handoff" / "for_yihui"

# Figures quoted in FINDINGS.md. Kept explicit so a missing file fails loudly.
FINDINGS_FIGURES = [
    "01_national_trend.png",
    "03_concentration.png",
    "04_volume_vs_intensity.png",
    "06_loglog_structure.png",
    "09_od_flows.png",
    "11_holdout_actual_vs_expected.png",
    "12_opportunity_gap_2025.png",
    "13_feature_importance.png",
]


def log(message: str = "") -> None:
    print(message, flush=True)


def main() -> int:
    FOR_HONGYIK.mkdir(parents=True, exist_ok=True)
    (FOR_YIHUI / "figures").mkdir(parents=True, exist_ok=True)

    features = _metadata()["features"]
    df = pd.read_parquet(PROCESSED / "features.parquet")
    df["state"] = df["state"].astype(str)
    table = (df[df.in_structural_sample & (df.year >= 2017)]
             .dropna(subset=features)[["state", "year", "visitors_000"] + features]
             .sort_values(["year", "state"])
             .reset_index(drop=True))

    path = FOR_HONGYIK / "state_features.csv"
    table.to_csv(path, index=False)
    log(f"  {path.relative_to(ML_DIR).as_posix()}: {len(table)} rows x {table.shape[1]} cols")

    # Predictions and gaps, computed per year so the shares are within-year.
    parts = []
    for year, group in table.groupby("year"):
        group = group.copy()
        group["expected_visitors_000"] = np.exp(_model().predict(group[features].to_numpy()))
        group["expected_share_pct"] = group.expected_visitors_000 / group.expected_visitors_000.sum() * 100
        group["actual_share_pct"] = group.visitors_000 / group.visitors_000.sum() * 100
        group["opportunity_gap_pp"] = group.expected_share_pct - group.actual_share_pct
        group["opportunity_gap_pct"] = (group.expected_share_pct / group.actual_share_pct - 1) * 100
        parts.append(group)
    predictions = pd.concat(parts, ignore_index=True)

    latest = int(predictions.year.max())
    predictions["is_holdout_year"] = predictions.year.isin(_metadata()["holdout_years"])
    # The forecast layer is the naive last-value method: Phase 7 found no model beat it.
    predictions["naive_forecast_next_year_000"] = np.where(
        predictions.year == latest, predictions.visitors_000, np.nan)

    columns = ["state", "year", "visitors_000", "expected_visitors_000",
               "actual_share_pct", "expected_share_pct", "opportunity_gap_pp",
               "opportunity_gap_pct", "is_holdout_year", "naive_forecast_next_year_000"]
    out = predictions[columns].round(4).sort_values(["year", "opportunity_gap_pct"],
                                                    ascending=[True, False])
    path = FOR_HONGYIK / "sample_predictions.csv"
    out.to_csv(path, index=False)
    log(f"  {path.relative_to(ML_DIR).as_posix()}: {len(out)} rows, "
        f"years {sorted(out.year.unique())}")
    log(f"     {int(out.is_holdout_year.sum())} rows are holdout years "
        f"({_metadata()['holdout_years']}), the rest are in-sample")

    missing = [name for name in FINDINGS_FIGURES if not (FIGURES / name).exists()]
    if missing:
        log(f"  MISSING FIGURES: {missing}")
        return 1
    for name in FINDINGS_FIGURES:
        shutil.copy2(FIGURES / name, FOR_YIHUI / "figures" / name)
    log(f"  handoff/for_yihui/figures/: {len(FINDINGS_FIGURES)} PNG files copied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
