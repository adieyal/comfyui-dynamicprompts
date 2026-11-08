"""Run the nodes without ComfyUI: stub `folder_paths` and put the repo root on sys.path."""

from __future__ import annotations

import sys
import tempfile
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE_PATH = Path(tempfile.mkdtemp(prefix="comfyui-base-"))

folder_paths = types.ModuleType("folder_paths")
folder_paths.base_path = str(BASE_PATH)  # type: ignore[attr-defined]
folder_paths.folder_names_and_paths = {}  # type: ignore[attr-defined]


def _add_model_folder_path(
    folder_name: str,
    full_folder_path: str,
    is_default: bool = False,
) -> None:
    paths, _ = folder_paths.folder_names_and_paths.setdefault(folder_name, ([], set()))
    if full_folder_path not in paths:
        if is_default:
            paths.insert(0, full_folder_path)
        else:
            paths.append(full_folder_path)


def _get_folder_paths(folder_name: str) -> list[str]:
    return folder_paths.folder_names_and_paths[folder_name][0][:]


folder_paths.add_model_folder_path = _add_model_folder_path  # type: ignore[attr-defined]
folder_paths.get_folder_paths = _get_folder_paths  # type: ignore[attr-defined]

sys.modules["folder_paths"] = folder_paths
sys.path.insert(0, str(REPO_ROOT))


def set_wildcard_roots(*roots: Path) -> None:
    folder_paths.folder_names_and_paths["wildcards"] = (
        [str(r) for r in roots],
        set(),
    )


@pytest.fixture
def wildcards(tmp_path: Path) -> Path:
    """A single, empty wildcard root replacing the registered ones."""
    root = tmp_path / "wildcards"
    root.mkdir()
    set_wildcard_roots(root)
    return root
