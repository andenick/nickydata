#!/usr/bin/env python3
"""
NickyData Registry — project_registry.json management
=======================================================

Read, validate, and update the project_registry.json file that serves as
the single source of truth for a NickyData project.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class ProjectRegistry:
    """
    Manages a NickyData project_registry.json file.

    The registry stores:
      - project metadata (name, version, language)
      - study definitions (research questions, datasets needed)
      - dataset mappings (source -> path -> processing steps)
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()
        self.registry_path = self.project_root / "project_registry.json"
        self._data: Dict[str, Any] = {}
        if self.registry_path.exists():
            self.load()

    def load(self) -> None:
        """Load registry from disk."""
        with open(self.registry_path, "r") as f:
            self._data = json.load(f)

    def save(self) -> None:
        """Save registry to disk."""
        self._data["last_updated"] = datetime.now().isoformat()
        with open(self.registry_path, "w") as f:
            json.dump(self._data, f, indent=2)

    @property
    def project_name(self) -> str:
        return self._data.get("project_name", "")

    @property
    def language(self) -> str:
        return self._data.get("language", "python")

    @property
    def studies(self) -> Dict[str, Dict]:
        return self._data.get("studies", {})

    @property
    def datasets(self) -> Dict[str, Dict]:
        return self._data.get("datasets", {})

    def add_study(self, study_id: str, name: str, datasets: List[str],
                  status: str = "Planned") -> None:
        """Add a study definition."""
        if "studies" not in self._data:
            self._data["studies"] = {}
        self._data["studies"][study_id] = {
            "name": name,
            "datasets": datasets,
            "status": status,
            "added_date": datetime.now().isoformat(),
        }

    def add_dataset(self, dataset_id: str, source: str, raw_path: str,
                    description: str = "") -> None:
        """Add a dataset mapping."""
        if "datasets" not in self._data:
            self._data["datasets"] = {}
        self._data["datasets"][dataset_id] = {
            "source": source,
            "raw_path": raw_path,
            "description": description,
            "added_date": datetime.now().isoformat(),
        }

    def update_study_status(self, study_id: str, status: str) -> None:
        """Update a study's status."""
        if study_id in self.studies:
            self._data["studies"][study_id]["status"] = status
            self._data["studies"][study_id]["status_updated"] = datetime.now().isoformat()

    def validate(self) -> List[str]:
        """
        Validate registry consistency.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not self.project_name:
            errors.append("Missing required field: project_name")

        if "registry_version" not in self._data:
            errors.append("Missing required field: registry_version")

        # Check that all study datasets are defined
        for study_id, study in self.studies.items():
            for dataset_id in study.get("datasets", []):
                if dataset_id not in self.datasets:
                    errors.append(
                        f"Study {study_id} references undefined dataset: {dataset_id}"
                    )

        return errors

    def __repr__(self) -> str:
        return (f"ProjectRegistry(name={self.project_name!r}, "
                f"studies={len(self.studies)}, datasets={len(self.datasets)})")
