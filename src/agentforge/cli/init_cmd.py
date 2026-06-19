"""agentforge init — Initialize AgentForge in the current project."""

from pathlib import Path

import click

from agentforge.cli._utils import console

try:
    from agentforge.core.config import AgentForgeConfig
except ImportError:
    AgentForgeConfig = None  # type: ignore[assignment,misc]


@click.command("init")
@click.option(
    "--agent",
    "-a",
    type=click.Choice(["claude_code", "cursor", "copilot", "aider", "hermes"]),
    default=None,
    help="Target agent.",
)
@click.option("--path", "project_path", type=click.Path(), default=".", help="Project root path.")
@click.pass_context
def init(ctx: click.Context, agent: str | None, project_path: str) -> None:
    """Initialize AgentForge in the current project."""
    project = Path(project_path).resolve()

    if agent is None:
        # Auto-detect
        detected = _detect_agent(project)
        if detected:
            agent = detected
            console.print(f"[green]✓[/] Detected agent: {agent}")
        else:
            agent = click.prompt(
                "Select agent",
                type=click.Choice(["claude_code", "cursor", "copilot", "aider", "hermes"]),
            )

    # Create .agentforge directory
    af_dir = project / ".agentforge"
    af_dir.mkdir(parents=True, exist_ok=True)

    # Save config
    if AgentForgeConfig:
        config = AgentForgeConfig(default_agent=agent)
        config.save(af_dir / "config.yml")

    console.print(f"[green]✓[/] AgentForge initialized for [cyan]{agent}[/]")
    console.print(f"[green]✓[/] Created {af_dir / 'config.yml'}")
    console.print("\n[dim]Run `agentforge install <skill>` to add skills.[/]")


def _detect_agent(project: Path) -> str | None:
    """Auto-detect which agent is configured in the project."""
    if (project / ".claude").is_dir():
        return "claude_code"
    if (project / ".cursor").is_dir() or (project / ".cursorrules").exists():
        return "cursor"
    if (project / ".github" / "copilot-instructions.md").exists():
        return "copilot"
    if (project / ".aider.conf.yml").exists():
        return "aider"
    if (Path.home() / ".hermes").is_dir():
        return "hermes"
    return None
