@echo off
echo ============================================================
echo    Iniciando Interface Web - IQ Option Trading Bot
echo ============================================================
echo.

REM Verificar se o ambiente virtual existe
if exist "venv\Scripts\activate.bat" (
    echo Ativando ambiente virtual...
    call venv\Scripts\activate.bat
) else (
    echo AVISO: Ambiente virtual nao encontrado.
    echo Criando ambiente virtual...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Instalando dependencias...
    pip install -r requirements.txt
)

echo.
echo Verificando dependencias...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Instalando Flask e dependencias...
    pip install -r requirements.txt
) else (
    echo Dependencias OK!
)

echo.
echo ============================================================
echo    Interface Web iniciando...
echo    Acesse: http://localhost:5000
echo ============================================================
echo.
echo Pressione Ctrl+C para parar o servidor
echo.

python app.py

pause

