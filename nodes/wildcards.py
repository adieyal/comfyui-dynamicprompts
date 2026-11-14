"""Wildcard folder registration and a WildcardManager that tracks file changes."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

import folder_paths
from dynamicprompts.wildcards import WildcardManager

logger = logging.getLogger(__name__)

FOLDER_NAME = "wildcards"
EXTENSION_WILDCARDS = Path(__file__).resolve().parent.parent / "wildcards"

_cached_manager: tuple[str, WildcardManager] | None = None


def register_wildcard_folders() -> None:
    """Register ComfyUI's and this extension's wildcard folders with ComfyUI."""
    EXTENSION_WILDCARDS.mkdir(parents=True, exist_ok=True)
    base_wildcards = Path(folder_paths.base_path) / "wildcards"
    folder_paths.add_model_folder_path(FOLDER_NAME, str(base_wildcards))
    folder_paths.add_model_folder_path(FOLDER_NAME, str(EXTENSION_WILDCARDS))


def wildcard_roots() -> list[Path]:
    """The registered wildcard folders that exist, in registration order."""
    paths = [Path(p) for p in folder_paths.get_folder_paths(FOLDER_NAME)]
    return [p for p in paths if p.is_dir()]


def wildcard_signature(roots: list[Path]) -> str:
    """A digest that changes when any file under `roots` is added, removed or modified."""
    digest = hashlib.sha256()
    for root in roots:
        digest.update(f"{root}\0".encode())
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            try:
                stat = path.stat()
            except OSError:  # removed between listing and stat
                continue
            digest.update(f"{path}\0{stat.st_mtime_ns}\0{stat.st_size}\0".encode())
    return digest.hexdigest()


def may_use_wildcards(text: str) -> bool:
    """Whether a standard (non-Jinja) template can reach wildcard files: only `__name__` does."""
    return "__" in text


def change_key(*parts: str | int, scan_wildcards: bool = True) -> str:
    """An IS_CHANGED value derived from node inputs and the wildcard signature."""
    signature = wildcard_signature(wildcard_roots()) if scan_wildcards else ""
    return hashlib.sha256(repr((*parts, signature)).encode()).hexdigest()


def get_wildcard_manager(scan_wildcards: bool = True) -> WildcardManager:
    """A manager over all wildcard roots, rebuilt when any wildcard file changes.

    Without `scan_wildcards`, return a manager with no roots, for templates that can't reach files.
    """
    global _cached_manager
    if not scan_wildcards:
        return WildcardManager()
    roots = wildcard_roots()
    signature = wildcard_signature(roots)
    if _cached_manager is None or _cached_manager[0] != signature:
        logger.debug("Loading wildcards from %s", roots)
        _cached_manager = (signature, WildcardManager(root_map={"": list(roots)}))
    return _cached_manager[1]
