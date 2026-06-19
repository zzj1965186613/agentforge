"""Tests for agentforge.core.skill — Skill and SkillVariable dataclasses."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentforge.core.skill import Skill, SkillVariable


# ---------------------------------------------------------------------------
# SkillVariable
# ---------------------------------------------------------------------------


class TestSkillVariable:
    """Tests for SkillVariable."""

    def test_defaults(self):
        v = SkillVariable(name="x")
        assert v.name == "x"
        assert v.description == ""
        assert v.default is None
        assert v.required is False

    def test_from_dict_minimal(self):
        v = SkillVariable.from_dict({"name": "foo"})
        assert v.name == "foo"
        assert v.description == ""
        assert v.default is None
        assert v.required is False

    def test_from_dict_full(self):
        v = SkillVariable.from_dict({
            "name": "bar",
            "description": "A bar variable",
            "default": "baz",
            "required": True,
        })
        assert v.name == "bar"
        assert v.description == "A bar variable"
        assert v.default == "baz"
        assert v.required is True

    def test_from_dict_empty(self):
        v = SkillVariable.from_dict({})
        assert v.name == ""


# ---------------------------------------------------------------------------
# Skill.from_string
# ---------------------------------------------------------------------------


class TestSkillFromString:
    """Tests for Skill.from_string()."""

    def test_valid_skill(self, sample_skill_path: Path):
        content = sample_skill_path.read_text(encoding="utf-8")
        skill = Skill.from_string(content)
        assert skill.name == "test-skill"
        assert skill.version == "1.0.0"
        assert skill.description == "A sample skill for testing purposes."
        assert skill.category == "testing"
        assert skill.tags == ["test", "sample", "fixture"]
        assert "claude_code" in skill.agent_compatibility
        assert "hermes" in skill.agent_compatibility
        assert len(skill.body) > 0

    def test_minimal_skill(self):
        content = "---\nname: min\nversion: 0.1.0\ndescription: minimal\n---\n\nBody text"
        skill = Skill.from_string(content)
        assert skill.name == "min"
        assert skill.version == "0.1.0"
        assert skill.description == "minimal"
        assert skill.body == "Body text"

    def test_no_frontmatter_gives_empty_name(self):
        content = "No frontmatter here"
        skill = Skill.from_string(content)
        assert skill.name == ""
        assert skill.body == "No frontmatter here"

    def test_tags_as_comma_string(self):
        content = "---\nname: s\nversion: 1.0.0\ndescription: d\ntags: a,b,c\n---\n\nBody"
        skill = Skill.from_string(content)
        assert skill.tags == ["a", "b", "c"]

    def test_requires_as_list(self):
        content = "---\nname: s\nversion: 1.0.0\ndescription: d\nrequires: [dep1, dep2]\n---\n\nBody"
        skill = Skill.from_string(content)
        assert skill.requires == ["dep1", "dep2"]

    def test_requires_as_string(self):
        content = "---\nname: s\nversion: 1.0.0\ndescription: d\nrequires: dep1,dep2\n---\n\nBody"
        skill = Skill.from_string(content)
        assert skill.requires == ["dep1", "dep2"]

    def test_conflicts_as_list(self):
        content = "---\nname: s\nversion: 1.0.0\ndescription: d\nconflicts: [bad]\n---\n\nBody"
        skill = Skill.from_string(content)
        assert skill.conflicts == ["bad"]

    def test_agent_compatibility_from_agents_key(self):
        content = "---\nname: s\nversion: 1.0.0\ndescription: d\nagents: [a1, a2]\n---\n\nBody"
        skill = Skill.from_string(content)
        assert skill.agent_compatibility == ["a1", "a2"]

    def test_variables_parsed(self):
        content = (
            "---\nname: s\nversion: 1.0.0\ndescription: d\n"
            "variables:\n  - name: X\n    description: desc\n    default: val\n    required: true\n"
            "---\n\nBody with {{X}}"
        )
        skill = Skill.from_string(content)
        assert len(skill.variables) == 1
        assert skill.variables[0].name == "X"
        assert skill.variables[0].default == "val"
        assert skill.variables[0].required is True

    def test_source_set(self):
        content = "---\nname: s\nversion: 1.0.0\ndescription: d\n---\n\nBody"
        skill = Skill.from_string(content, source="test.md")
        assert skill.source_path == Path("test.md")

    def test_body_stripped(self):
        content = "---\nname: s\nversion: 1.0.0\ndescription: d\n---\n\n  body with spaces  \n"
        skill = Skill.from_string(content)
        assert skill.body == "body with spaces"


# ---------------------------------------------------------------------------
# Skill.from_file
# ---------------------------------------------------------------------------


class TestSkillFromFile:
    """Tests for Skill.from_file()."""

    def test_valid_file(self, sample_skill_path: Path):
        skill = Skill.from_file(sample_skill_path)
        assert skill.name == "test-skill"
        assert skill.source_path == sample_skill_path

    def test_nonexistent_file(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            Skill.from_file(tmp_path / "nonexistent.md")

    def test_invalid_skill_has_empty_name(self, invalid_skill_path: Path):
        skill = Skill.from_file(invalid_skill_path)
        # No frontmatter -> no name
        assert skill.name == ""

    def test_file_roundtrip_content(self, sample_skill_path: Path):
        """The body should contain the actual markdown content."""
        skill = Skill.from_file(sample_skill_path)
        assert "System Prompt" in skill.body
        assert "test helper" in skill.body.lower()


# ---------------------------------------------------------------------------
# Skill.validate()
# ---------------------------------------------------------------------------


class TestSkillValidate:
    """Tests for Skill.validate()."""

    def test_valid_skill_no_errors(self):
        skill = Skill(name="my-skill", version="1.0.0", description="A valid skill")
        assert skill.validate() == []

    def test_missing_name(self):
        skill = Skill(version="1.0.0", description="desc")
        errors = skill.validate()
        assert any("name" in e.lower() for e in errors)

    def test_invalid_name_uppercase(self):
        skill = Skill(name="MySkill", version="1.0.0", description="desc")
        errors = skill.validate()
        assert any("name" in e.lower() for e in errors)

    def test_invalid_name_starts_with_number(self):
        skill = Skill(name="1skill", version="1.0.0", description="desc")
        errors = skill.validate()
        assert any("name" in e.lower() for e in errors)

    def test_valid_name_with_hyphens(self):
        skill = Skill(name="my-cool-skill", version="1.0.0", description="desc")
        assert skill.validate() == []

    def test_valid_name_with_digits(self):
        skill = Skill(name="skill2", version="1.0.0", description="desc")
        assert skill.validate() == []

    def test_missing_version(self):
        skill = Skill(name="skill", version="", description="desc")
        errors = skill.validate()
        assert any("version" in e.lower() for e in errors)

    def test_invalid_version(self):
        skill = Skill(name="skill", version="not-a-version", description="desc")
        errors = skill.validate()
        assert any("version" in e.lower() for e in errors)

    def test_valid_semver_with_prerelease(self):
        skill = Skill(name="skill", version="1.0.0-beta.1", description="desc")
        assert skill.validate() == []

    def test_missing_description(self):
        skill = Skill(name="skill", version="1.0.0")
        errors = skill.validate()
        assert any("description" in e.lower() for e in errors)

    def test_multiple_errors(self):
        skill = Skill(version="")
        errors = skill.validate()
        assert len(errors) == 3  # name, version, description

    def test_valid_from_fixture(self, sample_skill_path: Path):
        skill = Skill.from_file(sample_skill_path)
        errors = skill.validate()
        assert errors == []


# ---------------------------------------------------------------------------
# Skill.render()
# ---------------------------------------------------------------------------


class TestSkillRender:
    """Tests for Skill.render()."""

    def test_render_no_variables(self):
        skill = Skill(body="Hello world")
        assert skill.render() == "Hello world"

    def test_render_with_variables(self):
        skill = Skill(
            body="Hello {{NAME}}",
            variables=[SkillVariable(name="NAME", default="World")],
        )
        assert skill.render() == "Hello World"

    def test_render_override_default(self):
        skill = Skill(
            body="Hello {{NAME}}",
            variables=[SkillVariable(name="NAME", default="World")],
        )
        assert skill.render({"NAME": "Python"}) == "Hello Python"

    def test_render_no_defaults_no_override(self):
        skill = Skill(body="{{MISSING}}")
        assert skill.render() == "{{MISSING}}"

    def test_render_partial_override(self):
        skill = Skill(
            body="{{A}} and {{B}}",
            variables=[
                SkillVariable(name="A", default="alpha"),
                SkillVariable(name="B", default="beta"),
            ],
        )
        assert skill.render({"B": "BETA"}) == "alpha and BETA"


# ---------------------------------------------------------------------------
# Skill.is_compatible_with()
# ---------------------------------------------------------------------------


class TestSkillIsCompatibleWith:
    """Tests for Skill.is_compatible_with()."""

    def test_universal_compatible(self):
        skill = Skill(agent_compatibility=[])
        assert skill.is_compatible_with("any-agent") is True

    def test_exact_match(self):
        skill = Skill(agent_compatibility=["claude_code", "hermes"])
        assert skill.is_compatible_with("claude_code") is True

    def test_no_match(self):
        skill = Skill(agent_compatibility=["claude_code"])
        assert skill.is_compatible_with("hermes") is False

    def test_case_insensitive(self):
        skill = Skill(agent_compatibility=["Claude_Code"])
        assert skill.is_compatible_with("claude_code") is True

    def test_hyphen_underscore_normalization(self):
        skill = Skill(agent_compatibility=["claude-code"])
        assert skill.is_compatible_with("claude_code") is True

    def test_space_normalization(self):
        skill = Skill(agent_compatibility=["claude code"])
        assert skill.is_compatible_with("claude_code") is True


# ---------------------------------------------------------------------------
# Skill.full_name
# ---------------------------------------------------------------------------


class TestSkillFullName:
    def test_full_name(self):
        skill = Skill(name="test", version="2.0.0")
        assert skill.full_name == "test@2.0.0"


# ---------------------------------------------------------------------------
# Skill.to_dict / from_dict
# ---------------------------------------------------------------------------


class TestSkillSerialization:
    """Tests for Skill.to_dict() and Skill.from_dict()."""

    def test_roundtrip(self):
        original = Skill(
            name="ser-skill",
            version="1.2.3",
            description="Serialization test",
            category="testing",
            body="Body content",
            tags=["a", "b"],
            author="test-author",
            license="MIT",
            agent_compatibility=["hermes"],
            requires=["dep1"],
            conflicts=["bad-skill"],
            min_agentforge_version="0.1.0",
            variables=[SkillVariable(name="X", description="An X", default="x", required=False)],
        )
        d = original.to_dict()
        restored = Skill.from_dict(d)

        assert restored.name == original.name
        assert restored.version == original.version
        assert restored.description == original.description
        assert restored.category == original.category
        assert restored.tags == original.tags
        assert restored.author == original.author
        assert restored.license == original.license
        assert restored.agent_compatibility == original.agent_compatibility
        assert restored.requires == original.requires
        assert restored.conflicts == original.conflicts
        assert restored.min_agentforge_version == original.min_agentforge_version
        assert len(restored.variables) == 1
        assert restored.variables[0].name == "X"

    def test_to_dict_serializable(self):
        """to_dict output should be JSON-serializable."""
        import json
        skill = Skill(name="test", version="1.0.0", description="d")
        d = skill.to_dict()
        json.dumps(d)  # should not raise

    def test_from_dict_minimal(self):
        d = {"name": "m", "version": "0.1.0", "description": "min"}
        skill = Skill.from_dict(d)
        assert skill.name == "m"
        assert skill.tags == []

    def test_to_dict_paths_as_strings(self, tmp_path: Path):
        skill = Skill(
            name="t",
            version="1.0.0",
            description="d",
            source_path=tmp_path / "src.md",
            installed_path=tmp_path / "dst.md",
        )
        d = skill.to_dict()
        assert isinstance(d["source_path"], str)
        assert isinstance(d["installed_path"], str)

    def test_from_dict_with_paths(self, tmp_path: Path):
        d = {
            "name": "t",
            "version": "1.0.0",
            "description": "d",
            "source_path": str(tmp_path / "src.md"),
            "installed_path": str(tmp_path / "dst.md"),
        }
        skill = Skill.from_dict(d)
        assert skill.source_path == tmp_path / "src.md"
        assert skill.installed_path == tmp_path / "dst.md"

    def test_installed_flag_roundtrip(self):
        skill = Skill(name="t", version="1.0.0", description="d", installed=True, installed_agent="hermes")
        d = skill.to_dict()
        assert d["installed"] is True
        assert d["installed_agent"] == "hermes"


# ---------------------------------------------------------------------------
# Skill.__repr__
# ---------------------------------------------------------------------------


class TestSkillRepr:
    def test_repr(self):
        skill = Skill(name="foo", version="1.0.0")
        assert repr(skill) == "Skill('foo@1.0.0')"
