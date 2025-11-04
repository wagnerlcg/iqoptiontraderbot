@echo off
setlocal enabledelayedexpansion
REM Script para executar IQ Option API
REM Ordem de solicitações:
REM 1. Logar
REM 2. Solicitar se será conta de prática ou conta real
REM 3. Stop Loss
REM 4. Stop Win
REM 5. Tipo de Entrada (fixo ou percentual da banca)
REM 6. Valor da Entrada
REM 7. Estratégia (script a executar)

echo ============================================================
echo    IQ Option API - Configuracao e Execucao
echo ============================================================
echo.

REM ============================================================
REM PASSO 1: Email e Senha
REM ============================================================
:step1_credenciais
echo ============================================================
echo    PASSO 1: Credenciais de Login
echo ============================================================
echo.

REM Verificar arquivo .env
if not exist ".env" (
    echo Arquivo .env nao encontrado. Criando...
    if exist ".env.example" (
        copy .env.example .env
    ) else (
        echo IQ_OPTION_EMAIL= > .env
        echo IQ_OPTION_PASSWORD= >> .env
        echo IQ_OPTION_ACCOUNT_TYPE=PRACTICE >> .env
    )
    echo.
    echo IMPORTANTE: Edite o arquivo .env e adicione suas credenciais!
    echo Pressione qualquer tecla quando terminar...
    pause >nul
)

REM Carregar credenciais do .env
set EMAIL=
set PASSWORD=
if exist ".env" (
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        if "%%a"=="IQ_OPTION_EMAIL" set EMAIL=%%b
        if "%%a"=="IQ_OPTION_PASSWORD" set PASSWORD=%%b
    )
)

REM Verificar se credenciais existem
if "!EMAIL!"=="" (
    echo ERRO: Email nao encontrado no arquivo .env
    echo Por favor, configure IQ_OPTION_EMAIL no arquivo .env
    pause
    goto :step1_credenciais
)

if "!PASSWORD!"=="" (
    echo ERRO: Senha nao encontrada no arquivo .env
    echo Por favor, configure IQ_OPTION_PASSWORD no arquivo .env
    pause
    goto :step1_credenciais
)

echo Email: !EMAIL!
echo Validando credenciais...
echo.

REM Validar login (executar do diretório pai para evitar conflito com http/)
cd ..
python iqoptionapi\validar_login.py >temp_login_output.txt 2>&1
set LOGIN_RESULT=!errorlevel!
cd iqoptionapi

if !LOGIN_RESULT! NEQ 0 (
    echo.
    echo *** ERRO: Falha na validacao do login! ***
    echo.
    type ..\temp_login_output.txt 2>nul
    echo.
    echo Possiveis causas:
    echo - Email ou senha incorretos no arquivo .env
    echo - Problema de conexao com a internet
    echo - Autenticacao de dois fatores 2FA necessaria
    echo - Servidores IQ Option temporariamente indisponiveis
    echo.
    echo Verifique o arquivo .env e tente novamente.
    echo.
    del ..\temp_login_output.txt >nul 2>&1
    set /p retry="Deseja tentar novamente? (S/N): "
    if /i "!retry!"=="S" (
        goto :step1_credenciais
    ) else (
        echo Saindo...
        exit /b 1
    )
)

echo.
echo OK: Login validado com sucesso!
del ..\temp_login_output.txt >nul 2>&1
echo.
timeout /t 1 /nobreak >nul

REM Carregar valores padrão do .env
set STOP_LOSS=5
set STOP_WIN=100
set ENTRY_TYPE=PERCENT
set ENTRY_VALUE=1

REM Carregar do .env se existir
if exist ".env" (
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        if "%%a"=="IQ_OPTION_STOP_LOSS" set STOP_LOSS=%%b
        if "%%a"=="IQ_OPTION_STOP_WIN" set STOP_WIN=%%b
        if "%%a"=="IQ_OPTION_ENTRY_TYPE" set ENTRY_TYPE=%%b
        if "%%a"=="IQ_OPTION_ENTRY_VALUE" set ENTRY_VALUE=%%b
    )
)

REM ============================================================
REM PASSO 2: Tipo de Conta (Prática ou Real)
REM ============================================================
goto :step2_tipo_conta

:step2_tipo_conta
echo ============================================================
echo    PASSO 2: Tipo de Conta
echo ============================================================
echo.
echo   1. PRACTICE (Conta Demo - Sem dinheiro real)
echo   2. REAL (Conta Real - DINHEIRO REAL)
echo.
set /p account_choice="Escolha o tipo de conta (1 ou 2): "

if "!account_choice!"=="1" (
    set ACCOUNT_TYPE=PRACTICE
    echo.
    echo Tipo de conta selecionado: PRACTICE
    timeout /t 1 /nobreak >nul
) else if "!account_choice!"=="2" (
    echo.
    echo ============================================================
    echo    ATENCAO: CONTA REAL SELECIONADA
    echo ============================================================
    echo.
    echo Voce esta prestes a usar a conta REAL com DINHEIRO REAL!
    echo Operacoes nesta conta envolvem risco de perda financeira.
    echo.
    set confirm=
    set /p confirm="Tem certeza que deseja continuar? (SIM para confirmar): "
    set "confirm_check=!confirm!"
    if /i "!confirm_check!"=="SIM" (
        set ACCOUNT_TYPE=REAL
        echo.
        echo Tipo de conta selecionado: REAL
        timeout /t 1 /nobreak >nul
    ) else (
        echo Operacao cancelada. Voltando...
        timeout /t 2 /nobreak >nul
        goto :step2_tipo_conta
    )
) else (
    echo Opcao invalida!
    timeout /t 2 /nobreak >nul
    goto :step2_tipo_conta
)

REM ============================================================
REM PASSO 3: Stop Loss
REM ============================================================
:step3_stop_loss
echo.
echo ============================================================
echo    PASSO 3: Configurar Stop Loss
echo ============================================================
echo.
echo O Stop Loss e IMPRESCINDIVEL e tem PRIORIDADE MAXIMA.
echo O robo nao permitira nenhuma operacao se o stop loss
echo for atingido, independente de qualquer outra condicao.
echo.
echo Valor atual: !STOP_LOSS! percent
echo.
set /p new_stop_loss="Digite o Stop Loss em percent (ex: 5, minimo 0.1, maximo 99): "

REM Remover espaços em branco
set "new_stop_loss=!new_stop_loss: =!"

REM Validar se não está vazio
if "!new_stop_loss!"=="" (
    echo Valor invalido! Campo nao pode estar vazio.
    timeout /t 2 /nobreak >nul
    goto :step3_stop_loss
)

set STOP_LOSS=!new_stop_loss!
echo.
echo Stop Loss configurado: !STOP_LOSS! percent
timeout /t 1 /nobreak >nul

REM ============================================================
REM PASSO 4: Stop Win
REM ============================================================
:step4_stop_win
echo.
echo ============================================================
echo    PASSO 4: Configurar Stop Win
echo ============================================================
echo.
echo Valor atual: !STOP_WIN! percent
echo.
set /p new_stop_win="Digite o Stop Win em percent (ex: 100): "

REM Remover espaços em branco
set "new_stop_win=!new_stop_win: =!"

REM Validar se não está vazio
if "!new_stop_win!"=="" (
    echo Valor invalido! Campo nao pode estar vazio.
    timeout /t 2 /nobreak >nul
    goto :step4_stop_win
)

set STOP_WIN=!new_stop_win!
echo.
echo Stop Win configurado: !STOP_WIN! percent
timeout /t 1 /nobreak >nul

REM ============================================================
REM PASSO 5: Tipo de Entrada (Fixo ou Percentual)
REM ============================================================
:step5_tipo_entrada
echo.
echo ============================================================
echo    PASSO 5: Tipo de Entrada
echo ============================================================
echo.
echo Tipo de Entrada:
echo   1. PERCENT - Porcentagem da banca
echo   2. FIXED - Valor fixo
echo.
echo Tipo atual: !ENTRY_TYPE!
echo.
set /p entry_type_choice="Escolha o tipo de entrada (1 ou 2): "

if "!entry_type_choice!"=="1" (
    set ENTRY_TYPE=PERCENT
    echo.
    echo Tipo de entrada selecionado: PERCENT
) else if "!entry_type_choice!"=="2" (
    set ENTRY_TYPE=FIXED
    echo.
    echo Tipo de entrada selecionado: FIXED
) else (
    echo Opcao invalida!
    timeout /t 2 /nobreak >nul
    goto :step5_tipo_entrada
)
timeout /t 1 /nobreak >nul

REM ============================================================
REM PASSO 6: Valor da Entrada
REM ============================================================
:step6_valor_entrada
echo.
echo ============================================================
echo    PASSO 6: Valor da Entrada
echo ============================================================
echo.
if "!ENTRY_TYPE!"=="PERCENT" (
    echo Valor atual: !ENTRY_VALUE! percent da banca
    echo.
    set /p new_entry_value="Digite a porcentagem da banca (ex: 1 para 1 percent): "
) else (
    echo Valor atual: $!ENTRY_VALUE!
    echo.
    set /p new_entry_value="Digite o valor fixo em dolares (ex: 10): "
)

REM Remover espaços em branco
set "new_entry_value=!new_entry_value: =!"

REM Validar se não está vazio
if "!new_entry_value!"=="" (
    echo Valor invalido! Campo nao pode estar vazio.
    timeout /t 2 /nobreak >nul
    goto :step6_valor_entrada
)

set ENTRY_VALUE=!new_entry_value!
if "!ENTRY_TYPE!"=="PERCENT" (
    echo.
    echo Valor de entrada configurado: !ENTRY_VALUE! percent da banca
) else (
    echo.
    echo Valor de entrada configurado: $!ENTRY_VALUE!
)
timeout /t 1 /nobreak >nul

REM Salvar configurações no .env
call :save_config_to_env

REM ============================================================
REM PASSO 7: Estratégia (Script)
REM ============================================================
:step7_estrategia
echo.
echo ============================================================
echo    PASSO 7: Estrategia (Script)
echo ============================================================
echo.
echo Scripts Disponiveis:
echo   1. examples/basic_trading.py - Exemplo basico de trading
echo   2. examples/market_analysis.py - Analise de mercado
echo   3. examples/streaming_data.py - Streaming de dados em tempo real
echo   4. examples/portfolio_management.py - Gerenciamento de portfolio
echo   5. examples/stop_loss_example.py - Exemplo de protecao de Stop Loss
echo   6. examples/executar_sinais.py - Executar sinais do arquivo sinais.txt
echo.
set /p script_choice="Escolha a estrategia (1-6): "

if "!script_choice!"=="1" set SCRIPT_FILE=examples\basic_trading.py
if "!script_choice!"=="2" set SCRIPT_FILE=examples\market_analysis.py
if "!script_choice!"=="3" set SCRIPT_FILE=examples\streaming_data.py
if "!script_choice!"=="4" set SCRIPT_FILE=examples\portfolio_management.py
if "!script_choice!"=="5" set SCRIPT_FILE=examples\stop_loss_example.py
if "!script_choice!"=="6" set SCRIPT_FILE=examples\executar_sinais.py

if not defined SCRIPT_FILE (
    echo Opcao invalida!
    timeout /t 2 /nobreak >nul
    goto :step7_estrategia
)

echo.
echo Script selecionado: !SCRIPT_FILE!
timeout /t 1 /nobreak >nul

REM ============================================================
REM Executar Script
REM ============================================================
echo.
echo ============================================================
echo    Resumo da Configuracao
echo ============================================================
echo.
echo Email: !EMAIL!
echo Tipo de Conta: !ACCOUNT_TYPE!
echo Script: !SCRIPT_FILE!
echo.
echo Configuracoes de Trading:
echo   [PRIORIDADE MAXIMA] Stop Loss: !STOP_LOSS! percent
echo   Stop Win: !STOP_WIN! percent
echo   Tipo de Entrada: !ENTRY_TYPE!
if "!ENTRY_TYPE!"=="PERCENT" (
    echo   Valor de Entrada: !ENTRY_VALUE! percent da banca
) else (
    echo   Valor de Entrada: $!ENTRY_VALUE!
)
echo.
if "!ACCOUNT_TYPE!"=="REAL" (
    echo *** ATENCAO: Usando CONTA REAL com DINHEIRO REAL! ***
    echo.
)
echo ============================================================
echo    PROTECAO DE STOP LOSS ATIVADA - PRIORIDADE MAXIMA
echo ============================================================
echo.
echo O Stop Loss de !STOP_LOSS! percent sera monitorado continuamente.
echo Em hipotese alguma o robo permitira perdas acima deste limite.
echo Todas as operacoes serao PARADAS AUTOMATICAMENTE se o stop
echo loss for atingido, independente de qualquer outra condicao.
echo.
set /p confirm_run="Deseja executar agora? (S/N): "

if /i not "!confirm_run!"=="S" (
    echo Execucao cancelada.
    timeout /t 2 /nobreak >nul
    goto :step7_estrategia
)

echo.
echo Executando script...
echo.

REM Passar configurações para o Python via variáveis de ambiente
set IQ_OPTION_ACCOUNT_TYPE=!ACCOUNT_TYPE!
set IQ_OPTION_STOP_LOSS=!STOP_LOSS!
set IQ_OPTION_STOP_WIN=!STOP_WIN!
set IQ_OPTION_ENTRY_TYPE=!ENTRY_TYPE!
set IQ_OPTION_ENTRY_VALUE=!ENTRY_VALUE!

python !SCRIPT_FILE!

REM Limpar variáveis de ambiente após execução
set IQ_OPTION_ACCOUNT_TYPE=
set IQ_OPTION_STOP_LOSS=
set IQ_OPTION_STOP_WIN=
set IQ_OPTION_ENTRY_TYPE=
set IQ_OPTION_ENTRY_VALUE=

echo.
echo ============================================================
echo    Script finalizado
echo ============================================================
echo.
set /p again="Deseja executar outro script? (S/N): "
if /i "!again!"=="S" (
    set SCRIPT_FILE=
    goto :step7_estrategia
)

echo.
echo Saindo...
goto :eof

REM ============================================================
REM Funções Auxiliares
REM ============================================================

:configure_stop_loss_win
echo.
echo Configurar Stop Loss e Stop Win:
echo.
echo Valor atual Stop Loss: !STOP_LOSS! percent
set /p new_stop_loss="Digite o Stop Loss em percent (ex: 5, minimo 0.1, maximo 99): "
echo !new_stop_loss! | findstr /r "^[0-9]*\.*[0-9]*$" >nul
if errorlevel 1 (
    echo Valor invalido!
    timeout /t 2 /nobreak >nul
    goto :configure_stop_loss_win
)
set STOP_LOSS=!new_stop_loss!

echo.
echo Valor atual Stop Win: !STOP_WIN! percent
set /p new_stop_win="Digite o Stop Win em percent (ex: 100): "
echo !new_stop_win! | findstr /r "^[0-9]*\.*[0-9]*$" >nul
if errorlevel 1 (
    echo Valor invalido!
    timeout /t 2 /nobreak >nul
    goto :configure_stop_loss_win
)
set STOP_WIN=!new_stop_win!

REM Configurar tipo de entrada
echo.
echo Tipo de Entrada:
echo   1. PERCENT - Porcentagem da banca
echo   2. FIXED - Valor fixo
set /p entry_type_choice="Escolha (1 ou 2): "
if "!entry_type_choice!"=="1" (
    set ENTRY_TYPE=PERCENT
) else if "!entry_type_choice!"=="2" (
    set ENTRY_TYPE=FIXED
) else (
    echo Opcao invalida, usando PERCENT por padrao
    set ENTRY_TYPE=PERCENT
)

REM Configurar valor de entrada
echo.
if "!ENTRY_TYPE!"=="PERCENT" (
    set /p new_entry_value="Digite a porcentagem da banca (ex: 1 para 1 percent): "
) else (
    set /p new_entry_value="Digite o valor fixo em dolares (ex: 10): "
)
echo !new_entry_value! | findstr /r "^[0-9]*\.*[0-9]*$" >nul
if errorlevel 1 (
    echo Valor invalido!
    timeout /t 2 /nobreak >nul
    goto :configure_stop_loss_win
)
set ENTRY_VALUE=!new_entry_value!

REM Salvar no .env
call :save_config_to_env

echo.
echo Configuracao salva com sucesso!
timeout /t 2 /nobreak >nul
goto :eof

:save_config_to_env
REM Salvar configurações no arquivo .env
if not exist ".env" (
    echo IQ_OPTION_EMAIL= > ".env"
    echo IQ_OPTION_PASSWORD= >> ".env"
    echo IQ_OPTION_ACCOUNT_TYPE=PRACTICE >> ".env"
)

REM Remover linhas antigas se existirem
findstr /v /b /c:"IQ_OPTION_STOP_LOSS" ".env" > ".env.tmp" 2>nul
findstr /v /b /c:"IQ_OPTION_STOP_WIN" ".env.tmp" > ".env.tmp2" 2>nul
findstr /v /b /c:"IQ_OPTION_ENTRY_TYPE" ".env.tmp2" > ".env.tmp" 2>nul
findstr /v /b /c:"IQ_OPTION_ENTRY_VALUE" ".env.tmp" > ".env.tmp2" 2>nul

REM Adicionar novas configurações
echo IQ_OPTION_STOP_LOSS=!STOP_LOSS! >> ".env.tmp2"
echo IQ_OPTION_STOP_WIN=!STOP_WIN! >> ".env.tmp2"
echo IQ_OPTION_ENTRY_TYPE=!ENTRY_TYPE! >> ".env.tmp2"
echo IQ_OPTION_ENTRY_VALUE=!ENTRY_VALUE! >> ".env.tmp2"

move /y ".env.tmp2" ".env" >nul 2>&1
del ".env.tmp" >nul 2>&1
goto :eof
