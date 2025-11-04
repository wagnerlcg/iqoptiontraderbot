@echo off
setlocal enabledelayedexpansion
set confirm=
set /p confirm=Digite SIM: 
if /i "!confirm!" NEQ "SIM" (
    echo Nao confirmado: !confirm!
) else (
    echo Confirmado corretamente!
)
