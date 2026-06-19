"""Rich display helpers for AgentForge CLI output."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

if TYPE_CHECKING:
    from agentforge.core.skill import Skill

console = Console()


def print_skill_table(skills: Sequence[Skill], title: str = "Skills") -> None:
    """Display a table of skills."""
    table = Table(title=title, show_lines=False, expand=True)
    table.add_column("Name", style="cyan bold", no_wrap=True)
    table.add_column("Version", style="green")
    table.add_column("Category", style="magenta")
    table.add_column("Description", ratio=3)
    table.add_column("Tags", style="dim")
    table.add_column("Installed", justify="center")

    for skill in skills:
        tags_str = ", ".join(skill.tags) if skill.tags else ""
        installed = "✓" if skill.installed else ""
        table.add_row(
            skill.name,
            skill.version,
            skill.category or "",
            skill.description or "",
            tags_str,
            installed,
        )

    console.print(table)


def print_skill_info(skill: Skill) -> None:
    """Display detailed information about a single skill."""
    lines: list[str] = []
    lines.append(f"[bold cyan]Name:[/] {skill.full_name}")
    if skill.description:
        lines.append(f"[bold cyan]Description:[/] {skill.description}")
    if skill.author:
        lines.append(f"[bold cyan]Author:[/] {skill.author}")
    if skill.license:
        lines.append(f"[bold cyan]License:[/] {skill.license}")
    if skill.category:
        lines.append(f"[bold cyan]Category:[/] {skill.category}")
    if skill.tags:
        lines.append(f"[bold cyan]Tags:[/] {', '.join(skill.tags)}")
    if skill.agent_compatibility:
        lines.append(f"[bold cyan]Compatible with:[/] {', '.join(skill.agent_compatibility)}")
    if skill.requires:
        lines.append(f"[bold cyan]Requires:[/] {', '.join(skill.requires)}")
    if skill.conflicts:
        lines.append(f"[bold cyan]Conflicts:[/] {', '.join(skill.conflicts)}")
    if skill.variables:
        lines.append("[bold cyan]Variables:[/]")
        for var in skill.variables:
            if var.required:
                req = " (required)"
            elif var.default is not None:
                req = f" (default: {var.default!r})"
            else:
                req = ""
            lines.append(f"  - [yellow]{{{{{var.name}}}}}[/]{req}: {var.description or ''}")
    if skill.installed:
        lines.append(f"[bold cyan]Installed:[/] {skill.installed_path or 'yes'}")
        if skill.installed_agent:
            lines.append(f"[bold cyan]Agent:[/] {skill.installed_agent}")

    panel = Panel("\n".join(lines), title=f"Skill: {skill.name}", border_style="cyan")
    console.print(panel)


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[bold green]✓[/] {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[bold red]✗[/] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[bold yellow]⚠[/] {message}")
