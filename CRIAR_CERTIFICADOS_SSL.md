# Criar Certificados SSL com Let's Encrypt

## 📋 Passo a Passo

### 1. Instalar Certbot (se ainda não estiver instalado)

```bash
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx
```

### 2. Criar Certificados SSL

```bash
# Obter certificado SSL automaticamente
sudo certbot --nginx -d nomadtradersystem.com -d www.nomadtradersystem.com
```

**Durante a instalação, certbot vai perguntar:**
- **Email**: Seu email (para notificações)
- **Aceitar termos**: Digite `A` e pressione Enter
- **Compartilhar email**: Digite `N` (opcional)
- **Redirecionar HTTP para HTTPS**: Escolha `2` (redirecionar)

### 3. Verificar Certificados Criados

```bash
sudo ls -la /etc/letsencrypt/live/nomadtradersystem.com/
```

Você deve ver:
- `fullchain.pem` - Certificado completo
- `privkey.pem` - Chave privada
- `cert.pem` - Certificado
- `chain.pem` - Cadeia de certificados

### 4. Verificar Renovação Automática

```bash
# Testar renovação
sudo certbot renew --dry-run

# Verificar se o serviço de renovação está ativo
sudo systemctl status certbot.timer
```

### 5. Atualizar Configuração do Nginx

Depois que os certificados forem criados, você precisa atualizar o arquivo `nginx.conf` com os caminhos corretos. 

**Ou use o arquivo atualizado que já foi criado localmente.**

### 6. Recarregar Nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## ⚠️ Problemas Comuns

### Erro: "Could not bind to port 80"
```bash
# Verificar se algo está usando a porta 80
sudo netstat -tlnp | grep :80

# Parar temporariamente outros serviços se necessário
sudo systemctl stop apache2  # se estiver rodando
```

### Erro: "Domain validation failed"
- Verifique se o domínio `nomadtradersystem.com` aponta para o IP do servidor
- Verifique DNS: `dig nomadtradersystem.com`
- Certifique-se de que a porta 80 está acessível externamente

### Certbot não consegue acessar o domínio
```bash
# Verificar DNS
nslookup nomadtradersystem.com

# Verificar se o servidor está acessível
curl -I http://nomadtradersystem.com
```

## 🔄 Após Criar Certificados

Depois que os certificados forem criados, você pode:

1. **Copiar o arquivo nginx.conf atualizado** do Windows para o servidor
2. **Ou editar manualmente** o arquivo do Nginx para incluir a configuração HTTPS

O arquivo `nginx.conf` já está preparado com os caminhos corretos dos certificados!

