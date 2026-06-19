"""Tests for agentforge.core.installer — SkillInstaller and InstallResult."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from agentforge.core.installer import InstallResult, SkillInstaller
from agentforge.core.registry import SkillRegistry
from agentforge.core.skill import Skill


def _make_skill_file(
    path: Path, name: str = "test-skill", version: str = "1.0.0", description: str = "A test skill"
) -> Path:
    content = (
        f'---\nname: {name}\nversion: "{version}"\n'
        f'description: "{description}"\n---\n\nBody of {name}\n'
    )
    path.write_text(content, encoding="utf-8")
    return path


def _make_registry(tmp_path: Path) -> SkillRegistry:
    reg = SkillRegistry(base_path=tmp_path)
    reg._loaded = True
    return reg


# ---------------------------------------------------------------------------
# InstallResult
# ---------------------------------------------------------------------------


class TestInstallResult:
    def test_defaults(self):
        r = InstallResult(success=True, skill_name="x")
        assert r.success is True
        assert r.skill_name == "x"
        assert r.installed_path == ""
        assert r.message == ""


# ---------------------------------------------------------------------------
# SkillInstaller.install()
# ---------------------------------------------------------------------------


class TestInstallerInstall:
    """Test SkillInstaller.install()."""

    def test_install_success(self, tmp_path: Path):
        src = _make_skill_file(tmp_path / "src.md", name="my-skill")
        skill = Skill.from_file(src)
        reg = _make_registry(tmp_path)
        installer = SkillInstaller(registry=reg)

        project = tmp_path / "project"
        result = installer.install(skill, "hermes", project_path=project)

        assert result.success is True
        assert result.installed_path != ""
        assert Path(result.installed_path).exists()

    def test_install_creates_directory(self, tmp_path: Path):
        src = _make_skill_file(tmp_path / "src.md", name="new-skill")
        skill = Skill.from_file(src)
        reg = _make_registry(tmp_path)
        installer = SkillInstaller(registry=reg)

        deep_project = tmp_path / "a" / "b" / "c"
        result = installer.install(skill, "hermes", project_path=deep_project)
        assert result.success is True

    def test_install_incompatible_agent(self, tmp_path: Path):
        src = _make_skill_file(tmp_path / "src.md", name="claude-only")
        skill = Skill.from_file(src)
        skill.agent_compatibility = ["claude_code"]

        reg = _make_registry(tmp_path)
        installer = SkillInstaller(registry=reg)

        result = installer.install(skill, "hermes", project_path=tmp_path / "p")
        assert result.success is False
        assert "not compatible" in result.message.lower()

    def test_install_no_project_no_global(self, tmp_path: Path):
        src = _make_skill_file(tmp_path / "src.md")
        skill = Skill.from_file(src)
        reg = _make_registry(tmp_path)
        installer = SkillInstaller(registry=reg)

        result = installer.install(skill, "hermes")
        assert result.success is False
        assert "could not determine" in result.message.lower()

    def test_install_global(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        src = _make_skill_file(tmp_path / "src.md", name="global-skill")
        skill = Skill.from_file(src)
        monkeypatch.setattr(
            "agentforge.core.installer.SkillInstaller._resolve_dest_dir",
            lambda self, agent, pp, gi: tmp_path / "global-inst" / agent / "skills" if gi else None,
        )
        # Instead, let's just test with a project_path and global_install=True
        # The _resolve_dest_dir will use user_data_dir() for global
        monkeypatch.setattr("agentforge.utils.paths.user_data_dir", lambda: tmp_path / "userdata")
        reg = _make_registry(tmp_path)
        installer = SkillInstaller(registry=reg)
        result = installer.install(skill, "hermes", global_install=True)
        assert result.success is True

    def test_install_already_exists_no_force(self, tmp_path: Path):
        src = _make_skill_file(tmp_path / "src.md", name="dup-skill")
        skill = Skill.from_file(src)
        reg = _make_registry(tmp_path)
        installer = SkillInstaller(registry=reg)

        project = tmp_path / "project"
        # First install
        r1 = installer.install(skill, "hermes", project_path=project)
        assert r1.success is True

        # Second install without force
        r2 = installer.install(skill, "hermes", project_path=project)
        assert r2.success is False
        assert "already installed" in r2.message.lower()

    def test_install_force_overwrite(self, tmp_path: Path):
        src = _make_skill_file(tmp_path / "src.md", name="force-skill")
        skill = Skill.from_file(src)
        reg = _make_registry(tmp_path)
        installer = SkillInstaller(registry=reg)

        project = tmp_path / "project"
        installer.install(skill, "hermes", project_path=project)
        result = installer.install(skill, "hermes", project_path=project, force=True)
        assert result.success is True

    def test_install_no_source_path(self, tmp_path: Path):
        skill = Skill(name="no-source", version="1.0.0", description="d")
        reg = _make_registry(tmp_path)
        installer = SkillInstaller(registry=reg)

        result = installer.install(skill, "hermes", project_path=tmp_path / "p")
        assert result.success is False
        assert "source" in result.message.lower()

    def test_install_registers_in_registry(self, tmp_path: Path):
        src = _make_skill_file(tmp_path / "src.md", name="reg-skill")
        skill = Skill.from_file(src)
        reg = _make_registry(tmp_path)
        installer = SkillInstaller(registry=reg)

        project = tmp_path / "project"
        installer.install(skill, "hermes", project_path=project)
        assert "reg-skill" in reg._install_index

    def test_install_with_variables(self, tmp_path: Path):
        src = _make_skill_file(tmp_path / "src.md", name="var-skill")
        skill = Skill.from_file(src)
        reg = _make_registry(tmp_path)
        installer = SkillInstaller(registry=reg)

        project = tmp_path / "project"
        result = installer.install(skill, "hermes", project_path=project, variables={"X": "val"})
        assert result.success is True

    def test_install_with_adapter(self, tmp_path: Path):
        src = _make_skill_file(tmp_path / "src.md", name="adapt-skill")
        skill = Skill.from_file(src)
        reg = _make_registry(tmp_path)

        # Create a mock adapter
        adapter = MagicMock()
        adapter.install_path.return_value = str(tmp_path / "adapter-skills")

        installer = SkillInstaller(registry=reg, agent_adapters={"hermes": adapter})
        result = installer.install(skill, "hermes", project_path=tmp_path / "p")
        assert result.success is True
        adapter.install_path.assert_called_once()


# ---------------------------------------------------------------------------
# SkillInstaller.uninstall()
# ---------------------------------------------------------------------------


class TestInstallerUninstall:
    """Test SkillInstaller.uninstall()."""

    def test_uninstall_success(self, tmp_path: Path):
        src = _make_skill_file(tmp_path / "src.md", name="un-skill")
        skill = Skill.from_file(src)
        reg = _make_registry(tmp_path)
        installer = SkillInstaller(registry=reg)

        project = tmp_path / "project"
        installer.install(skill, "hermes", project_path=project)

        result = installer.uninstall("un-skill", "hermes", project_path=project)
        assert result.success is True
        assert "uninstalled" in result.message.lower()

    def test_uninstall_not_installed(self, tmp_path: Path):
        reg = _make_registry(tmp_path)
        installer = SkillInstaller(registry=reg)

        result = installer.uninstall("ghost", "hermes", project_path=tmp_path / "p")
        assert result.success is False
        assert "not found" in result.message.lower()

    def test_uninstall_removes_file(self, tmp_path: Path):
        src = _make_skill_file(tmp_path / "src.md", name="del-skill")
        skill = Skill.from_file(src)
        reg = _make_registry(tmp_path)
        installer = SkillInstaller(registry=reg)

        project = tmp_path / "project"
        install_result = installer.install(skill, "hermes", project_path=project)
        dest = Path(install_result.installed_path)
        assert dest.exists()

        installer.uninstall("del-skill", "hermes", project_path=project)
        assert not dest.exists()

    def test_uninstall_no_project_no_global(self, tmp_path: Path):
        reg = _make_registry(tmp_path)
        installer = SkillInstaller(registry=reg)
        result = installer.uninstall("x", "hermes")
        assert result.success is False


# ---------------------------------------------------------------------------
# SkillInstaller.install_many()
# ---------------------------------------------------------------------------


class TestInstallerInstallMany:
    """Test SkillInstaller.install_many()."""

    def test_install_many_success(self, tmp_path: Path):
        src1 = _make_skill_file(tmp_path / "src1.md", name="skill-a")
        src2 = _make_skill_file(tmp_path / "src2.md", name="skill-b")
        skill_a = Skill.from_file(src1)
        skill_b = Skill.from_file(src2)

        reg = _make_registry(tmp_path)
        reg._skills["skill-a"] = skill_a
        reg._skills["skill-b"] = skill_b
        installer = SkillInstaller(registry=reg)

        project = tmp_path / "project"
        results = installer.install_many(["skill-a", "skill-b"], "hermes", project_path=project)
        assert len(results) == 2
        assert all(r.success for r in results)

    def test_install_many_partial_missing(self, tmp_path: Path):
        src = _make_skill_file(tmp_path / "src.md", name="exists")
        skill = Skill.from_file(src)

        reg = _make_registry(tmp_path)
        reg._skills["exists"] = skill
        installer = SkillInstaller(registry=reg)

        project = tmp_path / "project"
        results = installer.install_many(["exists", "nope"], "hermes", project_path=project)
        assert len(results) == 2
        assert results[0].success is True
        assert results[1].success is False
        assert "not found" in results[1].message.lower()
