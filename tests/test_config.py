"""Tests for agentforge.core.config — AgentForgeConfig."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from agentforge.core.config import AgentForgeConfig

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------


class TestConfigDefaults:
    """Test default values."""

    def test_defaults(self):
        cfg = AgentForgeConfig()
        assert cfg.default_agent == ""
        assert cfg.default_global is False
        assert cfg.preferred_categories == []
        assert cfg.auto_update is True
        assert cfg.editor == ""


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------


class TestConfigLoad:
    """Test AgentForgeConfig.load()."""

    def test_load_nonexistent_returns_defaults(self, tmp_path: Path):
        cfg = AgentForgeConfig.load(tmp_path / "missing.yml")
        assert cfg.default_agent == ""
        assert cfg.auto_update is True

    def test_load_valid_config(self, tmp_path: Path):
        data = {
            "default_agent": "hermes",
            "default_global": True,
            "preferred_categories": ["coding", "writing"],
            "auto_update": False,
            "editor": "vim",
        }
        cfg_file = tmp_path / "config.yml"
        cfg_file.write_text(yaml.dump(data), encoding="utf-8")
        cfg = AgentForgeConfig.load(cfg_file)
        assert cfg.default_agent == "hermes"
        assert cfg.default_global is True
        assert cfg.preferred_categories == ["coding", "writing"]
        assert cfg.auto_update is False
        assert cfg.editor == "vim"

    def test_load_partial_config(self, tmp_path: Path):
        data = {"default_agent": "claude"}
        cfg_file = tmp_path / "config.yml"
        cfg_file.write_text(yaml.dump(data), encoding="utf-8")
        cfg = AgentForgeConfig.load(cfg_file)
        assert cfg.default_agent == "claude"
        assert cfg.auto_update is True  # default

    def test_load_empty_file(self, tmp_path: Path):
        cfg_file = tmp_path / "config.yml"
        cfg_file.write_text("", encoding="utf-8")
        cfg = AgentForgeConfig.load(cfg_file)
        assert cfg.default_agent == ""

    def test_load_malformed_yaml(self, tmp_path: Path):
        cfg_file = tmp_path / "config.yml"
        cfg_file.write_text(": invalid: yaml: [[[\n", encoding="utf-8")
        cfg = AgentForgeConfig.load(cfg_file)
        assert cfg.default_agent == ""  # fallback to defaults

    def test_load_default_path(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("agentforge.core.config.user_data_dir", lambda: tmp_path / "data")
        cfg_dir = tmp_path / "data"
        cfg_dir.mkdir(parents=True)
        data = {"default_agent": "from-default-path"}
        (cfg_dir / "config.yml").write_text(yaml.dump(data), encoding="utf-8")
        cfg = AgentForgeConfig.load()
        assert cfg.default_agent == "from-default-path"

    def test_load_default_path_nonexistent(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("agentforge.core.config.user_data_dir", lambda: tmp_path / "nodir")
        cfg = AgentForgeConfig.load()
        assert cfg.default_agent == ""


# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------


class TestConfigSave:
    """Test AgentForgeConfig.save()."""

    def test_save_and_reload(self, tmp_path: Path):
        cfg_file = tmp_path / "config.yml"
        cfg = AgentForgeConfig(
            default_agent="hermes",
            default_global=True,
            preferred_categories=["ai"],
            auto_update=False,
            editor="nano",
        )
        cfg.save(cfg_file)

        reloaded = AgentForgeConfig.load(cfg_file)
        assert reloaded.default_agent == "hermes"
        assert reloaded.default_global is True
        assert reloaded.preferred_categories == ["ai"]
        assert reloaded.auto_update is False
        assert reloaded.editor == "nano"

    def test_save_creates_parent_dirs(self, tmp_path: Path):
        cfg_file = tmp_path / "deep" / "nested" / "config.yml"
        cfg = AgentForgeConfig(default_agent="test")
        cfg.save(cfg_file)
        assert cfg_file.exists()

    def test_save_default_path(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        data_dir = tmp_path / "data"
        monkeypatch.setattr("agentforge.core.config.user_data_dir", lambda: data_dir)
        cfg = AgentForgeConfig(default_agent="default-save")
        cfg.save()
        assert (data_dir / "config.yml").exists()

    def test_save_overwrites(self, tmp_path: Path):
        cfg_file = tmp_path / "config.yml"
        AgentForgeConfig(default_agent="first").save(cfg_file)
        AgentForgeConfig(default_agent="second").save(cfg_file)
        reloaded = AgentForgeConfig.load(cfg_file)
        assert reloaded.default_agent == "second"

    def test_save_yaml_content(self, tmp_path: Path):
        cfg_file = tmp_path / "config.yml"
        AgentForgeConfig(default_agent="yaml-test", auto_update=False).save(cfg_file)
        raw = cfg_file.read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
        assert data["default_agent"] == "yaml-test"
        assert data["auto_update"] is False
