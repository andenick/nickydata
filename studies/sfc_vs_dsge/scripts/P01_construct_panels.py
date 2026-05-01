#!/usr/bin/env python3
"""P01 — Construct analysis panel

Combines FRED and BEA NIPA data into a single analysis-ready quarterly panel.
Computes log differences, lagged values, and standardized variables.

Inputs: data/raw-data/fred_quarterly.csv, data/raw-data/bea_nipa.csv
Output: data/final-data/analysis_panel.csv
"""
import json
import sys
from pathlib import Path
from datetime import datetime

try:
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(f"P01: Missing required package: {e}")
    sys.exit(1)


PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw-data"
INT_DIR = PROJECT_ROOT / "data" / "int-data"
FINAL_DIR = PROJECT_ROOT / "data" / "final-data"
LOG_PATH = PROJECT_ROOT / "logs" / "validation" / "P01_process.log"


def main():
    print("P01: Construct analysis panel")

    INT_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Load inputs
    fred_path = RAW_DIR / "fred_quarterly.csv"
    nipa_path = RAW_DIR / "bea_nipa.csv"
    if not fred_path.exists():
        print(f"  ERROR: {fred_path.name} not found")
        return {"status": "FAILED"}

    fred = pd.read_csv(fred_path, parse_dates=["date"])
    nipa = pd.read_csv(nipa_path, parse_dates=["date"]) if nipa_path.exists() else None

    print(f"  Loaded fred_quarterly: {len(fred)} rows, {fred.columns.tolist()}")
    if nipa is not None:
        print(f"  Loaded bea_nipa: {len(nipa)} rows")

    # Merge
    panel = fred.copy()
    if nipa is not None:
        keep_cols = [c for c in nipa.columns if c not in fred.columns or c == "date"]
        panel = panel.merge(nipa[keep_cols], on="date", how="left")

    # Transformations
    print("  Computing transformations...")

    # Log levels
    for col in ["real_gdp", "cpi", "real_govt_consumption"]:
        if col in panel.columns:
            panel[f"log_{col}"] = np.log(panel[col])

    # Quarter-over-quarter growth (annualized)
    for col in ["real_gdp", "cpi", "real_govt_consumption"]:
        if f"log_{col}" in panel.columns:
            panel[f"d_{col}"] = panel[f"log_{col}"].diff() * 400

    # Year-over-year growth
    for col in ["real_gdp", "cpi", "real_govt_consumption"]:
        if f"log_{col}" in panel.columns:
            panel[f"yoy_{col}"] = panel[f"log_{col}"].diff(4) * 100

    # Real interest rate
    if "fedfunds" in panel.columns and "yoy_cpi" in panel.columns:
        panel["real_rate"] = panel["fedfunds"] - panel["yoy_cpi"]

    # Output gap (HP filter)
    if "log_real_gdp" in panel.columns:
        try:
            from statsmodels.tsa.filters.hp_filter import hpfilter
            cycle, trend = hpfilter(panel["log_real_gdp"].dropna(), lamb=1600)
            panel["output_gap"] = np.nan
            panel.loc[cycle.index, "output_gap"] = cycle * 100
        except ImportError:
            print("  WARNING: statsmodels not available, skipping HP filter")

    # Drop initial NaN rows from differencing
    panel = panel.dropna(subset=["d_real_gdp"]).reset_index(drop=True)

    # Write final panel
    out_path = FINAL_DIR / "analysis_panel.csv"
    panel.to_csv(out_path, index=False)
    print(f"  Wrote {out_path.name}: {len(panel)} rows, {len(panel.columns)} cols")

    # Log
    with open(LOG_PATH, "w") as f:
        json.dump({
            "run_date": datetime.now().isoformat(),
            "input_files": [str(p.relative_to(PROJECT_ROOT)) for p in [fred_path, nipa_path] if p.exists()],
            "output_file": str(out_path.relative_to(PROJECT_ROOT)),
            "rows": len(panel),
            "columns": list(panel.columns),
            "date_range": [str(panel["date"].min()), str(panel["date"].max())],
        }, f, indent=2)

    print("P01: Process complete")
    return {"status": "SUCCESS", "phase": "P", "script": "P01"}


if __name__ == "__main__":
    main()
