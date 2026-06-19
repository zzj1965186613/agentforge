"""Adapter for Aider skill files."""

from __future__ import annotations

from pathlib import Path

from .base import SimpleAgentAdapter


class AiderAdapter(SimpleAgentAdapter):
    """Installs skills for the Aider AI coding assistant.

    Project install path : ``<project>/.aider/skills/<name>.md``
    Global install path  : ``~/.aider/skills/<name>.md``
    """

    # -- Identity -----------------------------------------------------------

    @property
    def name(self) -> str:
        return "aider"

    @property
    def display_name(self) -> str:
        return "Aider"

    # -- Detection ----------------------------------------------------------

    def detect(self, project_path: Path) -> bool:
        """Aider projects may have ``.aider`` dir or ``.aider.conf.yml``."""
        return (project_path / ".aider").is_dir() or (project_path / ".aider.conf.yml").is_file()

    # -- Paths --------------------------------------------------------------

    def install_path(self, project_path: Path, global_install: bool) -> Path:
        if global_install:
            return Path.home() / ".aider" / "skills"
        return project_path / ".aider" / "skills"
