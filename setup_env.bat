@echo off
REM Script de Configuração Rápida - IQ Option API (Windows)
REM Executa o script Python de setup

echo ============================================================
echo    Script de Configuracao - IQ Option API
echo ============================================================
echo.
echo Modo: Interativo (pergunta antes de desinstalar)
echo Para modo automatico, use: python setup_env.py --auto
echo.

python setup_env.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Script executado com sucesso!
) else (
    echo.
    echo Erro ao executar o script
    pause
)

