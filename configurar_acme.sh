#!/bin/bash
# Script para configurar Nginx para validação ACME
# Execute no servidor: bash configurar_acme.sh

set -e

echo "=========================================="
echo "  Configurar Nginx para Validação ACME"
echo "=========================================="
echo ""

# 1. Criar diretório para desafio ACME
echo "1. Criando diretório para desafio ACME..."
sudo mkdir -p /var/www/html/.well-known/acme-challenge
sudo chown -R www-data:www-data /var/www/html/.well-known
echo "✅ Diretório criado"

# 2. Fazer backup
echo ""
echo "2. Fazendo backup da configuração atual..."
sudo cp /etc/nginx/sites-available/iqoptiontraderbot /etc/nginx/sites-available/iqoptiontraderbot.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Backup criado"

# 3. Verificar se já existe a configuração do ACME
echo ""
echo "3. Verificando configuração atual..."
if grep -q "\.well-known/acme-challenge" /etc/nginx/sites-available/iqoptiontraderbot; then
    echo "⚠️  Configuração ACME já existe. Pulando..."
else
    echo "📝 Adicionando configuração ACME..."
    
    # Criar arquivo temporário com a configuração
    TEMP_FILE=$(mktemp)
    
    # Ler arquivo atual e adicionar location ACME antes do primeiro location
    awk '
    /^[[:space:]]*location/ && !found {
        print "    # CRÍTICO: Permitir desafio ACME do Let'\''s Encrypt (antes de qualquer outra regra)"
        print "    location /.well-known/acme-challenge/ {"
        print "        root /var/www/html;"
        print "        try_files $uri =404;"
        print "    }"
        print ""
        found = 1
    }
    { print }
    ' /etc/nginx/sites-available/iqoptiontraderbot > "$TEMP_FILE"
    
    # Se não encontrou location, adicionar antes do fechamento do server
    if ! grep -q "\.well-known/acme-challenge" "$TEMP_FILE"; then
        awk '
        /^[[:space:]]*server[[:space:]]*\{/ {
            print
            print "    # CRÍTICO: Permitir desafio ACME do Let'\''s Encrypt"
            print "    location /.well-known/acme-challenge/ {"
            print "        root /var/www/html;"
            print "        try_files $uri =404;"
            print "    }"
            next
        }
        { print }
        ' /etc/nginx/sites-available/iqoptiontraderbot > "$TEMP_FILE"
    fi
    
    # Copiar arquivo temporário para configuração
    sudo cp "$TEMP_FILE" /etc/nginx/sites-available/iqoptiontraderbot
    rm "$TEMP_FILE"
    
    echo "✅ Configuração ACME adicionada"
fi

# 4. Testar configuração
echo ""
echo "4. Testando configuração do Nginx..."
if sudo nginx -t; then
    echo "✅ Configuração válida"
else
    echo "❌ Erro na configuração! Verifique manualmente."
    exit 1
fi

# 5. Recarregar Nginx
echo ""
echo "5. Recarregando Nginx..."
sudo systemctl reload nginx
echo "✅ Nginx recarregado"

# 6. Testar acesso ao desafio
echo ""
echo "6. Testando acesso ao desafio ACME..."
echo "test" | sudo tee /var/www/html/.well-known/acme-challenge/test > /dev/null
if curl -s http://nomadtradersystem.com/.well-known/acme-challenge/test | grep -q "test"; then
    echo "✅ Acesso ao desafio ACME funcionando!"
else
    echo "⚠️  Não foi possível testar automaticamente. Verifique manualmente."
fi

echo ""
echo "=========================================="
echo "  Configuração concluída!"
echo "=========================================="
echo ""
echo "Agora você pode executar:"
echo "  sudo certbot --nginx -d nomadtradersystem.com -d www.nomadtradersystem.com"
echo ""

