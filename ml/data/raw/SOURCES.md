# Raw data sources — Phase 1

**Inventory date:** 2026-09-13
**Downloaded by:** `ml/src/download.py` (run from `ml/`: `python src/download.py`)
**This file is the only tracked file in `data/raw/`.** Everything else here is reproducible
from the URLs below and is git-ignored.

## How to read this file

- **Every file URL was read from the download/resource link rendered on the catalogue or
  publication page cited beside it.** Catalogue metadata was taken from each page's embedded
  `__NEXT_DATA__` JSON; publication resource links from each OpenDOSM publication page.
  No URL was typed from memory or constructed by pattern.
- **Time range and granularity were measured from the downloaded files**, not copied from
  page text, because the catalogue pages do not expose a begin/end date. CSV figures come
  from a pandas profile of each file; Excel figures from reading each workbook's sheet titles
  and year header rows. Where a figure is not measured it says so.
- **"Last updated"** is the catalogue page's `last_updated` for data-catalogue tables, and the
  OpenDOSM release date plus the storage server's HTTP `Last-Modified` header for
  publication workbooks (both checked 2026-09-13).
- Short hashes are the first 16 hex characters of SHA-256, as printed by `download.py`. If a
  re-download prints a different hash, DOSM has revised the file since this inventory.

## Why these datasets

The brief's hard rules shaped the shortlist `[ml/reports/00_brief.md §4, §5]`:

1. **Raw data must originate from within Malaysia** `[Booklet p.14]` → every file below is
   published by DOSM (or a Malaysian agency via DOSM's catalogue).
2. **Extra marks for official Malaysian data** `[Booklet p.11]` → OpenDOSM first.
3. **Rubric C2 (25%) rewards combining dataset types including geospatial, and integration
   that yields new insight** `[RA QLT3, QLT4]` → preference for **state-level** series that
   can be joined on `state × year` (or finer).

Tourism data is **not in the OpenDOSM data catalogue**. A keyword search of all 183 catalogue
datasets returned no tourism, hotel, arrival or visitor series. It lives in **OpenDOSM
Publications** instead (30 tourism publications found), as Excel resources on
`storage.dosm.gov.my`. D1–D4 come from there; D5–D9 are catalogue tables chosen as
state-level context that joins onto them.

---

## Summary

| ID | Dataset | Source page type | Geography | Time grain | Time range (measured) | Files | Dimension |
|---|---|---|---|---|---|---|---|
| D1 | Tourism Satellite Account | OpenDOSM publication | National | Annual | 2000–2024 across editions (see notes) | 15 xlsx | Economic |
| D2 | Domestic Tourism (annual) | OpenDOSM publication | National + **state visited** + origin×destination | Annual | Table 9 by state: **2016–2025** | 3 xlsx | Economic / Social |
| D3 | Domestic Tourism (quarterly) | OpenDOSM publication | National | Quarterly (+ annual) | Quarterly **2021 Q1 – 2026 Q1**; annual 2012–2025 | 5 xlsx (3 distinct) | Economic |
| D4 | Domestic Tourism by State | OpenDOSM publication | **State** (+ origin×destination) | Annual | Key stats **2017–2023**; hotel supply 2022, 2023 | 31 xlsx | Economic / Social |
| D5 | Monthly CPI by State & Division | OpenDOSM data catalogue | **State** | Monthly | **2010-01 – 2026-07** | 1 csv + lookup | Economic |
| D6 | Population Table: States | OpenDOSM data catalogue | **State** | Annual | **1970 – 2026** | 1 csv | Social (denominator) |
| D7 | Annual Real GDP by State & Sector | OpenDOSM data catalogue | **State** | Annual | **2015 – 2025** | 1 csv + lookup | Economic |
| D8 | Quarterly Labour Force by State | OpenDOSM data catalogue | **State** | Quarterly | **2017 Q1 – 2025 Q3** | 1 csv | Social |
| D9 | Water Consumption by State & Sector | OpenDOSM data catalogue | **State** (14 of 16) | Annual | **2003 – 2022** | 1 csv | Environmental |
| D10 | Monthly Arrivals by State of Entry | data.gov.my catalogue | **State of entry** (14 of 16) | Monthly | **2020-01 – 2024-10** | 1 csv | Economic (inbound) |

Totals: **62 files, 36.41 MB** (3 quarterly files are byte-identical; see D3). Largest
file: `population_state.csv`, 12.568 MB. Figures from the `download.py` runs of
2026-09-13 (61 files) and 2026-09-16 (D10 added).

---

## D1 — Tourism Satellite Account (TSA)

- **Publisher:** DOSM
- **Catalogue URLs:** `https://open.dosm.gov.my/publications/tourism_<year>` for each year
  2010–2024 (15 pages)
- **File URLs:** `https://storage.dosm.gov.my/tourism/tourism_<year>.xlsx`, 2010–2024. Each
  URL is listed on its own publication page as the "excel" resource.
- **Local path:** `data/raw/tourism_satellite_account/tourism_<year>.xlsx`
- **Geographic granularity:** National (Malaysia)
- **Time granularity:** Annual
- **Time range:** each edition carries a multi-year table history, measured from year header
  rows:
  - 2010 edition: 2000–2010
  - 2015 edition: 2010–2013/2014/2015 (varies by table)
  - 2018 edition: 2015–2016/2017/2018 (varies by table)
  - 2024 edition: 2015–2024 for most tables, 2015–2022 for Tables 5–6, and inbound indicators
    for 2019–2024
- **Last updated:** latest edition (2024) released 2025-09-12; HTTP Last-Modified
  2025-09-12. The 2010–2022 files all carry Last-Modified 2023-12-16.
- **Contents (sheet titles):** inbound visitors / tourists / excursionists; domestic
  visitors / tourists / excursionists; outbound; internal tourism consumption; production
  accounts; tourism ratios; employment.
- **Notes for Phase 2:**
  - **Layouts differ between editions.** Sheet names change (for example `table 1a inbd
    t.visitors` in 2010 becomes `Jad 1` in 2024), the sheet count ranges from 10 to 14, and
    column counts vary.
  - Editions overlap, and later editions revise earlier years. The 2018+ editions start
    at 2015, which suggests a base-year change. Prefer the latest edition for each year and
    document it.
  - National only, so it cannot join on `state`.

## D2 — Domestic Tourism (annual)

- **Publisher:** DOSM (Domestic Tourism Survey)
- **Catalogue URLs:**
  - `https://open.dosm.gov.my/publications/tourism_domestic_annual_2023` (released 2024-06-12)
  - `https://open.dosm.gov.my/publications/tourism_domestic_annual_2024` (released 2025-06-19)
  - `https://open.dosm.gov.my/publications/tourism_domestic_annual_2025` (released 2026-06-16)
- **File URLs:**
  - `https://storage.dosm.gov.my/tourism/tourism_domestic_2023.xlsx`
  - `https://storage.dosm.gov.my/tourism/tourism_domestic_2024.xlsx`
  - `https://storage.dosm.gov.my/tourism/tourism_domestic_2025.xlsx`
- **Local path:** `data/raw/domestic_tourism_annual/`
- **Geographic granularity:** National; **by state visited** (Table 9); **state of origin ×
  state visited** (Table 10); top-5 destinations and top-5 administrative districts per state
  (Tables 8A/8B — named places, not counts)
- **Time granularity:** Annual
- **Time range (measured from table titles and year headers):**
  - Table 1, key statistics: 2016–2023 / 2017–2024 / 2018–2025 across the three editions
  - **Table 9, domestic visitors by state visited: 2016–2023, 2017–2024, 2018–2025. The union
    is 2016–2025, which gives 16 states × 10 years.**
  - Table 10, tourists by origin × visited state: a single year per edition (2023, 2024, 2025)
  - Tables 2–7, 11–13: two most recent years per edition
- **Last updated:** 2025 edition released 2026-06-16; HTTP Last-Modified 2026-06-16
- **Notes for Phase 2:**
  - Now computed in full by `src/clean.py`: all **128** overlapping state-year cells agree
    across editions, largest relative disagreement **0.0000%**
    (see `reports/02_cleaning.md` §4).
  - The 2024 edition's Table 9 carries extra trailing cells per row (a value in units rather
    than thousands, a rank-like integer, and the state name repeated). These must be dropped.
  - The 2024 edition's Table 10 sheet has 45 non-empty rows against 22 in the other editions,
    so it likely holds a second table. Inspect before parsing.
  - Headers are bilingual (Malay / English) within the same cell, separated by line breaks.

## D3 — Domestic Tourism (quarterly)

- **Publisher:** DOSM (Domestic Tourism Survey)
- **Catalogue URLs:** `https://open.dosm.gov.my/publications/tourism_domestic_<quarter>` for
  `2024-q4` (released 2025-03-24), `2025-q1` (2025-06-19), `2025-q2` (2025-09-18), `2025-q4`
  (2026-03-17), `2026-q1` (2026-06-24)
- **File URLs:** `https://storage.dosm.gov.my/tourism/tourism_domestic_<quarter>.xlsx` for
  the same five quarters
- **Local path:** `data/raw/domestic_tourism_quarterly/`
- **Geographic granularity:** National
- **Time granularity:** Quarterly, with annual summary rows
- **Time range (measured from all rows of the 2026-q1 workbook, Table A):**
  - Annual rows: 2012–2025
  - **Quarterly rows: 2021 Q1 – 2026 Q1 (21 quarters)**
  - Columns: domestic visitors ('000), QoQ %, YoY %, total expenditure (RM million), and,
    **from 2025 Q1 only**, domestic tourists ('000)
- **Last updated:** 2026-q1 edition released 2026-06-24; HTTP Last-Modified 2026-06-24
- **⚠️ Data-quality issues found:**
  - **`tourism_domestic_2024-q4.xlsx`, `tourism_domestic_2025-q1.xlsx` and
    `tourism_domestic_2025-q2.xlsx` are byte-identical** (SHA-256
    `9e1be4d57e401f1ae7114f496f94477bf7744131da4629a02de11f02dd5342ca`). All three contain a
    sheet named `DTS 2024 Q4` with data to 2024 only. DOSM appears to have attached the
    2024 Q4 workbook to the 2025 Q1 and 2025 Q2 publications.
  - The 2025-q4 and 2026-q1 workbooks both name their sheet `DTS 2025 Q2`, although their
    titles say 2021–2025 and 2021–2026 respectively. Treat the title, not the sheet name, as
    authoritative.
  - Quarterly editions 4Q 2023 – 3Q 2024 are PDF-only on OpenDOSM; 3Q 2025 is not listed.
  - **Consequence:** the 2026-q1 workbook alone contains the whole quarterly history
    (2021 Q1 – 2026 Q1). The other four files are kept for provenance but add no rows.

## D4 — Domestic Tourism by State

- **Publisher:** DOSM (Domestic Tourism Survey)
- **Catalogue URLs:**
  - `https://open.dosm.gov.my/publications/tourism_domestic_state_2022` (released 2023-09-15)
  - `https://open.dosm.gov.my/publications/tourism_domestic_state_2023` (released 2024-09-20)
- **File URLs:** `https://storage.dosm.gov.my/tourism/tourism_domestic_<year>_<state>.xlsx`
  for year ∈ {2022, 2023} and state ∈ {johor, kedah, kelantan, melaka, pahang,
  negerisembilan, pulaupinang, perak, perlis, selangor, terengganu, sabah, sarawak,
  wpkualalumpur, wplabuan, wpputrajaya}. Each is listed on its publication page as an "excel"
  resource.
- **Local path:** `data/raw/domestic_tourism_by_state/`
- **Geographic granularity:** **State** (one workbook per state per edition); Table 10 adds
  origin × visited state
- **Time granularity:** Annual
- **Time range (measured from each workbook's Table 1 year header):**
  - **Table 1, key statistics per state: 2017–2022 (2022 edition), 2017–2023 (2023 edition)**
    — total receipts (RM million), domestic visitors ('000), domestic tourism trips ('000),
    average receipts per capita (RM), with annual growth rates
  - **Table 14, number of hotels and rooms by star rating per state: 2022 and 2023** — the
    only accommodation-supply series found in open DOSM data
  - Other tables (visitor type, receipts by trip type and component, purpose of visit, top-5
    destinations, mode of transport, visitor profile): edition year and the year before
- **Last updated:** 2023 edition released 2024-09-20; HTTP Last-Modified 2024-09-21
- **⚠️ Missing file:**
  - **`tourism_domestic_2022_selangor.xlsx` returns HTTP 404** (checked 2026-09-13), although
    the publication page lists it. It was not substituted.
  - **Impact is small.** The 2023 Selangor workbook covers Table 1 for 2017–2023, so the
    Selangor time series is intact. Only Selangor's 2022-edition hotel supply (Table 14) and
    other 2022-only tables are lost.
- **Notes for Phase 2:** all 31 workbooks have 11 sheets with a consistent structure within
  each edition. Table title wording differs slightly between the 2022 and 2023 editions
  ("…, Johor, 2017 - 2022" vs "… in Johor, 2017 - 2023").

## D5 — Monthly CPI by State & Division (2-digit)

- **Publisher:** DOSM
- **Catalogue URL:** `https://open.dosm.gov.my/data-catalogue/cpi_state`
- **File URL:** `https://storage.dosm.gov.my/cpi/cpi_2d_state.csv`
- **Lookup (catalogue):** `https://open.dosm.gov.my/data-catalogue/mcoicop` →
  `https://storage.dosm.gov.my/dictionaries/mcoicop.csv` (343 rows; decodes `division`)
- **Local path:** `data/raw/cpi_state/`
- **Geographic granularity:** State (16)
- **Time granularity:** Monthly
- **Time range:** **2010-01-01 – 2026-07-01** (199 months)
- **Last updated:** 2026-09-10 12:25 (next update listed as 2026-09-18 12:30)
- **Shape:** 44,576 rows × 4 columns (`state`, `date`, `division`, `index`), which is exactly
  16 states × 199 months × 14 divisions. 0 nulls, 0 duplicate rows. Index base 2010 = 100.

## D6 — Population Table: States

- **Publisher:** DOSM
- **Catalogue URL:** `https://open.dosm.gov.my/data-catalogue/population_state`
- **File URL:** `https://storage.dosm.gov.my/population/population_state.csv`
- **Local path:** `data/raw/population_state/`
- **Geographic granularity:** State (16)
- **Time granularity:** Annual
- **Time range:** **1970-01-01 – 2026-01-01** (57 years)
- **Last updated:** 2026-07-31 12:00 (next update 2027-07-31)
- **Shape:** 270,063 rows × 6 columns (`state`, `date`, `sex`, `age`, `ethnicity`,
  `population` in thousands). 0 nulls, 0 duplicate rows.
- **Role:** denominator for per-resident intensity measures (e.g. visitors per resident).
- **Note:** the `age` column mixes two coding schemes, `70+` and `80+` alongside `70-74`,
  `80-84` and `85+`. Filter to `age == 'overall'` unless age detail is needed.

## D7 — Annual Real GDP by State & Economic Sector

- **Publisher:** DOSM
- **Catalogue URL:** `https://open.dosm.gov.my/data-catalogue/gdp_state_real_supply`
- **File URL:** `https://storage.dosm.gov.my/gdp/gdp_state_real_supply.csv`
- **Lookup (catalogue):** `https://open.dosm.gov.my/data-catalogue/gdp_lookup` →
  `https://storage.dosm.gov.my/gdp/gdp_lookup.csv` (174 rows; decodes `sector`)
- **Local path:** `data/raw/gdp_state/`
- **Geographic granularity:** State. **17 values**: 15 states (W.P. Putrajaya is folded into
  W.P. Kuala Lumpur per the catalogue page), `W.P. Putrajaya`, and a non-geographic `Supra`
  row. The `W.P. Putrajaya` rows and `Supra` need checking in Phase 2.
- **Time granularity:** Annual
- **Time range:** **2015-01-01 – 2025-01-01** (11 years), constant 2015 prices
- **Last updated:** 2026-07-01 12:30 (next update 2027-07-01)
- **Shape:** 2,163 rows × 5 columns (`series`, `date`, `state`, `sector`, `value`); sectors
  `p0`–`p6`; series `abs` and `growth_yoy`. **1 null in `value`**; 0 duplicate rows.

## D8 — Quarterly Principal Labour Force Statistics by State

- **Publisher:** DOSM
- **Catalogue URL:** `https://open.dosm.gov.my/data-catalogue/lfs_qtr_state`
- **File URL:** `https://storage.dosm.gov.my/labour/lfs_qtr_state.csv`
- **Local path:** `data/raw/labour_force_state/`
- **Geographic granularity:** State (16)
- **Time granularity:** Quarterly
- **Time range:** **2017-01-01 – 2025-07-01**, i.e. 2017 Q1 – 2025 Q3 (35 quarters)
- **Last updated:** 2025-11-10 12:00. The page lists the next update as 2026-02-11, which has
  passed without a newer file.
- **Shape:** 560 rows × 8 columns (labour force, employed, unemployed, outside labour force,
  participation rate, unemployment rate) = 16 × 35. 0 nulls, 0 duplicate rows.

## D9 — Water Consumption by State and Sector

- **Publisher:** SPAN, NRES, DOSM (as listed on the catalogue page)
- **Catalogue URL:** `https://open.dosm.gov.my/data-catalogue/water_consumption`
- **File URL:** `https://storage.data.gov.my/water/water_consumption.csv`. This is the link
  the OpenDOSM catalogue page renders; the file is hosted on data.gov.my storage.
- **Local path:** `data/raw/water_consumption_state/`
- **Geographic granularity:** State. **14 states + `Malaysia`**; W.P. Kuala Lumpur and
  W.P. Putrajaya are absent.
- **Time granularity:** Annual
- **Time range:** **2003-01-01 – 2022-01-01** (20 years)
- **Last updated:** 2024-09-01 12:00 (next update "tbc")
- **Shape:** 600 rows × 4 columns (`state`, `sector` ∈ {domestic, nondomestic}, `date`,
  `value` in million litres/day). 0 nulls, 0 duplicate rows.
- **Role:** the only state-level environmental time series in the catalogue. Monthly
  `air_pollution` was considered and rejected because it has no state column.

## D10 — Monthly Arrivals by State of Entry, Nationality & Sex

- **Publisher:** Jabatan Imigresen Malaysia (Imigresen), via the data.gov.my catalogue
- **Catalogue URL:** `https://data.gov.my/data-catalogue/arrivals_soe`
- **File URL:** `https://storage.data.gov.my/demography/arrivals_soe.csv`
- **Local path:** `data/raw/arrivals_state_of_entry/arrivals_soe.csv` (2.791 MB,
  SHA-256 `2fe08e05c0249154`)
- **Approved:** 2026-09-16. This is the one file outside OpenDOSM.
- **Geographic granularity:** state **of entry**, and only **14 of the 16 states** appear —
  W.P. Kuala Lumpur and W.P. Putrajaya have no entry point of their own.
- **Time granularity:** Monthly
- **Time range (measured):** **2020-01-01 – 2024-10-01**, 58 months
- **Last updated:** 2024-11-25 16:00. The catalogue lists the next update as 2024-12-25,
  which has not happened.
- **Shape:** 92,674 rows × 6 columns; 224 nationalities.
- **⚠️ Two limitations that keep it out of the analysis panel:**
  1. The catalogue's own field description says the state of entry "may not be their final
     destination". KLIA is in Sepang, Selangor, so arrivals credited to Selangor include
     visitors bound for Kuala Lumpur. It measures **border crossings, not destinations**.
  2. It begins in January 2020, so there is **no pre-pandemic baseline**. Annual totals are
     6,172k (2020), 471k (2021), 15,149k (2022), 30,515k (2023), 31,899k (2024) — the 2021
     figure reflects border closure, not demand.
- Cleaned to `data/processed/arrivals_state_of_entry.parquet` as a standalone table.

---

## Considered but not downloaded

| Candidate | Where found | Why not downloaded |
|---|---|---|
| **Monthly Arrivals by State of Entry** (`arrivals_soe`) | see D10 below | **Approved and downloaded on 2026-09-16.** Kept out of the state-year analysis panel; see D10. |
| Monthly Arrivals by Nationality & Sex (`arrivals`) | data.gov.my catalogue → `https://storage.data.gov.my/demography/arrivals.csv` | National only; superseded by `arrivals_soe` if that is approved. |
| Tourism Malaysia statistics portal | `https://data.tourism.gov.my/` (cited in DOSM's "Discover DOSM Tourism Statistics" deck) | Datasets are behind registration ("To find more, please register"); only PDFs and infographics are public. Not open and publicly accessible, as the brief requires. |
| Domestic Tourism quarterly, 4Q 2023 – 3Q 2024 | OpenDOSM publications | PDF-only. The same quarters are already inside D3's 2026-q1 workbook. |
| Tourism Satellite Account for Sabah 2023 | `https://open.dosm.gov.my/publications/tourism_2023_sabah` | Single state and single year; cannot form a panel. |
| Monthly Air Pollution (`air_pollution`) | OpenDOSM catalogue | No state column; ends 2022. |
| Crime by District, Household Income by District, Employment by Sector, Productivity for Priority Subsectors, Quarterly GDP by Subsector, SPPI by Division | OpenDOSM catalogue | Inspected on their catalogue pages. Each is either national-only or only loosely tourism-related; deferred unless Phase 4 needs one. |

---

## Appendix — file manifest

`download.py` runs on 2026-09-13 (61 files) and 2026-09-16 (D10). All returned
`downloaded`, with 0 failures.

| Local path (under `data/raw/`) | MB | SHA-256 (16) |
|---|---:|---|
| `tourism_satellite_account/tourism_2010.xlsx` | 0.074 | `52b4262c98870ff0` |
| `tourism_satellite_account/tourism_2011.xlsx` | 0.070 | `738cc7e2e24c25d9` |
| `tourism_satellite_account/tourism_2012.xlsx` | 0.098 | `3e145fd335028cf3` |
| `tourism_satellite_account/tourism_2013.xlsx` | 0.105 | `60980c06ff74780f` |
| `tourism_satellite_account/tourism_2014.xlsx` | 0.094 | `4cd9eea40d58a706` |
| `tourism_satellite_account/tourism_2015.xlsx` | 0.772 | `69802643d21ee915` |
| `tourism_satellite_account/tourism_2016.xlsx` | 0.772 | `96323e44d8562213` |
| `tourism_satellite_account/tourism_2017.xlsx` | 0.376 | `ea024a5d3320c110` |
| `tourism_satellite_account/tourism_2018.xlsx` | 0.252 | `68d71ce95001c523` |
| `tourism_satellite_account/tourism_2019.xlsx` | 0.270 | `e10cdf238d54bad2` |
| `tourism_satellite_account/tourism_2020.xlsx` | 0.363 | `537083d517ff0222` |
| `tourism_satellite_account/tourism_2021.xlsx` | 0.365 | `d6df7b00542b8db6` |
| `tourism_satellite_account/tourism_2022.xlsx` | 0.452 | `30b81a0b80b4e9b3` |
| `tourism_satellite_account/tourism_2023.xlsx` | 0.533 | `5b0b1b6a136f5e65` |
| `tourism_satellite_account/tourism_2024.xlsx` | 0.654 | `eac7cea293cfb2bb` |
| `domestic_tourism_annual/tourism_domestic_2023.xlsx` | 0.053 | `c24245c79011f50c` |
| `domestic_tourism_annual/tourism_domestic_2024.xlsx` | 0.083 | `67e2aac05c5dc06d` |
| `domestic_tourism_annual/tourism_domestic_2025.xlsx` | 0.057 | `c9fe28d1c516e58e` |
| `domestic_tourism_quarterly/tourism_domestic_2024-q4.xlsx` | 0.068 | `9e1be4d57e401f1a` ⚠️ duplicate |
| `domestic_tourism_quarterly/tourism_domestic_2025-q1.xlsx` | 0.068 | `9e1be4d57e401f1a` ⚠️ duplicate |
| `domestic_tourism_quarterly/tourism_domestic_2025-q2.xlsx` | 0.068 | `9e1be4d57e401f1a` ⚠️ duplicate |
| `domestic_tourism_quarterly/tourism_domestic_2025-q4.xlsx` | 0.453 | `2fbbadeb68da07a7` |
| `domestic_tourism_quarterly/tourism_domestic_2026-q1.xlsx` | 0.453 | `7d57af9086293849` |
| `domestic_tourism_by_state/tourism_domestic_2022_johor.xlsx` | 0.386 | `05198b5844763716` |
| `domestic_tourism_by_state/tourism_domestic_2022_kedah.xlsx` | 0.386 | `4882dea919ff21d8` |
| `domestic_tourism_by_state/tourism_domestic_2022_kelantan.xlsx` | 0.386 | `b8c65f7c83ccd30f` |
| `domestic_tourism_by_state/tourism_domestic_2022_melaka.xlsx` | 0.386 | `beb3553ed17a8e75` |
| `domestic_tourism_by_state/tourism_domestic_2022_pahang.xlsx` | 0.382 | `5bf17ae8db0d5bb7` |
| `domestic_tourism_by_state/tourism_domestic_2022_negerisembilan.xlsx` | 0.382 | `63f125d506a626a8` |
| `domestic_tourism_by_state/tourism_domestic_2022_pulaupinang.xlsx` | 0.510 | `f3721c6920d978bd` |
| `domestic_tourism_by_state/tourism_domestic_2022_perak.xlsx` | 0.510 | `b4506da84046123d` |
| `domestic_tourism_by_state/tourism_domestic_2022_perlis.xlsx` | 0.510 | `12ce4a20f04a9c01` |
| `domestic_tourism_by_state/tourism_domestic_2022_terengganu.xlsx` | 0.510 | `0010969abc07ae31` |
| `domestic_tourism_by_state/tourism_domestic_2022_sabah.xlsx` | 0.510 | `b62b5d52d43ed10c` |
| `domestic_tourism_by_state/tourism_domestic_2022_sarawak.xlsx` | 0.510 | `1cbd1d32ba62e69b` |
| `domestic_tourism_by_state/tourism_domestic_2022_wpkualalumpur.xlsx` | 0.510 | `b14626342eb3cd72` |
| `domestic_tourism_by_state/tourism_domestic_2022_wplabuan.xlsx` | 0.510 | `4c871161ae376d3c` |
| `domestic_tourism_by_state/tourism_domestic_2022_wpputrajaya.xlsx` | 0.510 | `4b13de878ec082a2` |
| `domestic_tourism_by_state/tourism_domestic_2023_johor.xlsx` | 0.381 | `81631136111471db` |
| `domestic_tourism_by_state/tourism_domestic_2023_kedah.xlsx` | 0.381 | `c7a89b0a314e73f5` |
| `domestic_tourism_by_state/tourism_domestic_2023_kelantan.xlsx` | 0.381 | `9827f7014aa01092` |
| `domestic_tourism_by_state/tourism_domestic_2023_melaka.xlsx` | 0.381 | `1df9b2af25724ba5` |
| `domestic_tourism_by_state/tourism_domestic_2023_pahang.xlsx` | 0.381 | `feb28bc41cb0cfaf` |
| `domestic_tourism_by_state/tourism_domestic_2023_negerisembilan.xlsx` | 0.381 | `052d91c8303248f6` |
| `domestic_tourism_by_state/tourism_domestic_2023_pulaupinang.xlsx` | 0.381 | `fdcbdb484d4e3427` |
| `domestic_tourism_by_state/tourism_domestic_2023_perak.xlsx` | 0.382 | `e526e377077943ea` |
| `domestic_tourism_by_state/tourism_domestic_2023_perlis.xlsx` | 0.381 | `cf972dbe3bb5f793` |
| `domestic_tourism_by_state/tourism_domestic_2023_selangor.xlsx` | 0.381 | `61fe9d133e354b8e` |
| `domestic_tourism_by_state/tourism_domestic_2023_terengganu.xlsx` | 0.381 | `a44e11285f0a34de` |
| `domestic_tourism_by_state/tourism_domestic_2023_sabah.xlsx` | 0.381 | `6ed793ceaf56def3` |
| `domestic_tourism_by_state/tourism_domestic_2023_sarawak.xlsx` | 0.381 | `5f4fb809cc51408e` |
| `domestic_tourism_by_state/tourism_domestic_2023_wpkualalumpur.xlsx` | 0.381 | `d6e5e86d63088ee4` |
| `domestic_tourism_by_state/tourism_domestic_2023_wplabuan.xlsx` | 0.381 | `40021d44a9607cd7` |
| `domestic_tourism_by_state/tourism_domestic_2023_wpputrajaya.xlsx` | 0.381 | `671708bdf7aa5bfd` |
| `cpi_state/cpi_2d_state.csv` | 1.335 | `7f7f17c3f84f7c3e` |
| `cpi_state/mcoicop.csv` | 0.028 | `3b2b9fa17cb50df5` |
| `population_state/population_state.csv` | 12.568 | `a3ac1a8831a4e66d` |
| `gdp_state/gdp_state_real_supply.csv` | 0.080 | `0478e221408f5061` |
| `gdp_state/gdp_lookup.csv` | 0.013 | `ca3ba2dcbe5eb455` |
| `labour_force_state/lfs_qtr_state.csv` | 0.030 | `75e015ca77c1efd8` |
| `water_consumption_state/water_consumption.csv` | 0.021 | `729134dcae597746` |
| `arrivals_state_of_entry/arrivals_soe.csv` | 2.791 | `2fe08e05c0249154` |
