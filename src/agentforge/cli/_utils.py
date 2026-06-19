"""Shared CLI helpers to avoid duplication across command modules."""

from __future__ import annotations

from rich.console import Console

console = Console()


def parse_version_tuple(v: str) -> tuple[int, ...]:
    """Parse a 'major.minor.patch' string into a comparable tuple."""
    parts: list[int] = []
    for p in v.split("."):
        try:
            parts.append(int(p.split("-")[0].split("+")[0]))
        except (ValueError, IndexError):
            break
    return tuple(parts) or (0,)


def get_installer() -> tuple | None:
    """Return (SkillInstaller, SkillRegistry) or None if core is missing."""
    try:
        from agentforge.core.installer import SkillInstaller
        from agentforge.core.registry import SkillRegistry
    except ImportError:
        console.print("[bold red]Error:[/] agentforge.core is not available yet.")
        return None

    registry = SkillRegistry()
    adapters: dict = {}
    try:
        from agentforge.agents.aider import AiderAdapter
        from agentforge.agents.claude_code import ClaudeCodeAdapter
        from agentforge.agents.copilot import CopilotAdapter
        from agentforge.agents.cursor import CursorAdapter
        from agentforge.agents.hermes import HermesAdapter

        for cls in [ClaudeCodeAdapter, CursorAdapter, CopilotAdapter, AiderAdapter, HermesAdapter]:
            adapter = cls()
            adapters[adapter.name] = adapter
    except ImportError:
        pass
    return SkillInstaller(registry, adapters), registry
