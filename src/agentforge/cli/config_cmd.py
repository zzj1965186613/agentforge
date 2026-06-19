"""agentforge config — Manage AgentForge configuration."""

import dataclasses

import click
from rich.table import Table

from agentforge.cli._utils import console

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
    cfg = _get_config()
    if cfg is None:
        return

    table = Table(title="AgentForge Configuration")
    table.add_column("Key", style="cyan bold")
    table.add_column("Value", style="green")
    table.add_row("default_agent", str(cfg.default_agent or "(not set)"))
    table.add_row("default_global", str(cfg.default_global))
    table.add_row("preferred_categories", ", ".join(cfg.preferred_categories) or "(none)")
    table.add_row("auto_update", str(cfg.auto_update))
    table.add_row("editor", str(cfg.editor or "(not set)"))
    console.print(table)


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str) -> None:
    """Set a configuration KEY to VALUE."""
    cfg = _get_config()
    if cfg is None:
        return

    valid_keys = {f.name for f in dataclasses.fields(cfg)}
    if key not in valid_keys:
        console.print(f"[red]✗[/] Unknown config key: {key}")
        console.print(f"[dim]Valid keys: {', '.join(sorted(valid_keys))}[/]")
        return

    current = getattr(cfg, key)
    if isinstance(current, bool):
        converted = value.lower() in ("true", "1", "yes")
    elif isinstance(current, list):
        converted = [v.strip() for v in value.split(",") if v.strip()]
    elif isinstance(current, int):
        try:
            converted = int(value)
        except ValueError:
            console.print(f"[red]Error:[/] '{value}' is not a valid integer for '{key}'")
            return
    else:
        converted = value
    setattr(cfg, key, converted)
    cfg.save()
    console.print(f"[green]✓[/] Set {key} = {value}")


@config.command("reset")
def config_reset() -> None:
    """Reset configuration to defaults."""
    if AgentForgeConfig is None:
        console.print("[bold red]Error:[/] agentforge.core is not available yet.")
        return
    cfg = AgentForgeConfig()
    cfg.save()
    console.print("[green]✓[/] Configuration reset to defaults.")
