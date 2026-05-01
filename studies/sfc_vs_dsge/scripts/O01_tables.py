#!/usr/bin/env python3
"""O01 — Generate result tables

Produces LaTeX and CSV tables from A01, A02, A03 results.

Inputs: outputs/analysis/A01_*, A02_*, A03_*
Outputs: outputs/deliverables/table_multipliers.tex, table_multipliers.csv,
         table_coefficients.tex, table_coefficients.csv
"""
import json
import sys
from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path(__file__).parent.parent
ANALYSIS_DIR = PROJECT_ROOT / "outputs" / "analysis"
DELIVERABLES_DIR = PROJECT_ROOT / "outputs" / "deliverables"


def fmt_num(x, digits=3):
    if x is None:
        return "—"
    return f"{x:.{digits}f}"


def main():
    print("O01: Generate result tables")
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)

    # Load results
    with open(ANALYSIS_DIR / "A01_sfc_results.json") as f:
        sfc = json.load(f)
    with open(ANALYSIS_DIR / "A02_dsge_results.json") as f:
        dsge = json.load(f)
    with open(ANALYSIS_DIR / "A03_comparison.json") as f:
        comp = json.load(f)

    sfc_mult = sfc["results"].get("fiscal_multiplier", {})
    dsge_mult = dsge["results"].get("fiscal_multiplier", {})

    # Table: Fiscal Multipliers Comparison (CSV)
    csv_path = DELIVERABLES_DIR / "table_multipliers.csv"
    with open(csv_path, "w") as f:
        f.write("Horizon,SFC,DSGE,Difference\n")
        f.write(f"Impact,{fmt_num(sfc_mult.get('impact'))},{fmt_num(dsge_mult.get('impact'))},"
                f"{fmt_num((sfc_mult.get('impact') or 0) - (dsge_mult.get('impact') or 0))}\n")
        f.write(f"4-quarter cumulative,{fmt_num(sfc_mult.get('4q_cumulative'))},"
                f"{fmt_num(dsge_mult.get('4q_cumulative'))},"
                f"{fmt_num((sfc_mult.get('4q_cumulative') or 0) - (dsge_mult.get('4q_cumulative') or 0))}\n")
        f.write(f"8-quarter cumulative,{fmt_num(sfc_mult.get('8q_cumulative'))},"
                f"{fmt_num(dsge_mult.get('8q_cumulative'))},"
                f"{fmt_num((sfc_mult.get('8q_cumulative') or 0) - (dsge_mult.get('8q_cumulative') or 0))}\n")
    print(f"  Wrote {csv_path.name}")

    # Table: Fiscal Multipliers Comparison (LaTeX)
    tex_path = DELIVERABLES_DIR / "table_multipliers.tex"
    with open(tex_path, "w") as f:
        f.write("\\begin{table}[h]\n")
        f.write("\\centering\n")
        f.write("\\caption{Fiscal Multipliers: SFC vs DSGE}\n")
        f.write("\\begin{tabular}{lccc}\n")
        f.write("\\toprule\n")
        f.write("Horizon & SFC & DSGE & Difference \\\\\n")
        f.write("\\midrule\n")
        f.write(f"Impact & {fmt_num(sfc_mult.get('impact'))} & "
                f"{fmt_num(dsge_mult.get('impact'))} & "
                f"{fmt_num((sfc_mult.get('impact') or 0) - (dsge_mult.get('impact') or 0))} \\\\\n")
        f.write(f"4-quarter & {fmt_num(sfc_mult.get('4q_cumulative'))} & "
                f"{fmt_num(dsge_mult.get('4q_cumulative'))} & "
                f"{fmt_num((sfc_mult.get('4q_cumulative') or 0) - (dsge_mult.get('4q_cumulative') or 0))} \\\\\n")
        f.write(f"8-quarter & {fmt_num(sfc_mult.get('8q_cumulative'))} & "
                f"{fmt_num(dsge_mult.get('8q_cumulative'))} & "
                f"{fmt_num((sfc_mult.get('8q_cumulative') or 0) - (dsge_mult.get('8q_cumulative') or 0))} \\\\\n")
        f.write("\\bottomrule\n")
        f.write("\\end{tabular}\n")
        f.write("\\end{table}\n")
    print(f"  Wrote {tex_path.name}")

    # Table: Coefficients (CSV only, simpler)
    coef_path = DELIVERABLES_DIR / "table_coefficients.csv"
    with open(coef_path, "w") as f:
        f.write("Model,Equation,Coefficient,Estimate,t-statistic\n")

        sfc_eq = sfc["results"].get("gdp_govt_equation", {})
        if sfc_eq:
            for var, val in sfc_eq.get("coefficients", {}).items():
                tval = sfc_eq.get("tvalues", {}).get(var, None)
                f.write(f"SFC,GDP-Govt,{var},{fmt_num(val)},{fmt_num(tval, 2)}\n")

        for eq_name in ["is_curve", "phillips_curve", "taylor_rule"]:
            eq = dsge["results"].get(eq_name, {})
            if eq:
                for var, val in eq.get("coefficients", {}).items():
                    tval = eq.get("tvalues", {}).get(var, None)
                    f.write(f"DSGE,{eq_name},{var},{fmt_num(val)},{fmt_num(tval, 2)}\n")
    print(f"  Wrote {coef_path.name}")

    print("O01: Tables complete")
    return {"status": "SUCCESS", "phase": "O", "script": "O01"}


if __name__ == "__main__":
    main()
