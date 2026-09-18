"""Phase 1 - download raw datasets into ml/data/raw/ (write-once).

Every URL below was copied from the download / resource link rendered on the
OpenDOSM data-catalogue or publication page listed beside it in
ml/data/raw/SOURCES.md. None of them were constructed or guessed.

Rules this script enforces:
- A file that already exists in data/raw/ is NEVER overwritten or modified.
  Delete it by hand if you really want a fresh copy.
- Downloads stream to a ``.part`` file and are renamed only once complete, so an
  interrupted run never leaves a truncated file that looks finished.
- Any file larger than 200 MB is refused.

Usage (from the ml/ folder):
    python src/download.py
"""
from __future__ import annotations

import hashlib
import sys
import urllib.error
import urllib.request
from pathlib import Path

ML_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ML_DIR / "data" / "raw"

MAX_BYTES = 200 * 1024 * 1024
TIMEOUT_S = 120
CHUNK = 1 << 16
USER_AGENT = "Mozilla/5.0 (DOSM Datathon 2026 - Data & AI track)"

STATES = [
    "johor", "kedah", "kelantan", "melaka", "pahang", "negerisembilan",
    "pulaupinang", "perak", "perlis", "selangor", "terengganu", "sabah",
    "sarawak", "wpkualalumpur", "wplabuan", "wpputrajaya",
]

# (sub-folder under data/raw, file URL)
SOURCES: list[tuple[str, str]] = []

# D1 - Tourism Satellite Account, annual editions 2010-2024
#      https://open.dosm.gov.my/publications/tourism_<year>
SOURCES += [
    ("tourism_satellite_account", f"https://storage.dosm.gov.my/tourism/tourism_{year}.xlsx")
    for year in range(2010, 2025)
]

# D2 - Domestic Tourism, annual editions 2023-2025
#      https://open.dosm.gov.my/publications/tourism_domestic_annual_<year>
SOURCES += [
    ("domestic_tourism_annual", f"https://storage.dosm.gov.my/tourism/tourism_domestic_{year}.xlsx")
    for year in (2023, 2024, 2025)
]

# D3 - Domestic Tourism, quarterly editions that publish an Excel resource.
#      https://open.dosm.gov.my/publications/tourism_domestic_<quarter>
#      (4Q 2023 - 3Q 2024 are PDF-only; 3Q 2025 is not listed on OpenDOSM.)
SOURCES += [
    ("domestic_tourism_quarterly", f"https://storage.dosm.gov.my/tourism/tourism_domestic_{q}.xlsx")
    for q in ("2024-q4", "2025-q1", "2025-q2", "2025-q4", "2026-q1")
]

# D4 - Domestic Tourism by State, 2022 and 2023 editions
#      https://open.dosm.gov.my/publications/tourism_domestic_state_<year>
#      The 2022 Selangor link on the publication page returns HTTP 404
#      (checked 2026-09-13), so it is excluded rather than substituted.
SOURCES += [
    ("domestic_tourism_by_state", f"https://storage.dosm.gov.my/tourism/tourism_domestic_{year}_{state}.xlsx")
    for year in (2022, 2023)
    for state in STATES
    if not (year == 2022 and state == "selangor")
]

# D5-D9 - OpenDOSM data catalogue tables, plus the two lookup tables needed to
#         decode their category codes.
#         https://open.dosm.gov.my/data-catalogue/<id>
SOURCES += [
    ("cpi_state", "https://storage.dosm.gov.my/cpi/cpi_2d_state.csv"),
    ("cpi_state", "https://storage.dosm.gov.my/dictionaries/mcoicop.csv"),
    ("population_state", "https://storage.dosm.gov.my/population/population_state.csv"),
    ("gdp_state", "https://storage.dosm.gov.my/gdp/gdp_state_real_supply.csv"),
    ("gdp_state", "https://storage.dosm.gov.my/gdp/gdp_lookup.csv"),
    ("labour_force_state", "https://storage.dosm.gov.my/labour/lfs_qtr_state.csv"),
    ("water_consumption_state", "https://storage.data.gov.my/water/water_consumption.csv"),
]

# D10 - Monthly foreign arrivals by state of entry, from the data.gov.my catalogue
#       (https://data.gov.my/data-catalogue/arrivals_soe), source: Imigresen.
#       Outside OpenDOSM; approved separately on 2026-09-16. It records the point of
#       ENTRY, which the catalogue notes may not be the visitor's final destination,
#       so it is kept out of the state-year analysis panel.
SOURCES += [
    ("arrivals_state_of_entry", "https://storage.data.gov.my/demography/arrivals_soe.csv"),
]


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(CHUNK), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch(url: str, dest: Path) -> tuple[str, int]:
    """Download ``url`` to ``dest``. Returns (status, size_in_bytes)."""
    if dest.exists():
        return "exists", dest.stat().st_size

    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
        declared = int(response.headers.get("Content-Length") or 0)
        if declared > MAX_BYTES:
            raise ValueError(f"refused: declared size {declared} bytes exceeds 200 MB")
        written = 0
        with part.open("wb") as out:
            while chunk := response.read(CHUNK):
                written += len(chunk)
                if written > MAX_BYTES:
                    raise ValueError("refused: stream exceeded 200 MB")
                out.write(chunk)
    if declared and written != declared:
        part.unlink(missing_ok=True)
        raise ValueError(f"truncated: got {written} of {declared} bytes")
    part.rename(dest)
    return "downloaded", written


def main() -> int:
    failures: list[tuple[str, str]] = []
    total = 0
    for folder, url in SOURCES:
        dest = RAW_DIR / folder / url.rsplit("/", 1)[-1]
        rel = dest.relative_to(ML_DIR).as_posix()
        try:
            status, size = fetch(url, dest)
        except (urllib.error.URLError, ValueError, OSError) as exc:
            failures.append((url, str(exc)))
            print(f"FAILED      {rel}  <- {url}  ({exc})")
            continue
        total += size
        print(f"{status:<11} {size / 1e6:8.3f} MB  {sha256_of(dest)[:16]}  {rel}")

    print(f"\n{len(SOURCES) - len(failures)}/{len(SOURCES)} files present, {total / 1e6:.2f} MB")
    if failures:
        print(f"{len(failures)} failure(s):")
        for url, reason in failures:
            print(f"  {url}: {reason}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
