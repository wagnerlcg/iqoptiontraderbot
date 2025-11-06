#!/bin/bash
# Script para atualizar projeto sem usar Git (quando há problema de conexão)
# Execute após transferir arquivos via rsync/SCP
# Copie e cole este script diretamente no servidor se necessário

set -e

echo "=========================================="
echo "  Atualizar Projeto (Sem Git)"
echo "=========================================="
echo ""

PROJECT_DIR="/var/www/iqoptiontraderbot"
SERVICE_NAME="iqoptiontraderbot"

cd "$PROJECT_DIR"

echo "1. Ativando ambiente virtual..."
if [ ! -d "venv" ]; then
    echo "❌ Ambiente virtual não encontrado! Criando..."
    python3 -m venv venv
fi

source venv/bin/activate

echo ""
echo "2. Atualizando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "3. Verificando arquivo .env..."
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo "⚠️  Mantenha suas credenciais seguras!"
else
    echo "✅ Arquivo .env preservado"
fi

echo ""
echo "4. Ajustando permissões..."
sudo chown -R www-data:www-data "$PROJECT_DIR"
sudo chmod +x wsgi.py

echo ""
echo "5. Reiniciando serviço..."
sudo systemctl restart $SERVICE_NAME

echo ""
echo "6. Verificando status..."
sleep 2
sudo systemctl status $SERVICE_NAME --no-pager | head -n 15

echo ""
echo "=========================================="
echo "  Atualização concluída!"
echo "=========================================="
echo ""
echo "Verificar logs:"
echo "  sudo journalctl -u $SERVICE_NAME -f"
echo ""
