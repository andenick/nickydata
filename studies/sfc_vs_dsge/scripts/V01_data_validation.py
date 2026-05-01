#!/usr/bin/env python3
"""V01 — Data validation

Checks completeness, stationarity, distribution, and outliers in the analysis panel.

Input: data/final-data/analysis_panel.csv
Output: logs/validation/V01_validation.json
"""
import json
import sys
from pathlib import Path
from datetime import datetime

try:
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(f"V01: Missing required package: {e}")
    sys.exit(1)


PROJECT_ROOT = Path(__file__).parent.parent
FINAL_DIR = PROJECT_ROOT / "data" / "final-data"
LOG_DIR = PROJECT_ROOT / "logs" / "validation"


def main():
    print("V01: Data validation")
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    panel_path = FINAL_DIR / "analysis_panel.csv"
    if not panel_path.exists():
        print(f"  ERROR: {panel_path.name} not found. Run P01 first.")
        return {"status": "FAILED"}

    panel = pd.read_csv(panel_path, parse_dates=["date"])
    checks = {}

    # Check 1: Completeness
    print("  V01.1: Completeness")
    expected_quarters = pd.date_range(panel["date"].min(), panel["date"].max(), freq="Q")
    actual_quarters = pd.to_datetime(panel["date"])
    missing = len(expected_quarters) - len(actual_quarters)
    checks["completeness"] = {
        "expected_quarters": len(expected_quarters),
        "actual_quarters": len(actual_quarters),
        "missing": missing,
        "pass": missing == 0,
    }
    print(f"    Expected {len(expected_quarters)}, got {len(actual_quarters)}, missing {missing}: "
          f"{'PASS' if missing == 0 else 'FAIL'}")

    # Check 2: NaN counts per column
    print("  V01.2: NaN counts")
    nan_counts = panel.isna().sum().to_dict()
    high_nan = {k: v for k, v in nan_counts.items() if v > len(panel) * 0.1}
    checks["nan_counts"] = {
        "by_column": nan_counts,
        "high_nan_columns": high_nan,
        "pass": len(high_nan) == 0,
    }
    if high_nan:
        print(f"    WARNING: Columns with >10% NaN: {list(high_nan.keys())}")
    else:
        print(f"    All columns have <10% NaN: PASS")

    # Check 3: Outliers (z-score >3 for growth rates)
    print("  V01.3: Outliers")
    growth_cols = [c for c in panel.columns if c.startswith("d_") or c.startswith("yoy_")]
    outlier_summary = {}
    for col in growth_cols:
        if col in panel.columns:
            series = panel[col].dropna()
            if len(series) > 0:
                z = (series - series.mean()) / series.std()
                n_outliers = int((z.abs() > 3).sum())
                outlier_summary[col] = n_outliers
    checks["outliers"] = {
        "by_column": outlier_summary,
        "total": sum(outlier_summary.values()),
    }
    print(f"    Total outliers (|z|>3) across growth columns: {sum(outlier_summary.values())}")

    # Check 4: Stationarity (ADF test on key series)
    print("  V01.4: Stationarity (ADF)")
    try:
        from statsmodels.tsa.stattools import adfuller
        adf_results = {}
        for col in ["d_real_gdp", "yoy_cpi", "fedfunds"]:
            if col in panel.columns:
                series = panel[col].dropna()
                if len(series) > 20:
                    stat, pval, *_ = adfuller(series, autolag="AIC")
                    adf_results[col] = {
                        "statistic": float(stat),
                        "pvalue": float(pval),
                        "stationary_at_5pct": pval < 0.05,
                    }
        checks["stationarity"] = adf_results
        for col, r in adf_results.items():
            print(f"    {col}: ADF p={r['pvalue']:.4f} "
                  f"({'stationary' if r['stationary_at_5pct'] else 'NON-stationary'})")
    except ImportError:
        print("    WARNING: statsmodels not available")
        checks["stationarity"] = {"skipped": "statsmodels not available"}

    # Overall pass/fail
    all_passed = (
        checks["completeness"]["pass"]
        and checks["nan_counts"]["pass"]
    )

    # Write validation report
    out_path = LOG_DIR / "V01_validation.json"
    with open(out_path, "w") as f:
        json.dump({
            "run_date": datetime.now().isoformat(),
            "panel_file": str(panel_path.relative_to(PROJECT_ROOT)),
            "panel_rows": len(panel),
            "panel_cols": len(panel.columns),
            "checks": checks,
            "overall_pass": all_passed,
        }, f, indent=2)

    print(f"  Validation report: {out_path.name}")
    print(f"  Overall: {'PASS' if all_passed else 'WARNING'}")
    print("V01: Validation complete")

    return {"status": "SUCCESS" if all_passed else "WARNING", "phase": "V", "script": "V01"}


if __name__ == "__main__":
    main()
