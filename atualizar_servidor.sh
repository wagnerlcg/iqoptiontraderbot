#!/bin/bash
# Script para atualizar o projeto no servidor
# Execute: bash atualizar_servidor.sh

set -e

echo "=========================================="
echo "  Atualizar Projeto no Servidor"
echo "=========================================="
echo ""

# Configurações
PROJECT_DIR="/var/www/iqoptiontraderbot"
SERVICE_NAME="iqoptiontraderbot"

# Verificar se está no diretório correto
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Diretório $PROJECT_DIR não encontrado!"
    exit 1
fi

cd "$PROJECT_DIR"

echo "Diretório: $PROJECT_DIR"
echo ""

# Verificar se é um repositório Git
if [ -d ".git" ]; then
    echo "📦 Repositório Git detectado"
    echo ""
    
    echo "1. Verificando mudanças remotas..."
    git fetch origin
    
    echo ""
    echo "2. Status atual:"
    git status
    
    echo ""
    read -p "Atualizar do GitHub? (S/N): " updateGit
    if [ "$updateGit" = "S" ] || [ "$updateGit" = "s" ]; then
        echo ""
        echo "3. Fazendo pull do GitHub..."
        
        # Verificar se há mudanças locais
        if ! git diff-index --quiet HEAD --; then
            echo "⚠️  Há mudanças locais não commitadas"
            read -p "Descartar mudanças locais e usar versão do GitHub? (S/N): " discardLocal
            if [ "$discardLocal" = "S" ] || [ "$discardLocal" = "s" ]; then
                git reset --hard origin/main
            else
                echo "Salvando mudanças locais..."
                git stash
            fi
        fi
        
        git pull origin main
        
        if [ "$discardLocal" != "S" ] && [ "$discardLocal" != "s" ]; then
            echo "Aplicando mudanças locais salvas..."
            git stash pop || true
        fi
        
        echo "✅ Atualização do Git concluída"
    fi
else
    echo "⚠️  Não é um repositório Git"
    echo "Arquivos devem ser atualizados manualmente ou via SCP/rsync"
fi

echo ""
echo "4. Ativando ambiente virtual..."
if [ ! -d "venv" ]; then
    echo "❌ Ambiente virtual não encontrado!"
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

source venv/bin/activate

echo ""
echo "5. Atualizando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "6. Verificando arquivo .env..."
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo "Criando template..."
    cat > .env << EOF
# Configurações do IQ Option
IQ_OPTION_EMAIL=seu-email@exemplo.com
IQ_OPTION_PASSWORD=sua-senha
IQ_OPTION_ACCOUNT_TYPE=PRACTICE

# Configurações de Trading
IQ_OPTION_STOP_LOSS=5
IQ_OPTION_STOP_WIN=100
IQ_OPTION_ENTRY_TYPE=PERCENT
IQ_OPTION_ENTRY_VALUE=1
IQ_OPTION_GALE=0

# Flask
FLASK_ENV=production
FLASK_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
EOF
    echo "⚠️  EDITE O ARQUIVO .env COM SUAS CONFIGURAÇÕES!"
else
    echo "✅ Arquivo .env existe"
fi

echo ""
echo "7. Ajustando permissões..."
sudo chown -R www-data:www-data "$PROJECT_DIR"
sudo chmod +x wsgi.py

echo ""
echo "8. Reiniciando serviço..."
sudo systemctl restart $SERVICE_NAME

echo ""
echo "9. Verificando status do serviço..."
sleep 2
sudo systemctl status $SERVICE_NAME --no-pager | head -n 10

echo ""
echo "=========================================="
echo "  Atualização concluída!"
echo "=========================================="
echo ""
echo "Logs do serviço:"
echo "  sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "Verificar status:"
echo "  sudo systemctl status $SERVICE_NAME"
echo ""
echo "Testar aplicação:"
echo "  curl http://localhost:8000/bot/"
echo ""

