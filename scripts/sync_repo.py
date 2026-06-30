#!/usr/bin/env python
"""Clone or update one or more git repos into directories named after each repo.

Usage:
    python scripts/sync_repo.py <repo-url> [<repo-url> ...]

For each URL, the repo is checked out into ``<PIXI_PROJECT_ROOT>/<repo-name>``
(the directory takes the repo's name, e.g. mf6-training):

  * missing            -> clone it.
  * present, up to date -> do nothing.
  * present, out of date -> fast-forward to the remote.
  * present, but local commits / changes block the update (i.e. it can't
    fast-forward) -> discard all local changes and hard-reset to the remote.

This is intentionally generic so additional notebook repos (e.g. a future
MODFLOW 6 notebooks repo) can be synced with the same task by adding their URL.
"""

import os
import subprocess
import sys
from pathlib import Path


def git(args, cwd, check=True, capture=False):
    return subprocess.run(
        ["git", *args], cwd=str(cwd), check=check, text=True,
        capture_output=capture,
    )


def repo_dir_name(url: str) -> str:
    name = url.rstrip("/").split("/")[-1]
    return name[:-4] if name.endswith(".git") else name


def upstream_ref(cwd: Path) -> str:
    """Remote ref to track: origin/<current-branch>, else the remote default."""
    branch = git(["rev-parse", "--abbrev-ref", "HEAD"], cwd, capture=True).stdout.strip()
    if branch != "HEAD":
        r = git(["rev-parse", "--verify", "--quiet", f"origin/{branch}"],
                cwd, check=False, capture=True)
        if r.returncode == 0:
            return f"origin/{branch}"
    # detached HEAD or no matching remote branch: fall back to origin's default
    return git(["rev-parse", "--abbrev-ref", "origin/HEAD"], cwd, capture=True).stdout.strip()


def sync(url: str, root: Path) -> None:
    dest = root / repo_dir_name(url)

    if not (dest / ".git").exists():
        print(f"[sync-repo] cloning {url} -> {dest}")
        git(["clone", url, str(dest)], cwd=root)
        return

    print(f"[sync-repo] checking {dest.name}")
    git(["fetch", "--quiet", "origin"], cwd=dest)
    ref = upstream_ref(dest)
    local = git(["rev-parse", "HEAD"], cwd=dest, capture=True).stdout.strip()
    remote = git(["rev-parse", ref], cwd=dest, capture=True).stdout.strip()
    base = git(["merge-base", "HEAD", ref], cwd=dest, capture=True).stdout.strip()

    if local == remote:
        print(f"[sync-repo] {dest.name} is up to date ({local[:7]}).")
        return

    print(f"[sync-repo] {dest.name} is out of date "
          f"(local {local[:7]} -> {ref} {remote[:7]}); updating")

    # Purely behind (no local commits): try a clean fast-forward first.
    if local == base and git(["merge", "--ff-only", ref], cwd=dest, check=False).returncode == 0:
        print(f"[sync-repo] {dest.name} fast-forwarded.")
        return

    # Local commits / changes / conflicts block a clean update -> discard them.
    print(f"[sync-repo] {dest.name} has local commits or changes; "
          "discarding them and resetting to remote")
    git(["reset", "--hard", ref], cwd=dest)
    git(["clean", "-fd"], cwd=dest)
    print(f"[sync-repo] {dest.name} reset to {ref}.")


def main() -> None:
    urls = sys.argv[1:]
    if not urls:
        sys.exit("usage: sync_repo.py <repo-url> [<repo-url> ...]")
    root = Path(os.environ.get("PIXI_PROJECT_ROOT", os.getcwd()))
    for url in urls:
        sync(url, root)
    print("[sync-repo] done.")


if __name__ == "__main__":
    main()
