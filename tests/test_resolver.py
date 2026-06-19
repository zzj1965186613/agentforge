"""Tests for agentforge.core.resolver — DependencyResolver."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentforge.core.registry import SkillRegistry
from agentforge.core.resolver import DependencyResolver, Resolution
from agentforge.core.skill import Skill


def _make_registry(tmp_path: Path, skills: dict[str, Skill] | None = None) -> SkillRegistry:
    """Create a SkillRegistry pre-populated with the given skills."""
    reg = SkillRegistry(base_path=tmp_path)
    if skills:
        for name, skill in skills.items():
            reg._skills[name] = skill
    reg._loaded = True  # skip lazy scanning
    return reg


# ---------------------------------------------------------------------------
# Resolution dataclass
# ---------------------------------------------------------------------------


class TestResolutionDataclass:
    """Test the Resolution dataclass."""

    def test_defaults(self):
        r = Resolution()
        assert r.to_install == []
        assert r.already_present == []
        assert r.conflicts == []
        assert r.missing == []


# ---------------------------------------------------------------------------
# _topological_sort
# ---------------------------------------------------------------------------


class TestTopologicalSort:
    """Test DependencyResolver._topological_sort()."""

    def test_no_dependencies(self):
        graph = {"a": [], "b": [], "c": []}
        result = DependencyResolver._topological_sort(graph)
        assert set(result) == {"a", "b", "c"}

    def test_linear_chain(self):
        # a -> b -> c  (a depends on b, b depends on c)
        graph = {"a": ["b"], "b": ["c"], "c": []}
        result = DependencyResolver._topological_sort(graph)
        assert result.index("c") < result.index("b")
        assert result.index("b") < result.index("a")

    def test_diamond(self):
        # d depends on b and c; b and c both depend on a
        graph = {"d": ["b", "c"], "b": ["a"], "c": ["a"], "a": []}
        result = DependencyResolver._topological_sort(graph)
        assert result.index("a") < result.index("b")
        assert result.index("a") < result.index("c")
        assert result.index("b") < result.index("d")
        assert result.index("c") < result.index("d")

    def test_empty_graph(self):
        result = DependencyResolver._topological_sort({})
        assert result == []

    def test_cycle_raises(self):
        graph = {"a": ["b"], "b": ["a"]}
        with pytest.raises(ValueError, match="Circular"):
            DependencyResolver._topological_sort(graph)

    def test_self_cycle_raises(self):
        graph = {"a": ["a"]}
        with pytest.raises(ValueError, match="Circular"):
            DependencyResolver._topological_sort(graph)

    def test_independent_nodes(self):
        graph = {"x": [], "y": [], "z": ["x"]}
        result = DependencyResolver._topological_sort(graph)
        assert result.index("x") < result.index("z")
        assert "y" in result


# ---------------------------------------------------------------------------
# resolve()
# ---------------------------------------------------------------------------


class TestDependencyResolverResolve:
    """Test DependencyResolver.resolve()."""

    def test_simple_resolve(self, tmp_path: Path):
        skill_a = Skill(name="a", version="1.0.0", description="d")
        reg = _make_registry(tmp_path, {"a": skill_a})
        resolver = DependencyResolver(reg)
        result = resolver.resolve(["a"], "hermes")
        assert "a" in result.to_install
        assert result.missing == []

    def test_missing_skill(self, tmp_path: Path):
        reg = _make_registry(tmp_path, {})
        resolver = DependencyResolver(reg)
        result = resolver.resolve(["nonexistent"], "hermes")
        assert "nonexistent" in result.missing

    def test_already_installed(self, tmp_path: Path):
        skill = Skill(
            name="installed-skill",
            version="1.0.0",
            description="d",
            installed=True,
            installed_agent="hermes",
        )
        reg = _make_registry(tmp_path, {"installed-skill": skill})
        resolver = DependencyResolver(reg)
        result = resolver.resolve(["installed-skill"], "hermes")
        assert "installed-skill" in result.already_present
        assert "installed-skill" not in result.to_install

    def test_dependency_resolution(self, tmp_path: Path):
        skill_a = Skill(name="a", version="1.0.0", description="d", requires=["b"])
        skill_b = Skill(name="b", version="1.0.0", description="d")
        reg = _make_registry(tmp_path, {"a": skill_a, "b": skill_b})
        resolver = DependencyResolver(reg)
        result = resolver.resolve(["a"], "hermes")
        assert "a" in result.to_install
        assert "b" in result.to_install
        # b should come before a in topological order
        assert result.to_install.index("b") < result.to_install.index("a")

    def test_transitive_dependency(self, tmp_path: Path):
        skill_a = Skill(name="a", version="1.0.0", description="d", requires=["b"])
        skill_b = Skill(name="b", version="1.0.0", description="d", requires=["c"])
        skill_c = Skill(name="c", version="1.0.0", description="d")
        reg = _make_registry(tmp_path, {"a": skill_a, "b": skill_b, "c": skill_c})
        resolver = DependencyResolver(reg)
        result = resolver.resolve(["a"], "hermes")
        assert set(result.to_install) == {"a", "b", "c"}
        assert result.to_install.index("c") < result.to_install.index("b")
        assert result.to_install.index("b") < result.to_install.index("a")

    def test_missing_dependency(self, tmp_path: Path):
        skill_a = Skill(name="a", version="1.0.0", description="d", requires=["missing-dep"])
        reg = _make_registry(tmp_path, {"a": skill_a})
        resolver = DependencyResolver(reg)
        result = resolver.resolve(["a"], "hermes")
        assert "missing-dep" in result.missing

    def test_conflict_detection(self, tmp_path: Path):
        skill_a = Skill(name="a", version="1.0.0", description="d", conflicts=["b"])
        skill_b = Skill(name="b", version="1.0.0", description="d")
        reg = _make_registry(tmp_path, {"a": skill_a, "b": skill_b})
        resolver = DependencyResolver(reg)
        # Put "b" first so it's in `seen` when "a" is processed
        result = resolver.resolve(["b", "a"], "hermes")
        assert len(result.conflicts) > 0
        assert any("a" in c and "b" in c for c in result.conflicts)

    def test_incompatible_agent(self, tmp_path: Path):
        skill = Skill(
            name="platform", version="1.0.0", description="d", agent_compatibility=["claude_code"]
        )
        reg = _make_registry(tmp_path, {"platform": skill})
        resolver = DependencyResolver(reg)
        result = resolver.resolve(["platform"], "hermes")
        assert len(result.conflicts) > 0
        assert "platform" not in result.to_install

    def test_compatible_agent(self, tmp_path: Path):
        skill = Skill(
            name="platform", version="1.0.0", description="d", agent_compatibility=["hermes"]
        )
        reg = _make_registry(tmp_path, {"platform": skill})
        resolver = DependencyResolver(reg)
        result = resolver.resolve(["platform"], "hermes")
        assert result.conflicts == []
        assert "platform" in result.to_install

    def test_deduplicated_requests(self, tmp_path: Path):
        skill = Skill(name="dup", version="1.0.0", description="d")
        reg = _make_registry(tmp_path, {"dup": skill})
        resolver = DependencyResolver(reg)
        result = resolver.resolve(["dup", "dup", "dup"], "hermes")
        assert result.to_install.count("dup") == 1

    def test_mixed_installed_and_new(self, tmp_path: Path):
        installed = Skill(
            name="inst", version="1.0.0", description="d", installed=True, installed_agent="hermes"
        )
        new = Skill(name="new", version="1.0.0", description="d", requires=["inst"])
        reg = _make_registry(tmp_path, {"inst": installed, "new": new})
        resolver = DependencyResolver(reg)
        result = resolver.resolve(["new", "inst"], "hermes")
        assert "inst" in result.already_present
        assert "new" in result.to_install
