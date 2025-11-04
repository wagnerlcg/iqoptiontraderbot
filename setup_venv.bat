@echo off
REM Script Batch para configurar ambiente virtual - IQ Option API (Windows)
REM Execute: setup_venv.bat

echo ============================================================
echo    Configuracao de Ambiente Virtual - IQ Option API
echo ============================================================
echo.

echo 1. Verificando Python...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Python nao encontrado!
    echo Instale Python 3.7 ou superior de https://www.python.org/
    pause
    exit /b 1
)

echo.
echo 2. Criando ambiente virtual...
if exist venv (
    echo Ambiente virtual ja existe.
    echo Deseja recriar? (S/N)
    set /p response=
    if /i "%response%"=="S" (
        rmdir /s /q venv
        echo Ambiente virtual antigo removido.
    ) else (
        echo Usando ambiente virtual existente.
        goto activate
    )
)

python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo ERRO ao criar ambiente virtual!
    pause
    exit /b 1
)
echo Ambiente virtual criado com sucesso!

:activate
echo.
echo 3. Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo.
echo 4. Atualizando pip...
python -m pip install --upgrade pip

echo.
echo 5. Instalando dependencias...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ERRO ao instalar dependencias!
    pause
    exit /b 1
)
echo Dependencias instaladas com sucesso!

echo.
echo 6. Verificando arquivo .env...
if exist .env (
    echo Arquivo .env encontrado!
) else (
    if exist .env.example (
        copy .env.example .env
        echo Arquivo .env criado a partir do .env.example
    ) else (
        echo Criando arquivo .env...
        echo IQ_OPTION_EMAIL=seu_email@example.com > .env
        echo IQ_OPTION_PASSWORD=sua_senha_aqui >> .env
        echo Arquivo .env criado!
    )
    echo IMPORTANTE: Edite o arquivo .env e adicione suas credenciais reais!
)

echo.
echo 7. Testando instalacao...
python -c "from iqoptionapi import IQ_Option; print('OK: IQ_Option importado!')"

echo.
echo ============================================================
echo    Configuracao Concluida!
echo ============================================================
echo.
echo IMPORTANTE: Certifique-se de ativar o ambiente virtual antes de usar:
echo   venv\Scripts\activate.bat
echo.
echo Proximos passos:
echo 1. Ative o ambiente virtual: venv\Scripts\activate.bat
echo 2. Edite o arquivo .env com suas credenciais reais
echo 3. Execute: python TESTE_RAPIDO.py
echo.
pause

