#!/usr/bin/env python
"""Execute a GMDSI tutorial notebook against THIS pixi environment (for CI).

The GMDSI notebooks are written to use the repo's bundled flopy/pyemu and the
bundled binaries in ``bin_new/``. This runner patches a notebook so it instead
uses the pixi environment:

  * removes the ``assert "dependencies" in flopy/pyemu.__file__`` guards (we use
    the conda-installed flopy/pyemu), and
  * disables ``herebedragons.prep_bins(...)`` so model runs use the executables
    on PATH (extended mf6 from get-mf6, mp7/gridgen/triangle from get-exes, and
    pestpp from conda) instead of the bundled copies.

The (patched) notebook is executed in its own directory; the original file on
disk is not modified. Any cell error aborts with a non-zero exit code.

Usage: python scripts/run_notebook.py <notebook.ipynb> [timeout_seconds]
"""

import sys
from pathlib import Path

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor


def patch_source(src: str) -> str:
    out = []
    for line in src.splitlines():
        stripped = line.lstrip()
        if stripped.startswith(('assert "dependencies"', "assert 'dependencies'")):
            out.append("# [run_notebook] removed dependency assert: " + line)
        elif "prep_bins" in line:
            out.append("# [run_notebook] disabled prep_bins (use PATH exes): " + line)
        else:
            out.append(line)
    return "\n".join(out)


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("usage: run_notebook.py <notebook.ipynb> [timeout_seconds]")
    nb_path = Path(sys.argv[1]).resolve()
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 1800

    nb = nbformat.read(nb_path, as_version=4)
    for cell in nb.cells:
        if cell.cell_type == "code":
            cell.source = patch_source(cell.source)

    print(f"[run_notebook] executing {nb_path.name} "
          f"(cwd={nb_path.parent}, timeout={timeout}s)")
    ep = ExecutePreprocessor(timeout=timeout, kernel_name="python3")
    ep.preprocess(nb, {"metadata": {"path": str(nb_path.parent)}})
    print(f"[run_notebook] OK: {nb_path.name}")


if __name__ == "__main__":
    main()
