"""
NickyData — Reproducible Research Pipeline Architecture
========================================================

8-phase pipeline for empirical research projects:
  S## (Setup) -> L## (Load) -> P## (Process) -> V## (Validate)
   -> M## (Manual Adjust) -> A## (Analyze) -> O## (Output)
   + E## (Explore, concurrent)

Author: Nicholas Anderson
License: MIT
"""

from nickydata.scaffold import init_project
from nickydata.registry import ProjectRegistry
from nickydata.orchestrator import Orchestrator

__version__ = "1.0.0"
__author__ = "Nicholas Anderson"

__all__ = ["init_project", "ProjectRegistry", "Orchestrator"]
