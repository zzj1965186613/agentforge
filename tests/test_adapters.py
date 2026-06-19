"""Comprehensive tests for all agent adapters."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from agentforge.agents.aider import AiderAdapter
from agentforge.agents.base import SimpleAgentAdapter
from agentforge.agents.claude_code import ClaudeCodeAdapter
from agentforge.agents.copilot import CopilotAdapter
from agentforge.agents.cursor import CursorAdapter
from agentforge.agents.hermes import HermesAdapter

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SAMPLE_RENDERED = textwrap.dedent("""\
    ---
    name: test-skill
    version: "1.0.0"
    description: A sample skill for testing.
    ---

    ## Instructions

    Do the thing.
""")

SAMPLE_RENDERED_2 = textwrap.dedent("""\
    ---
    name: another-skill
    version: "2.0.0"
    description: Another sample skill.
    ---

    ## Instructions

    Do the other thing.
""")


def _make_skill(name: str = "test-skill") -> dict:
    """Return a minimal skill dict."""
    return {
        "name": name,
        "version": "1.0.0",
        "description": "A sample skill for testing.",
        "category": "testing",
        "tags": ["test"],
        "agent_compatibility": ["claude_code", "cursor", "copilot", "aider", "hermes"],
        "body": "## Instructions\n\nDo the thing.\n",
    }


# ===========================================================================
# TestClaudeCodeAdapter
# ===========================================================================


class TestClaudeCodeAdapter:
    """Tests for the Claude Code adapter."""

    def test_detect_positive(self, tmp_path: Path) -> None:
        project = tmp_path / "my-project"
        (project / ".claude").mkdir(parents=True)
        adapter = ClaudeCodeAdapter()
        assert adapter.detect(project) is True

    def test_detect_negative(self, tmp_path: Path) -> None:
        project = tmp_path / "bare-project"
        project.mkdir()
        adapter = ClaudeCodeAdapter()
        assert adapter.detect(project) is False

    def test_install_path_project(self, tmp_path: Path) -> None:
        project = tmp_path / "proj"
        adapter = ClaudeCodeAdapter()
        result = adapter.install_path(project, global_install=False)
        assert result == project / ".claude" / "commands"

    def test_install_path_global(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        fake_home = tmp_path / "home"
        monkeypatch.setattr(Path, "home", staticmethod(lambda: fake_home))
        adapter = ClaudeCodeAdapter()
        result = adapter.install_path(tmp_path / "proj", global_install=True)
        assert result == fake_home / ".claude" / "commands"

    def test_install_uninstall_roundtrip(self, tmp_path: Path) -> None:
        project = tmp_path / "proj"
        project.mkdir()
        adapter = ClaudeCodeAdapter()

        # Install
        dest = adapter.install_skill(_make_skill(), SAMPLE_RENDERED, project, global_install=False)
        assert dest.exists()
        assert dest.read_text(encoding="utf-8") == SAMPLE_RENDERED

        # Uninstall
        removed = adapter.uninstall_skill("test-skill", project, global_install=False)
        assert removed is True
        assert not dest.exists()

        # Uninstall again returns False
        assert adapter.uninstall_skill("test-skill", project, global_install=False) is False

    def test_list_installed(self, tmp_path: Path) -> None:
        project = tmp_path / "proj"
        project.mkdir()
        adapter = ClaudeCodeAdapter()

        adapter.install_skill(_make_skill("alpha"), SAMPLE_RENDERED, project, global_install=False)
        adapter.install_skill(_make_skill("beta"), SAMPLE_RENDERED_2, project, global_install=False)

        installed = adapter.list_installed(project, global_install=False)
        assert installed == ["alpha", "beta"]


# ===========================================================================
# TestCursorAdapter
# ===========================================================================


class TestCursorAdapter:
    """Tests for the Cursor adapter."""

    def test_detect_with_cursor_dir(self, tmp_path: Path) -> None:
        project = tmp_path / "proj"
        (project / ".cursor").mkdir(parents=True)
        adapter = CursorAdapter()
        assert adapter.detect(project) is True

    def test_detect_with_cursorrules(self, tmp_path: Path) -> None:
        project = tmp_path / "proj"
        project.mkdir()
        (project / ".cursorrules").write_text("# rules\n", encoding="utf-8")
        adapter = CursorAdapter()
        assert adapter.detect(project) is True

    def test_detect_negative(self, tmp_path: Path) -> None:
        project = tmp_path / "proj"
        project.mkdir()
        adapter = CursorAdapter()
        assert adapter.detect(project) is False

    def test_install_path(self, tmp_path: Path) -> None:
        project = tmp_path / "proj"
        adapter = CursorAdapter()
        result = adapter.install_path(project, global_install=False)
        assert result == project / ".cursor" / "rules"


# ===========================================================================
# TestCopilotAdapter
# ===========================================================================


class TestCopilotAdapter:
    """Tests for the GitHub Copilot adapter."""

    def test_detect_with_instructions_dir(self, tmp_path: Path) -> None:
        project = tmp_path / "proj"
        (project / ".github" / "copilot-instructions").mkdir(parents=True)
        adapter = CopilotAdapter()
        assert adapter.detect(project) is True

    def test_detect_with_instructions_file(self, tmp_path: Path) -> None:
        project = tmp_path / "proj"
        (project / ".github").mkdir(parents=True)
        (project / ".github" / "copilot-instructions.md").write_text(
            "# Instructions\n", encoding="utf-8"
        )
        adapter = CopilotAdapter()
        assert adapter.detect(project) is True

    def test_install_path(self, tmp_path: Path) -> None:
        project = tmp_path / "proj"
        adapter = CopilotAdapter()
        result = adapter.install_path(project, global_install=False)
        assert result == project / ".github" / "copilot-instructions"


# ===========================================================================
# TestAiderAdapter
# ===========================================================================


class TestAiderAdapter:
    """Tests for the Aider adapter."""

    def test_detect_with_aider_dir(self, tmp_path: Path) -> None:
        project = tmp_path / "proj"
        (project / ".aider").mkdir(parents=True)
        adapter = AiderAdapter()
        assert adapter.detect(project) is True

    def test_detect_with_config(self, tmp_path: Path) -> None:
        project = tmp_path / "proj"
        project.mkdir()
        (project / ".aider.conf.yml").write_text("auto-commits: false\n", encoding="utf-8")
        adapter = AiderAdapter()
        assert adapter.detect(project) is True

    def test_install_path(self, tmp_path: Path) -> None:
        project = tmp_path / "proj"
        adapter = AiderAdapter()
        result = adapter.install_path(project, global_install=False)
        assert result == project / ".aider" / "skills"


# ===========================================================================
# TestHermesAdapter
# ===========================================================================


class TestHermesAdapter:
    """Tests for the Hermes Agent adapter."""

    def test_detect_positive(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        fake_home = tmp_path / "home"
        (fake_home / ".hermes").mkdir(parents=True)
        monkeypatch.setattr(Path, "home", staticmethod(lambda: fake_home))
        adapter = HermesAdapter()
        assert adapter.detect(tmp_path / "any-project") is True

    def test_detect_negative(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        monkeypatch.setattr(Path, "home", staticmethod(lambda: fake_home))
        adapter = HermesAdapter()
        assert adapter.detect(tmp_path / "any-project") is False

    def test_install_path_always_global(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        fake_home = tmp_path / "home"
        monkeypatch.setattr(Path, "home", staticmethod(lambda: fake_home))
        adapter = HermesAdapter()
        project = tmp_path / "proj"

        path_local = adapter.install_path(project, global_install=False)
        path_global = adapter.install_path(project, global_install=True)
        expected = fake_home / ".hermes" / "skills"
        assert path_local == expected
        assert path_global == expected

    def test_subdirectory_pattern(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        fake_home = tmp_path / "home"
        (fake_home / ".hermes" / "skills").mkdir(parents=True)
        monkeypatch.setattr(Path, "home", staticmethod(lambda: fake_home))

        adapter = HermesAdapter()
        dest = adapter.install_skill(
            _make_skill("my skill"),
            SAMPLE_RENDERED,
            tmp_path / "proj",
            False,
        )

        # Should be ~/.hermes/skills/my-skill/skill.md, not ~/.hermes/skills/my-skill.md
        assert dest.name == "skill.md"
        assert dest.parent.name == "my-skill"
        assert dest.exists()
        assert not (fake_home / ".hermes" / "skills" / "my-skill.md").exists()

    def test_uninstall_removes_empty_dir(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        fake_home = tmp_path / "home"
        (fake_home / ".hermes" / "skills").mkdir(parents=True)
        monkeypatch.setattr(Path, "home", staticmethod(lambda: fake_home))

        adapter = HermesAdapter()
        adapter.install_skill(_make_skill("ephemeral"), SAMPLE_RENDERED, tmp_path / "proj", False)

        skill_dir = fake_home / ".hermes" / "skills" / "ephemeral"
        assert skill_dir.is_dir()

        removed = adapter.uninstall_skill("ephemeral", tmp_path / "proj", False)
        assert removed is True
        assert not skill_dir.exists(), "Empty skill directory should be removed"

    def test_uninstall_keeps_nonempty_dir(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        fake_home = tmp_path / "home"
        (fake_home / ".hermes" / "skills").mkdir(parents=True)
        monkeypatch.setattr(Path, "home", staticmethod(lambda: fake_home))

        adapter = HermesAdapter()
        adapter.install_skill(_make_skill("with-extra"), SAMPLE_RENDERED, tmp_path / "proj", False)

        # Drop an extra file in the skill directory
        skill_dir = fake_home / ".hermes" / "skills" / "with-extra"
        (skill_dir / "extra-resource.txt").write_text("don't delete me\n", encoding="utf-8")

        removed = adapter.uninstall_skill("with-extra", tmp_path / "proj", False)
        assert removed is True
        assert skill_dir.is_dir(), "Non-empty directory should be kept"
        assert (skill_dir / "extra-resource.txt").exists()
        assert not (skill_dir / "skill.md").exists()

    def test_list_installed(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        fake_home = tmp_path / "home"
        (fake_home / ".hermes" / "skills").mkdir(parents=True)
        monkeypatch.setattr(Path, "home", staticmethod(lambda: fake_home))

        adapter = HermesAdapter()
        adapter.install_skill(
            _make_skill("alpha-skill"),
            SAMPLE_RENDERED,
            tmp_path / "proj",
            False,
        )
        adapter.install_skill(
            _make_skill("beta-skill"),
            SAMPLE_RENDERED_2,
            tmp_path / "proj",
            False,
        )

        installed = adapter.list_installed(tmp_path / "proj", False)
        assert installed == ["alpha-skill", "beta-skill"]


# ===========================================================================
# TestSimpleAgentAdapter
# ===========================================================================


class _DummyAdapter(SimpleAgentAdapter):
    """Minimal concrete adapter for testing SimpleAgentAdapter defaults."""

    @property
    def name(self) -> str:
        return "dummy"

    @property
    def display_name(self) -> str:
        return "Dummy"

    def detect(self, project_path: Path) -> bool:
        return True

    def install_path(self, project_path: Path, global_install: bool) -> Path:
        return project_path / ".dummy" / "skills"


class TestSimpleAgentAdapter:
    """Tests for the SimpleAgentAdapter base class defaults."""

    def test_skill_filename(self) -> None:
        adapter = _DummyAdapter()
        assert adapter.skill_filename("My Cool Skill") == "my-cool-skill.md"
        assert adapter.skill_filename("already-lowercase") == "already-lowercase.md"
        assert adapter.skill_filename("UPPER") == "upper.md"

    def test_install_write_read(self, tmp_path: Path) -> None:
        project = tmp_path / "proj"
        project.mkdir()
        adapter = _DummyAdapter()

        dest = adapter.install_skill(_make_skill("reader"), SAMPLE_RENDERED, project, False)
        assert dest.exists()
        content = dest.read_text(encoding="utf-8")
        assert content == SAMPLE_RENDERED

    def test_list_installed_empty_dir(self, tmp_path: Path) -> None:
        project = tmp_path / "proj"
        (project / ".dummy" / "skills").mkdir(parents=True)
        adapter = _DummyAdapter()
        assert adapter.list_installed(project, False) == []
