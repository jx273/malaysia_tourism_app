"""Phase 2 - turn ml/data/raw/ into tidy Parquet tables in ml/data/processed/.

Run from the ml/ folder:   python src/clean.py

Outputs
-------
processed/state_year_panel.parquet        16 states x 2016-2025, one row per state-year
processed/od_flows.parquet                origin state -> destination state tourist flows
processed/national_quarterly.parquet      national quarterly visitors and expenditure
processed/arrivals_state_of_entry.parquet monthly foreign arrivals by state of entry

Every rule applied here is logged to stdout with row counts before and after, and
the same numbers are written up in reports/02_cleaning.md. Nothing is imputed
silently: gaps stay as nulls and are reported.

Raw files are opened read-only. This script never writes to data/raw/.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from xlsx_reader import read_sheets, year_header  # noqa: E402

ML_DIR = Path(__file__).resolve().parents[1]
RAW = ML_DIR / "data" / "raw"
PROCESSED = ML_DIR / "data" / "processed"

# The 16 state labels DOSM uses. Every table is harmonised onto these.
STATES = [
    "Johor", "Kedah", "Kelantan", "Melaka", "Negeri Sembilan", "Pahang",
    "Pulau Pinang", "Perak", "Perlis", "Selangor", "Terengganu", "Sabah",
    "Sarawak", "W.P. Kuala Lumpur", "W.P. Labuan", "W.P. Putrajaya",
]
# File-name slug -> canonical label, for the per-state workbooks.
SLUG_TO_STATE = {s.lower().replace(" ", "").replace(".", ""): s for s in STATES}

PANDEMIC_YEARS = (2020, 2021)
RECOVERY_YEAR = 2022


def log(message: str = "") -> None:
    print(message, flush=True)


def head(title: str) -> None:
    log(f"\n{'=' * 72}\n{title}\n{'=' * 72}")


def clean_label(cell: str) -> str:
    """DOSM headers stack Malay and English in one cell; keep the first line."""
    return cell.split("\n")[0].strip()


def to_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


# --------------------------------------------------------------------------
# D2 - domestic visitors by state visited (the model target)
# --------------------------------------------------------------------------
def load_visitors_by_state() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Table 9 of each annual edition. Returns (tidy frame, cross-edition check)."""
    records = []
    for edition in (2023, 2024, 2025):
        sheets = read_sheets(RAW / "domestic_tourism_annual" / f"tourism_domestic_{edition}.xlsx")
        rows = sheets["9"]
        years = year_header(rows)
        kept = 0
        for row in rows:
            state = clean_label(row[0])
            if state not in STATES:
                continue
            # Later editions append helper cells (value in units, a rank, the state
            # name again); taking only len(years) values after the label drops them.
            for year, value in zip(years, row[1:1 + len(years)]):
                records.append({"edition": edition, "state": state,
                                "year": int(year), "visitors_000": to_float(value)})
                kept += 1
        log(f"  edition {edition}: years {years[0]}-{years[-1]}, {kept} state-year cells")

    raw = pd.DataFrame.from_records(records)

    # Editions overlap. Compare them before collapsing, so any revision is visible.
    spread = (raw.dropna(subset=["visitors_000"])
                 .groupby(["state", "year"])["visitors_000"]
                 .agg(["min", "max", "count"]))
    overlapping = spread[spread["count"] > 1]
    worst = 0.0
    if len(overlapping):
        rel = (overlapping["max"] - overlapping["min"]) / overlapping["max"]
        worst = float(rel.max())
    log(f"  cross-edition overlap: {len(overlapping)} cells appear in more than one edition, "
        f"largest relative disagreement {worst:.4%}")

    # Newest edition wins.
    tidy = (raw.sort_values("edition")
               .drop_duplicates(["state", "year"], keep="last")
               .drop(columns="edition")
               .reset_index(drop=True))
    log(f"  after keeping the newest edition per state-year: {len(tidy)} rows")
    return tidy, overlapping.reset_index()


# --------------------------------------------------------------------------
# D4 - per-state key statistics and hotel supply
# --------------------------------------------------------------------------
KEY_METRICS = {
    "total receipts": "receipts_rm_mn",
    "domestic visitors": "visitors_000_state_edition",
    "domestic tourism trips": "trips_000",
    "average receipts per capita": "receipts_per_capita_rm",
}


def load_state_key_stats() -> pd.DataFrame:
    """Table 1 of each per-state workbook."""
    records = []
    files = sorted((RAW / "domestic_tourism_by_state").glob("*.xlsx"))
    for path in files:
        edition = int(path.stem.split("_")[2])
        state = SLUG_TO_STATE[path.stem.split("_", 3)[3]]
        rows = list(read_sheets(path).values())[0]
        years = year_header(rows)
        for row in rows:
            label = row[0].replace("\n", " ").lower()
            # Growth-rate rows carry one fewer value and would misalign with years.
            if "growth rate" in label or "kadar" in label:
                continue
            for needle, metric in KEY_METRICS.items():
                if needle in label:
                    for year, value in zip(years, row[1:1 + len(years)]):
                        records.append({"edition": edition, "state": state, "year": int(year),
                                        "metric": metric, "value": to_float(value)})
                    break
    raw = pd.DataFrame.from_records(records)
    log(f"  parsed {len(files)} workbooks -> {len(raw)} metric cells")

    tidy = (raw.sort_values("edition")
               .drop_duplicates(["state", "year", "metric"], keep="last")
               .pivot(index=["state", "year"], columns="metric", values="value")
               .reset_index())
    tidy.columns.name = None
    log(f"  after keeping the newest edition: {len(tidy)} state-year rows, "
        f"columns {[c for c in tidy.columns if c not in ('state', 'year')]}")
    return tidy


def load_hotel_supply() -> pd.DataFrame:
    """Table 14 of each per-state workbook: hotels and rooms by star rating."""
    records = []
    for path in sorted((RAW / "domestic_tourism_by_state").glob("*.xlsx")):
        edition = int(path.stem.split("_")[2])
        state = SLUG_TO_STATE[path.stem.split("_", 3)[3]]
        rows = list(read_sheets(path).values())[-1]
        started, hotels, rooms, ratings = False, 0.0, 0.0, 0
        for row in rows:
            label = row[0].replace("\n", " ").strip().lower()
            if "rating" in label or "penarafan" in label:
                started = True
                continue
            if not started:
                continue
            if label.startswith(("jumlah", "total")):
                break
            if len(row) >= 3:
                h, r = to_float(row[1]), to_float(row[2])
                if h is not None and r is not None:
                    hotels += h
                    rooms += r
                    ratings += 1
        if ratings:
            records.append({"edition": edition, "state": state,
                            "hotels": hotels, "rooms": rooms, "rating_rows": ratings})
    supply = pd.DataFrame.from_records(records)
    per_edition = supply.groupby("edition")["state"].nunique().to_dict()
    log(f"  hotel supply parsed for {len(supply)} state-editions; states per edition {per_edition}")
    log("  (the 2022 edition is missing Selangor: its source file returns HTTP 404)")
    return supply


# --------------------------------------------------------------------------
# D2 - origin x destination flows
# --------------------------------------------------------------------------
def load_od_flows() -> pd.DataFrame:
    records = []
    for edition in (2023, 2024, 2025):
        sheets = read_sheets(RAW / "domestic_tourism_annual" / f"tourism_domestic_{edition}.xlsx")
        rows = sheets["10"]
        header = next((r for r in rows
                       if sum(1 for c in r if clean_label(c) in STATES) >= 5), None)
        if header is None:
            log(f"  edition {edition}: no destination header found, skipped")
            continue
        destinations = [clean_label(c) for c in header]
        widths = set()
        kept = 0
        for row in rows:
            origin = clean_label(row[0])
            if origin not in STATES:
                continue
            widths.add(len(row))
            for dest, value in zip(destinations, row[1:1 + len(destinations)]):
                if dest not in STATES:      # the leading "Malaysia" column is a total
                    continue
                records.append({"year": edition, "origin": origin, "destination": dest,
                                "tourists_000": to_float(value)})
                kept += 1
        log(f"  edition {edition}: {kept} flows, origin row widths {sorted(widths)}")
    flows = pd.DataFrame.from_records(records)
    log(f"  total {len(flows)} origin-destination-year rows, "
        f"{flows['tourists_000'].isna().sum()} null values")
    return flows


# --------------------------------------------------------------------------
# D3 - national quarterly series
# --------------------------------------------------------------------------
def load_national_quarterly() -> pd.DataFrame:
    """Table A of the newest quarterly workbook, which carries the whole history.

    Row shapes vary by era, so columns are selected by how many values a row has
    rather than by position alone, and the result is checked against the annual
    totals printed in the same table.
    """
    rows = list(read_sheets(RAW / "domestic_tourism_quarterly"
                            / "tourism_domestic_2026-q1.xlsx").values())[0]
    quarterly, annual, current_year = [], {}, None
    for row in rows:
        first = row[0]
        values = [to_float(v) for v in row[1:]]
        if first.isdigit() and len(first) == 4:
            current_year = int(first)
            if values and values[0] is not None:
                annual[current_year] = values[0]
            continue
        if first.isdigit() and len(first) == 1 and current_year and 1 <= int(first) <= 4:
            n = len([v for v in values if v is not None])
            visitors = values[0]
            # 6 numeric values: visitors, QoQ, YoY, expenditure, QoQ, YoY
            # 9 numeric values: the same plus a tourists block inserted after visitors
            if n >= 9:
                tourists, expenditure = values[3], values[6]
            elif n >= 6:
                tourists, expenditure = None, values[3]
            else:
                tourists, expenditure = None, None
            quarterly.append({"year": current_year, "quarter": int(first),
                              "visitors_000": visitors, "tourists_000": tourists,
                              "expenditure_rm_mn": expenditure})
    q = pd.DataFrame.from_records(quarterly)
    log(f"  parsed {len(q)} quarters, {q['year'].min()} Q{q[q.year == q.year.min()].quarter.min()}"
        f" - {q['year'].max()} Q{q[q.year == q.year.max()].quarter.max()}")

    # Self-check: for complete years, the four quarters must sum to the annual total.
    checked = failed = 0
    for year, group in q.groupby("year"):
        if len(group) == 4 and year in annual and group["visitors_000"].notna().all():
            total, printed = group["visitors_000"].sum(), annual[year]
            checked += 1
            if abs(total - printed) / printed > 0.005:
                failed += 1
                log(f"  CHECK FAILED {year}: quarters sum to {total:,.1f} but the table "
                    f"prints {printed:,.1f}")
    log(f"  quarter-vs-annual check: {checked} complete years checked, {failed} mismatches")
    if failed:
        log("  -> column alignment is wrong somewhere; treat this table as unverified")
    return q


# --------------------------------------------------------------------------
# CSV predictors
# --------------------------------------------------------------------------
def load_csv_predictors() -> dict[str, pd.DataFrame]:
    out = {}

    pop = pd.read_csv(RAW / "population_state" / "population_state.csv", parse_dates=["date"])
    before = len(pop)
    pop = pop[(pop["sex"] == "both") & (pop["age"] == "overall") & (pop["ethnicity"] == "overall")]
    pop["year"] = pop["date"].dt.year
    out["population"] = pop[["state", "year", "population"]].rename(
        columns={"population": "population_000"})
    log(f"  population: {before} rows -> {len(out['population'])} after keeping "
        f"sex=both, age=overall, ethnicity=overall")

    gdp = pd.read_csv(RAW / "gdp_state" / "gdp_state_real_supply.csv", parse_dates=["date"])
    before = len(gdp)
    gdp = gdp[(gdp["series"] == "abs") & (gdp["sector"].isin(["p0", "p5"])) & (gdp["state"] != "Supra")]
    gdp["year"] = gdp["date"].dt.year
    gdp = (gdp.pivot_table(index=["state", "year"], columns="sector", values="value")
              .reset_index()
              .rename(columns={"p0": "gdp_total_rm_mn", "p5": "gdp_services_rm_mn"}))
    gdp.columns.name = None
    out["gdp"] = gdp
    log(f"  gdp: {before} rows -> {len(gdp)} state-year rows "
        f"(series=abs, sectors p0 total and p5 services, 'Supra' dropped)")

    lfs = pd.read_csv(RAW / "labour_force_state" / "lfs_qtr_state.csv", parse_dates=["date"])
    lfs["year"] = lfs["date"].dt.year
    quarters = lfs.groupby(["state", "year"])["date"].nunique().rename("lfs_quarters")
    agg = (lfs.groupby(["state", "year"])
              .agg(u_rate=("u_rate", "mean"), p_rate=("p_rate", "mean"),
                   lf_employed_000=("lf_employed", "mean"))
              .join(quarters).reset_index())
    partial = agg[agg["lfs_quarters"] < 4]
    out["lfs"] = agg
    log(f"  labour force: {len(lfs)} quarterly rows -> {len(agg)} state-year means; "
        f"{len(partial)} state-years built from fewer than 4 quarters "
        f"({sorted(partial['year'].unique())})")

    cpi = pd.read_csv(RAW / "cpi_state" / "cpi_2d_state.csv", parse_dates=["date"])
    before = len(cpi)
    cpi["year"] = cpi["date"].dt.year
    months = cpi.groupby(["state", "year"])["date"].nunique().rename("cpi_months")
    sel = cpi[cpi["division"].isin(["09", "11"])]
    wide = (sel.groupby(["state", "year", "division"])["index"].mean().unstack()
               .rename(columns={"09": "cpi_recreation", "11": "cpi_accom_food"})
               .join(months).reset_index())
    wide.columns.name = None
    out["cpi"] = wide
    log(f"  cpi: {before} rows -> {len(wide)} state-year rows "
        f"(division 09 Recreation Sport & Culture, 11 Restaurant & Accommodation Services; "
        f"annual mean of monthly index)")
    log(f"       state-years built from fewer than 12 months: "
        f"{int((wide['cpi_months'] < 12).sum())}")
    return out


def load_arrivals() -> pd.DataFrame:
    path = RAW / "arrivals_state_of_entry" / "arrivals_soe.csv"
    df = pd.read_csv(path, parse_dates=["date"])
    before = len(df)
    df = df.rename(columns={"soe": "state_of_entry"})
    unknown = sorted(set(df["state_of_entry"].unique()) - set(STATES))
    log(f"  arrivals: {before} rows, {df['state_of_entry'].nunique()} state-of-entry labels, "
        f"{df['country'].nunique()} nationalities, {df['date'].min().date()} to {df['date'].max().date()}")
    if unknown:
        log(f"  labels not matching the canonical 16 states: {unknown}")
    return df


# --------------------------------------------------------------------------
# assembly
# --------------------------------------------------------------------------
def build_panel() -> pd.DataFrame:
    head("D2  domestic visitors by state visited (target)")
    visitors, _ = load_visitors_by_state()

    head("D4  per-state key statistics")
    key_stats = load_state_key_stats()

    head("D4  hotel and room supply")
    supply = load_hotel_supply()

    head("D5-D8  CSV predictors")
    csv = load_csv_predictors()

    head("joins (row count before -> after)")
    panel = visitors.copy()
    log(f"  base (target): {len(panel)} rows")

    # Domestic-visitor figures also appear in the per-state workbooks. Keep the
    # annual-edition series as the single target and drop the duplicate column,
    # after checking the two agree.
    overlap = panel.merge(
        key_stats[["state", "year", "visitors_000_state_edition"]], on=["state", "year"], how="inner")
    both = overlap.dropna(subset=["visitors_000", "visitors_000_state_edition"])
    if len(both):
        rel = ((both["visitors_000"] - both["visitors_000_state_edition"]).abs()
               / both["visitors_000"]).max()
        log(f"  target cross-check against the per-state workbooks: {len(both)} shared cells, "
            f"largest relative difference {rel:.4%}")
    key_stats = key_stats.drop(columns=["visitors_000_state_edition"])

    for name, frame, keys in [
        ("key stats", key_stats, ["state", "year"]),
        ("population", csv["population"], ["state", "year"]),
        ("gdp", csv["gdp"], ["state", "year"]),
        ("labour force", csv["lfs"], ["state", "year"]),
        ("cpi", csv["cpi"], ["state", "year"]),
    ]:
        before = len(panel)
        panel = panel.merge(frame, on=keys, how="left")
        log(f"  left join {name:14s}: {before} -> {len(panel)} rows "
            f"(duplicate key check: {'OK' if len(panel) == before else 'ROW COUNT CHANGED'})")

    # Hotel supply exists for 2022 and 2023 only. Using the 2023 figure for earlier
    # years would leak future information into training, so 2022 and earlier take the
    # 2022 edition and 2023 onwards takes the 2023 edition. Selangor has no 2022 file,
    # so its 2017-2022 capacity stays null rather than being back-filled from 2023.
    supply_2022 = supply[supply["edition"] == 2022].set_index("state")
    supply_2023 = supply[supply["edition"] == 2023].set_index("state")
    panel["rooms"] = [
        supply_2022["rooms"].get(s) if y <= 2022 else supply_2023["rooms"].get(s)
        for s, y in zip(panel["state"], panel["year"])]
    panel["hotels"] = [
        supply_2022["hotels"].get(s) if y <= 2022 else supply_2023["hotels"].get(s)
        for s, y in zip(panel["state"], panel["year"])]
    log(f"  hotel supply attached with a carry-back rule (<=2022 uses the 2022 edition, "
        f">=2023 uses the 2023 edition): {panel['rooms'].isna().sum()} null room values")

    # Period flags. The structural sample follows the team decision of 2026-09-16:
    # exclude the movement-control years and the 2022 rebound, which ran at a median
    # state-level growth of +213.8% and is not a normal structural year.
    panel["is_pandemic_year"] = panel["year"].isin(PANDEMIC_YEARS)
    panel["is_recovery_year"] = panel["year"] == RECOVERY_YEAR
    panel["in_structural_sample"] = ~panel["year"].isin(PANDEMIC_YEARS + (RECOVERY_YEAR,))

    panel["year"] = panel["year"].astype("int16")
    panel["state"] = panel["state"].astype("category")
    panel = panel.sort_values(["state", "year"]).reset_index(drop=True)
    return panel


def main() -> int:
    PROCESSED.mkdir(parents=True, exist_ok=True)

    panel = build_panel()

    head("D2  origin x destination flows")
    flows = load_od_flows()

    head("D3  national quarterly series")
    quarterly = load_national_quarterly()

    head("D10  monthly arrivals by state of entry")
    arrivals = load_arrivals()

    head("outputs")
    for name, frame in [("state_year_panel", panel), ("od_flows", flows),
                        ("national_quarterly", quarterly),
                        ("arrivals_state_of_entry", arrivals)]:
        path = PROCESSED / f"{name}.parquet"
        frame.to_parquet(path, index=False)
        log(f"  {path.relative_to(ML_DIR).as_posix():48s} {frame.shape[0]:>7} rows x {frame.shape[1]} cols"
            f"  ({path.stat().st_size / 1e6:.2f} MB)")

    head("state_year_panel: completeness")
    log(f"  shape {panel.shape}, states {panel['state'].nunique()}, "
        f"years {panel['year'].min()}-{panel['year'].max()}")
    for column in panel.columns:
        missing = int(panel[column].isna().sum())
        log(f"  {column:26s} missing {missing:4d}  ({missing / len(panel):6.1%})")

    core = ["visitors_000", "population_000", "gdp_total_rm_mn", "u_rate", "cpi_accom_food"]
    complete = panel.dropna(subset=core)
    log(f"\n  complete on target + core structural predictors: {len(complete)} of {len(panel)}")
    structural = complete[complete["in_structural_sample"] & (complete["year"] >= 2017)]
    log(f"  structural sample (2017-2019 and 2023-2025): {len(structural)} rows")
    log(f"  forecasting sample (2017-2025, all years): "
        f"{len(complete[complete['year'] >= 2017])} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
