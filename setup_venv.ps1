# Script PowerShell para configurar ambiente virtual - IQ Option API
# Execute: .\setup_venv.ps1

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "    Configuracao de Ambiente Virtual - IQ Option API" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se Python está instalado
Write-Host "1. Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   ERRO: Python nao encontrado!" -ForegroundColor Red
    Write-Host "   Instale Python 3.7 ou superior de https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

# Criar ambiente virtual
Write-Host ""
Write-Host "2. Criando ambiente virtual..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "   Ambiente virtual ja existe. Deseja recriar? (S/N)" -ForegroundColor Yellow
    $response = Read-Host
    if ($response -eq "S" -or $response -eq "s") {
        Remove-Item -Recurse -Force venv
        Write-Host "   Ambiente virtual antigo removido." -ForegroundColor Green
    } else {
        Write-Host "   Usando ambiente virtual existente." -ForegroundColor Green
        goto :activate
    }
}

python -m venv venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ERRO ao criar ambiente virtual!" -ForegroundColor Red
    exit 1
}
Write-Host "   Ambiente virtual criado com sucesso!" -ForegroundColor Green

:activate
# Ativar ambiente virtual
Write-Host ""
Write-Host "3. Ativando ambiente virtual..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ERRO ao ativar ambiente virtual!" -ForegroundColor Red
    Write-Host "   Tente executar manualmente: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    exit 1
}
Write-Host "   Ambiente virtual ativado!" -ForegroundColor Green

# Atualizar pip
Write-Host ""
Write-Host "4. Atualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
Write-Host "   pip atualizado!" -ForegroundColor Green

# Instalar dependências
Write-Host ""
Write-Host "5. Instalando dependencias..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ERRO ao instalar dependencias!" -ForegroundColor Red
    exit 1
}
Write-Host "   Dependencias instaladas com sucesso!" -ForegroundColor Green

# Verificar arquivo .env
Write-Host ""
Write-Host "6. Verificando arquivo .env..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "   Arquivo .env encontrado!" -ForegroundColor Green
} else {
    Write-Host "   Arquivo .env nao encontrado!" -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item .env.example .env
        Write-Host "   Arquivo .env criado a partir do .env.example" -ForegroundColor Green
        Write-Host "   IMPORTANTE: Edite o arquivo .env e adicione suas credenciais reais!" -ForegroundColor Yellow
    } else {
        Write-Host "   Criando arquivo .env..." -ForegroundColor Yellow
        @"
IQ_OPTION_EMAIL=seu_email@example.com
IQ_OPTION_PASSWORD=sua_senha_aqui
"@ | Out-File -FilePath .env -Encoding utf8
        Write-Host "   Arquivo .env criado!" -ForegroundColor Green
        Write-Host "   IMPORTANTE: Edite o arquivo .env e adicione suas credenciais reais!" -ForegroundColor Yellow
    }
}

# Testar instalação
Write-Host ""
Write-Host "7. Testando instalacao..." -ForegroundColor Yellow
python -c "from iqoptionapi import IQ_Option; print('✅ IQ_Option importado com sucesso!')"

if ($LASTEXITCODE -eq 0) {
    Write-Host "   Teste passou!" -ForegroundColor Green
} else {
    Write-Host "   Teste falhou, mas isso pode ser normal." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "    Configuracao Concluida!" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Yellow
Write-Host "1. Certifique-se de que o ambiente virtual esta ativado" -ForegroundColor White
Write-Host "   (Voce deve ver (venv) no inicio do prompt)" -ForegroundColor White
Write-Host ""
Write-Host "2. Edite o arquivo .env com suas credenciais reais" -ForegroundColor White
Write-Host ""
Write-Host "3. Execute um exemplo:" -ForegroundColor White
Write-Host "   python TESTE_RAPIDO.py" -ForegroundColor Cyan
Write-Host "   ou" -ForegroundColor White
Write-Host "   python examples/basic_trading.py" -ForegroundColor Cyan
Write-Host ""

