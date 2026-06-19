"""agentforge update — Update installed skills or check for newer versions."""

from __future__ import annotations

import logging
from pathlib import Path

import click
from rich.table import Table

from agentforge.cli._utils import console, get_installer, parse_version_tuple

try:
    from agentforge.core.installer import SkillInstaller
    from agentforge.core.registry import SkillRegistry
except ImportError:
    SkillInstaller = None  # type: ignore[assignment,misc]
    SkillRegistry = None  # type: ignore[assignment,misc]

logger = logging.getLogger(__name__)


@click.command("update")
@click.argument("skill", required=False)
@click.option("--all", "update_all", is_flag=True, help="Update all installed skills.")
@click.option("--check", is_flag=True, help="Check for updates without installing.")
@click.option("--agent", "-a", type=str, default=None, help="Target agent.")
@click.option("--global", "install_global", is_flag=True, help="Update globally.")
@click.pass_context
def update(
    ctx: click.Context,
    skill: str | None,
    update_all: bool,
    check: bool,
    agent: str | None,
    install_global: bool,
) -> None:
    """Update installed skills or check for newer bundled versions."""
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False

    result = get_installer()
    if result is None:
        return

    installer, registry = result

    # Default agent
    if agent is None:
        agent = "claude_code"

    project_path = Path.cwd()

    if check:
        _show_update_check(registry, agent, project_path, install_global, verbose)
        return

    if skill:
        # Update a single named skill
        _update_single(installer, registry, skill, agent, project_path, install_global, verbose)
    elif update_all:
        _update_all(installer, registry, agent, project_path, install_global, verbose)
    else:
        console.print("[yellow]Specify a skill name or use --all to update.[/]")
        console.print("  [dim]agentforge update <skill-name>[/]")
        console.print("  [dim]agentforge update --all[/]")


def _update_single(
    installer: SkillInstaller,
    registry: SkillRegistry,
    skill_name: str,
    agent: str,
    project_path: Path,
    install_global: bool,
    verbose: bool,
) -> None:
    """Reinstall a single skill by name (forces overwrite)."""
    bundled = registry.get(skill_name)
    if bundled is None:
        console.print(f"[bold red]Error:[/] Skill '{skill_name}' not found in registry.")
        return

    if not bundled.installed:
        console.print(f"[yellow]Skill '{skill_name}' not installed. Use 'install' instead.[/]")
        return

    console.print(f"[dim]Reinstalling '{skill_name}' (force overwrite)...[/]")
    if verbose:
        console.print(f"  [dim]source: {bundled.source_path}[/]")
        console.print(f"  [dim]version: {bundled.version}[/]")
        console.print(f"  [dim]agent: {agent}[/]")

    install_result = installer.install(
        bundled,
        agent,
        project_path=project_path,
        global_install=install_global,
        force=True,
    )
    if install_result.success:
        console.print(f"[green]✓[/] {install_result.skill_name}: {install_result.message}")
    else:
        console.print(f"[red]✗[/] {install_result.skill_name}: {install_result.message}")


def _update_all(
    installer: SkillInstaller,
    registry: SkillRegistry,
    agent: str,
    project_path: Path,
    install_global: bool,
    verbose: bool,
) -> None:
    """Reinstall all currently installed skills."""
    # Use all_skills() + filter instead of direct scan_installed()
    installed = [s for s in registry.all_skills() if s.installed]
    if not installed:
        console.print("[yellow]No installed skills found.[/]")
        return

    console.print(f"[dim]Updating {len(installed)} installed skill(s)...[/]")

    for sk in installed:
        if verbose:
            console.print(f"  [dim]Reinstalling {sk.full_name}...[/]")
        result = installer.install(
            sk,
            agent,
            project_path=project_path,
            global_install=install_global,
            force=True,
        )
        if result.success:
            console.print(f"[green]✓[/] {result.skill_name}: {result.message}")
        else:
            console.print(f"[red]✗[/] {result.skill_name}: {result.message}")


def _show_update_check(
    registry: SkillRegistry,
    agent: str,
    project_path: Path,
    install_global: bool,
    verbose: bool,
) -> None:
    """Compare installed skill versions against the bundled registry."""
    # Use all_skills() + filter instead of direct scan_installed()
    installed = [s for s in registry.all_skills() if s.installed]
    if not installed:
        console.print("[yellow]No installed skills found.[/]")
        return

    # Collect bundled versions for comparison
    bundled_skills = {s.name: s for s in registry.all_skills()}

    table = Table(title="Update Check", show_lines=True)
    table.add_column("Skill", style="cyan bold")
    table.add_column("Installed", style="green")
    table.add_column("Bundled", style="magenta")
    table.add_column("Status", style="bold")

    updates_available = 0

    for sk in installed:
        bundled = bundled_skills.get(sk.name)
        if bundled is None:
            table.add_row(sk.name, sk.version, "—", "[dim]not in registry[/]")
            continue

        installed_ver = parse_version_tuple(sk.version)
        bundled_ver = parse_version_tuple(bundled.version)

        if bundled_ver > installed_ver:
            status = "[yellow]⬆ update available[/]"
            updates_available += 1
        elif bundled_ver == installed_ver:
            status = "[green]✓ up to date[/]"
        else:
            status = "[dim]⬇ installed is newer[/]"

        if verbose:
            console.print(f"  [dim]{sk.name}: installed={installed_ver}, bundled={bundled_ver}[/]")

        table.add_row(sk.name, sk.version, bundled.version, status)

    console.print(table)

    if updates_available:
        console.print(
            f"\n[yellow]{updates_available} skill(s) can be updated. "
            "Run 'agentforge update --all' to update.[/]"
        )
    else:
        console.print("\n[green]All installed skills are up to date.[/]")
