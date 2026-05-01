#!/usr/bin/env python3
"""
SFC vs DSGE — Master Orchestrator
==================================

Reference NickyData study: comparing SFC and DSGE fiscal policy transmission.

Auto-discovers and runs scripts in phase order:
  S## -> L## -> P## (+ E## concurrent) -> V## -> M## -> A## -> V## -> O##

Usage:
  python run.py                 # Full pipeline
  python run.py --dry-run       # Show plan without executing
  python run.py --from A        # From analysis phase only
  python run.py --phases L,P,V  # Specific phases only
"""
import sys
from pathlib import Path

# Add nickydata package to path (assumes running from study directory)
NICKYDATA_PACKAGE = Path(__file__).parent.parent.parent
sys.path.insert(0, str(NICKYDATA_PACKAGE))

from nickydata import Orchestrator


def main():
    project_root = Path(__file__).parent.resolve()
    orch = Orchestrator(project_root=project_root)
    orch.run_from_cli(sys.argv[1:])


if __name__ == "__main__":
    main()
