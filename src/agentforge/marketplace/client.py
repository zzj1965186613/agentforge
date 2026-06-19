"""HTTP client for the AgentForge skill marketplace (stub).

This module provides a thin async HTTP client that will communicate
with the AgentForge marketplace API once the service is available.
All methods currently raise ``NotImplementedError`` or return stub
data so that the rest of the codebase can be developed in parallel.
"""

# ==========================================================================
# EXPERIMENTAL / NOT YET AVAILABLE
#
# This module is part of the *future* marketplace feature.  None of the
# public methods are functional yet – they will be wired up once the
# marketplace API backend is deployed.  Importing this module is safe,
# but calling any method will return a clear "not implemented" message
# instead of raising a raw ``NotImplementedError``.
# ==========================================================================

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import httpx  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    httpx = None  # type: ignore[assignment]

from .cache import SkillCache
from .models import MarketplaceSkill, SkillSearchResult

logger = logging.getLogger(__name__)

_DEFAULT_BASE_URL = "https://marketplace.agentforge.dev/api/v1"


@dataclass
class MarketplaceClient:
    """Async-capable HTTP client for the AgentForge marketplace.

    Parameters
    ----------
    base_url:
        Root URL of the marketplace API.
    cache_dir:
        Local directory for caching downloaded skill bundles.
    api_key:
        Optional bearer token for authenticated endpoints.
    """

    base_url: str = _DEFAULT_BASE_URL
    cache_dir: Path = field(default_factory=lambda: Path.home() / ".agentforge" / "cache")
    api_key: str | None = None

    def __post_init__(self) -> None:
        self._cache = SkillCache(self.cache_dir)

    @staticmethod
    def _not_implemented(method: str) -> None:
        """Log a clear message that *method* is not yet available.

        This helper is used by stub methods so callers get a friendly
        log entry instead of a raw ``NotImplementedError``.
        """
        logger.warning(
            "MarketplaceClient.%s is not yet implemented. The marketplace API is not available.",
            method,
        )

    # -- Public API ---------------------------------------------------------

    async def search(
        self,
        query: str,
        *,
        category: str | None = None,
        tags: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> SkillSearchResult:
        """Search the marketplace for skills matching *query*.

        Raises
        ------
        NotImplementedError
            The marketplace API is not yet available.
        """
        self._not_implemented("search")
        raise NotImplementedError("Marketplace search is not yet implemented.")

    async def get_skill(self, skill_id: str) -> MarketplaceSkill:
        """Fetch full details for a single skill by its unique *skill_id*.

        Raises
        ------
        NotImplementedError
            The marketplace API is not yet available.
        """
        self._not_implemented("get_skill")
        raise NotImplementedError("Marketplace skill lookup is not yet implemented.")

    async def download_skill(self, skill_id: str, *, version: str | None = None) -> Path:
        """Download a skill bundle and return its local cache path.

        Parameters
        ----------
        skill_id:
            Unique identifier of the skill to download.
        version:
            Specific version to fetch.  ``None`` means latest.

        Returns
        -------
        Path
            Path to the downloaded ``.tar.gz`` bundle in the local cache.

        Raises
        ------
        NotImplementedError
            The marketplace API is not yet available.
        """
        self._not_implemented("download_skill")
        raise NotImplementedError("Marketplace downloads are not yet implemented.")

    async def publish_skill(
        self,
        skill_path: Path,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Upload a skill to the marketplace (requires authentication).

        Returns the newly assigned skill ID.

        Raises
        ------
        NotImplementedError
            The marketplace API is not yet available.
        """
        self._not_implemented("publish_skill")
        raise NotImplementedError("Skill publishing is not yet implemented.")

    async def list_categories(self) -> list[str]:
        """Return all available skill categories.

        Raises
        ------
        NotImplementedError
            The marketplace API is not yet available.
        """
        self._not_implemented("list_categories")
        raise NotImplementedError("Category listing is not yet implemented.")

    async def check_updates(self, installed: dict[str, str]) -> dict[str, str | None]:
        """Given ``{skill_name: installed_version}``, return skills with updates.

        Returns ``{skill_name: latest_version}`` for those that have a
        newer version, or an empty dict if none.

        Raises
        ------
        NotImplementedError
            The marketplace API is not yet available.
        """
        self._not_implemented("check_updates")
        raise NotImplementedError("Update checking is not yet implemented.")
