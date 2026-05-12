# NickyData — Reproducible Research Pipeline Architecture

**A language-agnostic 8-phase pipeline architecture for empirical research projects. Designed so AI agents construct the analysis but the final pipeline runs without any agent in the loop.**

---

## Quick Start

```bash
git clone https://github.com/andenick/nickydata.git
cd nickydata
pip install -e .

# Run the reference study (SFC vs DSGE models on US fiscal data)
cd studies/sfc_vs_dsge
pip install -r requirements.txt
python run.py --dry-run    # See the plan
python run.py              # Full pipeline (~3-5 minutes with FRED API key)
```

---

## What NickyData Solves

When an AI agent helps you build an empirical research project — panel econometrics, time-series analysis, dissertation work — three things break down:

1. **The pipeline becomes opaque**: Scripts proliferate, dependencies are implicit, and only the agent knows how it all fits together.
2. **Reviewers can't reproduce the work**: A reviewer gets a folder full of code and has no idea which script runs first.
3. **Manual adjustments get baked in**: When the agent had to "tweak" a number, that tweak is now invisible in the codebase.

NickyData solves these by enforcing an **8-phase pipeline structure** where every script's role is encoded in its name (S##, L##, P##, V##, M##, A##, O##, E##), every decision is logged, and the entire pipeline runs from a single `run.py` orchestrator.

**Zip the folder, hand it to a reviewer, they run `python run.py`, they get your results.**

---

## The 8 Phases

| Prefix | Phase | Purpose | Reads From | Writes To |
|--------|-------|---------|-----------|-----------|
| **S##** | Setup | Package installation, API keys, environment validation | (system) | `logs/setup/` |
| **L##** | Load | Acquire raw data from files and APIs (with caching, vintage tracking) | `data/user-inputs/` + APIs | `data/raw-data/` |
| **P##** | Process | Clean, transform, merge, construct analysis-ready datasets | `data/raw-data/` | `data/int-data/` + `data/final-data/` |
| **V##** | Validate | Data integrity, completeness, distributions, model diagnostics | `data/final-data/` | `logs/validation/` |
| **M##** | Manual Adjust | Documented manual corrections (never modify final-data, write to adjusted-final-data) | `data/final-data/` | `data/adjusted-final-data/` |
| **A##** | Analyze | Econometric estimation, robustness, cross-model comparison | `data/final-data/` | `outputs/analysis/` |
| **O##** | Output | Publication-quality tables, figures, reports (runs LAST) | `outputs/analysis/` | `outputs/deliverables/` |
| **E##** | Explore | Exploratory scripts (outputs ephemeral, scripts never deleted) | Any | `data/scratch/` |

### Running Order

```
S## → L## → P## (+ E## concurrent) → V## → M## → A## → V## (diagnostics) → O##
```

- **S##** runs first to ensure environment is ready
- **L##** loads all raw data
- **P##** processes data; **E##** exploration can run concurrently after L## completes
- **V##** validates the processed data (data quality)
- **M##** applies any justified manual adjustments
- **A##** runs all analysis (estimation, robustness, comparison)
- **V##** runs again for model diagnostics (Sargan, AR tests, Hausman, etc.)
- **O##** runs **LAST** — generates final outputs after everything else

---

## Core Principles

1. **Containment**: Everything in one folder. Zip it, hand it to a reviewer.
2. **Chronological Legibility**: Numbered scripts run in defined order. Anyone can reconstruct the pipeline.
3. **Separation of Concerns**: Raw data is never modified. Manual adjustments are clearly delineated from programmatic processing.
4. **Reproducibility Without Agents**: The entire pipeline runs via `python run.py` (or `Rscript run.R`) without AI intervention.
5. **Audit Trail**: Every transformation, parameter choice, and model run is logged in structured JSON.
6. **Exploration Preservation**: Exploratory work feeds `data/scratch/` (ephemeral); conclusions go to `DECISION_LOG.md`. E## scripts are never deleted.

---

## Quick Start

### Install

```bash
pip install nickydata
```

### Initialize a New Project

```bash
nickydata init my_research_project --language python
cd my_research_project
```

This generates:

```
my_research_project/
├── project_registry.json    # Study definitions, dataset mappings
├── CHECKLIST.md             # Pre/post-analysis verification
├── DECISION_LOG.md          # Research decisions with rationale
├── run.py                   # Master orchestrator
├── data/
│   ├── user-inputs/         # Read-only originals
│   ├── raw-data/            # L## output
│   ├── int-data/            # P## intermediate
│   ├── final-data/          # P## final
│   ├── adjusted-final-data/ # M## output
│   └── scratch/             # E## ephemeral
├── scripts/
│   ├── S01_setup.py
│   ├── L01_load_template.py
│   ├── P01_process_template.py
│   ├── V01_validate_template.py
│   └── ...
├── outputs/
│   ├── analysis/
│   └── deliverables/
└── logs/
    ├── setup/
    └── validation/
```

### Run the Pipeline

```bash
python run.py                 # Full pipeline
python run.py --from A        # From analysis phase only
python run.py --dry-run       # Show plan without executing
python run.py --phases S,L,P  # Specific phases only
```

---

## Reference Implementation: SFC vs DSGE

This repository includes a complete working empirical study comparing Stock-Flow Consistent and DSGE models on US fiscal policy transmission.

### Study Overview

**Question**: How do SFC and DSGE models differ in their predictions of fiscal policy multipliers using US quarterly data 1990-2025?

**Path**: `studies/sfc_vs_dsge/`

**Pipeline**:
- **S01** Environment setup (Python, R, packages, API keys)
- **L01** Load FRED data (GDP, CPI, unemployment, fed funds, govt spending)
- **L02** Load BEA NIPA (sectoral balances, fiscal data)
- **P01** Construct analysis panel (transformations, lags, normalization)
- **V01** Data validation (completeness, stationarity, outliers)
- **A01** SFC estimation (sectoral balance equations)
- **A02** DSGE estimation (New Keynesian benchmark)
- **A03** Cross-tradition comparison (impulse responses, BMA weights)
- **V02** Model diagnostics (residual tests, parameter stability)
- **O01** Result tables (LaTeX/CSV)
- **O02** Comparison figures (matplotlib)

To run:

```bash
cd studies/sfc_vs_dsge
pip install -r requirements.txt
python run.py
```

Outputs land in `studies/sfc_vs_dsge/outputs/deliverables/`.

---

## Why This Matters for AI Safety

NickyData implements three patterns that generalize to safe AI deployment:

### 1. Phase-Gated Execution
The pipeline cannot skip from L## to A## — it must pass through P## and V##. This is analogous to constraining agent action sequences: the agent cannot fetch data and immediately deploy a model; it must validate first.

### 2. Single Source of Truth
`project_registry.json` defines every study, every dataset, every parameter. The agent cannot silently change scope mid-pipeline — modifications to the registry are tracked changes.

### 3. Manual Adjustments Are Auditable
When automated processing can't fully replicate something, the adjustment is an explicit M## script with full justification in DECISION_LOG.md. The pattern: agent makes the adjustment, human reviews the decision log, the codebase is auditable forever after.

### Comparison to MCP Principles

NickyData implements the same principles Anthropic champions in Model Context Protocol:

| MCP Principle | NickyData Implementation |
|---------------|--------------------------|
| Secure data routing | data/user-inputs/ is read-only during pipeline execution |
| Tool authorization | Phase-gated execution prevents out-of-order tool use |
| Audit trail | LOAD_LOG.json, PROCESS_LOG.json record every operation |
| Constrained agent behavior | Agent writes scripts, but cannot execute outside the pipeline |

---

## Relationship to Anu Suite

NickyData and the [Anu Suite](https://github.com/andenick/anu-suite) are complementary:

| | Anu Replicator | NickyData |
|---|---|---|
| **Purpose** | Replicate published data series | Original empirical research |
| **Phases** | L## + P## (2 phases) | S## + L## + P## + V## + M## + A## + O## + E## (8 phases) |
| **Central config** | `series_registry.json` | `project_registry.json` |
| **Language** | Python only | Any (R, Python, Stata, mixed) |
| **Validation** | Reference value checks inside P## | Dedicated V## phase |
| **Analysis** | Not applicable (replication only) | Full econometric estimation, robustness |

A project can use **both**: Anu Replicator for replicating published series, NickyData for original analysis on top of those series.

---

## Repository Structure

```
nickydata/
├── README.md
├── CLAUDE.md                # Reviewer quick-start
├── LICENSE                  # MIT
├── requirements.txt
├── nickydata/               # Python package
│   ├── __init__.py
│   ├── scaffold.py          # `nickydata init` command
│   ├── registry.py          # project_registry.json management
│   ├── orchestrator.py      # run.py generator and executor
│   └── validators.py        # Checklist validation
├── templates/
│   ├── project_registry_template.json
│   ├── CHECKLIST_template.md
│   ├── DECISION_LOG_template.md
│   ├── S_script_template.py
│   ├── L_script_template.py
│   ├── P_script_template.py
│   ├── V_script_template.py
│   └── A_script_template.py
├── studies/
│   └── sfc_vs_dsge/         # Complete working study
└── docs/
    ├── ARCHITECTURE.md
    └── ANU_COMPARISON.md
```

---

## Portfolio Context

One of four repositories demonstrating an integrated system for AI-driven economic research:

1. **[hdarp](https://github.com/andenick/hdarp)** — Input layer: multi-engine OCR consensus
2. **[anu-suite](https://github.com/andenick/anu-suite)** — Protocol layer: agent-driven data construction
3. **nickydata** (this repo) — Reproducibility layer: language-agnostic pipeline
4. **[capitalism-data](https://github.com/andenick/capitalism-data)** — Demonstration: 235 years of economic data

---

## License

MIT
