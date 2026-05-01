# SFC vs DSGE — Pre/Post-Analysis Checklist

## Pre-Analysis (before running A##)

- [ ] S01 environment setup completed
- [ ] L01 FRED data loaded (verify `data/raw-data/fred_quarterly.csv` exists)
- [ ] L02 BEA NIPA data loaded (verify `data/raw-data/bea_nipa.csv` exists)
- [ ] P01 analysis panel constructed (verify `data/final-data/analysis_panel.csv` exists)
- [ ] V01 data validation passed (or warnings reviewed)
- [ ] DECISION_LOG.md updated with analytical choices
- [ ] project_registry.json reflects current scope

## Pre-Adjustment (before running M##)

This study has no M## scripts. If extended:
- [ ] V01 flagged the issues being adjusted
- [ ] Adjustment justification documented in DECISION_LOG.md
- [ ] Reference for the adjustment exists (paper, methodology, expert input)

## Post-Analysis (after running A##)

- [ ] V02 model diagnostics passed
- [ ] Robustness checks completed (E## scripts)
- [ ] Cross-model comparisons logged (A03 output present)
- [ ] Multipliers in reasonable range ([-1, 5] for 4q cumulative)

## Pre-Output (before running O##)

- [ ] All A## analyses validated
- [ ] All decisions logged
- [ ] No unresolved warnings in logs/validation/
