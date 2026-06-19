"""Adapter for Hermes Agent (Nous Research)."""

from __future__ import annotations

import contextlib
from pathlib import Path
from typing import Any

from .base import AgentAdapter


class HermesAdapter(AgentAdapter):
    """Installs skills into the Hermes global skills directory.

    Hermes skills always install globally at:
    ``~/.hermes/skills/<name>/skill.md``

    Each skill lives in its own subdirectory, following the Hermes
    convention where a skill folder may contain additional resources
    alongside the primary ``skill.md`` manifest.
    """

    # -- Identity -----------------------------------------------------------

    @property
    def name(self) -> str:
        return "hermes"

    @property
    def display_name(self) -> str:
        return "Hermes Agent"

    # -- Detection ----------------------------------------------------------

    def detect(self, project_path: Path) -> bool:
        """Hermes is always available (installed globally)."""
        return (Path.home() / ".hermes").is_dir()

    # -- Paths --------------------------------------------------------------

    def install_path(self, project_path: Path, global_install: bool) -> Path:
        """Hermes skills are always global regardless of the flag."""
        return Path.home() / ".hermes" / "skills"

    def skill_filename(self, skill_name: str) -> str:
        """Hermes uses ``skill.md`` inside a named subdirectory.

        The directory name is the sanitised skill name; the file is
        always called ``skill.md``.
        """
        return "skill.md"

    def _resolve_skill_path(
        self, skill_name: str, project_path: Path, global_install: bool
    ) -> Path:
        safe = skill_name.replace(" ", "-").lower()
        return self.install_path(project_path, global_install) / safe / "skill.md"

    # -- Install / Uninstall / List -----------------------------------------

    def install_skill(
        self,
        skill: dict[str, Any],
        rendered_content: str,
        project_path: Path,
        global_install: bool,
    ) -> Path:
        dest = self._resolve_skill_path(skill["name"], project_path, global_install)
        self._ensure_dir(dest)
        dest.write_text(rendered_content, encoding="utf-8")
        return dest

    def uninstall_skill(
        self,
        skill_name: str,
        project_path: Path,
        global_install: bool,
    ) -> bool:
        dest = self._resolve_skill_path(skill_name, project_path, global_install)
        if dest.exists():
            dest.unlink()
            # Remove the now-empty skill directory if possible
            with contextlib.suppress(OSError):
                dest.parent.rmdir()  # Directory not empty (has other resources)
            return True
        return False

    def list_installed(self, project_path: Path, global_install: bool) -> list[str]:
        base = self.install_path(project_path, global_install)
        if not base.is_dir():
            return []
        results: list[str] = []
        for child in sorted(base.iterdir()):
            if child.is_dir() and (child / "skill.md").is_file():
                results.append(child.name)
        return results
