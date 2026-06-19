"""agentforge share — Export or share a custom skill."""

import click
from rich.console import Console

console = Console()

try:
    from agentforge.core.registry import SkillRegistry
except ImportError:
    SkillRegistry = None  # type: ignore[assignment,misc]


@click.command("share")
@click.argument("skill_name")
@click.option("--output", "-o", type=click.Path(), default=None, help="Write to file.")
@click.option("--gist", is_flag=True, help="Create a GitHub Gist (requires gh CLI).")
@click.pass_context
def share(ctx: click.Context, skill_name: str, output: str | None, gist: bool) -> None:
    """Export or share SKILL_NAME."""
    if SkillRegistry is None:
        console.print("[bold red]Error:[/] agentforge.core is not available yet.")
        return

    registry = SkillRegistry()
    skill = registry.get(skill_name)
    if skill is None:
        console.print(f"[red]Skill not found:[/] {skill_name}")
        return

    # Read the full skill file content
    if skill.source_path and skill.source_path.exists():
        content = skill.source_path.read_text(encoding="utf-8")
    else:
        console.print(f"[red]Could not read skill source for:[/] {skill_name}")
        return

    if output:
        from pathlib import Path

        Path(output).write_text(content, encoding="utf-8")
        console.print(f"[green]✓[/] Skill exported to {output}")
    elif gist:
        import subprocess

        try:
            result = subprocess.run(
                ["gh", "gist", "create", "--filename", f"{skill_name}.md", "-"],
                input=content,
                capture_output=True,
                text=True,
                check=True,
            )
            console.print(f"[green]✓[/] Gist created: {result.stdout.strip()}")
        except FileNotFoundError:
            console.print("[red]Error:[/] gh CLI not found. Install from https://cli.github.com/")
        except subprocess.CalledProcessError as exc:
            console.print(f"[red]Error creating gist:[/] {exc.stderr}")
    else:
        # Print to stdout
        console.print(content)
