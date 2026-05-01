#!/usr/bin/env python3
"""O02 — Generate comparison figures

Produces matplotlib comparison figures.

Inputs: outputs/analysis/A03_comparison.json, data/final-data/analysis_panel.csv
Outputs: outputs/deliverables/fig_multipliers.png, fig_data_overview.png
"""
import json
import sys
from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path(__file__).parent.parent
ANALYSIS_DIR = PROJECT_ROOT / "outputs" / "analysis"
FINAL_DIR = PROJECT_ROOT / "data" / "final-data"
DELIVERABLES_DIR = PROJECT_ROOT / "outputs" / "deliverables"


def main():
    print("O02: Generate figures")
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import pandas as pd
    except ImportError:
        print("  WARNING: matplotlib or pandas not installed; skipping figures")
        return {"status": "WARNING", "phase": "O", "script": "O02"}

    # Figure 1: Multiplier comparison
    with open(ANALYSIS_DIR / "A03_comparison.json") as f:
        comp = json.load(f)

    mult = comp["comparison"]["fiscal_multiplier_comparison"]
    horizons = ["Impact", "4-quarter", "8-quarter"]
    sfc_vals = [mult["impact"]["sfc"] or 0, mult["4q_cumulative"]["sfc"] or 0,
                mult["8q_cumulative"]["sfc"] or 0]
    dsge_vals = [mult["impact"]["dsge"] or 0, mult["4q_cumulative"]["dsge"] or 0,
                 mult["8q_cumulative"]["dsge"] or 0]

    fig, ax = plt.subplots(figsize=(8, 5))
    x = range(len(horizons))
    width = 0.35
    ax.bar([i - width/2 for i in x], sfc_vals, width, label="SFC", color="#1f77b4")
    ax.bar([i + width/2 for i in x], dsge_vals, width, label="DSGE", color="#ff7f0e")
    ax.set_xticks(x)
    ax.set_xticklabels(horizons)
    ax.set_ylabel("Fiscal Multiplier")
    ax.set_title("Fiscal Multipliers: SFC vs DSGE")
    ax.axhline(y=0, color="black", linewidth=0.5)
    ax.axhline(y=1, color="gray", linestyle="--", linewidth=0.5, label="Multiplier = 1")
    ax.legend()
    ax.grid(True, alpha=0.3)

    fig_path = DELIVERABLES_DIR / "fig_multipliers.png"
    fig.savefig(fig_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Wrote {fig_path.name}")

    # Figure 2: Data overview
    panel_path = FINAL_DIR / "analysis_panel.csv"
    if panel_path.exists():
        panel = pd.read_csv(panel_path, parse_dates=["date"])

        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        for ax, col, title in zip(
            axes.flatten(),
            ["d_real_gdp", "yoy_cpi", "fedfunds", "d_real_govt_consumption"],
            ["Real GDP Growth (annualized)", "CPI Inflation (YoY)",
             "Fed Funds Rate", "Real Govt Consumption Growth"]
        ):
            if col in panel.columns:
                ax.plot(panel["date"], panel[col], linewidth=1, color="#1f77b4")
                ax.set_title(title)
                ax.grid(True, alpha=0.3)
                ax.axhline(y=0, color="black", linewidth=0.3)

        fig.suptitle("US Quarterly Macro Data 1990-2025", fontsize=14)
        fig.tight_layout()

        fig_path2 = DELIVERABLES_DIR / "fig_data_overview.png"
        fig.savefig(fig_path2, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"  Wrote {fig_path2.name}")

    print("O02: Figures complete")
    return {"status": "SUCCESS", "phase": "O", "script": "O02"}


if __name__ == "__main__":
    main()
