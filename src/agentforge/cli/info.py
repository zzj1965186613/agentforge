"""agentforge info — Show detailed information about a skill."""

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

try:
    from agentforge.core.registry import SkillRegistry
except ImportError:
    SkillRegistry = None  # type: ignore[assignment,misc]


def _get_registry():
    if SkillRegistry is None:
        console.print("[bold red]Error:[/] agentforge.core is not available yet.")
        return None
    return SkillRegistry()


@click.command("info")
@click.argument("skill_name")
@click.pass_context
def info(ctx: click.Context, skill_name: str) -> None:
    """Show detailed information about SKILL_NAME."""
    registry = _get_registry()
    if registry is None:
        return

    skill = registry.get(skill_name)
    if skill is None:
        console.print(f'[bold red]Skill not found:[/] "{skill_name}"')
        console.print("[dim]Run `agentforge list` to see available skills.[/]")
        return

    text = Text()
    text.append("Name: ", style="bold")
    text.append(f"{skill.name}\n")
    text.append("Version: ", style="bold")
    text.append(f"{skill.version}\n")
    text.append("Author: ", style="bold")
    text.append(f"{skill.author}\n")
    text.append("Category: ", style="bold")
    text.append(f"{skill.category}\n")
    text.append("License: ", style="bold")
    text.append(f"{skill.license}\n")
    text.append("Installed: ", style="bold")
    installed_text = "Yes ✓\n" if skill.installed else "No ✗\n"
    installed_style = "green" if skill.installed else "red"
    text.append(installed_text, style=installed_style)

    if skill.tags:
        text.append("Tags: ", style="bold")
        text.append(", ".join(skill.tags) + "\n")

    if skill.agent_compatibility:
        text.append("Agents: ", style="bold")
        text.append(", ".join(skill.agent_compatibility) + "\n")

    if skill.requires:
        text.append("Requires: ", style="bold")
        text.append(", ".join(skill.requires) + "\n")

    if skill.conflicts:
        text.append("Conflicts: ", style="bold")
        text.append(", ".join(skill.conflicts) + "\n")

    if skill.variables:
        text.append("\nVariables:\n", style="bold underline")
        for v in skill.variables:
            req = " (required)" if v.required else f" (default: {v.default})"
            text.append(f"  • {v.name}: {v.description}{req}\n")

    text.append("\nDescription:\n", style="bold underline")
    text.append(f"{skill.description}\n")

    panel = Panel(text, title=f"[bold cyan]{skill.name}[/]", border_style="cyan", padding=(1, 2))
    console.print(panel)
