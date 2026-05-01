#!/usr/bin/env python3
"""L01 — Load FRED data

Fetches quarterly US macro data from FRED API:
- GDPC1: Real GDP
- CPIAUCSL: CPI (monthly, aggregated to quarterly)
- UNRATE: Unemployment rate (monthly, aggregated)
- FEDFUNDS: Fed Funds rate (monthly, aggregated)
- GCEC1: Real government consumption

Output: data/raw-data/fred_quarterly.csv
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime

try:
    import pandas as pd
    import requests
except ImportError as e:
    print(f"L01: Missing required package: {e}")
    sys.exit(1)


PROJECT_ROOT = Path(__file__).parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw-data"
LOG_PATH = PROJECT_ROOT / "logs" / "setup" / "L01_load.log"

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"

# Series to load: (FRED_id, target_name, source_freq, target_freq)
SERIES = [
    ("GDPC1", "real_gdp", "Q", "Q"),
    ("CPIAUCSL", "cpi", "M", "Q"),
    ("UNRATE", "unrate", "M", "Q"),
    ("FEDFUNDS", "fedfunds", "M", "Q"),
    ("GCEC1", "real_govt_consumption", "Q", "Q"),
]

START_DATE = "1990-01-01"
END_DATE = "2025-12-31"


def fetch_series(series_id: str, api_key: str) -> pd.DataFrame:
    """Fetch a single FRED series."""
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": START_DATE,
        "observation_end": END_DATE,
    }
    response = requests.get(FRED_BASE, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data["observations"])
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df[["date", "value"]].rename(columns={"value": series_id})


def aggregate_to_quarterly(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    """Average monthly values to quarterly."""
    df = df.set_index("date")
    quarterly = df[value_col].resample("Q").mean().reset_index()
    return quarterly


def main():
    print("L01: Load FRED quarterly data")

    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        print("  ERROR: FRED_API_KEY not set in environment")
        print("  Get a key at: https://fred.stlouisfed.org/docs/api/api_key.html")
        return {"status": "FAILED", "reason": "missing_api_key"}

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Load and merge all series
    all_data = None
    log_entries = []

    for series_id, target_name, source_freq, target_freq in SERIES:
        try:
            print(f"  Fetching {series_id} ({target_name})...", end=" ", flush=True)
            df = fetch_series(series_id, api_key)

            if source_freq == "M" and target_freq == "Q":
                df = aggregate_to_quarterly(df, series_id)

            df = df.rename(columns={series_id: target_name})

            if all_data is None:
                all_data = df
            else:
                all_data = all_data.merge(df, on="date", how="outer")

            print(f"OK ({len(df)} obs)")
            log_entries.append({
                "series_id": series_id,
                "target_name": target_name,
                "obs_count": len(df),
                "status": "SUCCESS",
            })
        except Exception as e:
            print(f"FAIL: {e}")
            log_entries.append({
                "series_id": series_id,
                "target_name": target_name,
                "status": "FAILED",
                "error": str(e),
            })

    # Sort and write
    if all_data is not None:
        all_data = all_data.sort_values("date").reset_index(drop=True)
        out_path = RAW_DATA_DIR / "fred_quarterly.csv"
        all_data.to_csv(out_path, index=False)
        print(f"  Wrote {out_path.name} ({len(all_data)} rows, {len(all_data.columns) - 1} series)")

    # Write log
    with open(LOG_PATH, "w") as f:
        json.dump({
            "run_date": datetime.now().isoformat(),
            "series_loaded": log_entries,
            "output_file": str(out_path.relative_to(PROJECT_ROOT)) if all_data is not None else None,
        }, f, indent=2)

    print("L01: Load complete")
    return {"status": "SUCCESS", "phase": "L", "script": "L01"}


if __name__ == "__main__":
    main()
