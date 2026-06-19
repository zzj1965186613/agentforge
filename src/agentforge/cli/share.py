"""agentforge share — Export or share a custom skill."""

import click

from agentforge.cli._utils import console, get_registry


@click.command("share")
@click.argument("skill_name")
@click.option("--output", "-o", type=click.Path(), default=None, help="Write to file.")
@click.option("--gist", is_flag=True, help="Create a GitHub Gist (requires gh CLI).")
@click.pass_context
def share(ctx: click.Context, skill_name: str, output: str | None, gist: bool) -> None:
    """Export or share SKILL_NAME."""
    registry = get_registry()
    if registry is None:
        return

    skill = registry.get(skill_name)
    if skill is None:
        console.print(f"[red]Skill not found:[/] {skill_name}")
        return

    # Read the full skill file content
    if skill.source_path and skill.source_path.exists():
        try:
            content = skill.source_path.read_text(encoding="utf-8")
        except OSError as exc:
            console.print(f"[red]Error reading skill file:[/] {exc}")
            return
    else:
        console.print(f"[red]Could not read skill source for:[/] {skill_name}")
        return

    if output:
        from pathlib import Path

        try:
            Path(output).write_text(content, encoding="utf-8")
            console.print(f"[green]✓[/] Skill exported to {output}")
        except OSError as exc:
            console.print(f"[red]Error writing file:[/] {exc}")
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
