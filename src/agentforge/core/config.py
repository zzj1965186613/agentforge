"""AgentForge configuration management."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from agentforge.utils.paths import user_data_dir


@dataclass
class AgentForgeConfig:
    """User-level configuration for AgentForge."""

    default_agent: str = ""
    default_global: bool = False
    preferred_categories: list[str] = field(default_factory=list)
    auto_update: bool = True
    editor: str = ""

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    @classmethod
    def load(cls, path: str | Path | None = None) -> AgentForgeConfig:
        """Load configuration from *path* (default ``~/.agentforge/config.yml``).

        Returns a default config if the file doesn't exist or is malformed.
        """
        if path is None:
            path = user_data_dir() / "config.yml"
        path = Path(path)

        if not path.exists():
            return cls()

        try:
            raw = path.read_text(encoding="utf-8")
            data: dict[str, Any] = yaml.safe_load(raw) or {}
        except (yaml.YAMLError, OSError):
            return cls()

        cats_raw = data.get("preferred_categories", [])
        categories = [str(c) for c in cats_raw] if isinstance(cats_raw, list) else []

        return cls(
            default_agent=str(data.get("default_agent", "")),
            default_global=bool(data.get("default_global", False)),
            preferred_categories=categories,
            auto_update=bool(data.get("auto_update", True)),
            editor=str(data.get("editor", "")),
        )

    def save(self, path: str | Path | None = None) -> None:
        """Write configuration to *path* (default ``~/.agentforge/config.yml``)."""
        if path is None:
            path = user_data_dir() / "config.yml"
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data: dict[str, Any] = {
            "default_agent": self.default_agent,
            "default_global": self.default_global,
            "preferred_categories": self.preferred_categories,
            "auto_update": self.auto_update,
            "editor": self.editor,
        }
        path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=True), encoding="utf-8")
