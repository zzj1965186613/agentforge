"""agentforge search — Search for skills by query, category, or tag."""

import click
from rich.table import Table

from agentforge.cli._utils import console, get_registry


@click.command("search")
@click.argument("query")
@click.option("--category", type=str, default=None, help="Filter by category.")
@click.option("--tag", type=str, default=None, help="Filter by tag.")
@click.pass_context
def search(ctx: click.Context, query: str, category: str | None, tag: str | None) -> None:
    """Search for skills by QUERY across name, description, and tags."""
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False
    registry = get_registry()
    if registry is None:
        return

    try:
        results = registry.search(query=query, category=category or "", tag=tag or "")
    except Exception as exc:
        console.print(f"[bold red]Error:[/] {exc}")
        return

    if not results:
        console.print(f'[yellow]No skills found matching "{query}".[/]')
        return

    table = Table(title=f'Search Results for "{query}"', show_lines=True)
    table.add_column("Name", style="cyan bold", no_wrap=True)
    table.add_column("Version", style="green")
    table.add_column("Category", style="magenta")
    table.add_column("Tags", style="blue")
    table.add_column("Description", max_width=50)

    if verbose:
        from agentforge.core.registry import SkillRegistry

        table.add_column("Score", style="dim", justify="right")

    for skill in results:
        tags = ", ".join(skill.tags) if skill.tags else "—"
        desc = skill.description or ""
        desc_trunc = desc[:47] + "..." if len(desc) > 50 else desc

        if verbose:
            score = SkillRegistry._score(skill, query.lower())
            table.add_row(skill.name, skill.version, skill.category, tags, desc_trunc, str(score))
        else:
            table.add_row(skill.name, skill.version, skill.category, tags, desc_trunc)

    console.print(table)
    console.print(f"\n[dim]{len(results)} result(s) found.[/]")
