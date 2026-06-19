"""Local disk cache for marketplace skill bundles (stub).

Provides a simple file-system–backed cache that stores downloaded
skill tarballs and their metadata.  The implementation is intentionally
minimal; it will be fleshed out once the marketplace API is live.
"""

# ==========================================================================
# EXPERIMENTAL / NOT YET AVAILABLE
#
# This module is part of the *future* marketplace feature.  The cache
# interface is defined here but the marketplace backend that populates
# it is not yet live.  Importing this module is safe, but the cache
# will remain empty until the marketplace API is deployed.
# ==========================================================================

from __future__ import annotations

import hashlib
import json
import logging
import shutil
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_CACHE_META_FILE = "cache_meta.json"


@dataclass
class CacheEntry:
    """Metadata for a single cached skill bundle."""

    skill_id: str
    version: str
    path: Path
    sha256: str = ""
    downloaded_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class SkillCache:
    """File-system cache for downloaded skill bundles.

    Parameters
    ----------
    cache_dir:
        Root directory for all cached data.
    max_size_mb:
        Maximum total cache size in megabytes.  ``0`` means unlimited.
    """

    cache_dir: Path
    max_size_mb: int = 500

    def __post_init__(self) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._meta_path = self.cache_dir / _CACHE_META_FILE

    # -- Internal helpers ---------------------------------------------------

    def _load_meta(self) -> dict[str, Any]:
        """Load cache metadata from disk."""
        if self._meta_path.exists():
            return json.loads(self._meta_path.read_text(encoding="utf-8"))
        return {"entries": {}}

    def _save_meta(self, meta: dict[str, Any]) -> None:
        """Persist cache metadata to disk."""
        self._meta_path.write_text(
            json.dumps(meta, indent=2, default=str),
            encoding="utf-8",
        )

    # -- Public API ---------------------------------------------------------

    def get(self, skill_id: str, version: str) -> Path | None:
        """Return the path to a cached bundle, or ``None`` if not cached."""
        meta = self._load_meta()
        key = f"{skill_id}@{version}"
        entry = meta.get("entries", {}).get(key)
        if entry is None:
            return None
        path = Path(entry["path"])
        if path.exists():
            return path
        # Stale entry – remove it
        meta["entries"].pop(key, None)
        self._save_meta(meta)
        return None

    def put(
        self,
        skill_id: str,
        version: str,
        source_path: Path,
        *,
        sha256: str = "",
    ) -> Path:
        """Copy a bundle into the cache and return the cached path."""
        dest = self.cache_dir / skill_id / f"{version}.tar.gz"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, dest)

        meta = self._load_meta()
        key = f"{skill_id}@{version}"
        meta.setdefault("entries", {})[key] = {
            "skill_id": skill_id,
            "version": version,
            "path": str(dest),
            "sha256": sha256 or self._hash_file(dest),
            "downloaded_at": datetime.now(UTC).isoformat(),
        }
        self._save_meta(meta)
        logger.info("Cached %s -> %s", key, dest)
        return dest

    def evict(self, skill_id: str, version: str) -> bool:
        """Remove a specific cached entry.  Returns ``True`` if removed."""
        meta = self._load_meta()
        key = f"{skill_id}@{version}"
        entry = meta.get("entries", {}).get(key)
        if entry is None:
            return False
        path = Path(entry["path"])
        if path.exists():
            path.unlink()
        meta["entries"].pop(key, None)
        self._save_meta(meta)
        return True

    def clear(self) -> int:
        """Remove all cached data.  Returns the number of entries removed."""
        meta = self._load_meta()
        count = len(meta.get("entries", {}))
        shutil.rmtree(self.cache_dir, ignore_errors=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        return count

    def list_cached(self) -> list[str]:
        """Return a list of ``skill_id@version`` strings for all cached entries."""
        meta = self._load_meta()
        return sorted(meta.get("entries", {}).keys())

    # -- Utilities ----------------------------------------------------------

    @staticmethod
    def _hash_file(path: Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
