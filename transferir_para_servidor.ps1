# Script PowerShell para Transferir Arquivos para o Servidor (Sem rsync)
# Usa SCP nativo do Windows
# Execute: .\transferir_para_servidor.ps1

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Transferir Arquivos para Servidor" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Configurações
$SERVER_HOST = "10104"  # IP ou hostname do servidor
$SERVER_USER = "root"
$SERVER_PATH = "/var/www/iqoptiontraderbot"
$PROJECT_PATH = $PSScriptRoot

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
Write-Host "Escolha o método de transferência:" -ForegroundColor Yellow
Write-Host "  1. SCP direto (mais rápido para poucos arquivos)" -ForegroundColor Cyan
Write-Host "  2. ZIP + SCP (mais rápido para muitos arquivos)" -ForegroundColor Cyan
Write-Host ""
$method = Read-Host "Escolha (1 ou 2)"

if ($method -eq "1") {
    # Método 1: SCP direto
    Write-Host ""
    Write-Host "Transferindo arquivos via SCP..." -ForegroundColor Yellow
    
    # Lista de exclusões
    $excludePatterns = @(
        'venv',
        '__pycache__',
        '*.pyc',
        '.env',
        'logs',
        '.git',
        'node_modules'
    )
    
    # Lista de arquivos para transferir
    $files = Get-ChildItem -Path $PROJECT_PATH -Recurse -File | 
        Where-Object { 
            $filePath = $_.FullName
            $relativePath = $filePath.Substring($PROJECT_PATH.Length + 1)
            
            $shouldExclude = $false
            foreach ($pattern in $excludePatterns) {
                if ($relativePath -like "*$pattern*" -or $_.Name -eq $pattern) {
                    $shouldExclude = $true
                    break
                }
            }
            
            -not $shouldExclude
        }
    
    $total = $files.Count
    $current = 0
    
    Write-Host "Total de arquivos: $total" -ForegroundColor Gray
    Write-Host ""
    
    foreach ($file in $files) {
        $current++
        $relativePath = $file.FullName.Substring($PROJECT_PATH.Length + 1)
        $relativePath = $relativePath.Replace('\', '/')
        $serverDir = Split-Path -Path $relativePath -Parent
        
        # Criar diretório no servidor se necessário
        if ($serverDir -ne '' -and $serverDir -ne '.') {
            $dirPath = "$SERVER_PATH/$serverDir"
            ssh -o "StrictHostKeyChecking=no" "${SERVER_USER}@${SERVER_HOST}" "mkdir -p `"$dirPath`"" 2>$null | Out-Null
        }
        
        # Mostrar progresso
        $percent = [math]::Round(($current / $total) * 100)
        Write-Progress -Activity "Transferindo arquivos" -Status "$relativePath" -PercentComplete $percent
        
        # Transferir arquivo
        scp -o "StrictHostKeyChecking=no" "$($file.FullName)" "${SERVER_USER}@${SERVER_HOST}:$SERVER_PATH/$relativePath" 2>$null
        
        if ($current % 10 -eq 0) {
            Write-Host "[$current/$total] Transferindo..." -ForegroundColor Gray
        }
    }
    
    Write-Progress -Activity "Transferindo arquivos" -Completed
    
} elseif ($method -eq "2") {
    # Método 2: ZIP + SCP
    Write-Host ""
    Write-Host "Criando arquivo ZIP..." -ForegroundColor Yellow
    
    $zipFile = "$env:TEMP\iqoptiontraderbot_update.zip"
    
    # Remover ZIP anterior se existir
    if (Test-Path $zipFile) {
        Remove-Item $zipFile -Force
    }
    
    # Criar lista de arquivos para incluir
    Write-Host "Preparando arquivos..." -ForegroundColor Gray
    
    $files = Get-ChildItem -Path $PROJECT_PATH -Recurse -File | 
        Where-Object { 
            $filePath = $_.FullName
            $relativePath = $filePath.Substring($PROJECT_PATH.Length + 1)
            
            $shouldExclude = $false
            $excludePatterns = @('venv', '__pycache__', '.env', 'logs', '.git', 'node_modules')
            foreach ($pattern in $excludePatterns) {
                if ($relativePath -like "*$pattern*" -or $_.Name -eq $pattern) {
                    $shouldExclude = $true
                    break
                }
            }
            
            -not $shouldExclude
        }
    
    Write-Host "Total de arquivos: $($files.Count)" -ForegroundColor Gray
    
    # Criar ZIP
    Write-Host "Compactando arquivos..." -ForegroundColor Yellow
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    
    $zip = [System.IO.Compression.ZipFile]::Open($zipFile, [System.IO.Compression.ZipArchiveMode]::Create)
    
    foreach ($file in $files) {
        $relativePath = $file.FullName.Substring($PROJECT_PATH.Length + 1)
        $relativePath = $relativePath.Replace('\', '/')
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $file.FullName, $relativePath) | Out-Null
    }
    
    $zip.Dispose()
    
    $zipSize = (Get-Item $zipFile).Length / 1MB
    Write-Host "✅ ZIP criado: $zipFile ($([math]::Round($zipSize, 2)) MB)" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "Transferindo ZIP para o servidor..." -ForegroundColor Yellow
    scp -o "StrictHostKeyChecking=no" $zipFile "${SERVER_USER}@${SERVER_HOST}:/tmp/iqoptiontraderbot_update.zip"
    
    Write-Host ""
    Write-Host "Extraindo arquivos no servidor..." -ForegroundColor Yellow
    ssh -o "StrictHostKeyChecking=no" "${SERVER_USER}@${SERVER_HOST}" "cd $SERVER_PATH && unzip -o /tmp/iqoptiontraderbot_update.zip && rm /tmp/iqoptiontraderbot_update.zip"
    
    Write-Host ""
    Write-Host "Limpando arquivo temporário local..." -ForegroundColor Gray
    Remove-Item $zipFile -Force
    
    Write-Host "✅ Transferência concluída!" -ForegroundColor Green
    
} else {
    Write-Host "Opção inválida!" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Próximos Passos no Servidor" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Execute os seguintes comandos no servidor:" -ForegroundColor White
Write-Host ""
Write-Host "cd $SERVER_PATH" -ForegroundColor Cyan
Write-Host "chmod +x atualizar_sem_git.sh" -ForegroundColor Cyan
Write-Host "bash atualizar_sem_git.sh" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ou manualmente:" -ForegroundColor White
Write-Host "source venv/bin/activate" -ForegroundColor Gray
Write-Host "pip install -r requirements.txt" -ForegroundColor Gray
Write-Host "sudo chown -R www-data:www-data $SERVER_PATH" -ForegroundColor Gray
Write-Host "sudo systemctl restart iqoptiontraderbot" -ForegroundColor Gray
Write-Host "sudo systemctl status iqoptiontraderbot" -ForegroundColor Gray
Write-Host ""

# Copiar script de atualização para o servidor
Write-Host "Copiando script de atualização para o servidor..." -ForegroundColor Yellow
if (Test-Path "atualizar_sem_git.sh") {
    scp -o "StrictHostKeyChecking=no" "atualizar_sem_git.sh" "${SERVER_USER}@${SERVER_HOST}:$SERVER_PATH/"
    Write-Host "✅ Script copiado!" -ForegroundColor Green
}

Write-Host ""
$sshNow = Read-Host "Conectar ao servidor agora via SSH? (S/N)"
if ($sshNow -eq "S" -or $sshNow -eq "s") {
    ssh "${SERVER_USER}@${SERVER_HOST}"
}

Write-Host ""
Write-Host "✅ Processo concluído!" -ForegroundColor Green
