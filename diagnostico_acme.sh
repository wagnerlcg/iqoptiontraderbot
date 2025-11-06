#!/bin/bash
# Script de diagnóstico completo para problema ACME
# Execute: bash diagnostico_acme.sh

echo "=========================================="
echo "  Diagnóstico Completo - Let's Encrypt"
echo "=========================================="
echo ""

# 1. IP do servidor
echo "1. IP do servidor:"
INTERNAL_IP=$(hostname -I | awk '{print $1}')
EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || echo "Não conseguiu obter IP externo")
echo "  IP Interno: $INTERNAL_IP"
echo "  IP Externo: $EXTERNAL_IP"
echo ""

# 2. Verificar DNS
echo "2. Verificação DNS:"
DNS_IP=$(nslookup nomadtradersystem.com | grep -A 1 "Name:" | tail -1 | awk '{print $2}' || echo "Erro ao resolver")
echo "  DNS nomadtradersystem.com → $DNS_IP"
if [ "$DNS_IP" = "$EXTERNAL_IP" ]; then
    echo "  ✅ DNS aponta para IP correto"
else
    echo "  ⚠️  DNS NÃO aponta para IP do servidor!"
    echo "     Configure DNS: nomadtradersystem.com → $EXTERNAL_IP"
fi
echo ""

# 3. Verificar Firewall
echo "3. Status do Firewall:"
if command -v ufw &> /dev/null; then
    UFW_STATUS=$(sudo ufw status | head -1)
    echo "  $UFW_STATUS"
    if echo "$UFW_STATUS" | grep -q "Status: active"; then
        echo "  Verificando portas 80/443:"
        sudo ufw status | grep -E "(80|443)" || echo "  ⚠️  Portas 80/443 não encontradas nas regras"
    fi
else
    echo "  UFW não instalado"
fi
echo ""

# 4. Verificar porta 80
echo "4. Serviços na porta 80:"
PORTA_80=$(sudo netstat -tlnp 2>/dev/null | grep :80 || sudo ss -tlnp 2>/dev/null | grep :80 || echo "Nada encontrado")
if [ -n "$PORTA_80" ]; then
    echo "  $PORTA_80"
else
    echo "  ⚠️  Nenhum serviço escutando na porta 80!"
fi
echo ""

# 5. Verificar Nginx
echo "5. Status do Nginx:"
if systemctl is-active --quiet nginx; then
    echo "  ✅ Nginx está rodando"
    NGINX_LISTEN=$(sudo nginx -T 2>/dev/null | grep "listen.*80" | head -1 || echo "Não encontrado")
    echo "  Configuração listen: $NGINX_LISTEN"
else
    echo "  ⚠️  Nginx NÃO está rodando!"
fi
echo ""

# 6. Testar acesso local
echo "6. Teste de acesso local:"
sudo mkdir -p /var/www/html/.well-known/acme-challenge
echo "test-local" | sudo tee /var/www/html/.well-known/acme-challenge/test-local > /dev/null
LOCAL_TEST=$(curl -s http://localhost/.well-known/acme-challenge/test-local 2>&1)
if echo "$LOCAL_TEST" | grep -q "test-local"; then
    echo "  ✅ Acesso local funciona"
else
    echo "  ❌ Acesso local NÃO funciona: $LOCAL_TEST"
fi
echo ""

# 7. Verificar configurações conflitantes
echo "7. Configurações conflitantes:"
CONFLICTS=$(sudo grep -r "listen.*80" /etc/nginx/sites-available/ /etc/nginx/sites-enabled/ 2>/dev/null | grep -v "^#" | wc -l)
echo "  Encontradas $CONFLICTS configurações listen 80"
if [ "$CONFLICTS" -gt 1 ]; then
    echo "  ⚠️  Múltiplas configurações podem causar conflito!"
    sudo grep -r "listen.*80" /etc/nginx/sites-available/ /etc/nginx/sites-enabled/ 2>/dev/null | grep -v "^#"
fi
echo ""

# 8. Resumo e Recomendações
echo "=========================================="
echo "  Resumo e Recomendações"
echo "=========================================="
echo ""

if [ "$DNS_IP" != "$EXTERNAL_IP" ]; then
    echo "❌ CORRIGIR DNS primeiro!"
    echo "   Configure: nomadtradersystem.com → $EXTERNAL_IP"
    echo ""
fi

if ! systemctl is-active --quiet nginx; then
    echo "❌ Iniciar Nginx: sudo systemctl start nginx"
    echo ""
fi

if command -v ufw &> /dev/null && sudo ufw status | grep -q "Status: active"; then
    echo "⚠️  Verificar firewall: sudo ufw allow 80/tcp && sudo ufw allow 443/tcp"
    echo ""
fi

echo "Opções para criar certificados:"
echo ""
echo "A) Se DNS e porta 80 OK:"
echo "   sudo certbot --nginx -d nomadtradersystem.com -d www.nomadtradersystem.com"
echo ""
echo "B) Se porta 80 não acessível externamente:"
echo "   sudo certbot certonly --manual --preferred-challenges dns -d nomadtradersystem.com -d www.nomadtradersystem.com"
echo ""
echo "C) Se usar Cloudflare/Proxy:"
echo "   Desative proxy temporariamente OU use DNS-01 challenge"
echo ""

