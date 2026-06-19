"""Skill installer — copies rendered skill files into agent directories."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from agentforge.core.registry import SkillRegistry
from agentforge.core.skill import Skill

logger = logging.getLogger(__name__)


@dataclass
class InstallResult:
    """Outcome of a single skill installation."""

    success: bool
    skill_name: str
    installed_path: str = ""
    message: str = ""


class SkillInstaller:
    """Installs and uninstalls skills into agent-specific directories."""

    def __init__(
        self,
        registry: SkillRegistry,
        agent_adapters: dict[str, Any] | None = None,
    ) -> None:
        self.registry = registry
        self.agent_adapters = agent_adapters or {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def install(
        self,
        skill: Skill,
        agent: str,
        project_path: Path | None = None,
        global_install: bool = False,
        force: bool = False,
        variables: dict[str, str] | None = None,
    ) -> InstallResult:
        """Install *skill* for *agent*.

        Parameters
        ----------
        skill:
            The skill object to install.
        agent:
            Target agent name (e.g. ``hermes``, ``claude``).
        project_path:
            Project root; required when ``global_install`` is False.
        global_install:
            Install into the user-level agent config directory instead.
        force:
            Overwrite existing installation.
        variables:
            Variable values for ``{{VARIABLE}}`` substitution.
        """
        name = skill.name

        # Compatibility check
        if not skill.is_compatible_with(agent):
            return InstallResult(
                success=False,
                skill_name=name,
                message=f"Skill '{name}' is not compatible with agent '{agent}'",
            )

        # Determine target directory
        dest_dir = self._resolve_dest_dir(agent, project_path, global_install)
        if dest_dir is None:
            return InstallResult(
                success=False,
                skill_name=name,
                message="Could not determine installation directory",
            )

        dest_file = dest_dir / f"{name}.md"

        # Already installed?
        if dest_file.exists() and not force:
            return InstallResult(
                success=False,
                skill_name=name,
                installed_path=str(dest_file),
                message=(
                    f"Skill '{name}' already installed at {dest_file}. Use --force to overwrite."
                ),
            )

        # Ensure source is available
        source_path = skill.source_path
        if source_path is None or not source_path.exists():
            return InstallResult(
                success=False,
                skill_name=name,
                message=f"Skill source file not found for '{name}'",
            )

        # Render body with variables
        rendered_body = skill.render(variables)

        # Reconstruct the full file (frontmatter + rendered body)
        frontmatter: dict[str, Any] = {
            "name": skill.name,
            "version": skill.version,
            "description": skill.description,
        }
        if skill.category:
            frontmatter["category"] = skill.category
        if skill.tags:
            frontmatter["tags"] = skill.tags
        if skill.author:
            frontmatter["author"] = skill.author
        if skill.license:
            frontmatter["license"] = skill.license
        if skill.agent_compatibility:
            frontmatter["agent_compatibility"] = skill.agent_compatibility
        if skill.requires:
            frontmatter["requires"] = skill.requires
        if skill.conflicts:
            frontmatter["conflicts"] = skill.conflicts
        if skill.variables:
            frontmatter["variables"] = [
                {
                    "name": v.name,
                    "description": v.description,
                    "default": v.default,
                    "required": v.required,
                }
                for v in skill.variables
            ]

        yaml_str = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False).strip()
        rendered_file = f"---\n{yaml_str}\n---\n\n{rendered_body}\n"

        # Write to destination
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file.write_text(rendered_file, encoding="utf-8")

        # Register the install
        self.registry.register_install(skill, agent, dest_file)

        return InstallResult(
            success=True,
            skill_name=name,
            installed_path=str(dest_file),
            message=f"Skill '{name}' installed to {dest_file}",
        )

    def uninstall(
        self,
        skill_name: str,
        agent: str,
        project_path: Path | None = None,
        global_install: bool = False,
    ) -> InstallResult:
        """Remove a previously installed skill."""
        dest_dir = self._resolve_dest_dir(agent, project_path, global_install)
        if dest_dir is None:
            return InstallResult(
                success=False,
                skill_name=skill_name,
                message="Could not determine installation directory",
            )

        dest_file = dest_dir / f"{skill_name}.md"
        if not dest_file.exists():
            return InstallResult(
                success=False,
                skill_name=skill_name,
                message=f"Skill '{skill_name}' not found at {dest_file}",
            )

        dest_file.unlink()
        self.registry.unregister_install(skill_name, agent)

        return InstallResult(
            success=True,
            skill_name=skill_name,
            message=f"Skill '{skill_name}' uninstalled from {dest_file}",
        )

    def install_many(
        self,
        names: list[str],
        agent: str,
        project_path: Path | None = None,
        global_install: bool = False,
        force: bool = False,
        variables: dict[str, str] | None = None,
    ) -> list[InstallResult]:
        """Install multiple skills by name."""
        results: list[InstallResult] = []
        for name in names:
            skill = self.registry.get(name)
            if skill is None:
                results.append(
                    InstallResult(
                        success=False,
                        skill_name=name,
                        message=f"Skill '{name}' not found in registry",
                    )
                )
                continue
            results.append(
                self.install(
                    skill,
                    agent,
                    project_path=project_path,
                    global_install=global_install,
                    force=force,
                    variables=variables,
                )
            )
        return results

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _resolve_dest_dir(
        self,
        agent: str,
        project_path: Path | None,
        global_install: bool,
    ) -> Path | None:
        """Determine the target skills directory for *agent*.

        Uses the agent adapter if one is registered; otherwise falls back
        to a reasonable default layout.
        """
        # Check for a registered adapter
        adapter = self.agent_adapters.get(agent.lower())
        if adapter is not None:
            method = getattr(adapter, "install_path", None)
            if method is not None:
                return Path(
                    method(
                        project_path=project_path or Path("."),
                        global_install=global_install,
                    )
                )

        # Fallback defaults
        if global_install:
            from agentforge.utils.paths import user_data_dir

            return user_data_dir() / "installed" / agent / "skills"

        if project_path is not None:
            return Path(project_path) / ".agentforge" / "skills" / agent

        return None
