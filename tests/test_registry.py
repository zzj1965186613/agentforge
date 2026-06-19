"""Tests for agentforge.core.registry — SkillRegistry."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentforge.core.registry import SkillRegistry
from agentforge.core.skill import Skill


def _make_skill_file(
    path: Path,
    name: str = "test-skill",
    version: str = "1.0.0",
    description: str = "A test skill",
    category: str = "testing",
    tags: list[str] | None = None,
    body: str = "Body text",
) -> Path:
    """Write a minimal valid skill .md file and return its path."""
    tags = tags or []
    tag_str = "[" + ", ".join(tags) + "]" if tags else "[]"
    content = (
        f"---\n"
        f"name: {name}\n"
        f'version: "{version}"\n'
        f'description: "{description}"\n'
        f"category: {category}\n"
        f"tags: {tag_str}\n"
        f"---\n\n"
        f"{body}\n"
    )
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Init / construction
# ---------------------------------------------------------------------------


class TestSkillRegistryInit:
    """Test SkillRegistry initialisation."""

    def test_default_init_creates_registry(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("agentforge.core.registry.user_data_dir", lambda: tmp_path / "data")
        reg = SkillRegistry()
        assert reg._base_path == tmp_path / "data"

    def test_custom_base_path(self, tmp_path: Path):
        reg = SkillRegistry(base_path=tmp_path / "custom")
        assert reg._base_path == tmp_path / "custom"

    def test_empty_registry_has_no_skills(self, tmp_path: Path):
        reg = SkillRegistry(base_path=tmp_path)
        # _skills is empty before lazy load (no bundled/installed dirs)
        assert len(reg._skills) == 0


# ---------------------------------------------------------------------------
# scan_bundled
# ---------------------------------------------------------------------------


class TestSkillRegistryScanBundled:
    """Test scan_bundled()."""

    def test_scan_finds_skill_files(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        _make_skill_file(skills_dir / "alpha.md", name="alpha")
        _make_skill_file(skills_dir / "beta.md", name="beta")

        monkeypatch.setattr("agentforge.core.registry.bundled_skills_dir", lambda: skills_dir)
        reg = SkillRegistry(base_path=tmp_path)
        loaded = reg.scan_bundled()
        names = {s.name for s in loaded}
        assert "alpha" in names
        assert "beta" in names

    def test_scan_skips_invalid_files(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        _make_skill_file(skills_dir / "good.md", name="good")
        (skills_dir / "bad.md").write_text("no frontmatter here", encoding="utf-8")

        monkeypatch.setattr("agentforge.core.registry.bundled_skills_dir", lambda: skills_dir)
        reg = SkillRegistry(base_path=tmp_path)
        loaded = reg.scan_bundled()
        names = {s.name for s in loaded}
        assert "good" in names
        # bad.md has no name so it's skipped (name check: `if skill.name and skill.name not in ...`)
        assert len([s for s in loaded if s.name == ""]) == 0

    def test_scan_nonexistent_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(
            "agentforge.core.registry.bundled_skills_dir", lambda: tmp_path / "nonexistent"
        )
        reg = SkillRegistry(base_path=tmp_path)
        loaded = reg.scan_bundled()
        assert loaded == []

    def test_scan_nested_directories(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        skills_dir = tmp_path / "skills"
        (skills_dir / "subdir").mkdir(parents=True)
        _make_skill_file(skills_dir / "subdir" / "nested.md", name="nested")

        monkeypatch.setattr("agentforge.core.registry.bundled_skills_dir", lambda: skills_dir)
        reg = SkillRegistry(base_path=tmp_path)
        loaded = reg.scan_bundled()
        assert any(s.name == "nested" for s in loaded)

    def test_scan_no_overwrite_existing(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """If a skill name is already registered, scan_bundled skips duplicates."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        _make_skill_file(skills_dir / "dup.md", name="dup")

        monkeypatch.setattr("agentforge.core.registry.bundled_skills_dir", lambda: skills_dir)
        reg = SkillRegistry(base_path=tmp_path)
        # Manually add a skill with name "dup"
        reg._skills["dup"] = Skill(name="dup", version="0.0.0", description="original")
        reg.scan_bundled()
        # Should not overwrite
        assert reg._skills["dup"].version == "0.0.0"


# ---------------------------------------------------------------------------
# scan_installed
# ---------------------------------------------------------------------------


class TestSkillRegistryScanInstalled:
    """Test scan_installed()."""

    def test_scan_installed_from_index(self, tmp_path: Path):
        # Write a skill file
        skill_dir = tmp_path / "installed"
        skill_dir.mkdir()
        _make_skill_file(skill_dir / "inst.md", name="installed-skill")

        # Write registry index
        reg = SkillRegistry(base_path=tmp_path)
        reg._install_index = {"installed-skill": {"hermes": {"path": str(skill_dir / "inst.md")}}}
        loaded = reg.scan_installed()
        assert len(loaded) == 1
        assert loaded[0].name == "installed-skill"
        assert loaded[0].installed is True
        assert loaded[0].installed_agent == "hermes"

    def test_scan_installed_missing_file(self, tmp_path: Path):
        reg = SkillRegistry(base_path=tmp_path)
        reg._install_index = {"ghost": {"hermes": {"path": str(tmp_path / "ghost.md")}}}
        loaded = reg.scan_installed()
        assert loaded == []


# ---------------------------------------------------------------------------
# get / search
# ---------------------------------------------------------------------------


class TestSkillRegistryLookup:
    """Test get() and search()."""

    def _populate_registry(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> SkillRegistry:
        """Create a registry with a few skills for lookup tests."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        _make_skill_file(
            skills_dir / "a.md",
            name="alpha",
            description="The first skill",
            category="core",
            tags=["essential", "basic"],
        )
        _make_skill_file(
            skills_dir / "b.md",
            name="beta",
            description="A beta skill",
            category="experimental",
            tags=["beta", "new"],
        )
        _make_skill_file(
            skills_dir / "c.md",
            name="gamma",
            description="Third letter",
            category="core",
            tags=["basic"],
        )

        monkeypatch.setattr("agentforge.core.registry.bundled_skills_dir", lambda: skills_dir)
        reg = SkillRegistry(base_path=tmp_path)
        reg.scan_bundled()
        reg._loaded = True
        return reg

    def test_get_existing(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        reg = self._populate_registry(tmp_path, monkeypatch)
        skill = reg.get("alpha")
        assert skill is not None
        assert skill.name == "alpha"

    def test_get_nonexistent(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        reg = self._populate_registry(tmp_path, monkeypatch)
        assert reg.get("nonexistent") is None

    def test_search_by_query_name(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        reg = self._populate_registry(tmp_path, monkeypatch)
        results = reg.search(query="alpha")
        assert len(results) == 1
        assert results[0].name == "alpha"

    def test_search_by_query_description(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        reg = self._populate_registry(tmp_path, monkeypatch)
        results = reg.search(query="beta skill")
        assert len(results) == 1
        assert results[0].name == "beta"

    def test_search_by_query_tag(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        reg = self._populate_registry(tmp_path, monkeypatch)
        results = reg.search(query="essential")
        assert len(results) == 1
        assert results[0].name == "alpha"

    def test_search_by_category(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        reg = self._populate_registry(tmp_path, monkeypatch)
        results = reg.search(category="core")
        names = {s.name for s in results}
        assert "alpha" in names
        assert "gamma" in names

    def test_search_by_tag(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        reg = self._populate_registry(tmp_path, monkeypatch)
        results = reg.search(tag="basic")
        names = {s.name for s in results}
        assert "alpha" in names
        assert "gamma" in names

    def test_search_combined_filters(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        reg = self._populate_registry(tmp_path, monkeypatch)
        results = reg.search(query="first", category="core")
        assert len(results) == 1
        assert results[0].name == "alpha"

    def test_search_no_results(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        reg = self._populate_registry(tmp_path, monkeypatch)
        results = reg.search(query="zzzzz")
        assert results == []

    def test_search_empty_query_returns_all(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        reg = self._populate_registry(tmp_path, monkeypatch)
        results = reg.search()
        assert len(results) == 3


# ---------------------------------------------------------------------------
# register_install / unregister_install
# ---------------------------------------------------------------------------


class TestSkillRegistryInstallTracking:
    """Test register_install() and unregister_install()."""

    def test_register_and_get(self, tmp_path: Path):
        reg = SkillRegistry(base_path=tmp_path)
        skill = Skill(name="my-skill", version="1.0.0", description="d")
        reg.register_install(skill, "hermes", tmp_path / "my-skill.md")

        assert skill.installed is True
        assert skill.installed_agent == "hermes"
        assert "my-skill" in reg._install_index
        assert "hermes" in reg._install_index["my-skill"]

    def test_register_persists_to_disk(self, tmp_path: Path):
        reg = SkillRegistry(base_path=tmp_path)
        skill = Skill(name="persist", version="1.0.0", description="d")
        reg.register_install(skill, "hermes", tmp_path / "persist.md")

        registry_file = tmp_path / "registry.json"
        assert registry_file.exists()
        data = json.loads(registry_file.read_text(encoding="utf-8"))
        assert "persist" in data

    def test_unregister_removes_record(self, tmp_path: Path):
        reg = SkillRegistry(base_path=tmp_path)
        skill = Skill(name="rem", version="1.0.0", description="d")
        reg.register_install(skill, "hermes", tmp_path / "rem.md")
        reg.unregister_install("rem", "hermes")

        assert "rem" not in reg._install_index
        assert skill.installed is False
        assert skill.installed_agent == ""

    def test_unregister_nonexistent_is_noop(self, tmp_path: Path):
        reg = SkillRegistry(base_path=tmp_path)
        # Should not raise
        reg.unregister_install("nonexistent", "hermes")

    def test_register_multiple_agents(self, tmp_path: Path):
        reg = SkillRegistry(base_path=tmp_path)
        skill = Skill(name="multi", version="1.0.0", description="d")
        reg.register_install(skill, "hermes", tmp_path / "multi-hermes.md")
        reg.register_install(skill, "claude", tmp_path / "multi-claude.md")

        assert "hermes" in reg._install_index["multi"]
        assert "claude" in reg._install_index["multi"]

    def test_unregister_one_agent_keeps_other(self, tmp_path: Path):
        reg = SkillRegistry(base_path=tmp_path)
        skill = Skill(name="multi", version="1.0.0", description="d")
        reg.register_install(skill, "hermes", tmp_path / "multi-hermes.md")
        reg.register_install(skill, "claude", tmp_path / "multi-claude.md")
        reg.unregister_install("multi", "hermes")

        assert "hermes" not in reg._install_index["multi"]
        assert "claude" in reg._install_index["multi"]


# ---------------------------------------------------------------------------
# Persistence (save / load)
# ---------------------------------------------------------------------------


class TestSkillRegistryPersistence:
    """Test save() and load_from_registry_index()."""

    def test_save_and_reload(self, tmp_path: Path):
        reg = SkillRegistry(base_path=tmp_path)
        skill = Skill(name="persist-skill", version="1.0.0", description="d")
        reg.register_install(skill, "hermes", tmp_path / "persist-skill.md")

        # Create a fresh registry from the same base_path
        reg2 = SkillRegistry(base_path=tmp_path)
        assert "persist-skill" in reg2._install_index

    def test_load_with_corrupt_registry(self, tmp_path: Path):
        reg_file = tmp_path / "registry.json"
        reg_file.write_text("NOT VALID JSON {{{", encoding="utf-8")
        # Should not raise
        reg = SkillRegistry(base_path=tmp_path)
        assert reg._install_index == {}


# ---------------------------------------------------------------------------
# load()
# ---------------------------------------------------------------------------


class TestSkillRegistryLoad:
    """Test the public load() method."""

    def test_load_resets_and_reloads(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        _make_skill_file(skills_dir / "s.md", name="loadable")

        monkeypatch.setattr("agentforge.core.registry.bundled_skills_dir", lambda: skills_dir)
        reg = SkillRegistry(base_path=tmp_path)
        reg.load()
        assert "loadable" in reg._skills
