# SFC vs DSGE — Decision Log

## DEC-001: Reduced-form representation
**Date**: 2026-04-26
**Phase**: A##
**Decision**: Use reduced-form OLS estimation rather than full Bayesian structural estimation
**Rationale**: This is a reference implementation demonstrating the NickyData pipeline pattern. Full Bayesian structural estimation would require substantial additional code (priors, MCMC, identification analysis) that obscures the pipeline architecture. Reduced-form captures key transmission channels and produces interpretable multiplier estimates.
**Alternatives considered**: PyMC Bayesian structural estimation, dynare-py, manual MCMC
**Reference**: Smets & Wouters (2007); Godley & Lavoie (2007); the focus here is the pipeline, not the model

## DEC-002: Sample period 1990-2025
**Date**: 2026-04-26
**Phase**: L##
**Decision**: Restrict sample to 1990-2025 quarterly
**Rationale**: Pre-1990 quarterly data has measurement breaks (CPI methodology changes, NIPA revisions). Post-1990 sample is consistent across all key series and includes meaningful fiscal policy variation (1990-91 recession, GFC, COVID).
**Alternatives considered**: 1947-2025 (full FRED history, with measurement caveats); 2000-2025 (cleaner but smaller sample)
**Reference**: Standard choice in fiscal multiplier literature

## DEC-003: BEA NIPA via FRED proxy
**Date**: 2026-04-26
**Phase**: L##
**Decision**: Use FRED-derived government consumption series (GCEC1) rather than direct BEA NIPA tables
**Rationale**: For the reference implementation, FRED's GCEC1 is sufficient and avoids BEA's CSV download format (which requires additional parsing). A production implementation would use direct BEA NIPA CSV downloads for full sectoral decomposition (3.1 receipts/expenditures, 3.9.5 by function).
**Alternatives considered**: Direct BEA NIPA CSV parsing
**Reference**: FRED documentation for GCEC1; BEA NIPA Table 3.1

## DEC-004: HP filter for output gap
**Date**: 2026-04-26
**Phase**: P##
**Decision**: Use HP filter (lambda=1600) for output gap construction
**Rationale**: Standard practice for quarterly data. Output gap is needed for DSGE Phillips curve and Taylor rule.
**Alternatives considered**: Linear detrending, CBO output gap series, one-sided HP filter
**Reference**: Hodrick & Prescott (1997); standard quarterly DSGE preprocessing

## DEC-005: BMA weights via R-squared normalization
**Date**: 2026-04-26
**Phase**: A##
**Decision**: Compute BMA-style weights using normalized R-squared rather than full marginal likelihoods
**Rationale**: Full BMA requires marginal likelihood computation which is non-trivial for non-Bayesian estimates. R-squared normalization gives a comparable weighting scheme for the reference implementation.
**Alternatives considered**: Bayes factors, AIC weights, BIC weights
**Reference**: Hoeting et al. (1999) for full BMA; this study uses simplified weighting
