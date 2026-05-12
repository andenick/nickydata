# NickyData — For Claude Code Reviewers

## What This Is

NickyData is a language-agnostic pipeline architecture for empirical research projects. The agent constructs the analysis; the final pipeline runs as plain Python (or R) without any agent in the loop.

**Key insight**: 8-phase script naming (S##/L##/P##/V##/M##/A##/O##/E##) makes the pipeline self-documenting. Anyone reading the file system can reconstruct the dependency graph.

## Quick Orientation

The interesting parts:

- **`studies/sfc_vs_dsge/`** — Complete working study. Clone, install requirements, run `python run.py`, get a real empirical comparison of SFC and DSGE models on US fiscal data.
- **`nickydata/scaffold.py`** — `nickydata init` command. Generates the 8-phase folder structure for a new project.
- **`nickydata/orchestrator.py`** — Auto-discovers XX## scripts and runs them in phase order.

## Try It

### Run the reference study

```bash
cd studies/sfc_vs_dsge
pip install -r requirements.txt
python run.py --dry-run    # See the plan
python run.py              # Full pipeline (~3-5 minutes with FRED API key)
```

### Initialize a new project

```bash
pip install -e .
nickydata init my_project --language python
cd my_project
python run.py
```

## Why This Matters

Three patterns that map directly to AI safety concerns:

1. **Phase-gated execution** — Agent cannot skip validation. Analogous to constraining agent action sequences.
2. **Single source of truth** — `project_registry.json` makes scope changes visible and auditable.
3. **Manual adjustments are explicit** — M## scripts with DECISION_LOG.md entries; nothing hidden.

This is essentially MCP principles applied to research workflow: secure data routing (data/user-inputs/ is read-only), tool authorization (phase-gating), and audit trail (LOAD_LOG.json + PROCESS_LOG.json).

## Context

One of four repositories demonstrating AI-driven economic research:
1. **[hdarp](https://github.com/andenick/hdarp)** — Input layer
2. **[anu-data-framework](https://github.com/andenick/anu-data-framework)** — Protocol layer
3. **nickydata** (this repo) — Reproducibility layer
4. **[capitalism-data](https://github.com/andenick/capitalism-data)** — Demonstration at scale
