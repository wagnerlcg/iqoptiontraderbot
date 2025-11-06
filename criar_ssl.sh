#!/bin/bash
# Script para criar certificados SSL e configurar HTTPS

echo "=========================================="
echo "  Criar Certificados SSL"
echo "=========================================="
echo ""

# Verificar se certbot está instalado
if ! command -v certbot &> /dev/null; then
    echo "Instalando Certbot..."
    sudo apt-get update
    sudo apt-get install -y certbot python3-certbot-nginx
fi

echo ""
echo "Criando certificados SSL para nomadtradersystem.com..."
echo ""
echo "⚠️  IMPORTANTE:"
echo "  1. O domínio nomadtradersystem.com deve apontar para este servidor"
echo "  2. A porta 80 deve estar acessível externamente"
echo "  3. Você precisará fornecer um email para notificações"
echo ""

# Criar certificados
sudo certbot --nginx -d nomadtradersystem.com -d www.nomadtradersystem.com

echo ""
echo "Verificando certificados criados..."
sudo ls -la /etc/letsencrypt/live/nomadtradersystem.com/

echo ""
echo "Testando renovação automática..."
sudo certbot renew --dry-run

echo ""
echo "=========================================="
echo "  Próximos Passos"
echo "=========================================="
echo ""
echo "1. Copiar arquivo nginx.conf atualizado do Windows"
echo "2. Ou editar manualmente: sudo nano /etc/nginx/sites-available/iqoptiontraderbot"
echo "3. Testar configuração: sudo nginx -t"
echo "4. Recarregar: sudo systemctl reload nginx"
echo ""

