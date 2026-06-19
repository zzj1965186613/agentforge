"""Skill dataclass and parser for AgentForge."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentforge.utils.markdown import parse_frontmatter, render_variables

_SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)
_NAME_RE = re.compile(r"^[a-z][a-z0-9-]*$")


@dataclass
class SkillVariable:
    """A variable placeholder that can be substituted when rendering a skill."""

    name: str
    description: str = ""
    default: str | None = None
    required: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SkillVariable:
        return cls(
            name=str(data.get("name", "")),
            description=str(data.get("description", "")),
            default=data.get("default"),
            required=bool(data.get("required", False)),
        )


@dataclass
class Skill:
    """Represents a single AgentForge skill (parsed from a .md file with YAML frontmatter)."""

    name: str = ""
    version: str = "0.0.0"
    description: str = ""
    category: str = ""
    body: str = ""
    tags: list[str] = field(default_factory=list)
    author: str = ""
    license: str = ""
    agent_compatibility: list[str] = field(default_factory=list)
    requires: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    min_agentforge_version: str = ""
    variables: list[SkillVariable] = field(default_factory=list)
    source_path: Path | None = None
    installed: bool = False
    installed_agent: str = ""
    installed_path: Path | None = None

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_file(cls, path: str | Path) -> Skill:
        """Parse a skill from a Markdown file with YAML frontmatter.

        Raises:
            FileNotFoundError: If *path* does not exist.
            ValueError: If the file cannot be parsed.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Skill file not found: {path}")

        content = path.read_text(encoding="utf-8")
        skill = cls.from_string(content, source=str(path))
        skill.source_path = path
        return skill

    @classmethod
    def from_string(cls, content: str, source: str = "<string>") -> Skill:
        """Parse a skill from a raw Markdown string."""
        metadata, body = parse_frontmatter(content)

        tags_raw = metadata.get("tags", [])
        if isinstance(tags_raw, str):
            tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        elif isinstance(tags_raw, list):
            tags = [str(t) for t in tags_raw]
        else:
            tags = []

        compat_raw = metadata.get("agent_compatibility", metadata.get("agents", []))
        if isinstance(compat_raw, str):
            compatibility = [c.strip() for c in compat_raw.split(",") if c.strip()]
        elif isinstance(compat_raw, list):
            compatibility = [str(c) for c in compat_raw]
        else:
            compatibility = []

        requires_raw = metadata.get("requires", [])
        if isinstance(requires_raw, str):
            requires = [r.strip() for r in requires_raw.split(",") if r.strip()]
        elif isinstance(requires_raw, list):
            requires = [str(r) for r in requires_raw]
        else:
            requires = []

        conflicts_raw = metadata.get("conflicts", [])
        if isinstance(conflicts_raw, str):
            conflicts = [c.strip() for c in conflicts_raw.split(",") if c.strip()]
        elif isinstance(conflicts_raw, list):
            conflicts = [str(c) for c in conflicts_raw]
        else:
            conflicts = []

        variables_raw = metadata.get("variables", [])
        if isinstance(variables_raw, list):
            variables = [SkillVariable.from_dict(v) for v in variables_raw if isinstance(v, dict)]
        else:
            variables = []

        return cls(
            name=str(metadata.get("name", "")),
            version=str(metadata.get("version", "0.0.0")),
            description=str(metadata.get("description", "")),
            category=str(metadata.get("category", "")),
            body=body.strip(),
            tags=tags,
            author=str(metadata.get("author", "")),
            license=str(metadata.get("license", "")),
            agent_compatibility=compatibility,
            requires=requires,
            conflicts=conflicts,
            min_agentforge_version=str(metadata.get("min_agentforge_version", "")),
            variables=variables,
            source_path=Path(source) if source else None,
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> list[str]:
        """Return a list of validation error messages (empty = valid)."""
        errors: list[str] = []

        if not self.name:
            errors.append("Missing required field: name")
        elif not _NAME_RE.match(self.name):
            errors.append(
                f"Invalid skill name '{self.name}': must be lowercase letters, "
                "digits, and hyphens, starting with a letter"
            )

        if not self.version:
            errors.append("Missing required field: version")
        elif not _SEMVER_RE.match(self.version):
            errors.append(f"Invalid version '{self.version}': must be semver (e.g. 1.2.3)")

        if not self.description:
            errors.append("Missing required field: description")

        return errors

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render(self, variables: dict[str, str] | None = None) -> str:
        """Return the skill body with ``{{VARIABLE}}`` placeholders substituted.

        Default values from the skill's variable definitions are used unless
        overridden by *variables*.
        """
        merged: dict[str, str] = {}
        for var in self.variables:
            if var.default is not None:
                merged[var.name] = var.default
        if variables:
            merged.update(variables)
        return render_variables(self.body, merged)

    # ------------------------------------------------------------------
    # Compatibility
    # ------------------------------------------------------------------

    def is_compatible_with(self, agent: str) -> bool:
        """Return True if this skill is compatible with the given agent.

        If no ``agent_compatibility`` list is set the skill is considered
        universally compatible.  Normalizes underscores/hyphens for matching.
        """
        if not self.agent_compatibility:
            return True
        agent_norm = agent.lower().replace("-", "_").replace(" ", "_")
        normalized = (
            a.lower().replace("-", "_").replace(" ", "_") for a in self.agent_compatibility
        )
        return agent_norm in normalized

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def full_name(self) -> str:
        """Return ``name@version``."""
        return f"{self.name}@{self.version}"

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable dict of installation metadata."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "category": self.category,
            "tags": self.tags,
            "author": self.author,
            "license": self.license,
            "agent_compatibility": self.agent_compatibility,
            "requires": self.requires,
            "conflicts": self.conflicts,
            "min_agentforge_version": self.min_agentforge_version,
            "installed": self.installed,
            "installed_agent": self.installed_agent,
            "installed_path": str(self.installed_path) if self.installed_path else None,
            "source_path": str(self.source_path) if self.source_path else None,
            "variables": [
                {
                    "name": v.name,
                    "description": v.description,
                    "default": v.default,
                    "required": v.required,
                }
                for v in self.variables
            ],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Skill:
        """Reconstruct a Skill from a dict produced by ``to_dict``."""
        variables = [
            SkillVariable.from_dict(v) for v in data.get("variables", []) if isinstance(v, dict)
        ]
        source = data.get("source_path")
        installed = data.get("installed_path")
        return cls(
            name=data.get("name", ""),
            version=data.get("version", "0.0.0"),
            description=data.get("description", ""),
            category=data.get("category", ""),
            body=data.get("body", ""),
            tags=data.get("tags", []),
            author=data.get("author", ""),
            license=data.get("license", ""),
            agent_compatibility=data.get("agent_compatibility", []),
            requires=data.get("requires", []),
            conflicts=data.get("conflicts", []),
            min_agentforge_version=data.get("min_agentforge_version", ""),
            variables=variables,
            source_path=Path(source) if source else None,
            installed=data.get("installed", False),
            installed_agent=data.get("installed_agent", ""),
            installed_path=Path(installed) if installed else None,
        )

    def __repr__(self) -> str:
        return f"Skill({self.full_name!r})"
