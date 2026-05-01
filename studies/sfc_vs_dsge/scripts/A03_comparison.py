#!/usr/bin/env python3
"""A03 — Cross-Model Comparison

Compares fiscal multiplier estimates from SFC and DSGE models.
Computes Bayesian Model Averaging weights based on in-sample fit.

Inputs: outputs/analysis/A01_sfc_results.json, A02_dsge_results.json
Output: outputs/analysis/A03_comparison.json
"""
import json
import sys
from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path(__file__).parent.parent
ANALYSIS_DIR = PROJECT_ROOT / "outputs" / "analysis"


def main():
    print("A03: Cross-model comparison")

    sfc_path = ANALYSIS_DIR / "A01_sfc_results.json"
    dsge_path = ANALYSIS_DIR / "A02_dsge_results.json"

    if not sfc_path.exists() or not dsge_path.exists():
        print("  ERROR: A01 or A02 results not found")
        return {"status": "FAILED"}

    with open(sfc_path) as f:
        sfc = json.load(f)
    with open(dsge_path) as f:
        dsge = json.load(f)

    sfc_mult = sfc["results"].get("fiscal_multiplier", {})
    dsge_mult = dsge["results"].get("fiscal_multiplier", {})

    comparison = {
        "fiscal_multiplier_comparison": {
            "impact": {
                "sfc": sfc_mult.get("impact"),
                "dsge": dsge_mult.get("impact"),
                "difference": (
                    sfc_mult.get("impact", 0) - dsge_mult.get("impact", 0)
                ),
            },
            "4q_cumulative": {
                "sfc": sfc_mult.get("4q_cumulative"),
                "dsge": dsge_mult.get("4q_cumulative"),
                "difference": (
                    sfc_mult.get("4q_cumulative", 0) - dsge_mult.get("4q_cumulative", 0)
                ),
            },
            "8q_cumulative": {
                "sfc": sfc_mult.get("8q_cumulative"),
                "dsge": dsge_mult.get("8q_cumulative"),
                "difference": (
                    sfc_mult.get("8q_cumulative", 0) - dsge_mult.get("8q_cumulative", 0)
                ),
            },
        }
    }

    # BMA weights based on R-squared (simplified)
    sfc_r2 = sfc["results"].get("gdp_govt_equation", {}).get("rsquared", 0)
    dsge_r2 = dsge["results"].get("is_curve", {}).get("rsquared", 0)
    total_r2 = sfc_r2 + dsge_r2
    if total_r2 > 0:
        comparison["bma_weights"] = {
            "sfc_weight": sfc_r2 / total_r2,
            "dsge_weight": dsge_r2 / total_r2,
            "method": "R-squared normalization (simplified, not full BMA)",
        }

        # BMA-averaged multiplier
        if sfc_mult and dsge_mult:
            w_sfc = sfc_r2 / total_r2
            w_dsge = dsge_r2 / total_r2
            comparison["bma_averaged_multiplier"] = {
                "impact": w_sfc * sfc_mult.get("impact", 0) + w_dsge * dsge_mult.get("impact", 0),
                "4q": w_sfc * sfc_mult.get("4q_cumulative", 0) + w_dsge * dsge_mult.get("4q_cumulative", 0),
                "8q": w_sfc * sfc_mult.get("8q_cumulative", 0) + w_dsge * dsge_mult.get("8q_cumulative", 0),
            }

    print("  Fiscal multiplier comparison:")
    print(f"    Impact:    SFC {sfc_mult.get('impact', 0):.3f} vs DSGE {dsge_mult.get('impact', 0):.3f}")
    print(f"    4-quarter: SFC {sfc_mult.get('4q_cumulative', 0):.3f} vs DSGE {dsge_mult.get('4q_cumulative', 0):.3f}")
    print(f"    8-quarter: SFC {sfc_mult.get('8q_cumulative', 0):.3f} vs DSGE {dsge_mult.get('8q_cumulative', 0):.3f}")

    out_path = ANALYSIS_DIR / "A03_comparison.json"
    with open(out_path, "w") as f:
        json.dump({
            "run_date": datetime.now().isoformat(),
            "comparison": comparison,
        }, f, indent=2)
    print(f"  Wrote {out_path.name}")
    print("A03: Comparison complete")
    return {"status": "SUCCESS", "phase": "A", "script": "A03"}


if __name__ == "__main__":
    main()
