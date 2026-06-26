@echo off
REM Activation hook (Windows): download parallel MODFLOW 6 on first activation.
REM Fast no-op once mf6 exists in THIS env. Never fails activation: if the
REM download errors, it warns and you can retry with `pixi run get-mf6`.
if exist "%CONDA_PREFIX%\bin\mf6.exe" goto :eof
python "%PIXI_PROJECT_ROOT%\scripts\get_mf6.py" || echo [get_mf6] WARNING: MODFLOW 6 setup failed; run "pixi run get-mf6" to retry. 1>&2
