"""agentforge config — Manage AgentForge configuration."""

import click
from rich.console import Console
from rich.table import Table

console = Console()

try:
    from agentforge.core.config import AgentForgeConfig
except ImportError:
    AgentForgeConfig = None  # type: ignore[assignment,misc]


def _get_config():
    if AgentForgeConfig is None:
        console.print("[bold red]Error:[/] agentforge.core is not available yet.")
        return None
    return AgentForgeConfig.load()


@click.group("config")
def config() -> None:
    """Manage AgentForge configuration."""


@config.command("show")
def config_show() -> None:
    """Show current configuration."""
    config = _get_config()
    if config is None:
        return

    table = Table(title="AgentForge Configuration")
    table.add_column("Key", style="cyan bold")
    table.add_column("Value", style="green")
    table.add_row("default_agent", str(config.default_agent or "(not set)"))
    table.add_row("default_global", str(config.default_global))
    table.add_row("preferred_categories", ", ".join(config.preferred_categories) or "(none)")
    table.add_row("auto_update", str(config.auto_update))
    table.add_row("editor", str(config.editor or "(not set)"))
    console.print(table)


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str) -> None:
    """Set a configuration KEY to VALUE."""
    config = _get_config()
    if config is None:
        return

    if hasattr(config, key):
        current = getattr(config, key)
        if isinstance(current, bool):
            converted = value.lower() in ("true", "1", "yes")
        elif isinstance(current, list):
            converted = [v.strip() for v in value.split(",") if v.strip()]
        elif isinstance(current, int):
            converted = int(value)
        else:
            converted = value
        setattr(config, key, converted)
        config.save()
        console.print(f"[green]✓[/] Set {key} = {value}")
    else:
        console.print(f"[red]✗[/] Unknown config key: {key}")


@config.command("reset")
def config_reset() -> None:
    """Reset configuration to defaults."""
    if AgentForgeConfig is None:
        console.print("[bold red]Error:[/] agentforge.core is not available yet.")
        return
    config = AgentForgeConfig()
    config.save()
    console.print("[green]✓[/] Configuration reset to defaults.")
