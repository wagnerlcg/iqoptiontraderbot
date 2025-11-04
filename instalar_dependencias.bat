@echo off
echo ============================================================
echo    Instalando Dependencias - IQ Option Trading Bot
echo ============================================================
echo.

REM Verificar se o ambiente virtual existe
if exist "venv\Scripts\activate.bat" (
    echo Ativando ambiente virtual...
    call venv\Scripts\activate.bat
) else (
    echo Criando ambiente virtual...
    python -m venv venv
    call venv\Scripts\activate.bat
)

echo.
echo Instalando dependencias do requirements.txt...
pip install -r requirements.txt

echo.
echo ============================================================
echo    Dependencias instaladas com sucesso!
echo ============================================================
echo.
pause

