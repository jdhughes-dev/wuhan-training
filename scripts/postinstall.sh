#!/usr/bin/env bash
# Activation hook (Unix): build parallel MODFLOW 6 on first activation.
# Fast no-op once mf6 exists in THIS env. Never fails activation: if the build
# errors (e.g. no network), it warns and you can retry with `pixi run get-mf6`.
if [ ! -x "${CONDA_PREFIX}/bin/mf6" ]; then
  python "${PIXI_PROJECT_ROOT}/scripts/get_mf6.py" || \
    echo "[get_mf6] WARNING: MODFLOW 6 setup failed; run 'pixi run get-mf6' to retry." >&2
fi
