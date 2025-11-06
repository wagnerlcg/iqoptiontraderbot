#!/bin/bash
# Script para limpar configuração conflitante e preparar para certificados
# Execute: bash preparar_certificados.sh

set -e

echo "=========================================="
echo "  Preparar para Certificados SSL"
echo "=========================================="
echo ""

# 1. Verificar DNS atual
echo "1. Verificando DNS atual..."
DNS_IP=$(nslookup nomadtradersystem.com | grep -A 1 "Name:" | tail -1 | awk '{print $2}' || echo "Erro")
SERVER_IP=$(curl -s ifconfig.me)
echo "   DNS atual: $DNS_IP"
echo "   IP servidor: $SERVER_IP"

if [ "$DNS_IP" != "$SERVER_IP" ]; then
    echo ""
    echo "⚠️  DNS NÃO aponta para IP correto!"
    echo "   Configure DNS: nomadtradersystem.com → $SERVER_IP"
    echo ""
    read -p "Continuar mesmo assim? (S/N): " continuar
    if [ "$continuar" != "S" ] && [ "$continuar" != "s" ]; then
        echo "Cancelado. Corrija DNS primeiro."
        exit 1
    fi
else
    echo "✅ DNS está correto!"
fi

# 2. Limpar configurações conflitantes
echo ""
echo "2. Limpando configurações conflitantes..."
CONFLICTS=$(sudo grep -r "seu-dominio.com" /etc/nginx/sites-available/ /etc/nginx/sites-enabled/ 2>/dev/null || true)
if [ -n "$CONFLICTS" ]; then
    echo "   Configurações conflitantes encontradas:"
    echo "$CONFLICTS" | sed 's/^/   /'
    echo ""
    echo "   Removendo/comentando configurações conflitantes..."
    
    # Comentar configurações com seu-dominio.com
    sudo sed -i 's/^[^#]*seu-dominio.com/# &/' /etc/nginx/sites-available/* 2>/dev/null || true
    sudo sed -i 's/^[^#]*seu-dominio.com/# &/' /etc/nginx/sites-enabled/* 2>/dev/null || true
    
    echo "✅ Configurações conflitantes comentadas"
else
    echo "✅ Nenhuma configuração conflitante encontrada"
fi

# 3. Verificar configuração do Nginx
echo ""
echo "3. Verificando configuração do Nginx..."
if sudo nginx -t; then
    echo "✅ Configuração válida"
else
    echo "❌ Erro na configuração!"
    exit 1
fi

# 4. Recarregar Nginx
echo ""
echo "4. Recarregando Nginx..."
sudo systemctl reload nginx
echo "✅ Nginx recarregado"

# 5. Verificar acesso ao desafio ACME
echo ""
echo "5. Verificando acesso ao desafio ACME..."
sudo mkdir -p /var/www/html/.well-known/acme-challenge
echo "test-$(date +%s)" | sudo tee /var/www/html/.well-known/acme-challenge/test > /dev/null
sleep 1
TEST_RESULT=$(curl -s http://nomadtradersystem.com/.well-known/acme-challenge/test 2>&1 || echo "ERRO")
if echo "$TEST_RESULT" | grep -q "test"; then
    echo "✅ Acesso ao desafio ACME funcionando"
else
    echo "⚠️  Acesso ao desafio pode não estar funcionando: $TEST_RESULT"
fi

echo ""
echo "=========================================="
echo "  Preparação concluída!"
echo "=========================================="
echo ""
echo "Próximos passos:"
echo ""
if [ "$DNS_IP" != "$SERVER_IP" ]; then
    echo "1. CORRIGIR DNS primeiro!"
    echo "   Configure: nomadtradersystem.com → $SERVER_IP"
    echo ""
    echo "2. Aguardar propagação DNS (verifique com: nslookup nomadtradersystem.com)"
    echo ""
    echo "3. Depois executar:"
    echo "   sudo certbot --nginx -d nomadtradersystem.com -d www.nomadtradersystem.com"
else
    echo "✅ DNS está correto. Pode criar certificados agora:"
    echo ""
    echo "   sudo certbot --nginx -d nomadtradersystem.com -d www.nomadtradersystem.com"
fi
echo ""
echo "OU usar DNS-01 challenge (não precisa corrigir DNS):"
echo "   sudo certbot certonly --manual --preferred-challenges dns -d nomadtradersystem.com -d www.nomadtradersystem.com"
echo ""

