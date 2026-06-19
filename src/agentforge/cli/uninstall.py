"""agentforge uninstall — Remove installed skills."""

from pathlib import Path

import click

from agentforge.cli._utils import console, get_installer


@click.command("uninstall")
@click.argument("skills", nargs=-1, required=True)
@click.option("--agent", "-a", type=str, default=None, help="Target agent.")
@click.option("--global", "uninstall_global", is_flag=True, help="Uninstall globally.")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt.")
@click.pass_context
def uninstall(
    ctx: click.Context,
    skills: tuple[str, ...],
    agent: str | None,
    uninstall_global: bool,
    yes: bool,
) -> None:
    """Remove one or more SKILLs."""
    result = get_installer()
    if result is None:
        return
    installer, _registry = result

    if agent is None:
        agent = "claude_code"

    project_path = Path.cwd()

    if (
        len(skills) > 1
        and not yes
        and not click.confirm(f"Uninstall {len(skills)} skills from {agent}?")
    ):
        console.print("[dim]Cancelled.[/]")
        return

    for skill_name in skills:
        result = installer.uninstall(skill_name, agent, project_path, uninstall_global)
        if result.success:
            console.print(f"[green]✓[/] {result.message}")
        else:
            console.print(f"[red]✗[/] {result.message}")
