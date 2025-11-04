#!/bin/bash
# Script de deploy para Bot IQ Option API
# Execute com: bash deploy.sh

set -e

echo "=========================================="
echo "  Deploy Bot IQ Option API"
echo "=========================================="

# Variáveis - AJUSTE CONFORME SEU AMBIENTE
PROJECT_DIR="/var/www/iqoptiontraderbot"
PROJECT_USER="www-data"
SERVICE_NAME="iqoptiontraderbot"
NGINX_SITE="iqoptiontraderbot"
DOMAIN="seu-dominio.com"

echo ""
echo "1. Verificando dependências do sistema..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado. Instale pip primeiro."
    exit 1
fi

# Verificar nginx
if ! command -v nginx &> /dev/null; then
    echo "⚠️  Nginx não encontrado. Instalando..."
    sudo apt-get update
    sudo apt-get install -y nginx
fi

echo "✅ Dependências verificadas"

echo ""
echo "2. Criando ambiente virtual..."

cd "$PROJECT_DIR"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Ambiente virtual criado"
else
    echo "✅ Ambiente virtual já existe"
fi

echo ""
echo "3. Ativando ambiente virtual e instalando dependências..."

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Dependências instaladas"

echo ""
echo "4. Criando diretório de logs..."

mkdir -p logs
chown -R $PROJECT_USER:$PROJECT_USER logs

echo "✅ Diretório de logs criado"

echo ""
echo "5. Configurando arquivo .env..."

if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado. Criando template..."
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
    echo "✅ Template .env criado. EDITE O ARQUIVO .env COM SUAS CONFIGURAÇÕES!"
else
    echo "✅ Arquivo .env já existe"
fi

echo ""
echo "6. Configurando Gunicorn..."

# Verificar se gunicorn.conf.py existe
if [ ! -f "gunicorn.conf.py" ]; then
    echo "❌ Arquivo gunicorn.conf.py não encontrado!"
    exit 1
fi

# Atualizar caminhos no gunicorn.conf.py se necessário
sed -i "s|basedir = .*|basedir = \"$PROJECT_DIR\"|g" gunicorn.conf.py

echo "✅ Gunicorn configurado"

echo ""
echo "7. Configurando Nginx..."

# Copiar configuração do nginx
sudo cp nginx.conf /etc/nginx/sites-available/$NGINX_SITE

# Atualizar caminhos no arquivo de configuração
sudo sed -i "s|/var/www/iqoptiontraderbot|$PROJECT_DIR|g" /etc/nginx/sites-available/$NGINX_SITE
sudo sed -i "s|nomadtradersystem.com|$DOMAIN|g" /etc/nginx/sites-available/$NGINX_SITE

# Criar link simbólico
if [ ! -L "/etc/nginx/sites-enabled/$NGINX_SITE" ]; then
    sudo ln -s /etc/nginx/sites-available/$NGINX_SITE /etc/nginx/sites-enabled/
fi

# Remover configuração padrão se existir
if [ -L "/etc/nginx/sites-enabled/default" ]; then
    sudo rm /etc/nginx/sites-enabled/default
fi

# Testar configuração do nginx
sudo nginx -t

echo "✅ Nginx configurado"

echo ""
echo "8. Configurando systemd service..."

# Copiar arquivo de serviço
sudo cp iqoptiontraderbot.service /etc/systemd/system/$SERVICE_NAME.service

# Atualizar caminhos no arquivo de serviço
sudo sed -i "s|/var/www/iqoptiontraderbot|$PROJECT_DIR|g" /etc/systemd/system/$SERVICE_NAME.service

# Recarregar systemd
sudo systemctl daemon-reload

echo "✅ Systemd service configurado"

echo ""
echo "9. Configurando permissões..."

sudo chown -R $PROJECT_USER:$PROJECT_USER "$PROJECT_DIR"
sudo chmod +x "$PROJECT_DIR/wsgi.py"

echo "✅ Permissões configuradas"

echo ""
echo "10. Iniciando serviços..."

# Reiniciar nginx
sudo systemctl restart nginx

# Iniciar serviço da aplicação
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

echo "✅ Serviços iniciados"

echo ""
echo "=========================================="
echo "  Deploy concluído com sucesso!"
echo "=========================================="
echo ""
echo "Status do serviço:"
sudo systemctl status $SERVICE_NAME --no-pager | head -n 10
echo ""
echo "Logs do serviço:"
echo "  sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "Logs do Nginx:"
echo "  sudo tail -f /var/log/nginx/iqoptiontraderbot_error.log"
echo ""
echo "Acesse sua aplicação em:"
echo "  http://$DOMAIN"
echo ""
echo "⚠️  IMPORTANTE:"
echo "  1. Edite o arquivo .env com suas credenciais do IQ Option"
echo "  2. Configure SSL com Let's Encrypt (certbot) para HTTPS"
echo "  3. Verifique os logs se houver problemas"
echo ""

