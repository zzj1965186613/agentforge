"""agentforge list — List available or installed skills."""

import json
import time

import click
from rich.table import Table

from agentforge.cli._utils import console, get_registry


@click.command("list")
@click.option(
    "--installed",
    is_flag=True,
    default=False,
    help="Show only locally installed skills.",
)
@click.option(
    "--category",
    type=str,
    default=None,
    help="Filter by category.",
)
@click.option(
    "--agent",
    type=str,
    default=None,
    help="Filter by agent name.",
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["table", "json", "names"]),
    default="table",
    help="Output format.",
)
@click.pass_context
def list_cmd(
    ctx: click.Context,
    installed: bool,
    category: str | None,
    agent: str | None,
    fmt: str,
) -> None:
    """List available or installed skills."""
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False
    registry = get_registry()
    if registry is None:
        return

    try:
        t0 = time.monotonic()
        all_skills = registry.all_skills()  # triggers lazy load once
        skills = [s for s in all_skills if s.installed] if installed else all_skills
        scan_elapsed = time.monotonic() - t0

        # Apply filters
        if category:
            skills = [s for s in skills if s.category == category]
        if agent:
            skills = [s for s in skills if s.is_compatible_with(agent)]
    except Exception as exc:
        console.print(f"[bold red]Error:[/] {exc}")
        return

    if not skills:
        console.print("[yellow]No skills found.[/]")
        return

    if fmt == "json":
        data = [
            {
                "name": s.name,
                "version": s.version,
                "category": s.category,
                "description": s.description,
                "tags": s.tags,
                "installed": s.installed,
            }
            for s in skills
        ]
        console.print_json(json.dumps(data, indent=2))
        return

    if fmt == "names":
        for skill in skills:
            click.echo(skill.name)
        return

    # Default: rich table
    table = Table(title="AgentForge Skills", show_lines=True)
    table.add_column("Name", style="cyan bold", no_wrap=True)
    table.add_column("Version", style="green")
    table.add_column("Category", style="magenta")
    table.add_column("Description", max_width=60)
    table.add_column("Installed", justify="center")

    for skill in skills:
        desc = skill.description or ""
        table.add_row(
            skill.name,
            skill.version,
            skill.category,
            desc[:57] + "..." if len(desc) > 60 else desc,
            "✓" if skill.installed else "✗",
        )

    console.print(table)

    if verbose:
        console.print(
            f"[dim]Scan completed in {scan_elapsed:.3f}s — {len(skills)} skill(s) listed.[/]"
        )
