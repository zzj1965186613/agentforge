"""Root CLI group for AgentForge."""

import logging

import click
from rich.console import Console

from agentforge import __version__

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="agentforge")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    help="Enable verbose output.",
)
@click.option(
    "-c",
    "--config",
    type=click.Path(),
    default=None,
    help="Path to a custom config file.",
)
@click.pass_context
def cli(ctx: click.Context, verbose: bool, config: str | None) -> None:
    """AgentForge — The definitive skill manager for AI agents.

    Discover, install, and manage AI agent skills from the command line.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["config"] = config

    if verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s %(name)s %(levelname)s: %(message)s",
        )


# ---------------------------------------------------------------------------
# Register subcommands
# ---------------------------------------------------------------------------

from agentforge.cli.config_cmd import config  # noqa: E402
from agentforge.cli.info import info  # noqa: E402
from agentforge.cli.init_cmd import init  # noqa: E402
from agentforge.cli.install import install  # noqa: E402
from agentforge.cli.list_cmd import list_cmd  # noqa: E402
from agentforge.cli.search import search  # noqa: E402
from agentforge.cli.share import share  # noqa: E402
from agentforge.cli.uninstall import uninstall  # noqa: E402
from agentforge.cli.update import update  # noqa: E402

cli.add_command(list_cmd, "list")
cli.add_command(search)
cli.add_command(info)
cli.add_command(install)
cli.add_command(uninstall)
cli.add_command(init)
cli.add_command(update)
cli.add_command(share)
cli.add_command(config)
