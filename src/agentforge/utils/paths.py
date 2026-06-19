"""Path helpers for AgentForge."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def user_data_dir() -> Path:
    """Return the user-level data directory for AgentForge.

    Uses XDG_DATA_HOME on Linux, APPDATA on Windows, ~/Library on macOS.
    Falls back to ~/.agentforge if none of those are set.
    """
    if sys.platform == "win32":
        base = os.environ.get("APPDATA")
        if base:
            return Path(base) / "agentforge"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "agentforge"
    else:
        xdg = os.environ.get("XDG_DATA_HOME")
        if xdg:
            return Path(xdg) / "agentforge"
    # Fallback
    return Path.home() / ".agentforge"


def project_config_dir(project_path: str | Path) -> Path:
    """Return the .agentforge directory inside a project."""
    return Path(project_path) / ".agentforge"


def bundled_skills_dir() -> Path:
    """Return the path to the bundled skills directory shipped with the package.

    Uses importlib.resources for reliable resolution in both development
    (editable install) and distributed (wheel) installations.
    Falls back to the legacy relative-path approach for development.
    """
    import importlib.resources as pkg_resources

    # Try importlib.resources first (works for installed wheels)
    try:
        ref = pkg_resources.files("agentforge") / "skills"
        resolved = Path(str(ref))
        if resolved.is_dir():
            return resolved
    except (TypeError, ModuleNotFoundError):
        pass

    # Fallback: development mode — skills/ is at project root
    dev_path = Path(__file__).resolve().parent.parent.parent.parent / "skills"
    if dev_path.is_dir():
        return dev_path

    # Last resort: return the importlib path even if it doesn't exist yet
    return resolved
