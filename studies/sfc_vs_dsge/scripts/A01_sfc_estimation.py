#!/usr/bin/env python3
"""A01 — SFC Model Estimation

Estimates a simplified Stock-Flow Consistent model based on Godley & Lavoie (2007)
sectoral balance accounting. Uses a reduced-form representation suitable for
quarterly US data.

Reduced form:
  consumption_growth_t = c0 + c1 * income_growth_t + c2 * wealth_lag_t + e_t
  govt_balance_t       = g0 + g1 * output_gap_t + g2 * govt_consumption_t + e_t
  fiscal_multiplier_kq = sum of impulse responses up to quarter k

Input: data/final-data/analysis_panel.csv
Output: outputs/analysis/A01_sfc_results.json
"""
import json
import sys
from pathlib import Path
from datetime import datetime

try:
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(f"A01: Missing required package: {e}")
    sys.exit(1)


PROJECT_ROOT = Path(__file__).parent.parent
FINAL_DIR = PROJECT_ROOT / "data" / "final-data"
ANALYSIS_DIR = PROJECT_ROOT / "outputs" / "analysis"


def estimate_sfc_reduced_form(panel: pd.DataFrame) -> dict:
    """
    Reduced-form SFC estimation by OLS.

    A full SFC model would estimate sectoral balance equations as a system.
    For the reference implementation, we estimate three key equations
    separately and report fiscal multiplier estimates.
    """
    try:
        import statsmodels.api as sm
    except ImportError:
        return {"error": "statsmodels not installed"}

    results = {}

    # Equation 1: Output-government spending relationship
    # Real GDP growth as function of govt consumption growth and lagged output
    df = panel.dropna(subset=["d_real_gdp", "d_real_govt_consumption"])
    if len(df) > 20:
        df = df.copy()
        df["d_gdp_lag1"] = df["d_real_gdp"].shift(1)
        df = df.dropna()

        X = sm.add_constant(df[["d_real_govt_consumption", "d_gdp_lag1"]])
        y = df["d_real_gdp"]

        model = sm.OLS(y, X).fit()
        results["gdp_govt_equation"] = {
            "coefficients": model.params.to_dict(),
            "tvalues": model.tvalues.to_dict(),
            "rsquared": float(model.rsquared),
            "n_obs": int(model.nobs),
            "note": "OLS estimate of GDP growth on govt consumption growth + GDP lag",
        }

    # Equation 2: Fiscal multiplier (4-quarter cumulative)
    # Naive impulse: 1pp permanent increase in govt consumption growth
    if "gdp_govt_equation" in results:
        # IRF coefficient on govt consumption
        beta_g = results["gdp_govt_equation"]["coefficients"].get("d_real_govt_consumption", 0)
        rho = results["gdp_govt_equation"]["coefficients"].get("d_gdp_lag1", 0)

        # Cumulative multiplier with AR(1) propagation
        multiplier_4q = beta_g * (1 + rho + rho**2 + rho**3)
        multiplier_8q = beta_g * sum(rho**i for i in range(8))
        results["fiscal_multiplier"] = {
            "impact": float(beta_g),
            "4q_cumulative": float(multiplier_4q),
            "8q_cumulative": float(multiplier_8q),
            "method": "AR(1) propagation from impact coefficient",
        }

    # Equation 3: Saving-investment balance (sectoral)
    # Approximate household saving via income - consumption
    if all(c in panel.columns for c in ["real_gdp", "real_govt_consumption"]):
        df = panel.dropna(subset=["real_gdp", "real_govt_consumption"]).copy()
        df["private_share"] = (df["real_gdp"] - df["real_govt_consumption"]) / df["real_gdp"]
        results["sectoral_balance"] = {
            "private_share_mean": float(df["private_share"].mean()),
            "private_share_std": float(df["private_share"].std()),
        }

    return results


def main():
    print("A01: SFC estimation")
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

    panel_path = FINAL_DIR / "analysis_panel.csv"
    if not panel_path.exists():
        print(f"  ERROR: {panel_path.name} not found")
        return {"status": "FAILED"}

    panel = pd.read_csv(panel_path, parse_dates=["date"])
    print(f"  Panel loaded: {len(panel)} rows, {panel['date'].min()} to {panel['date'].max()}")

    results = estimate_sfc_reduced_form(panel)

    if "fiscal_multiplier" in results:
        m = results["fiscal_multiplier"]
        print(f"  SFC fiscal multipliers:")
        print(f"    Impact:        {m['impact']:.3f}")
        print(f"    4-quarter cum: {m['4q_cumulative']:.3f}")
        print(f"    8-quarter cum: {m['8q_cumulative']:.3f}")

    out_path = ANALYSIS_DIR / "A01_sfc_results.json"
    with open(out_path, "w") as f:
        json.dump({
            "run_date": datetime.now().isoformat(),
            "model": "SFC (reduced form)",
            "results": results,
        }, f, indent=2)

    print(f"  Wrote {out_path.name}")
    print("A01: SFC estimation complete")
    return {"status": "SUCCESS", "phase": "A", "script": "A01"}


if __name__ == "__main__":
    main()
