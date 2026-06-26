#!/usr/bin/env python
"""Clone (or update) the GMDSI tutorial notebooks into the project.

Clones https://github.com/gmdsi/GMDSI_notebooks into ./GMDSI_notebooks. If the
directory already exists it fast-forward pulls instead, so the task is safe to
re-run. Run via `pixi run get-notebooks`.
"""

import os
import subprocess
import sys
from pathlib import Path

REPO = "https://github.com/gmdsi/GMDSI_notebooks.git"
DEST_NAME = "GMDSI_notebooks"


def main() -> None:
    root = Path(os.environ.get("PIXI_PROJECT_ROOT", os.getcwd()))
    dest = root / DEST_NAME
    if (dest / ".git").exists():
        print(f"[get-notebooks] {dest} exists; pulling latest")
        subprocess.check_call(["git", "-C", str(dest), "pull", "--ff-only"])
    else:
        print(f"[get-notebooks] cloning {REPO} -> {dest}")
        subprocess.check_call(["git", "clone", REPO, str(dest)])
    print("[get-notebooks] done.")


if __name__ == "__main__":
    main()
