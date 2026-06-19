"""Adapter for Anthropic Claude Code (slash-command style)."""

from __future__ import annotations

from pathlib import Path

from .base import SimpleAgentAdapter


class ClaudeCodeAdapter(SimpleAgentAdapter):
    """Installs skills as Claude Code custom slash-commands.

    Project install path : ``<project>/.claude/commands/<name>.md``
    Global install path  : ``~/.claude/commands/<name>.md``
    """

    # -- Identity -----------------------------------------------------------

    @property
    def name(self) -> str:
        return "claude_code"

    @property
    def display_name(self) -> str:
        return "Claude Code"

    # -- Detection ----------------------------------------------------------

    def detect(self, project_path: Path) -> bool:
        """Claude Code projects contain a ``.claude`` directory."""
        return (project_path / ".claude").is_dir()

    # -- Paths --------------------------------------------------------------

    def install_path(self, project_path: Path, global_install: bool) -> Path:
        if global_install:
            return Path.home() / ".claude" / "commands"
        return project_path / ".claude" / "commands"
