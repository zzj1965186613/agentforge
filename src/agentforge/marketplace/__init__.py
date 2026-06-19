"""AgentForge marketplace — skill discovery, caching, and publishing.

.. warning::
    **EXPERIMENTAL / NOT YET AVAILABLE**

    The marketplace module is part of a planned feature.  The API
    backend is not deployed yet, so all client methods will raise
    ``NotImplementedError``.  The cache and model classes are safe
    to import for development and type-checking purposes.
"""

from .cache import CacheEntry, SkillCache
from .client import MarketplaceClient
from .models import (
    MarketplaceSkill,
    PublishRequest,
    PublishResponse,
    SkillAuthor,
    SkillSearchResult,
    SkillVersion,
)

__all__: list[str] = [
    # Client
    "MarketplaceClient",
    # Cache
    "CacheEntry",
    "SkillCache",
    # Models
    "MarketplaceSkill",
    "PublishRequest",
    "PublishResponse",
    "SkillAuthor",
    "SkillSearchResult",
    "SkillVersion",
]
