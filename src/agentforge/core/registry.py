"""Skill registry — tracks bundled and installed skills."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from agentforge.core.skill import Skill
from agentforge.utils.paths import bundled_skills_dir, user_data_dir

logger = logging.getLogger(__name__)


class SkillRegistry:
    """Central registry that knows about all available and installed skills."""

    def __init__(self, base_path: Path | None = None) -> None:
        self._base_path = base_path or user_data_dir()
        self._skills: dict[str, Skill] = {}
        # Install records: skill_name -> {agent: {"path": str}}
        self._install_index: dict[str, dict[str, dict[str, str]]] = {}
        self._loaded = False

        # Load install index eagerly (small file), defer bundled scan
        self._load_from_registry_index()

    def _ensure_loaded(self) -> None:
        """Lazily scan bundled and installed skills on first access."""
        if not self._loaded:
            self.scan_bundled()
            self.scan_installed()
            self._loaded = True

    # ------------------------------------------------------------------
    # Scanning
    # ------------------------------------------------------------------

    def scan_bundled(self) -> list[Skill]:
        """Scan the ``skills/`` directory shipped with the package."""
        skills_dir = bundled_skills_dir()
        loaded: list[Skill] = []
        if not skills_dir.is_dir():
            return loaded

        for md_file in sorted(skills_dir.glob("**/*.md")):
            try:
                skill = Skill.from_file(md_file)
                if skill.name and skill.name not in self._skills:
                    self._skills[skill.name] = skill
                    loaded.append(skill)
            except Exception:
                logger.warning("Failed to parse bundled skill %s", md_file, exc_info=True)
        return loaded

    def scan_installed(self) -> list[Skill]:
        """Return skills recorded in the install index."""
        loaded: list[Skill] = []
        seen_names: set[str] = set()
        for _name, agents in self._install_index.items():
            for agent, info in agents.items():
                skill_path = info.get("path")
                if skill_path and Path(skill_path).exists():
                    try:
                        skill = Skill.from_file(skill_path)
                        skill.installed = True
                        skill.installed_agent = agent
                        skill.installed_path = Path(skill_path)
                        self._skills[skill.name] = skill
                        if skill.name not in seen_names:
                            loaded.append(skill)
                            seen_names.add(skill.name)
                    except Exception:
                        logger.warning(
                            "Failed to parse installed skill %s",
                            skill_path,
                            exc_info=True,
                        )
        return loaded

    # ------------------------------------------------------------------
    # Lookup / Search
    # ------------------------------------------------------------------

    def get(self, name: str) -> Skill | None:
        """Return a skill by *name*, or ``None``."""
        self._ensure_loaded()
        return self._skills.get(name)

    def all_skills(self) -> list[Skill]:
        """Return all known skills (bundled + installed). Triggers lazy load."""
        self._ensure_loaded()
        return list(self._skills.values())

    def search(
        self,
        query: str = "",
        category: str = "",
        tag: str = "",
    ) -> list[Skill]:
        """Search skills by query string, category, and/or tag.

        Results are ranked by relevance: exact name match > name substring >
        tag match > description substring.
        """
        self._ensure_loaded()
        scored: list[tuple[int, Skill]] = []
        query_lower = query.lower()
        category_lower = category.lower()
        tag_lower = tag.lower()

        for skill in self._skills.values():
            if category_lower and category_lower != (skill.category or "").lower():
                continue
            if tag_lower and not any(tag_lower == t.lower() for t in skill.tags):
                continue

            if query_lower:
                score = self._score(skill, query_lower)
                if score == 0:
                    continue
                scored.append((score, skill))
            else:
                scored.append((0, skill))

        # Sort by relevance score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        return [skill for _, skill in scored]

    @staticmethod
    def _score(skill: Skill, query_lower: str) -> int:
        """Return a relevance score for a skill against a query."""
        name_lower = skill.name.lower()
        desc_lower = (skill.description or "").lower()

        # Exact name match
        if query_lower == name_lower:
            return 100
        # Name starts with query
        if name_lower.startswith(query_lower):
            return 90
        # Query is a substring of name
        if query_lower in name_lower:
            return 80
        # Exact tag match
        if any(query_lower == t.lower() for t in skill.tags):
            return 70
        # Tag contains query
        if any(query_lower in t.lower() for t in skill.tags):
            return 60
        # Description contains query
        if query_lower in desc_lower:
            return 50
        # Full name contains query
        if query_lower in skill.full_name.lower():
            return 40
        return 0

    # ------------------------------------------------------------------
    # Install book-keeping
    # ------------------------------------------------------------------

    def register_install(self, skill: Skill, agent: str, path: str | Path) -> None:
        """Record that *skill* was installed for *agent* at *path*."""
        name = skill.name
        if name not in self._install_index:
            self._install_index[name] = {}
        self._install_index[name][agent] = {"path": str(path)}
        # Update in-memory skill too
        skill.installed = True
        skill.installed_agent = agent
        skill.installed_path = Path(path)
        self._skills[name] = skill
        self.save()

    def unregister_install(self, name: str, agent: str) -> None:
        """Remove install record for *name* on *agent*."""
        if name in self._install_index:
            self._install_index[name].pop(agent, None)
            if not self._install_index[name]:
                del self._install_index[name]
        skill = self._skills.get(name)
        if skill and skill.installed_agent == agent:
            skill.installed = False
            skill.installed_agent = ""
            skill.installed_path = None
        self.save()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _registry_path(self) -> Path:
        return self._base_path / "registry.json"

    def save(self) -> None:
        """Persist the install index to disk."""
        path = self._registry_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            path.write_text(json.dumps(self._install_index, indent=2), encoding="utf-8")
        except OSError:
            logger.warning("Failed to save registry index to %s", path, exc_info=True)

    def _load_from_registry_index(self) -> None:
        """Load install index from disk (called on init)."""
        path = self._registry_path()
        if not path.exists():
            return
        try:
            raw = path.read_text(encoding="utf-8")
            self._install_index = json.loads(raw)
        except (json.JSONDecodeError, OSError):
            logger.warning("Failed to read registry index at %s", path, exc_info=True)
            self._install_index = {}

    def load(self) -> None:
        """Public reload — re-read from disk and re-scan."""
        self._install_index = {}
        self._skills.clear()
        self._loaded = False
        self._load_from_registry_index()
        self._ensure_loaded()  # single entry point for scanning
