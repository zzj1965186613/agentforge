"""Adapter for GitHub Copilot instructions."""

from __future__ import annotations

from pathlib import Path

from .base import SimpleAgentAdapter


class CopilotAdapter(SimpleAgentAdapter):
    """Installs skills as Copilot instruction files.

    Project install path : ``<project>/.github/copilot-instructions/<name>.md``
    Global install path  : ``~/.config/github-copilot/instructions/<name>.md``
    """

    # -- Identity -----------------------------------------------------------

    @property
    def name(self) -> str:
        return "copilot"

    @property
    def display_name(self) -> str:
        return "GitHub Copilot"

    # -- Detection ----------------------------------------------------------

    def detect(self, project_path: Path) -> bool:
        """Copilot projects typically have a ``.github`` directory."""
        gh_dir = project_path / ".github"
        return gh_dir.is_dir() and (
            (gh_dir / "copilot-instructions").is_dir()
            or (gh_dir / "copilot-instructions.md").is_file()
        )

    # -- Paths --------------------------------------------------------------

    def install_path(self, project_path: Path, global_install: bool) -> Path:
        if global_install:
            return Path.home() / ".config" / "github-copilot" / "instructions"
        return project_path / ".github" / "copilot-instructions"
