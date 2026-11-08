from __future__ import annotations

import subprocess

from conftest import REPO_ROOT

JS_DIR = REPO_ROOT / "tests" / "js"


def test_old_combinatorial_layouts_are_migrated_on_load() -> None:
    """[SCENARIO SC17@1]

    Runs web/js/combinatorial_migration.js unchanged under Node, with ComfyUI's app.js
    stubbed, and checks the 4- and 5-value layouts, the marker, and the new-node marker.
    """
    result = subprocess.run(
        [
            "node",
            "--import",
            str(JS_DIR / "register.mjs"),
            str(JS_DIR / "combinatorial_migration_check.mjs"),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
