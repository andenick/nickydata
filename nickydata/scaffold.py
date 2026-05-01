#!/usr/bin/env python3
"""
NickyData Scaffold — Generate 8-phase project structure
=========================================================

Creates a complete NickyData project with all required folders, templates,
and the run.py orchestrator.

Usage:
    nickydata init <project_name> [--language python|R|stata]
    python -m nickydata.scaffold <project_name>
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime


PROJECT_REGISTRY_TEMPLATE = {
    "project_name": "{PROJECT_NAME}",
    "registry_version": "1.0.0",
    "created_date": "{CREATED_DATE}",
    "language": "{LANGUAGE}",
    "studies": {},
    "datasets": {}
}

CHECKLIST_TEMPLATE = """# Pre/Post-Analysis Checklist

## Pre-Analysis (before running A##)

- [ ] All L## scripts completed successfully
- [ ] All P## scripts completed successfully
- [ ] V## data validation passed
- [ ] DECISION_LOG.md updated with analytical choices
- [ ] project_registry.json reflects current scope

## Pre-Adjustment (before running M##)

- [ ] V## flagged the issues being adjusted
- [ ] Adjustment justification documented in DECISION_LOG.md
- [ ] Reference for the adjustment exists (paper, methodology, expert input)

## Post-Analysis (after running A##)

- [ ] V## diagnostics passed (Sargan, AR tests, residual checks)
- [ ] Robustness checks completed
- [ ] Cross-model comparisons logged

## Pre-Output (before running O##)

- [ ] All analyses validated
- [ ] All decisions logged
- [ ] Reference values match expected outputs
- [ ] No unresolved warnings in logs/validation/
"""

DECISION_LOG_TEMPLATE = """# Decision Log

## DEC-001: [Decision Title]
**Date**: {DATE}
**Phase**: [S/L/P/V/M/A/O/E]
**Decision**: [What was decided]
**Rationale**: [Why this decision was made]
**Alternatives considered**: [What else was considered]
**Reference**: [Citation, expert input, or methodology source]

---

(Add new decisions above this line)
"""

RUN_PY_TEMPLATE = '''#!/usr/bin/env python3
"""
{PROJECT_NAME} — Master Orchestrator
{HEADER_LINE}

Auto-discovers and runs scripts in phase order:
  S## -> L## -> P## (+ E## concurrent) -> V## -> M## -> A## -> V## -> O##

Usage:
  python run.py                 # Full pipeline
  python run.py --from A        # From analysis phase only
  python run.py --dry-run       # Show plan without executing
  python run.py --phases S,L,P  # Specific phases only
"""

import sys
from pathlib import Path

# Add nickydata package to path if installed editable
sys.path.insert(0, str(Path(__file__).parent))

from nickydata import Orchestrator


def main():
    project_root = Path(__file__).parent.resolve()
    orch = Orchestrator(project_root=project_root)
    orch.run_from_cli(sys.argv[1:])


if __name__ == "__main__":
    main()
'''


PHASE_FOLDERS = [
    "data/user-inputs",
    "data/raw-data",
    "data/int-data",
    "data/final-data",
    "data/adjusted-final-data",
    "data/scratch",
    "scripts",
    "outputs/analysis",
    "outputs/deliverables",
    "logs/setup",
    "logs/validation",
]

S_TEMPLATE = '''#!/usr/bin/env python3
"""S01 — Environment Setup

Validates Python version, installs packages if needed, checks API keys.
"""
import sys
import os
from pathlib import Path


def main():
    print("S01: Environment setup")

    # Verify Python version
    if sys.version_info < (3, 9):
        raise RuntimeError(f"Python 3.9+ required, got {sys.version}")

    # Check API keys
    required_keys = []  # e.g. ["FRED_API_KEY", "BEA_API_KEY"]
    missing = [k for k in required_keys if not os.environ.get(k)]
    if missing:
        print(f"  WARNING: Missing API keys: {missing}")
        print(f"  Affected series will be skipped")

    # Ensure log directory exists
    Path(__file__).parent.parent.joinpath("logs/setup").mkdir(parents=True, exist_ok=True)

    print("S01: Setup complete")
    return {"status": "SUCCESS", "phase": "S", "script": "S01"}


if __name__ == "__main__":
    main()
'''


def init_project(project_name: str, language: str = "python", target_dir: Path = None):
    """
    Create a new NickyData project structure.

    Args:
        project_name: Name of the project (used as folder name and in registry)
        language: Primary language ("python", "R", "stata", or "mixed")
        target_dir: Parent directory (defaults to current working directory)

    Returns:
        Path to created project directory
    """
    if target_dir is None:
        target_dir = Path.cwd()

    project_dir = target_dir / project_name

    if project_dir.exists():
        raise FileExistsError(f"Directory already exists: {project_dir}")

    print(f"Creating NickyData project: {project_dir}")

    # Create folders
    for folder in PHASE_FOLDERS:
        (project_dir / folder).mkdir(parents=True, exist_ok=True)

    # Write project_registry.json
    registry = dict(PROJECT_REGISTRY_TEMPLATE)
    registry["project_name"] = project_name
    registry["created_date"] = datetime.now().isoformat()
    registry["language"] = language
    with open(project_dir / "project_registry.json", "w") as f:
        json.dump(registry, f, indent=2)

    # Write CHECKLIST.md
    (project_dir / "CHECKLIST.md").write_text(CHECKLIST_TEMPLATE)

    # Write DECISION_LOG.md
    (project_dir / "DECISION_LOG.md").write_text(
        DECISION_LOG_TEMPLATE.replace("{DATE}", datetime.now().strftime("%Y-%m-%d"))
    )

    # Write run.py
    header = "=" * len(project_name)
    run_py = (RUN_PY_TEMPLATE
              .replace("{PROJECT_NAME}", project_name)
              .replace("{HEADER_LINE}", header))
    (project_dir / "run.py").write_text(run_py)

    # Write template scripts
    (project_dir / "scripts" / "S01_setup.py").write_text(S_TEMPLATE)

    # README
    readme = f"""# {project_name}

A NickyData research project with 8-phase pipeline architecture.

## Pipeline

```
S## (Setup) -> L## (Load) -> P## (Process) -> V## (Validate)
 -> M## (Manual Adjust) -> A## (Analyze) -> O## (Output)
 + E## (Explore, concurrent)
```

## Run

```bash
python run.py                # Full pipeline
python run.py --dry-run      # Show plan
python run.py --from A       # Analysis phase onward
```

## Configuration

- `project_registry.json` — Study definitions and dataset mappings
- `CHECKLIST.md` — Pre/post-analysis verification
- `DECISION_LOG.md` — All research decisions with rationale

## Adding Scripts

Place numbered scripts in `scripts/`:
- `S##_*.py` — Setup
- `L##_*.py` — Load
- `P##_*.py` — Process
- `V##_*.py` — Validate
- `M##_*.py` — Manual adjust
- `A##_*.py` — Analyze
- `O##_*.py` — Output
- `E##_*.py` — Explore

The orchestrator auto-discovers all numbered scripts via glob pattern.
"""
    (project_dir / "README.md").write_text(readme)

    print(f"\n  Created folders: {len(PHASE_FOLDERS)}")
    print(f"  Created files: project_registry.json, CHECKLIST.md, DECISION_LOG.md, run.py, README.md")
    print(f"  Created template script: scripts/S01_setup.py")
    print(f"\nNext steps:")
    print(f"  cd {project_name}")
    print(f"  # Add L## scripts to scripts/ to load your data")
    print(f"  python run.py --dry-run")

    return project_dir


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a NickyData research project",
        prog="nickydata init"
    )
    parser.add_argument("project_name", help="Project directory name")
    parser.add_argument(
        "--language",
        choices=["python", "R", "stata", "mixed"],
        default="python",
        help="Primary scripting language (default: python)"
    )
    parser.add_argument(
        "--target-dir",
        type=Path,
        default=None,
        help="Parent directory (default: current working directory)"
    )

    args = parser.parse_args()

    try:
        init_project(args.project_name, args.language, args.target_dir)
    except FileExistsError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
