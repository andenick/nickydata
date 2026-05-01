#!/usr/bin/env python3
"""
NickyData Orchestrator — Auto-discover and run pipeline scripts
================================================================

Discovers numbered scripts in scripts/ directory and runs them in phase order:
  S## -> L## -> P## (+ E## concurrent) -> V## -> M## -> A## -> V## -> O##
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


# Phase ordering. Note V## runs twice (after P## for data validation,
# after A## for model diagnostics). E## runs concurrently with P##.
PHASE_ORDER = ["S", "L", "P", "V", "M", "A", "V_diag", "O"]


class Orchestrator:
    """
    Auto-discovers numbered scripts and runs them in phase order.
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()
        self.scripts_dir = self.project_root / "scripts"
        self.logs_dir = self.project_root / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def discover_scripts(self) -> Dict[str, List[Path]]:
        """
        Find all numbered scripts and group by phase prefix.

        Returns:
            Dict mapping phase letter (S, L, P, V, M, A, O, E) to list of paths
            sorted by number.
        """
        if not self.scripts_dir.exists():
            return {}

        scripts: Dict[str, List[Path]] = {phase: [] for phase in "SLPVMAOE"}
        pattern = re.compile(r"^([SLPVMAOE])(\d{2})_.*\.(py|R|do)$")

        for path in sorted(self.scripts_dir.iterdir()):
            if not path.is_file():
                continue
            match = pattern.match(path.name)
            if match:
                phase_letter = match.group(1)
                scripts[phase_letter].append(path)

        # Sort each phase by number
        for phase in scripts:
            scripts[phase].sort(key=lambda p: p.name)

        return scripts

    def build_plan(self, from_phase: Optional[str] = None,
                   only_phases: Optional[List[str]] = None) -> List[Path]:
        """
        Build the ordered list of scripts to execute.

        Args:
            from_phase: If set, skip phases before this one
            only_phases: If set, only run these phases

        Returns:
            Ordered list of script paths to execute
        """
        scripts = self.discover_scripts()
        plan: List[Path] = []

        # Standard phase order with V## running twice (data + diagnostics)
        execution_order = ["S", "L", "P", "E", "V", "M", "A", "V", "O"]

        seen_v = False
        for phase in execution_order:
            phase_scripts = scripts.get(phase, [])

            # V appears twice: first for data validation, second for diagnostics
            if phase == "V":
                if not seen_v:
                    seen_v = True
                    # Data validation V## scripts (run after P##)
                else:
                    # Model diagnostics V## scripts (run after A##)
                    pass

            if from_phase and phase < from_phase and phase != "E":
                continue

            if only_phases and phase not in only_phases:
                continue

            plan.extend(phase_scripts)

        return plan

    def run_script(self, script_path: Path) -> Tuple[bool, str]:
        """
        Execute a single script.

        Returns:
            Tuple of (success, output)
        """
        ext = script_path.suffix.lower()
        if ext == ".py":
            cmd = [sys.executable, str(script_path)]
        elif ext == ".r":
            cmd = ["Rscript", str(script_path)]
        elif ext == ".do":
            cmd = ["stata", "-b", "do", str(script_path)]
        else:
            return False, f"Unsupported script extension: {ext}"

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                check=False,
            )
            success = result.returncode == 0
            output = result.stdout + ("\n" + result.stderr if result.stderr else "")
            return success, output
        except FileNotFoundError as e:
            return False, f"Interpreter not found: {e}"

    def run(self, from_phase: Optional[str] = None,
            only_phases: Optional[List[str]] = None,
            dry_run: bool = False) -> Dict:
        """
        Execute the pipeline.

        Returns:
            Run summary dict.
        """
        plan = self.build_plan(from_phase=from_phase, only_phases=only_phases)

        print("=" * 70)
        print("NickyData Orchestrator")
        print("=" * 70)
        print(f"Project: {self.project_root}")
        print(f"Scripts found: {len(plan)}")
        if dry_run:
            print(f"Mode: DRY RUN")
        print()

        if dry_run:
            print("Execution plan:")
            for i, path in enumerate(plan, 1):
                print(f"  {i:3d}. {path.name}")
            return {"status": "DRY_RUN", "scripts_planned": len(plan)}

        results = []
        run_log = {
            "run_date": datetime.now().isoformat(),
            "scripts_planned": len(plan),
            "scripts_executed": 0,
            "scripts_succeeded": 0,
            "scripts_failed": 0,
            "results": [],
        }

        for i, path in enumerate(plan, 1):
            print(f"[{i}/{len(plan)}] {path.name}", end=" ", flush=True)
            success, output = self.run_script(path)
            run_log["scripts_executed"] += 1
            if success:
                run_log["scripts_succeeded"] += 1
                print("OK")
            else:
                run_log["scripts_failed"] += 1
                print("FAIL")
                print(f"  {output[:200]}")
            run_log["results"].append({
                "script": path.name,
                "success": success,
                "output_excerpt": output[:500],
            })

            # Stop on first failure unless told otherwise
            if not success:
                print(f"\nPipeline halted on failure of {path.name}")
                break

        # Write run log
        log_path = self.logs_dir / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_path, "w") as f:
            json.dump(run_log, f, indent=2)

        print()
        print("=" * 70)
        print(f"Pipeline complete: {run_log['scripts_succeeded']}/{run_log['scripts_executed']} succeeded")
        print(f"Run log: {log_path.relative_to(self.project_root)}")
        print("=" * 70)

        return run_log

    def run_from_cli(self, args: List[str]) -> None:
        """Parse CLI args and run."""
        parser = argparse.ArgumentParser(
            description="NickyData pipeline orchestrator",
            prog="run.py"
        )
        parser.add_argument(
            "--from", dest="from_phase",
            help="Start from this phase (S/L/P/V/M/A/O)"
        )
        parser.add_argument(
            "--phases",
            help="Only run these phases (comma-separated, e.g. S,L,P)"
        )
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Show execution plan without running"
        )

        opts = parser.parse_args(args)

        only_phases = None
        if opts.phases:
            only_phases = [p.strip().upper() for p in opts.phases.split(",")]

        result = self.run(
            from_phase=opts.from_phase,
            only_phases=only_phases,
            dry_run=opts.dry_run,
        )

        if result.get("scripts_failed", 0) > 0:
            sys.exit(1)
