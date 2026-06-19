"""Dependency resolver for AgentForge skills."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field

from agentforge.core.registry import SkillRegistry


@dataclass
class Resolution:
    """Result of resolving a set of skill names."""

    to_install: list[str] = field(default_factory=list)
    already_present: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)


class DependencyResolver:
    """Resolve skill dependencies and detect conflicts before installation."""

    def __init__(self, registry: SkillRegistry) -> None:
        self.registry = registry

    def resolve(self, names: list[str], agent: str) -> Resolution:
        """Determine what needs to be installed for *names* on *agent*.

        Walks the dependency graph recursively and checks for:
        * already-installed skills
        * skills that must be installed
        * conflicts between requested skills
        * dependencies that cannot be found in the registry
        """
        resolution = Resolution()
        seen: set[str] = set()
        queue: deque[str] = deque(names)

        while queue:
            name = queue.popleft()
            if name in seen:
                continue
            seen.add(name)

            skill = self.registry.get(name)
            if skill is None:
                resolution.missing.append(name)
                continue

            # Check compatibility
            if not skill.is_compatible_with(agent):
                resolution.conflicts.append(f"{name} is not compatible with agent '{agent}'")
                continue

            # Check conflicts against other resolved skills
            for conflict_name in skill.conflicts:
                if conflict_name in seen or conflict_name in resolution.to_install:
                    resolution.conflicts.append(f"{name} conflicts with {conflict_name}")

            # Check if already installed
            if skill.installed and skill.installed_agent == agent:
                resolution.already_present.append(name)
            else:
                resolution.to_install.append(name)

            # Enqueue dependencies
            for dep in skill.requires:
                if dep not in seen:
                    queue.append(dep)

        # Topological sort of to_install
        if resolution.to_install:
            graph: dict[str, list[str]] = {}
            for name in resolution.to_install:
                skill = self.registry.get(name)
                if skill is not None:
                    graph[name] = [d for d in skill.requires if d in resolution.to_install]
                else:
                    graph[name] = []
            resolution.to_install = self._topological_sort(graph)

        return resolution

    @staticmethod
    def _topological_sort(graph: dict[str, list[str]]) -> list[str]:
        """Kahn's algorithm for topological sort.

        Nodes that are not in *graph* keys but appear as dependencies are
        included only if they have their own entry.  Raises ``ValueError``
        on cycles.
        """
        in_degree: dict[str, int] = defaultdict(int)
        for node in graph:
            in_degree.setdefault(node, 0)
        for _node, deps in graph.items():
            for dep in deps:
                in_degree.setdefault(dep, 0)

        # Build adjacency: dep -> [dependents]
        dependents: dict[str, list[str]] = defaultdict(list)
        for node, deps in graph.items():
            for dep in deps:
                dependents[dep].append(node)
                in_degree[node] += 1

        queue = deque(n for n, d in in_degree.items() if d == 0)
        sorted_nodes: list[str] = []

        while queue:
            node = queue.popleft()
            if node in graph:
                sorted_nodes.append(node)
            for dependent in dependents.get(node, []):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(sorted_nodes) != len(graph):
            raise ValueError("Circular dependency detected among: " + ", ".join(graph))

        return sorted_nodes
