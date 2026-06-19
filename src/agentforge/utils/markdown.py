"""Markdown parsing utilities for AgentForge skill files."""

from __future__ import annotations

import re
from typing import Any

import yaml

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_VARIABLE_RE = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter from a Markdown string.

    Returns:
        A tuple of (metadata_dict, body_string).  If no frontmatter is found
        the metadata dict will be empty and the entire content is the body.
    """
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return {}, content

    raw_yaml = match.group(1)
    try:
        metadata: dict[str, Any] = yaml.safe_load(raw_yaml) or {}
    except yaml.YAMLError:
        metadata = {}

    body = content[match.end() :]
    return metadata, body


def render_variables(content: str, variables: dict[str, str]) -> str:
    """Substitute ``{{VARIABLE}}`` placeholders in *content*.

    Each key in *variables* is matched case-sensitively.  Unrecognised
    placeholders are left intact.
    """

    def _replacer(match: re.Match[str]) -> str:
        key = match.group(1)
        if key in variables:
            return variables[key]
        return match.group(0)  # leave unchanged

    return _VARIABLE_RE.sub(_replacer, content)
