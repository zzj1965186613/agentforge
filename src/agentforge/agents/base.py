"""Abstract base class for agent adapters."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class AgentAdapter(ABC):
    """Base class that all agent adapters must implement.

    An adapter translates AgentForge skill definitions into the native
    format expected by a specific coding agent (Claude Code, Cursor, etc.).
    """

    # ------------------------------------------------------------------
    # Identity – subclasses override these
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def name(self) -> str:
        """Short machine-readable identifier, e.g. ``'claude_code'``."""

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-friendly name shown in CLI output, e.g. ``'Claude Code'``."""

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    @abstractmethod
    def detect(self, project_path: Path) -> bool:
        """Return *True* if the project at *project_path* uses this agent.

        Adapters look for tell-tale files such as ``.claude/`` or
        ``.cursorrules`` to determine whether the agent is active.
        """

    # ------------------------------------------------------------------
    # Path helpers
    # ------------------------------------------------------------------

    @abstractmethod
    def install_path(self, project_path: Path, global_install: bool) -> Path:
        """Return the directory into which skills should be installed.

        Parameters
        ----------
        project_path:
            Root of the current project.
        global_install:
            When *True*, return the user-level (global) directory instead
            of the project-local one.
        """

    def skill_filename(self, skill_name: str) -> str:
        """Return the filename for *skill_name* (without directory).

        The default implementation sanitises the name and appends
        ``.md``.  Subclasses may override if the target agent uses a
        different convention.
        """
        safe = skill_name.replace(" ", "-").lower()
        return f"{safe}.md"

    # ------------------------------------------------------------------
    # Install / Uninstall / List
    # ------------------------------------------------------------------

    @abstractmethod
    def install_skill(
        self,
        skill: dict[str, Any],
        rendered_content: str,
        project_path: Path,
        global_install: bool,
    ) -> Path:
        """Write the rendered skill content to the target location.

        Returns the path of the newly created file.
        """

    @abstractmethod
    def uninstall_skill(
        self,
        skill_name: str,
        project_path: Path,
        global_install: bool,
    ) -> bool:
        """Remove the installed skill file.

        Returns *True* if a file was actually deleted, *False* if it
        did not exist.
        """

    @abstractmethod
    def list_installed(self, project_path: Path, global_install: bool) -> list[str]:
        """Return a list of skill names currently installed for this agent."""

    # ------------------------------------------------------------------
    # Convenience helpers (shared by most adapters)
    # ------------------------------------------------------------------

    def _resolve_skill_path(
        self, skill_name: str, project_path: Path, global_install: bool
    ) -> Path:
        """Combine ``install_path`` and ``skill_filename``."""
        return self.install_path(project_path, global_install) / self.skill_filename(skill_name)

    def _ensure_dir(self, path: Path) -> None:
        """Create parent directories if they don't exist."""
        path.parent.mkdir(parents=True, exist_ok=True)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"


class SimpleAgentAdapter(AgentAdapter):
    """Convenience base class providing default implementations for the
    install/uninstall/list contract.

    Subclasses only need to supply ``name``, ``display_name``, ``detect()``,
    and ``install_path()``.  The ``skill_filename()``, ``install_skill()``,
    ``uninstall_skill()``, and ``list_installed()`` methods use sensible
    defaults (write/read/delete ``*.md`` files under the install path).
    """

    # -- skill_filename (default: sanitize + .md) ----------------------------

    def skill_filename(self, skill_name: str) -> str:
        safe = skill_name.replace(" ", "-").lower()
        return f"{safe}.md"

    # -- Install / Uninstall / List (concrete) --------------------------------

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
            return True
        return False

    def list_installed(self, project_path: Path, global_install: bool) -> list[str]:
        base = self.install_path(project_path, global_install)
        if not base.is_dir():
            return []
        return sorted(p.stem for p in base.glob("*.md"))
