# Resolver Erro 404 em HTTPS - nomadtradersystem.com/bot

## 🔴 Problema
Erro 404 ao acessar `https://nomadtradersystem.com/bot`

## 🔍 Causa
A configuração HTTPS do Nginx está comentada ou não tem configuração para o caminho `/bot`.

## ✅ Solução

### Passo 1: Verificar configuração atual do Nginx no servidor

```bash
# Conectar ao servidor
ssh root@10104

# Verificar configuração atual
sudo cat /etc/nginx/sites-available/iqoptiontraderbot
# ou
sudo cat /etc/nginx/sites-enabled/iqoptiontraderbot
```

### Passo 2: Atualizar configuração do Nginx

O arquivo `nginx.conf` já foi atualizado com a configuração HTTPS completa. 

**Opções:**

#### Opção A: Copiar arquivo atualizado para o servidor

**No Windows:**
```powershell
cd "C:\Users\conta\apps-python\Bot-MHI-IQ\API Funcional\iqoptionapi"
scp nginx.conf root@10104:/tmp/nginx.conf
```

**No servidor:**
```bash
# Fazer backup da configuração atual
sudo cp /etc/nginx/sites-available/iqoptiontraderbot /etc/nginx/sites-available/iqoptiontraderbot.backup

# Copiar nova configuração
sudo cp /tmp/nginx.conf /etc/nginx/sites-available/iqoptiontraderbot

# Verificar sintaxe
sudo nginx -t

# Se OK, recarregar
sudo systemctl reload nginx
```

#### Opção B: Editar diretamente no servidor

```bash
sudo nano /etc/nginx/sites-available/iqoptiontraderbot
```

Adicione esta configuração completa:

```nginx
# Redirecionar HTTP para HTTPS
server {
    listen 80;
    server_name nomadtradersystem.com www.nomadtradersystem.com;
    return 301 https://$server_name$request_uri;
}

# Configuração HTTPS
server {
    listen 443 ssl http2;
    server_name nomadtradersystem.com www.nomadtradersystem.com;
    
    # Certificados SSL
    ssl_certificate /etc/letsencrypt/live/nomadtradersystem.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/nomadtradersystem.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    access_log /var/log/nginx/iqoptiontraderbot_access.log;
    error_log /var/log/nginx/iqoptiontraderbot_error.log;
    
    client_max_body_size 10M;
    
    # Proxy para /bot
    location /bot {
        rewrite ^/bot/?(.*) /$1 break;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header SCRIPT_NAME /bot;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    location = /bot {
        return 301 /bot/;
    }
    
    location /bot/static {
        alias /var/www/iqoptiontraderbot/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    location ~ \.(env|pyc|py|log)$ {
        deny all;
        access_log off;
        log_not_found off;
    }
}
```

### Passo 3: Verificar certificados SSL

```bash
# Verificar se certificados existem
sudo ls -la /etc/letsencrypt/live/nomadtradersystem.com/

# Se não existirem, criar com certbot
sudo certbot --nginx -d nomadtradersystem.com -d www.nomadtradersystem.com
```

### Passo 4: Testar e recarregar

```bash
# Testar configuração
sudo nginx -t

# Se OK, recarregar Nginx
sudo systemctl reload nginx

# Verificar status
sudo systemctl status nginx
```

### Passo 5: Verificar se está funcionando

```bash
# Ver logs
sudo tail -f /var/log/nginx/iqoptiontraderbot_error.log

# Testar localmente
curl -I https://nomadtradersystem.com/bot/
```

## 🔧 Verificações Adicionais

### Verificar se Gunicorn está rodando

```bash
sudo systemctl status iqoptiontraderbot
```

### Verificar se porta 8000 está acessível

```bash
curl http://127.0.0.1:8000/
```

### Verificar logs do Gunicorn

```bash
sudo journalctl -u iqoptiontraderbot -f
```

## 📝 Notas Importantes

1. **Certificados SSL**: Certifique-se de que os certificados SSL estão corretos
2. **Caminho do certificado**: Pode variar, verifique em `/etc/letsencrypt/live/`
3. **Porta 8000**: Gunicorn deve estar rodando na porta 8000 (verifique `gunicorn.conf.py`)

