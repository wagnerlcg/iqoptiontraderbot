# Diagnóstico Completo - Let's Encrypt Não Consegue Acessar Porta 80

## 🔴 Problema
Let's Encrypt não consegue acessar `http://nomadtradersystem.com/.well-known/acme-challenge/` - recebe 404 ou timeout.

## 🔍 Diagnóstico Passo a Passo

### 1. Verificar Firewall

```bash
# Verificar se firewall está bloqueando porta 80
sudo ufw status
sudo iptables -L -n | grep 80

# Se UFW estiver ativo, permitir porta 80
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload
```

### 2. Verificar DNS

```bash
# Verificar se DNS aponta para o IP correto
nslookup nomadtradersystem.com
nslookup www.nomadtradersystem.com

# Verificar IP do servidor
hostname -I
curl ifconfig.me

# Comparar: DNS deve apontar para o IP do servidor
```

### 3. Verificar Porta 80 Localmente

```bash
# Verificar se algo está escutando na porta 80
sudo netstat -tlnp | grep :80
sudo ss -tlnp | grep :80

# Testar localmente
curl -I http://localhost/.well-known/acme-challenge/test
curl -I http://127.0.0.1/.well-known/acme-challenge/test
```

### 4. Verificar Acesso Externo

```bash
# Testar de fora (use outro servidor ou online tool)
# Ou use curl de outro lugar para testar

# Criar arquivo de teste
echo "test" | sudo tee /var/www/html/.well-known/acme-challenge/test

# Verificar se está acessível
curl -v http://nomadtradersystem.com/.well-known/acme-challenge/test
```

### 5. Verificar Configuração do Nginx

```bash
# Ver configuração completa
sudo nginx -T | grep -A 20 "server_name nomadtradersystem"

# Verificar se há múltiplos server blocks na porta 80
sudo grep -r "listen 80" /etc/nginx/sites-available/
```

## ✅ Soluções

### Solução 1: Abrir Portas no Firewall

```bash
# UFW
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload

# iptables direto
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables-save

# Se usar firewalld
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### Solução 2: Verificar DNS

```bash
# Verificar DNS atual
dig nomadtradersystem.com
dig www.nomadtradersystem.com

# Verificar IP do servidor
hostname -I

# Se DNS não apontar para o IP correto:
# 1. Acesse seu provedor de DNS
# 2. Configure registro A:
#    nomadtradersystem.com → IP_DO_SERVIDOR
#    www.nomadtradersystem.com → IP_DO_SERVIDOR
# 3. Aguarde propagação DNS (pode levar até 48h, geralmente minutos)
```

### Solução 3: Verificar Cloudflare ou Proxy

Se você usa Cloudflare ou outro proxy:

```bash
# Cloudflare: Certbot precisa usar DNS-01 challenge
sudo certbot certonly --manual --preferred-challenges dns -d nomadtradersystem.com -d www.nomadtradersystem.com

# Ou desative proxy temporariamente no Cloudflare (modo DNS apenas)
```

### Solução 4: Usar Validação DNS (DNS-01 Challenge)

Se porta 80 não está acessível:

```bash
# Método DNS-01 (não precisa de porta 80)
sudo certbot certonly --manual --preferred-challenges dns -d nomadtradersystem.com -d www.nomadtradersystem.com

# Ele vai pedir para adicionar registro TXT no DNS
# Depois que criar certificados, configure Nginx manualmente
```

### Solução 5: Configurar Nginx Manualmente Após Certificados

Se conseguir certificados via DNS-01:

```bash
# 1. Criar certificados via DNS
sudo certbot certonly --manual --preferred-challenges dns -d nomadtradersystem.com -d www.nomadtradersystem.com

# 2. Configurar Nginx manualmente com certificados
sudo nano /etc/nginx/sites-available/iqoptiontraderbot
```

Adicione configuração HTTPS manualmente (veja `nginx.conf` completo).

## 🚀 Solução Rápida Recomendada

Execute este script de diagnóstico completo:

```bash
cat > /tmp/diagnostico_acme.sh << 'EOF'
#!/bin/bash
echo "=== Diagnóstico ACME ==="
echo ""
echo "1. IP do servidor:"
hostname -I
curl -s ifconfig.me
echo ""
echo "2. DNS:"
nslookup nomadtradersystem.com | grep Address
echo ""
echo "3. Firewall:"
sudo ufw status || echo "UFW não instalado"
echo ""
echo "4. Porta 80:"
sudo netstat -tlnp | grep :80 || echo "Nada escutando na porta 80"
echo ""
echo "5. Teste local:"
curl -I http://localhost/.well-known/acme-challenge/test 2>&1 | head -1
echo ""
echo "6. Configuração Nginx porta 80:"
sudo grep -r "listen 80" /etc/nginx/sites-available/ /etc/nginx/sites-enabled/ 2>/dev/null
EOF

chmod +x /tmp/diagnostico_acme.sh
bash /tmp/diagnostico_acme.sh
```

## 📝 Próximos Passos Após Diagnóstico

1. **Se firewall bloqueando**: Abra portas 80 e 443
2. **Se DNS incorreto**: Corrija registros DNS
3. **Se porta 80 ocupada**: Verifique qual serviço está usando
4. **Se usar Cloudflare/Proxy**: Use DNS-01 challenge ou desative proxy temporariamente

