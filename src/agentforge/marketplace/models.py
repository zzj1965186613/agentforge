"""Pydantic models for the AgentForge marketplace (stub).

These dataclasses represent the shape of marketplace API responses.
They use ``dataclasses`` as a lightweight stand-in; a future version
will migrate to Pydantic v2 once the API contract is finalised.
"""

# ==========================================================================
# EXPERIMENTAL / NOT YET AVAILABLE
#
# This module is part of the *future* marketplace feature.  The data
# models defined here describe the shape of marketplace API responses
# but are not used by any live endpoint yet.  Importing this module
# is safe for type-checking and development purposes.
# ==========================================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

# ---------------------------------------------------------------------------
# Skill metadata
# ---------------------------------------------------------------------------


@dataclass
class SkillAuthor:
    """An author who contributed to a marketplace skill."""

    name: str
    url: str | None = None
    email: str | None = None


@dataclass
class SkillVersion:
    """A single published version of a skill."""

    version: str
    released_at: datetime | None = None
    changelog: str = ""
    download_url: str | None = None


@dataclass
class MarketplaceSkill:
    """Full representation of a skill as returned by the marketplace API."""

    id: str
    name: str
    display_name: str
    description: str
    version: str
    category: str
    tags: list[str] = field(default_factory=list)
    authors: list[SkillAuthor] = field(default_factory=list)
    license: str = "MIT"
    homepage: str | None = None
    repository: str | None = None
    versions: list[SkillVersion] = field(default_factory=list)
    downloads: int = 0
    rating: float = 0.0
    agent_compatibility: list[str] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    extra: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Search / listing responses
# ---------------------------------------------------------------------------


@dataclass
class SkillSearchResult:
    """Paginated search result from the marketplace."""

    query: str
    total: int = 0
    limit: int = 20
    offset: int = 0
    results: list[MarketplaceSkill] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Publish request / response
# ---------------------------------------------------------------------------


@dataclass
class PublishRequest:
    """Payload sent when publishing a new skill."""

    name: str
    display_name: str
    description: str
    version: str
    category: str
    tags: list[str] = field(default_factory=list)
    license: str = "MIT"
    homepage: str | None = None
    repository: str | None = None
    agent_compatibility: list[str] = field(default_factory=list)


@dataclass
class PublishResponse:
    """Response after successfully publishing a skill."""

    id: str
    version: str
    message: str = "Skill published successfully."
