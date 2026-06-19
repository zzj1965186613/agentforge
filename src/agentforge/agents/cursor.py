"""Adapter for Cursor IDE rules."""

from __future__ import annotations

from pathlib import Path

from .base import SimpleAgentAdapter


class CursorAdapter(SimpleAgentAdapter):
    """Installs skills as Cursor rule files.

    Project install path : ``<project>/.cursor/rules/<name>.md``
    Global install path  : ``~/.cursor/rules/<name>.md``
    """

    # -- Identity -----------------------------------------------------------

    @property
    def name(self) -> str:
        return "cursor"

    @property
    def display_name(self) -> str:
        return "Cursor"

    # -- Detection ----------------------------------------------------------

    def detect(self, project_path: Path) -> bool:
        """Cursor projects have ``.cursor`` or ``.cursorrules``."""
        return (project_path / ".cursor").is_dir() or (project_path / ".cursorrules").is_file()

    # -- Paths --------------------------------------------------------------

    def install_path(self, project_path: Path, global_install: bool) -> Path:
        if global_install:
            return Path.home() / ".cursor" / "rules"
        return project_path / ".cursor" / "rules"
