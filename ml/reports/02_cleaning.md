# 02 — Cleaning log

**Phase:** 2
**Script:** `ml/src/clean.py` (with `ml/src/xlsx_reader.py`)
**Run:** 2026-09-16, from `ml/`: `python src/clean.py`
**Every number in this file is printed by that script.** Re-running reproduces them.

## Outputs

| File | Rows | Cols | Size | Contents |
|---|---:|---:|---:|---|
| `data/processed/state_year_panel.parquet` | 160 | 21 | 0.03 MB | 16 states × 2016–2025, the analysis panel |
| `data/processed/od_flows.parquet` | 768 | 4 | 0.01 MB | origin state → destination state tourist flows, 2023–2025 |
| `data/processed/national_quarterly.parquet` | 21 | 5 | 0.00 MB | national quarterly visitors / tourists / expenditure, 2021 Q1 – 2026 Q1 |
| `data/processed/arrivals_state_of_entry.parquet` | 92,674 | 6 | 0.28 MB | monthly foreign arrivals by state of entry and nationality |

None of these are tracked by git; `data/processed/` is reproducible from `data/raw/`.

---

## 1. Why a custom Excel reader

DOSM publishes tourism statistics as **formatted Excel reports, not tidy tables**: one
workbook holds several numbered tables, the header stacks Malay and English inside a single
cell, and the sheet layout changes between editions. `ml/src/xlsx_reader.py` reads a workbook
with the standard library only and returns each sheet as rows of non-empty cell strings;
`clean.py` then locates each table by shape rather than by fixed cell coordinates.

`openpyxl` was approved but is **not used**: the stdlib reader already handles all 62 raw
files, so `requirements.txt` stays at six packages. Judges never run this code — they open
the dashboard file — so this choice affects only our own setup.

Tables are found by **shape, not position**: `year_header()` returns the first row holding at
least four 4-digit years. The number of title rows above the header differs between editions,
so a fixed row index would silently misread some workbooks.

---

## 2. Rules applied, by source

### 2.1 Label harmonisation

- **Canonical state labels** are the 16 DOSM uses: Johor, Kedah, Kelantan, Melaka, Negeri
  Sembilan, Pahang, Pulau Pinang, Perak, Perlis, Selangor, Terengganu, Sabah, Sarawak,
  W.P. Kuala Lumpur, W.P. Labuan, W.P. Putrajaya.
- **Bilingual cells**: DOSM writes `"Negeri\nState"` and `"Jumlah Perbelanjaan (RM juta)\nTotal
  Expenditure (RM million)"` in one cell. `clean_label()` keeps the text before the first line
  break, which is the Malay label, and matching is done on that.
- **File-name slugs** (`wpkualalumpur`, `negerisembilan`, …) map back to canonical labels via
  `SLUG_TO_STATE`.
- **The CSV catalogue tables already use the canonical spelling**, so no renaming was needed
  for population, GDP, labour force or CPI. This was verified by the joins below producing no
  unmatched rows.
- `arrivals_soe` uses the same spelling: **no unmatched state-of-entry labels** were found.

### 2.2 Duplicate handling — overlapping editions

D2 and D4 publish overlapping years in successive editions, so the same state-year appears
more than once.

- **Rule: the newest edition wins**, applied with a sort on edition followed by
  `drop_duplicates(..., keep="last")`.
- **Before collapsing, the editions are compared.** For the target:
  - 128 state-year cells appear in more than one edition
  - **largest relative disagreement: 0.0000%** — the editions are identical on every
    overlapping cell, so no revision policy question arises
- D4's key statistics: 808 metric cells parsed from 31 workbooks → **112 state-year rows**
  after keeping the newest edition.

### 2.3 Row-level exclusions

| Source | Rule | Effect |
|---|---|---|
| D2 Table 9 | Take only `len(years)` values after the state label | Drops the helper cells the 2024 edition appends (the value in units, a rank integer, the state name repeated) |
| D4 Table 1 | Skip rows whose label contains "growth rate" or "kadar" | Growth rows carry one fewer value and would misalign with the year header |
| D2 Table 10 | Keep only columns whose header is one of the 16 states | Drops the leading "Malaysia" total column. Also makes the 2024 edition's two extra columns harmless: its rows are 20 cells wide against 18 elsewhere, but alignment is by header name, not position |
| GDP | Keep `series == "abs"`, sectors `p0` and `p5`, drop the `Supra` pseudo-state | 2,163 → 168 state-year rows |
| Population | Keep `sex == "both"`, `age == "overall"`, `ethnicity == "overall"` | 270,063 → 841 rows |
| CPI | Keep divisions `09` and `11` | 44,576 → 272 state-year rows |

Division codes were resolved from `mcoicop.csv`, not assumed:
**`11` = Restaurant & Accommodation Services**, **`09` = Recreation, Sport & Culture**.
GDP sector codes came from `gdp_lookup.csv`: **`p0` = GDP at purchasers' prices**,
**`p5` = Services**.

### 2.4 Aggregation

- **Labour force**: quarterly → annual **mean** of `u_rate`, `p_rate`, `lf_employed`.
  560 quarterly rows → 144 state-year means. A `lfs_quarters` column records how many quarters
  each mean is built from: **16 state-years (all of 2025) use 3 quarters, not 4**, because
  `lfs_qtr_state` ends at 2025 Q3.
- **CPI**: monthly index → annual **mean**. A `cpi_months` column records the month count:
  **16 state-years use fewer than 12 months** (2026, which has data to July only). 2026 is
  outside the panel's year range and does not reach the analysis sample.

### 2.5 Missing values — nothing is imputed

Gaps are left as nulls and reported. No forward-fill, no interpolation, no mean substitution.
The one exception is documented below and is a *selection* rule, not an imputation.

### 2.6 Hotel supply and the leakage rule

`rooms` and `hotels` exist for **2022 and 2023 only** (D4 Table 14).

Filling every year with the 2023 figure would put information from 2023 into rows for 2017,
which is future information at prediction time. The rule applied instead:

- **year ≤ 2022 → the 2022 edition's figure**
- **year ≥ 2023 → the 2023 edition's figure**

Selangor has **no 2022 workbook** (its source URL returns HTTP 404), so Selangor's 2016–2022
capacity is **left null rather than back-filled from 2023**. This is the whole of the 7 null
`rooms`/`hotels` values.

This is still a carry-back assumption for 2016–2021 and must be stated in the report's
methodology: capacity is treated as approximately constant within the period, which is
reasonable given that rooms changed by less than 5% between the two observed years for most
states, but it is an assumption, not a measurement.

### 2.7 Period flags

Three boolean columns implement the team decision of 2026-09-16:

- `is_pandemic_year` — 2020, 2021
- `is_recovery_year` — 2022
- `in_structural_sample` — **not** 2020, 2021 or 2022

2022 is excluded from the structural sample because it is a rebound year, not a structural
one: **median state-level growth in 2022 was +213.8%** (range +85.5% to +485.5%), against
+7.7% to +8.5% nationally in 2017–2019.

### 2.8 Dtypes

`year` → `int16`; `state` → `category`; all measures → `float64`; flags → `bool`.
Dates in the quarterly and arrivals tables are parsed to `datetime64`.

---

## 3. Joins

All joins are **left joins onto the target**, keyed on `(state, year)`. A row count that
changes would mean duplicate keys on the right-hand side; none did.

| Join | Rows before | Rows after | Duplicate keys |
|---|---:|---:|---|
| base — target (D2 Table 9) | — | 160 | — |
| + key stats (D4 Table 1) | 160 | 160 | none |
| + population (D6) | 160 | 160 | none |
| + GDP (D7) | 160 | 160 | none |
| + labour force (D8) | 160 | 160 | none |
| + CPI (D5) | 160 | 160 | none |
| + hotel supply (D4 Table 14) | 160 | 160 | assigned by rule, not joined |

---

## 4. Validation checks that actually ran

Three independent checks, all in `clean.py`:

1. **Cross-edition agreement (target).** 128 overlapping state-year cells across the 2023,
   2024 and 2025 editions. **Largest relative disagreement: 0.0000%.**

2. **Target cross-check against a different publication.** The annual editions' Table 9 and
   the per-state workbooks' Table 1 are separate publications that both report domestic
   visitors. 112 shared cells compared:
   - **median absolute relative difference: 0.000000%**
   - **111 of 112 cells match exactly**
   - one cell differs: **W.P. Labuan 2020 — 107.0 in the annual edition against 107.53 in the
     per-state workbook (0.4953%)**, which is the annual edition rounding to one decimal.
   The per-state figure is not used; the annual edition is the single source for the target.

3. **Quarterly sums against printed annual totals.** For every year where all four quarters
   are present, the quarters must sum to the annual total printed in the same table.
   **5 complete years checked, 0 mismatches.** This is what confirms the column alignment in
   the quarterly workbook, whose row shape changes between eras (6 numeric values per quarter
   before 2025, 9 from 2025 once a domestic-tourists block was inserted).

---

## 5. `state_year_panel.parquet` — completeness

160 rows, 16 states, 2016–2025.

| Column | Missing | % |
|---|---:|---:|
| `state`, `year`, `visitors_000` | 0 | 0.0% |
| `population_000` | 0 | 0.0% |
| `cpi_recreation`, `cpi_accom_food`, `cpi_months` | 0 | 0.0% |
| `gdp_total_rm_mn`, `gdp_services_rm_mn` | 7 | 4.4% |
| `rooms`, `hotels` | 7 | 4.4% |
| `u_rate`, `p_rate`, `lf_employed_000`, `lfs_quarters` | 16 | 10.0% |
| `receipts_rm_mn`, `trips_000`, `receipts_per_capita_rm` | 48 | 30.0% |
| `is_pandemic_year`, `is_recovery_year`, `in_structural_sample` | 0 | 0.0% |

**Where the gaps are, exactly:**

- **GDP — 7 nulls = W.P. Putrajaya, 2016–2022.** Consistent with the catalogue note that
  Putrajaya is subsumed under W.P. Kuala Lumpur in the earlier state GDP series.
- **Hotel supply — 7 nulls = Selangor, 2016–2022** (the HTTP 404 file; see §2.6).
- **Labour force — 16 nulls = all 16 states in 2016.** `lfs_qtr_state` begins at 2017 Q1.
- **Receipts / trips / receipts per capita — 48 nulls = 2016, 2024 and 2025.** D4 Table 1
  covers 2017–2023 only. **This is why receipts cannot be the model target**: there is no
  recent holdout year for it.

## 6. Analysis samples

| Sample | Definition | Rows |
|---|---|---:|
| Full panel | 16 states × 2016–2025 | 160 |
| Complete on target + core predictors | target, population, GDP total, unemployment rate, CPI accommodation | 138 |
| **Forecasting sample** (Model A) | 2017–2025, all years kept, pandemic flagged | **138** |
| **Structural sample** (Model B) | 2017–2019 and 2023–2025 | **93** |

The structural sample is 93 and not 96 because W.P. Putrajaya has no GDP for 2017–2019.

## 7. Other processed tables

**`od_flows.parquet`** — 768 rows = 3 years × 16 origins × 16 destinations, **0 nulls**.
Diagonal entries (origin = destination) are within-state tourists and are kept.

**`national_quarterly.parquet`** — 21 quarters, 2021 Q1 – 2026 Q1. `tourists_000` is null
before 2025 Q1, when DOSM began publishing it.

**`arrivals_state_of_entry.parquet`** — 92,674 rows, 224 nationalities, 58 months,
**2020-01 to 2024-10**. Two limitations found on profiling, both material:

1. **Only 14 states appear.** W.P. Kuala Lumpur and W.P. Putrajaya have no entry point of
   their own — KLIA sits in Sepang, Selangor — so arrivals credited to Selangor include
   visitors whose destination is Kuala Lumpur. Combined with the catalogue's own note that
   the state of entry "may not be their final destination", this table measures **where
   visitors crossed the border, not where they went**.
2. **The series starts in January 2020**, so it contains no pre-pandemic baseline, and 2021
   totals 471 thousand arrivals against 31,899 thousand in 2024 — border closure, not demand.

For both reasons it is **kept out of `state_year_panel.parquet`** and left as a standalone
table for Phase 3 to judge.

## 8. What was deliberately not done

- **The Tourism Satellite Account (D1) was not parsed.** 15 editions with sheet names and
  layouts that change between them, all national-annual, and nothing in it joins on `state`.
  It is available in `data/raw/` if Phase 3 wants national context. [not computed]
- **No geographic coordinates or distances.** Neither catalogue index lists a geojson,
  centroid or boundary file, so a distance-based gravity model on `od_flows` is not possible
  from current sources.
- **No imputation** of any kind, beyond the documented hotel-capacity carry-back rule.
