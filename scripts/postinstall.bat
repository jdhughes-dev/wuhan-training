@echo off
REM Activation hook (Windows).

REM Point SSL_CERT_DIR at the dir that actually holds the conda cert bundle.
REM conda-forge's openssl otherwise sets it to an empty certs\ subdir, which
REM makes nested `pixi` calls inside the activated env warn
REM "ignoring SSL_CERT_DIR: no certificates found".
set "SSL_CERT_DIR=%CONDA_PREFIX%\Library\ssl"

REM Download parallel MODFLOW 6 on first activation. Fast no-op once mf6 exists
REM in THIS env. Never fails activation: if the download errors, it warns and
REM you can retry with `pixi run get-mf6`.
if exist "%CONDA_PREFIX%\bin\mf6.exe" goto :eof
python "%PIXI_PROJECT_ROOT%\scripts\get_mf6.py" || echo [get_mf6] WARNING: MODFLOW 6 setup failed; run "pixi run get-mf6" to retry. 1>&2
