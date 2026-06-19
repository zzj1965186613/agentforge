"""Shared pytest fixtures for AgentForge tests."""

from __future__ import annotations

import shutil
import textwrap
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_skill_path() -> Path:
    """Return the path to the bundled sample skill fixture."""
    return Path(__file__).parent / "fixtures" / "sample_skill.md"


@pytest.fixture
def invalid_skill_path() -> Path:
    """Return the path to the invalid skill fixture."""
    return Path(__file__).parent / "fixtures" / "invalid_skill.md"


# ---------------------------------------------------------------------------
# Skill data
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_skill() -> dict:
    """Return a parsed skill dictionary matching the sample fixture."""
    return {
        "name": "test-skill",
        "version": "1.0.0",
        "description": "A sample skill for testing purposes.",
        "category": "testing",
        "tags": ["test", "sample", "fixture"],
        "agent_compatibility": ["claude_code", "cursor", "copilot", "aider", "hermes"],
        "body": textwrap.dedent("""\
            ## System Prompt

            You are a test helper.

            ## Instructions

            1. Read the input.
            2. Echo it back.

            ## Output Format

            ```
            Echo: <input>
            ```

            ## Examples

            Input: "hello"
            Output: "Echo: hello"
        """),
    }


# ---------------------------------------------------------------------------
# Temporary directories
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_agentforge(tmp_path: Path) -> Path:
    """Create a temporary AgentForge directory structure.

    Returns the root path.  The directory tree looks like::

        <tmp>/
            skills/
            agents/
            marketplace/
    """
    root = tmp_path / "agentforge"
    for subdir in ("skills", "agents", "marketplace", "cache"):
        (root / subdir).mkdir(parents=True)
    return root


@pytest.fixture
def mock_claude_project(tmp_path: Path) -> Path:
    """Create a fake project directory that looks like a Claude Code project.

    Returns the project root which contains a ``.claude/commands/`` directory.
    """
    project = tmp_path / "my-project"
    (project / ".claude" / "commands").mkdir(parents=True)
    # Add a sample existing command
    (project / ".claude" / "commands" / "existing.md").write_text(
        "# Existing Command\n\nThis was already here.\n",
        encoding="utf-8",
    )
    return project


@pytest.fixture
def mock_cursor_project(tmp_path: Path) -> Path:
    """Create a fake project directory with a ``.cursor`` directory."""
    project = tmp_path / "cursor-project"
    (project / ".cursor" / "rules").mkdir(parents=True)
    return project


@pytest.fixture
def mock_hermes_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Override ``Path.home()`` so HermesAdapter writes to a temp directory.

    Returns the fake home path.
    """
    fake_home = tmp_path / "fake-home"
    (fake_home / ".hermes" / "skills").mkdir(parents=True)

    original_home = Path.home

    def _fake_home() -> Path:
        return fake_home

    monkeypatch.setattr(Path, "home", staticmethod(_fake_home))
    yield fake_home
    # Restore
    monkeypatch.setattr(Path, "home", staticmethod(original_home))
