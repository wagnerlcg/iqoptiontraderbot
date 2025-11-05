# Script PowerShell para Atualizar Projeto no Servidor
# Execute: .\atualizar_servidor.ps1

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Atualizar Projeto no Servidor" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Configurações - AJUSTE CONFORME SEU AMBIENTE
$SERVER_USER = Read-Host "Usuário do servidor SSH (ex: root ou ubuntu)"
$SERVER_HOST = Read-Host "IP ou domínio do servidor (ex: 192.168.1.100 ou seu-servidor.com)"
$SERVER_PATH = "/var/www/iqoptiontraderbot"
$PROJECT_PATH = $PSScriptRoot

Write-Host ""
Write-Host "Configurações:" -ForegroundColor Yellow
Write-Host "  Servidor: $SERVER_USER@$SERVER_HOST" -ForegroundColor Gray
Write-Host "  Caminho no servidor: $SERVER_PATH" -ForegroundColor Gray
Write-Host "  Caminho local: $PROJECT_PATH" -ForegroundColor Gray
Write-Host ""

$confirm = Read-Host "Continuar? (S/N)"
if ($confirm -ne "S" -and $confirm -ne "s") {
    Write-Host "Cancelado." -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "Escolha o método de atualização:" -ForegroundColor Yellow
Write-Host "  1. Via Git (recomendado - precisa ter repositório configurado)" -ForegroundColor Cyan
Write-Host "  2. Via SCP (transferência direta de arquivos)" -ForegroundColor Cyan
Write-Host ""
$method = Read-Host "Escolha (1 ou 2)"

if ($method -eq "1") {
    # Método 1: Via Git
    Write-Host ""
    Write-Host "=== Método 1: Via Git ===" -ForegroundColor Green
    
    # Verificar se Git está inicializado
    if (-not (Test-Path ".git")) {
        Write-Host "Git não inicializado. Inicializando..." -ForegroundColor Yellow
        git init
        git add .
        $commitMsg = Read-Host "Mensagem do commit"
        git commit -m $commitMsg
    }
    
    # Verificar se há remote configurado
    $remote = git remote -v
    if (-not $remote) {
        Write-Host ""
        Write-Host "⚠️  Nenhum repositório remoto configurado!" -ForegroundColor Yellow
        $setupGit = Read-Host "Configurar Git agora? (S/N)"
        if ($setupGit -eq "S" -or $setupGit -eq "s") {
            $gitRepo = Read-Host "URL do repositório GitHub (ex: https://github.com/usuario/repo.git)"
            git remote add origin $gitRepo
            git branch -M main
            Write-Host "Fazendo push para GitHub..." -ForegroundColor Yellow
            git push -u origin main
        } else {
            Write-Host "Git não configurado. Use o método 2 (SCP) ou configure manualmente." -ForegroundColor Red
            exit
        }
    }
    
    # Fazer commit de mudanças locais
    Write-Host ""
    Write-Host "Verificando mudanças locais..." -ForegroundColor Yellow
    git add .
    $status = git status --porcelain
    if ($status) {
        $commitMsg = Read-Host "Há mudanças locais. Mensagem do commit"
        git commit -m $commitMsg
        Write-Host "Fazendo push para GitHub..." -ForegroundColor Yellow
        git push origin main
    } else {
        Write-Host "Nenhuma mudança local para commitar." -ForegroundColor Green
    }
    
    # Atualizar no servidor
    Write-Host ""
    Write-Host "Atualizando no servidor..." -ForegroundColor Yellow
    Write-Host "Execute os seguintes comandos no servidor:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "cd $SERVER_PATH" -ForegroundColor White
    Write-Host "git pull origin main" -ForegroundColor White
    Write-Host "source venv/bin/activate" -ForegroundColor White
    Write-Host "pip install -r requirements.txt" -ForegroundColor White
    Write-Host "sudo systemctl restart iqoptiontraderbot" -ForegroundColor White
    Write-Host "sudo systemctl status iqoptiontraderbot" -ForegroundColor White
    Write-Host ""
    
    $sshNow = Read-Host "Conectar ao servidor agora via SSH? (S/N)"
    if ($sshNow -eq "S" -or $sshNow -eq "s") {
        ssh "$SERVER_USER@$SERVER_HOST"
    }
    
} elseif ($method -eq "2") {
    # Método 2: Via SCP
    Write-Host ""
    Write-Host "=== Método 2: Via SCP ===" -ForegroundColor Green
    
    # Verificar se rsync está disponível (mais eficiente)
    $rsyncAvailable = Get-Command rsync -ErrorAction SilentlyContinue
    
    if ($rsyncAvailable) {
        Write-Host "Usando rsync (mais eficiente)..." -ForegroundColor Yellow
        rsync -avz `
            --exclude='venv' `
            --exclude='__pycache__' `
            --exclude='*.pyc' `
            --exclude='.env' `
            --exclude='logs' `
            --exclude='.git' `
            "$PROJECT_PATH/" "$SERVER_USER@${SERVER_HOST}:$SERVER_PATH/"
    } else {
        Write-Host "Usando SCP..." -ForegroundColor Yellow
        Write-Host "⚠️  Nota: SCP pode ser lento. Considere instalar rsync (winget install rsync)" -ForegroundColor Yellow
        
        # Criar lista de arquivos para transferir
        $files = Get-ChildItem -Path $PROJECT_PATH -Recurse | 
            Where-Object { 
                $_.FullName -notmatch 'venv' -and
                $_.FullName -notmatch '__pycache__' -and
                $_.FullName -notmatch '\.pyc$' -and
                $_.Name -ne '.env' -and
                $_.FullName -notmatch '\\logs\\'
            }
        
        Write-Host "Transferindo arquivos..." -ForegroundColor Yellow
        foreach ($file in $files) {
            $relativePath = $file.FullName.Substring($PROJECT_PATH.Length + 1)
            $serverDir = Split-Path -Path $relativePath -Parent
            $serverDir = $serverDir.Replace('\', '/')
            
            if ($serverDir -ne '') {
                ssh "$SERVER_USER@$SERVER_HOST" "mkdir -p $SERVER_PATH/$serverDir"
            }
            
            scp "$($file.FullName)" "$SERVER_USER@${SERVER_HOST}:$SERVER_PATH/$relativePath"
        }
    }
    
    Write-Host ""
    Write-Host "Arquivos transferidos!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Execute os seguintes comandos no servidor:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "cd $SERVER_PATH" -ForegroundColor White
    Write-Host "source venv/bin/activate" -ForegroundColor White
    Write-Host "pip install -r requirements.txt" -ForegroundColor White
    Write-Host "sudo chown -R www-data:www-data $SERVER_PATH" -ForegroundColor White
    Write-Host "sudo systemctl restart iqoptiontraderbot" -ForegroundColor White
    Write-Host "sudo systemctl status iqoptiontraderbot" -ForegroundColor White
    Write-Host ""
    
    $sshNow = Read-Host "Conectar ao servidor agora via SSH? (S/N)"
    if ($sshNow -eq "S" -or $sshNow -eq "s") {
        ssh "$SERVER_USER@$SERVER_HOST"
    }
    
} else {
    Write-Host "Opção inválida!" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Processo concluído!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Yellow
Write-Host "  1. Conecte-se ao servidor via SSH" -ForegroundColor White
Write-Host "  2. Execute os comandos mostrados acima" -ForegroundColor White
Write-Host "  3. Verifique os logs: sudo journalctl -u iqoptiontraderbot -f" -ForegroundColor White
Write-Host ""

