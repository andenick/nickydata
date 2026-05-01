# SFC vs DSGE: Fiscal Policy Transmission

A reference NickyData study comparing Stock-Flow Consistent (SFC) and DSGE
models on US quarterly fiscal data 1990-2025.

**Research question**: How do SFC and DSGE models differ in their predictions
of government spending multipliers?

## Pipeline

| Script | Phase | Purpose |
|--------|-------|---------|
| S01_setup.py | Setup | Validate environment, check API keys |
| L01_load_fred.py | Load | Fetch GDP, CPI, unemployment, fed funds from FRED |
| L02_load_bea.py | Load | Fetch government spending, sectoral balances from BEA |
| P01_construct_panels.py | Process | Build analysis-ready quarterly panel |
| V01_data_validation.py | Validate | Stationarity, completeness, outlier checks |
| A01_sfc_estimation.py | Analyze | SFC sectoral balance estimation |
| A02_dsge_estimation.py | Analyze | DSGE benchmark estimation |
| A03_comparison.py | Analyze | Cross-model fiscal multiplier comparison |
| V02_diagnostics.py | Validate | Residual tests, parameter stability |
| O01_tables.py | Output | LaTeX/CSV results tables |
| O02_figures.py | Output | Comparison figures |

## Run

```bash
pip install -r requirements.txt
export FRED_API_KEY=your_key_here    # Required for L01
python run.py --dry-run              # Show plan
python run.py                        # Full pipeline
```

Outputs land in `outputs/deliverables/`.

## Data Sources

- **FRED**: GDPC1 (real GDP), CPIAUCSL (inflation), UNRATE (unemployment), FEDFUNDS (policy rate), GCEC1 (govt consumption)
- **BEA NIPA**: Government spending decomposition (Tables 3.1, 3.9.5)

All data is public. Set `FRED_API_KEY` (free at https://fred.stlouisfed.org/docs/api/api_key.html). BEA access uses the public NIPA tables CSV downloads (no key required).

## Methodology Notes

The SFC implementation follows Godley & Lavoie (2007) sectoral balance accounting.
The DSGE benchmark uses a small-scale New Keynesian model (Smets-Wouters style).
Both are estimated by Bayesian methods with informative priors documented in
`DECISION_LOG.md`.

This is a **reference implementation** demonstrating the NickyData pipeline pattern,
not a publishable comparison. Real comparison work would require:
- Sensitivity to lag structure
- Robustness across alternative SFC closures
- Out-of-sample fit evaluation
- Identification analysis

These extensions are sketched in E## exploration scripts.
