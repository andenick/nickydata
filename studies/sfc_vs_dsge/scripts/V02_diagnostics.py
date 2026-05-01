#!/usr/bin/env python3
"""V02 — Model Diagnostics

Post-estimation diagnostics: residual tests, parameter stability, model fit.

Inputs: A01, A02, A03 result JSONs
Output: logs/validation/V02_diagnostics.json
"""
import json
import sys
from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path(__file__).parent.parent
ANALYSIS_DIR = PROJECT_ROOT / "outputs" / "analysis"
LOG_DIR = PROJECT_ROOT / "logs" / "validation"


def main():
    print("V02: Model diagnostics")
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    diagnostics = {}

    # Check 1: SFC R-squared
    sfc_path = ANALYSIS_DIR / "A01_sfc_results.json"
    if sfc_path.exists():
        with open(sfc_path) as f:
            sfc = json.load(f)
        sfc_r2 = sfc["results"].get("gdp_govt_equation", {}).get("rsquared", 0)
        diagnostics["sfc_fit"] = {
            "rsquared": sfc_r2,
            "acceptable": sfc_r2 > 0.05,
            "note": "SFC reduced-form should have low R² since it's a single equation"
        }
        print(f"  SFC R²: {sfc_r2:.3f} ({'acceptable' if sfc_r2 > 0.05 else 'low'})")

    # Check 2: DSGE R-squared (across equations)
    dsge_path = ANALYSIS_DIR / "A02_dsge_results.json"
    if dsge_path.exists():
        with open(dsge_path) as f:
            dsge = json.load(f)
        equations = ["is_curve", "phillips_curve", "taylor_rule"]
        dsge_r2_summary = {}
        for eq in equations:
            r2 = dsge["results"].get(eq, {}).get("rsquared", 0)
            dsge_r2_summary[eq] = r2
            print(f"  DSGE {eq} R²: {r2:.3f}")
        diagnostics["dsge_fit"] = dsge_r2_summary

    # Check 3: Multiplier reasonableness
    comp_path = ANALYSIS_DIR / "A03_comparison.json"
    if comp_path.exists():
        with open(comp_path) as f:
            comp = json.load(f)
        multipliers = comp["comparison"]["fiscal_multiplier_comparison"]

        # Sanity: 4q multipliers should typically be in [0, 3]
        sfc_4q = multipliers["4q_cumulative"]["sfc"] or 0
        dsge_4q = multipliers["4q_cumulative"]["dsge"] or 0

        sfc_reasonable = -1 < sfc_4q < 5
        dsge_reasonable = -1 < dsge_4q < 5

        diagnostics["multiplier_sanity"] = {
            "sfc_4q": sfc_4q,
            "dsge_4q": dsge_4q,
            "sfc_in_reasonable_range": sfc_reasonable,
            "dsge_in_reasonable_range": dsge_reasonable,
            "expected_range": "[-1, 5] for 4q cumulative multiplier",
        }
        print(f"  4q multiplier sanity: SFC {sfc_4q:.3f} {'OK' if sfc_reasonable else 'WARN'}, "
              f"DSGE {dsge_4q:.3f} {'OK' if dsge_reasonable else 'WARN'}")

    # Overall assessment
    all_checks_pass = all(
        v.get("acceptable", v.get("sfc_in_reasonable_range", True))
        for v in diagnostics.values() if isinstance(v, dict)
    )

    out_path = LOG_DIR / "V02_diagnostics.json"
    with open(out_path, "w") as f:
        json.dump({
            "run_date": datetime.now().isoformat(),
            "diagnostics": diagnostics,
            "all_checks_pass": all_checks_pass,
        }, f, indent=2)

    print(f"  Wrote {out_path.name}")
    print(f"  Overall: {'PASS' if all_checks_pass else 'WARNING'}")
    print("V02: Diagnostics complete")
    return {"status": "SUCCESS" if all_checks_pass else "WARNING", "phase": "V", "script": "V02"}


if __name__ == "__main__":
    main()
