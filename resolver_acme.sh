#!/bin/bash
# Script para resolver problema de validação ACME
# Execute: bash resolver_acme.sh

set -e

echo "=========================================="
echo "  Resolver Validação ACME"
echo "=========================================="
echo ""

# 1. Verificar configuração atual
echo "1. Verificando configuração atual..."
if sudo grep -q "\.well-known/acme-challenge" /etc/nginx/sites-available/iqoptiontraderbot; then
    echo "✅ Configuração ACME encontrada"
    sudo grep -A 5 "well-known" /etc/nginx/sites-available/iqoptiontraderbot
else
    echo "❌ Configuração ACME NÃO encontrada!"
fi

# 2. Verificar diretório
echo ""
echo "2. Verificando diretório..."
if [ -d "/var/www/html/.well-known/acme-challenge" ]; then
    echo "✅ Diretório existe"
    ls -la /var/www/html/.well-known/acme-challenge/
else
    echo "❌ Diretório não existe! Criando..."
    sudo mkdir -p /var/www/html/.well-known/acme-challenge
    sudo chown -R www-data:www-data /var/www/html/.well-known
fi

# 3. Verificar configurações conflitantes
echo ""
echo "3. Verificando configurações conflitantes..."
CONFLICTS=$(sudo grep -r "seu-dominio.com" /etc/nginx/sites-available/ /etc/nginx/sites-enabled/ 2>/dev/null || true)
if [ -n "$CONFLICTS" ]; then
    echo "⚠️  Configurações conflitantes encontradas:"
    echo "$CONFLICTS"
else
    echo "✅ Nenhuma configuração conflitante"
fi

# 4. Testar acesso manual
echo ""
echo "4. Testando acesso manual..."
echo "test-manual-$(date +%s)" | sudo tee /var/www/html/.well-known/acme-challenge/test-manual > /dev/null
TEST_RESULT=$(curl -s http://nomadtradersystem.com/.well-known/acme-challenge/test-manual 2>&1 || echo "ERRO")
if echo "$TEST_RESULT" | grep -q "test-manual"; then
    echo "✅ Acesso funcionando!"
else
    echo "❌ Acesso NÃO funcionando: $TEST_RESULT"
fi

# 5. Oferecer soluções
echo ""
echo "=========================================="
echo "  Escolha uma solução:"
echo "=========================================="
echo ""
echo "A) Usar Certbot Standalone (recomendado se acima falhou)"
echo "B) Corrigir configuração manualmente"
echo "C) Usar método webroot"
echo ""
read -p "Escolha (A/B/C): " escolha

case $escolha in
    A|a)
        echo ""
        echo "Usando método Standalone..."
        echo "⚠️  Nginx será parado temporariamente"
        read -p "Continuar? (S/N): " confirmar
        if [ "$confirmar" = "S" ] || [ "$confirmar" = "s" ]; then
            sudo systemctl stop nginx
            sudo certbot certonly --standalone -d nomadtradersystem.com -d www.nomadtradersystem.com
            sudo systemctl start nginx
            echo ""
            echo "✅ Certificados criados! Agora configure Nginx:"
            echo "sudo certbot --nginx -d nomadtradersystem.com -d www.nomadtradersystem.com"
        fi
        ;;
    B|b)
        echo ""
        echo "Abra o editor para corrigir manualmente:"
        echo "sudo nano /etc/nginx/sites-available/iqoptiontraderbot"
        echo ""
        echo "Certifique-se de que esta linha está ANTES de qualquer location /bot:"
        echo ""
        echo "    location /.well-known/acme-challenge/ {"
        echo "        root /var/www/html;"
        echo "        allow all;"
        echo "    }"
        ;;
    C|c)
        echo ""
        echo "Usando método Webroot..."
        sudo certbot certonly --webroot -w /var/www/html -d nomadtradersystem.com -d www.nomadtradersystem.com
        ;;
    *)
        echo "Opção inválida"
        ;;
esac

echo ""
echo "=========================================="
echo "  Diagnóstico concluído!"
echo "=========================================="

