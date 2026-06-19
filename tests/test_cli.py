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

        with patch("agentforge.cli.list_cmd.get_registry", return_value=mock_registry):
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

        with patch("agentforge.cli.list_cmd.get_registry", return_value=mock_registry):
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

        with patch("agentforge.cli.list_cmd.get_registry", return_value=mock_registry):
            result = runner.invoke(cli, ["list", "--format", "names"])
            assert result.exit_code == 0
            assert "name-skill" in result.output

    def test_list_empty(self, runner: CliRunner):
        mock_registry = MagicMock()
        mock_registry._skills = {}
        mock_registry.all_skills.return_value = []
        mock_registry.scan_installed.return_value = []

        with patch("agentforge.cli.list_cmd.get_registry", return_value=mock_registry):
            result = runner.invoke(cli, ["list"])
            assert result.exit_code == 0
            assert "No skills found" in result.output

    def test_list_core_unavailable(self, runner: CliRunner):
        with patch("agentforge.cli.list_cmd.get_registry", return_value=None):
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

        with patch("agentforge.cli.search.get_registry", return_value=mock_registry):
            result = runner.invoke(cli, ["search", "found"])
            assert result.exit_code == 0
            assert "found-skill" in result.output

    def test_search_no_results(self, runner: CliRunner):
        mock_registry = MagicMock()
        mock_registry.search.return_value = []

        with patch("agentforge.cli.search.get_registry", return_value=mock_registry):
            result = runner.invoke(cli, ["search", "nothing"])
            assert result.exit_code == 0
            assert "No skills found" in result.output

    def test_search_with_category_filter(self, runner: CliRunner):
        mock_registry = MagicMock()
        mock_registry.search.return_value = []

        with patch("agentforge.cli.search.get_registry", return_value=mock_registry):
            result = runner.invoke(cli, ["search", "test", "--category", "core"])
            assert result.exit_code == 0
            mock_registry.search.assert_called_once_with(query="test", category="core", tag="")

    def test_search_core_unavailable(self, runner: CliRunner):
        with patch("agentforge.cli.search.get_registry", return_value=None):
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

        with patch("agentforge.cli.info.get_registry", return_value=mock_registry):
            result = runner.invoke(cli, ["info", "info-skill"])
            assert result.exit_code == 0
            assert "info-skill" in result.output

    def test_info_not_found(self, runner: CliRunner):
        mock_registry = MagicMock()
        mock_registry.get.return_value = None

        with patch("agentforge.cli.info.get_registry", return_value=mock_registry):
            result = runner.invoke(cli, ["info", "missing"])
            assert result.exit_code == 0
            assert "not found" in result.output.lower()

    def test_info_core_unavailable(self, runner: CliRunner):
        with patch("agentforge.cli.info.get_registry", return_value=None):
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


# ---------------------------------------------------------------------------
# agentforge update — Functional tests
# ---------------------------------------------------------------------------


class TestCLIUpdateFunctional:
    """Functional tests for 'agentforge update' command."""

    def test_update_single_success(self, runner: CliRunner):
        from agentforge.core.installer import InstallResult
        from agentforge.core.skill import Skill

        mock_skill = Skill(name="my-skill", version="1.0.0", description="d", installed=True)
        mock_registry = MagicMock()
        mock_registry.get.return_value = mock_skill

        mock_installer = MagicMock()
        mock_installer.install.return_value = InstallResult(
            success=True, skill_name="my-skill", message="Installed"
        )

        _patch_tgt = "agentforge.cli.update.get_installer"
        with patch(_patch_tgt, return_value=(mock_installer, mock_registry)):
            result = runner.invoke(cli, ["update", "my-skill"])
            assert result.exit_code == 0
            mock_installer.install.assert_called_once()
            assert mock_installer.install.call_args[1].get("force") is True

    def test_update_single_not_found(self, runner: CliRunner):
        mock_registry = MagicMock()
        mock_registry.get.return_value = None
        mock_installer = MagicMock()

        _patch_tgt = "agentforge.cli.update.get_installer"
        with patch(_patch_tgt, return_value=(mock_installer, mock_registry)):
            result = runner.invoke(cli, ["update", "nonexistent"])
            assert result.exit_code == 0
            assert "not found" in result.output.lower()

    def test_update_single_not_installed(self, runner: CliRunner):
        from agentforge.core.skill import Skill

        mock_skill = Skill(name="my-skill", version="1.0.0", description="d", installed=False)
        mock_registry = MagicMock()
        mock_registry.get.return_value = mock_skill
        mock_installer = MagicMock()

        _patch_tgt = "agentforge.cli.update.get_installer"
        with patch(_patch_tgt, return_value=(mock_installer, mock_registry)):
            result = runner.invoke(cli, ["update", "my-skill"])
            assert result.exit_code == 0
            assert "not installed" in result.output.lower()

    def test_update_all_with_installed(self, runner: CliRunner):
        from agentforge.core.installer import InstallResult
        from agentforge.core.skill import Skill

        sk1 = Skill(name="skill-a", version="1.0.0", description="a", installed=True)
        sk2 = Skill(name="skill-b", version="2.0.0", description="b", installed=True)

        mock_registry = MagicMock()
        mock_registry.all_skills.return_value = [sk1, sk2]

        mock_installer = MagicMock()
        mock_installer.install.return_value = InstallResult(
            success=True, skill_name="test", message="ok"
        )

        _patch_tgt = "agentforge.cli.update.get_installer"
        with patch(_patch_tgt, return_value=(mock_installer, mock_registry)):
            result = runner.invoke(cli, ["update", "--all"])
            assert result.exit_code == 0
            assert mock_installer.install.call_count == 2

    def test_update_all_no_installed(self, runner: CliRunner):
        mock_registry = MagicMock()
        mock_registry.all_skills.return_value = []
        mock_installer = MagicMock()

        _patch_tgt = "agentforge.cli.update.get_installer"
        with patch(_patch_tgt, return_value=(mock_installer, mock_registry)):
            result = runner.invoke(cli, ["update", "--all"])
            assert result.exit_code == 0
            assert "No installed skills found" in result.output

    def test_update_check_shows_table(self, runner: CliRunner):
        from agentforge.core.skill import Skill

        sk1 = Skill(name="skill-a", version="1.0.0", description="a", installed=True)
        sk2 = Skill(name="skill-b", version="2.0.0", description="b", installed=True)

        mock_registry = MagicMock()
        mock_registry.all_skills.return_value = [sk1, sk2]
        mock_installer = MagicMock()

        _patch_tgt = "agentforge.cli.update.get_installer"
        with patch(_patch_tgt, return_value=(mock_installer, mock_registry)):
            result = runner.invoke(cli, ["update", "--check"])
            assert result.exit_code == 0
            assert "skill-a" in result.output
            assert "skill-b" in result.output


# ---------------------------------------------------------------------------
# agentforge share — Functional tests
# ---------------------------------------------------------------------------


class TestCLIShareFunctional:
    """Functional tests for 'agentforge share' command."""

    def test_share_to_file(self, runner: CliRunner, tmp_path):
        from agentforge.core.skill import Skill

        source = tmp_path / "my-skill.md"
        source.write_text("# My Skill\nContent here")

        mock_skill = Skill(name="my-skill", version="1.0.0", description="d", source_path=source)
        mock_registry = MagicMock()
        mock_registry.get.return_value = mock_skill

        output_file = tmp_path / "output.md"

        with patch("agentforge.cli.share.get_registry", return_value=mock_registry):
            result = runner.invoke(cli, ["share", "my-skill", "--output", str(output_file)])
            assert result.exit_code == 0
            assert output_file.exists()
            assert "My Skill" in output_file.read_text()

    def test_share_not_found(self, runner: CliRunner):
        mock_registry = MagicMock()
        mock_registry.get.return_value = None

        with patch("agentforge.cli.share.get_registry", return_value=mock_registry):
            result = runner.invoke(cli, ["share", "nonexistent"])
            assert result.exit_code == 0
            assert "not found" in result.output.lower()

    def test_share_no_source(self, runner: CliRunner):
        from agentforge.core.skill import Skill

        mock_skill = Skill(name="my-skill", version="1.0.0", description="d", source_path=None)
        mock_registry = MagicMock()
        mock_registry.get.return_value = mock_skill

        with patch("agentforge.cli.share.get_registry", return_value=mock_registry):
            result = runner.invoke(cli, ["share", "my-skill"])
            assert result.exit_code == 0
            assert "could not read" in result.output.lower()

    def test_share_to_stdout(self, runner: CliRunner, tmp_path):
        from agentforge.core.skill import Skill

        source = tmp_path / "my-skill.md"
        source.write_text("# Test Skill\nHello world")

        mock_skill = Skill(name="my-skill", version="1.0.0", description="d", source_path=source)
        mock_registry = MagicMock()
        mock_registry.get.return_value = mock_skill

        with patch("agentforge.cli.share.get_registry", return_value=mock_registry):
            result = runner.invoke(cli, ["share", "my-skill"])
            assert result.exit_code == 0
            assert "Test Skill" in result.output


# ---------------------------------------------------------------------------
# agentforge init — Functional tests
# ---------------------------------------------------------------------------


class TestCLIInitFunctional:
    """Functional tests for 'agentforge init' command."""

    def test_init_with_agent_flag(self, runner: CliRunner, tmp_path):
        with patch("agentforge.cli.init_cmd.AgentForgeConfig") as mock_config:
            mock_cfg = MagicMock()
            mock_config.return_value = mock_cfg

            result = runner.invoke(cli, ["init", "--agent", "claude_code", "--path", str(tmp_path)])
            assert result.exit_code == 0
            assert (tmp_path / ".agentforge").is_dir()
            mock_cfg.save.assert_called_once()

    def test_init_auto_detect_claude(self, runner: CliRunner, tmp_path):
        (tmp_path / ".claude").mkdir()

        with patch("agentforge.cli.init_cmd.AgentForgeConfig") as mock_config:
            mock_cfg = MagicMock()
            mock_config.return_value = mock_cfg

            result = runner.invoke(cli, ["init", "--path", str(tmp_path)])
            assert result.exit_code == 0
            assert "claude_code" in result.output

    def test_init_creates_directory(self, runner: CliRunner, tmp_path):
        with patch("agentforge.cli.init_cmd.AgentForgeConfig") as mock_config:
            mock_cfg = MagicMock()
            mock_config.return_value = mock_cfg

            result = runner.invoke(cli, ["init", "--agent", "hermes", "--path", str(tmp_path)])
            assert result.exit_code == 0
            assert (tmp_path / ".agentforge").is_dir()


# ---------------------------------------------------------------------------
# agentforge config — Functional tests
# ---------------------------------------------------------------------------


class TestCLIConfigFunctional:
    """Functional tests for 'agentforge config' command."""

    def test_config_show(self, runner: CliRunner, tmp_path, monkeypatch):
        import yaml

        config_dir = tmp_path / "agentforge"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_data = {
            "default_agent": "hermes",
            "default_global": False,
            "preferred_categories": [],
            "auto_update": True,
            "editor": "",
        }
        (config_dir / "config.yml").write_text(yaml.dump(config_data))

        monkeypatch.setattr("agentforge.core.config.user_data_dir", lambda: config_dir)

        result = runner.invoke(cli, ["config", "show"])
        assert result.exit_code == 0
        assert "default_agent" in result.output
        assert "hermes" in result.output

    def test_config_set(self, runner: CliRunner, tmp_path, monkeypatch):
        import yaml

        config_dir = tmp_path / "agentforge"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_data = {
            "default_agent": "",
            "default_global": False,
            "preferred_categories": [],
            "auto_update": True,
            "editor": "",
        }
        (config_dir / "config.yml").write_text(yaml.dump(config_data))

        monkeypatch.setattr("agentforge.core.config.user_data_dir", lambda: config_dir)

        result = runner.invoke(cli, ["config", "set", "default_agent", "hermes"])
        assert result.exit_code == 0
        assert "hermes" in result.output

        updated = yaml.safe_load((config_dir / "config.yml").read_text())
        assert updated["default_agent"] == "hermes"

    def test_config_set_invalid_key(self, runner: CliRunner, tmp_path, monkeypatch):
        import yaml

        config_dir = tmp_path / "agentforge"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_data = {
            "default_agent": "",
            "default_global": False,
            "preferred_categories": [],
            "auto_update": True,
            "editor": "",
        }
        (config_dir / "config.yml").write_text(yaml.dump(config_data))

        monkeypatch.setattr("agentforge.core.config.user_data_dir", lambda: config_dir)

        result = runner.invoke(cli, ["config", "set", "nonexistent", "value"])
        assert result.exit_code == 0
        assert "Unknown config key" in result.output

    def test_config_reset(self, runner: CliRunner, tmp_path, monkeypatch):
        import yaml

        config_dir = tmp_path / "agentforge"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_data = {
            "default_agent": "custom_agent",
            "default_global": True,
            "preferred_categories": ["cat1"],
            "auto_update": False,
            "editor": "vim",
        }
        (config_dir / "config.yml").write_text(yaml.dump(config_data))

        monkeypatch.setattr("agentforge.core.config.user_data_dir", lambda: config_dir)

        result = runner.invoke(cli, ["config", "reset"])
        assert result.exit_code == 0
        assert "reset to defaults" in result.output.lower()

        updated = yaml.safe_load((config_dir / "config.yml").read_text())
        assert updated["default_agent"] == ""
        assert updated["auto_update"] is True


# ---------------------------------------------------------------------------
# agentforge uninstall — Functional tests
# ---------------------------------------------------------------------------


class TestCLIUninstallFunctional:
    """Functional tests for 'agentforge uninstall' command."""

    def test_uninstall_confirmation_prompt(self, runner: CliRunner):
        from agentforge.core.installer import InstallResult

        mock_installer = MagicMock()
        mock_installer.uninstall.return_value = InstallResult(
            success=True, skill_name="test", message="ok"
        )
        mock_registry = MagicMock()

        _patch_tgt = "agentforge.cli.uninstall.get_installer"
        with patch(_patch_tgt, return_value=(mock_installer, mock_registry)):
            result = runner.invoke(cli, ["uninstall", "skill-a", "skill-b"], input="n\n")
            assert result.exit_code == 0
            assert "Cancelled" in result.output
            mock_installer.uninstall.assert_not_called()

    def test_uninstall_yes_flag_skips_prompt(self, runner: CliRunner):
        from agentforge.core.installer import InstallResult

        mock_installer = MagicMock()
        mock_installer.uninstall.return_value = InstallResult(
            success=True, skill_name="test", message="ok"
        )
        mock_registry = MagicMock()

        _patch_tgt = "agentforge.cli.uninstall.get_installer"
        with patch(_patch_tgt, return_value=(mock_installer, mock_registry)):
            result = runner.invoke(cli, ["uninstall", "skill-a", "skill-b", "--yes"])
            assert result.exit_code == 0
            assert mock_installer.uninstall.call_count == 2

    def test_uninstall_single_no_prompt(self, runner: CliRunner):
        from agentforge.core.installer import InstallResult

        mock_installer = MagicMock()
        mock_installer.uninstall.return_value = InstallResult(
            success=True, skill_name="test", message="ok"
        )
        mock_registry = MagicMock()

        _patch_tgt = "agentforge.cli.uninstall.get_installer"
        with patch(_patch_tgt, return_value=(mock_installer, mock_registry)):
            result = runner.invoke(cli, ["uninstall", "skill-a"])
            assert result.exit_code == 0
            assert mock_installer.uninstall.call_count == 1


# ---------------------------------------------------------------------------
# agentforge install — Functional tests
# ---------------------------------------------------------------------------


class TestCLIInstallFunctional:
    """Functional tests for 'agentforge install' command."""

    def test_install_success(self, runner: CliRunner):
        from agentforge.core.installer import InstallResult
        from agentforge.core.resolver import Resolution
        from agentforge.core.skill import Skill

        mock_skill = Skill(name="my-skill", version="1.0.0", description="d")
        mock_registry = MagicMock()
        mock_registry.get.return_value = mock_skill

        mock_installer = MagicMock()
        mock_installer.install_many.return_value = [
            InstallResult(success=True, skill_name="my-skill", message="Installed")
        ]

        mock_resolver = MagicMock()
        mock_resolver.resolve.return_value = Resolution(to_install=["my-skill"])

        _installer_patcher = patch(
            "agentforge.cli.install.get_installer",
            return_value=(mock_installer, mock_registry),
        )
        with (
            _installer_patcher,
            patch("agentforge.cli.install.DependencyResolver", return_value=mock_resolver),
        ):
            result = runner.invoke(cli, ["install", "my-skill"])
            assert result.exit_code == 0
            assert "my-skill" in result.output

    def test_install_with_conflict(self, runner: CliRunner):
        from agentforge.core.resolver import Resolution

        mock_registry = MagicMock()
        mock_installer = MagicMock()

        mock_resolver = MagicMock()
        mock_resolver.resolve.return_value = Resolution(
            conflicts=["skill-a conflicts with skill-b"]
        )

        _installer_patcher = patch(
            "agentforge.cli.install.get_installer",
            return_value=(mock_installer, mock_registry),
        )
        with (
            _installer_patcher,
            patch("agentforge.cli.install.DependencyResolver", return_value=mock_resolver),
        ):
            result = runner.invoke(cli, ["install", "skill-a", "skill-b"])
            assert result.exit_code == 0
            assert "Conflict" in result.output
