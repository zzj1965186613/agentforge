"""Tests for agentforge.cli — CLI commands via click.testing.CliRunner."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from agentforge.cli.main import cli


@pytest.fixture
def runner():
    return CliRunner()


# ---------------------------------------------------------------------------
# Root CLI
# ---------------------------------------------------------------------------


class TestCLIRoot:
    """Test the root CLI group."""

    def test_help(self, runner: CliRunner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "AgentForge" in result.output

    def test_version(self, runner: CliRunner):
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_verbose_flag(self, runner: CliRunner):
        result = runner.invoke(cli, ["-v", "--help"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# agentforge list
# ---------------------------------------------------------------------------


class TestCLIList:
    """Test 'agentforge list' command."""

    def test_list_help(self, runner: CliRunner):
        result = runner.invoke(cli, ["list", "--help"])
        assert result.exit_code == 0
        assert "List available" in result.output

    def test_list_with_mocked_registry(self, runner: CliRunner):
        from agentforge.core.skill import Skill

        mock_skill = Skill(
            name="test-skill",
            version="1.0.0",
            category="testing",
            description="A test skill",
            tags=["test"],
        )

        mock_registry = MagicMock()
        mock_registry._skills = {"test-skill": mock_skill}
        mock_registry.scan_installed.return_value = [mock_skill]

        with patch("agentforge.cli.list_cmd._get_registry", return_value=mock_registry):
            result = runner.invoke(cli, ["list"])
            assert result.exit_code == 0

    def test_list_json_format(self, runner: CliRunner):
        from agentforge.core.skill import Skill

        mock_skill = Skill(
            name="json-skill",
            version="2.0.0",
            category="test",
            description="JSON test",
        )
        mock_registry = MagicMock()
        mock_registry._skills = {"json-skill": mock_skill}
        mock_registry.all_skills.return_value = [mock_skill]
        mock_registry.scan_installed.return_value = [mock_skill]

        with patch("agentforge.cli.list_cmd._get_registry", return_value=mock_registry):
            result = runner.invoke(cli, ["list", "--format", "json"])
            assert result.exit_code == 0
            assert "json-skill" in result.output

    def test_list_names_format(self, runner: CliRunner):
        from agentforge.core.skill import Skill

        mock_skill = Skill(name="name-skill", version="1.0.0", description="d")
        mock_registry = MagicMock()
        mock_registry._skills = {"name-skill": mock_skill}
        mock_registry.all_skills.return_value = [mock_skill]
        mock_registry.scan_installed.return_value = [mock_skill]

        with patch("agentforge.cli.list_cmd._get_registry", return_value=mock_registry):
            result = runner.invoke(cli, ["list", "--format", "names"])
            assert result.exit_code == 0
            assert "name-skill" in result.output

    def test_list_empty(self, runner: CliRunner):
        mock_registry = MagicMock()
        mock_registry._skills = {}
        mock_registry.all_skills.return_value = []
        mock_registry.scan_installed.return_value = []

        with patch("agentforge.cli.list_cmd._get_registry", return_value=mock_registry):
            result = runner.invoke(cli, ["list"])
            assert result.exit_code == 0
            assert "No skills found" in result.output

    def test_list_core_unavailable(self, runner: CliRunner):
        with patch("agentforge.cli.list_cmd._get_registry", return_value=None):
            result = runner.invoke(cli, ["list"])
            assert result.exit_code == 0


# ---------------------------------------------------------------------------
# agentforge search
# ---------------------------------------------------------------------------


class TestCLISearch:
    """Test 'agentforge search' command."""

    def test_search_help(self, runner: CliRunner):
        result = runner.invoke(cli, ["search", "--help"])
        assert result.exit_code == 0
        assert "QUERY" in result.output

    def test_search_with_results(self, runner: CliRunner):
        from agentforge.core.skill import Skill

        mock_skill = Skill(
            name="found-skill",
            version="1.0.0",
            category="test",
            description="Found it",
            tags=["search"],
        )
        mock_registry = MagicMock()
        mock_registry.search.return_value = [mock_skill]

        with patch("agentforge.cli.search._get_registry", return_value=mock_registry):
            result = runner.invoke(cli, ["search", "found"])
            assert result.exit_code == 0
            assert "found-skill" in result.output

    def test_search_no_results(self, runner: CliRunner):
        mock_registry = MagicMock()
        mock_registry.search.return_value = []

        with patch("agentforge.cli.search._get_registry", return_value=mock_registry):
            result = runner.invoke(cli, ["search", "nothing"])
            assert result.exit_code == 0
            assert "No skills found" in result.output

    def test_search_with_category_filter(self, runner: CliRunner):
        mock_registry = MagicMock()
        mock_registry.search.return_value = []

        with patch("agentforge.cli.search._get_registry", return_value=mock_registry):
            result = runner.invoke(cli, ["search", "test", "--category", "core"])
            assert result.exit_code == 0
            mock_registry.search.assert_called_once_with(query="test", category="core", tag="")

    def test_search_core_unavailable(self, runner: CliRunner):
        with patch("agentforge.cli.search._get_registry", return_value=None):
            result = runner.invoke(cli, ["search", "test"])
            assert result.exit_code == 0


# ---------------------------------------------------------------------------
# agentforge info
# ---------------------------------------------------------------------------


class TestCLIInfo:
    """Test 'agentforge info' command."""

    def test_info_help(self, runner: CliRunner):
        result = runner.invoke(cli, ["info", "--help"])
        assert result.exit_code == 0
        assert "SKILL_NAME" in result.output

    def test_info_found(self, runner: CliRunner):
        from agentforge.core.skill import Skill

        mock_skill = Skill(
            name="info-skill",
            version="1.0.0",
            description="An info skill",
            category="test",
            tags=["tag1"],
            author="tester",
            license="MIT",
        )
        mock_registry = MagicMock()
        mock_registry.get.return_value = mock_skill

        with patch("agentforge.cli.info._get_registry", return_value=mock_registry):
            result = runner.invoke(cli, ["info", "info-skill"])
            assert result.exit_code == 0
            assert "info-skill" in result.output

    def test_info_not_found(self, runner: CliRunner):
        mock_registry = MagicMock()
        mock_registry.get.return_value = None

        with patch("agentforge.cli.info._get_registry", return_value=mock_registry):
            result = runner.invoke(cli, ["info", "missing"])
            assert result.exit_code == 0
            assert "not found" in result.output.lower()

    def test_info_core_unavailable(self, runner: CliRunner):
        with patch("agentforge.cli.info._get_registry", return_value=None):
            result = runner.invoke(cli, ["info", "test"])
            assert result.exit_code == 0


# ---------------------------------------------------------------------------
# agentforge install
# ---------------------------------------------------------------------------


class TestCLIInstall:
    """Test 'agentforge install' command."""

    def test_install_help(self, runner: CliRunner):
        result = runner.invoke(cli, ["install", "--help"])
        assert result.exit_code == 0
        assert "SKILL" in result.output

    def test_install_no_args_shows_error(self, runner: CliRunner):
        result = runner.invoke(cli, ["install"])
        assert result.exit_code != 0  # click requires at least one argument

    def test_install_dry_run(self, runner: CliRunner):
        from agentforge.core.resolver import Resolution
        from agentforge.core.skill import Skill

        mock_registry = MagicMock()
        mock_registry.get.return_value = Skill(name="s", version="1.0.0", description="d")

        mock_resolver_inst = MagicMock()
        mock_resolver_inst.resolve.return_value = Resolution(to_install=["s"])

        with (
            patch("agentforge.cli._utils.get_installer", return_value=(MagicMock(), mock_registry)),
            patch("agentforge.cli.install.DependencyResolver", return_value=mock_resolver_inst),
        ):
            result = runner.invoke(cli, ["install", "s", "--dry-run"])
            assert result.exit_code == 0
            assert "DRY RUN" in result.output


# ---------------------------------------------------------------------------
# agentforge uninstall
# ---------------------------------------------------------------------------


class TestCLIUninstall:
    """Test 'agentforge uninstall' command."""

    def test_uninstall_help(self, runner: CliRunner):
        result = runner.invoke(cli, ["uninstall", "--help"])
        assert result.exit_code == 0
        assert "SKILL" in result.output

    def test_uninstall_no_args_shows_error(self, runner: CliRunner):
        result = runner.invoke(cli, ["uninstall"])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# agentforge init
# ---------------------------------------------------------------------------


class TestCLIInit:
    """Test 'agentforge init' command."""

    def test_init_help(self, runner: CliRunner):
        result = runner.invoke(cli, ["init", "--help"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# agentforge update
# ---------------------------------------------------------------------------


class TestCLIUpdate:
    """Test 'agentforge update' command."""

    def test_update_help(self, runner: CliRunner):
        result = runner.invoke(cli, ["update", "--help"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# agentforge share
# ---------------------------------------------------------------------------


class TestCLIShare:
    """Test 'agentforge share' command."""

    def test_share_help(self, runner: CliRunner):
        result = runner.invoke(cli, ["share", "--help"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# agentforge config
# ---------------------------------------------------------------------------


class TestCLIConfig:
    """Test 'agentforge config' command."""

    def test_config_help(self, runner: CliRunner):
        result = runner.invoke(cli, ["config", "--help"])
        assert result.exit_code == 0
