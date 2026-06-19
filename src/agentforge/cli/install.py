"""agentforge install — Install one or more skills."""

from pathlib import Path

import click

from agentforge import __version__
from agentforge.cli._utils import console, get_installer, parse_version_tuple

try:
    from agentforge.agents import base as _agents_base  # noqa: F401 – side-effect import
    from agentforge.core.resolver import DependencyResolver
except ImportError:
    DependencyResolver = None  # type: ignore[assignment,misc]


@click.command("install")
@click.argument("skills", nargs=-1, required=True)
@click.option("--agent", "-a", type=str, default=None, help="Target agent.")
@click.option("--global", "install_global", is_flag=True, help="Install globally.")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing.")
@click.option("--dry-run", "-d", is_flag=True, help="Preview without installing.")
@click.pass_context
def install(
    ctx: click.Context,
    skills: tuple[str, ...],
    agent: str | None,
    install_global: bool,
    force: bool,
    dry_run: bool,
) -> None:
    """Install one or more SKILLs from the registry."""
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False
    result = get_installer()
    if result is None:
        return
    installer, registry = result

    if dry_run:
        console.print("[bold yellow]DRY RUN[/] — no changes will be made.\n")

    # Default agent
    if agent is None:
        agent = "claude_code"

    project_path = Path.cwd()

    # Resolve dependencies
    if DependencyResolver is not None:
        resolver = DependencyResolver(registry)
        resolution = resolver.resolve(list(skills), agent)

        if resolution.conflicts:
            for conflict in resolution.conflicts:
                console.print(f"[bold red]Conflict:[/] {conflict}")
            if not force:
                console.print("[dim]Use --force to override conflicts.[/]")
                return

        if resolution.missing:
            for name in resolution.missing:
                console.print(f"[bold red]Missing dependency:[/] {name}")
            return

        # Show dependency info
        if resolution.to_install and len(resolution.to_install) > len(skills):
            deps = [s for s in resolution.to_install if s not in skills]
            console.print(f"[dim]Dependencies to install: {', '.join(deps)}[/]")

        if resolution.already_present:
            console.print(f"[dim]Already installed: {', '.join(resolution.already_present)}[/]")

        install_names = resolution.to_install
    else:
        install_names = list(skills)

    # --- min_agentforge_version validation ---
    current_ver = parse_version_tuple(__version__)
    filtered_names: list[str] = []
    for name in install_names:
        skill = registry.get(name)
        if skill and skill.min_agentforge_version:
            required_ver = parse_version_tuple(skill.min_agentforge_version)
            if current_ver < required_ver:
                console.print(
                    f"[bold yellow]Warning:[/] Skipping '{name}' — requires "
                    f"agentforge >= {skill.min_agentforge_version} (installed: {__version__})"
                )
                continue
        filtered_names.append(name)
    install_names = filtered_names

    if not install_names:
        console.print("[yellow]Nothing to install.[/]")
        return

    if dry_run:
        for name in install_names:
            msg = (
                f"[yellow]Would install:[/] {name}"
                f" -> agent={agent}, global={install_global}, force={force}"
            )
            console.print(msg)
    else:
        results = installer.install_many(
            names=install_names,
            agent=agent,
            project_path=project_path,
            global_install=install_global,
            force=force,
        )

        for result in results:
            if result.success:
                console.print(f"[green]✓[/] {result.skill_name}: {result.message}")
                if verbose and result.installed_path:
                    console.print(f"  [dim]written to: {result.installed_path}[/]")
            else:
                console.print(f"[red]✗[/] {result.skill_name}: {result.message}")
