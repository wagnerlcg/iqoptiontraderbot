# Guia de Deploy - Bot IQ Option API com Nginx e Gunicorn

Este guia explica como fazer o deploy da aplicação Bot IQ Option API em um servidor Linux com Nginx e Gunicorn.

## Pré-requisitos

- Servidor Linux (Ubuntu 20.04+ recomendado)
- Python 3.8 ou superior
- Acesso root ou sudo
- Domínio configurado (opcional, mas recomendado para HTTPS)

## Passo a Passo

### 1. Preparar o Servidor

```bash
# Atualizar sistema
sudo apt-get update
sudo apt-get upgrade -y

# Instalar dependências básicas
sudo apt-get install -y python3 python3-pip python3-venv nginx git
```

### 2. Transferir o Projeto para o Servidor

Você pode usar `scp`, `rsync` ou `git`:

```bash
# Usando scp (do seu computador local)
scp -r /caminho/local/iqoptionapi usuario@servidor:/caminho/destino/

# Ou usando git (se o projeto estiver em um repositório)
git clone seu-repositorio.git /caminho/destino/iqoptionapi
```

### 3. Configurar Variáveis de Ambiente

Edite o arquivo `.env` com suas configurações:

```bash
cd /caminho/destino/iqoptionapi
nano .env
```

Configure pelo menos:
- `IQ_OPTION_EMAIL`: Seu email do IQ Option
- `IQ_OPTION_PASSWORD`: Sua senha do IQ Option
- `FLASK_SECRET_KEY`: Uma chave secreta aleatória (gerada automaticamente pelo deploy.sh)

### 4. Executar o Script de Deploy

```bash
chmod +x deploy.sh
sudo bash deploy.sh
```

O script irá:
- Criar ambiente virtual Python
- Instalar dependências
- Configurar Gunicorn
- Configurar Nginx
- Criar e iniciar serviço systemd

### 5. Configuração Manual (se necessário)

#### Editar caminhos nos arquivos de configuração:

**gunicorn.conf.py:**
- Ajuste `basedir` para o caminho do seu projeto
- Ajuste `bind` se necessário (padrão: 127.0.0.1:8000)

**nginx.conf:**
- Substitua `seu-dominio.com` pelo seu domínio
- Ajuste o caminho em `location /static` para o diretório static do projeto

**iqoptiontraderbot.service:**
- Ajuste `WorkingDirectory` e `PATH` para o caminho do seu projeto
- Ajuste `User` e `Group` conforme necessário

### 6. Configurar SSL/HTTPS (Recomendado)

```bash
# Instalar Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obter certificado SSL
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com

# Renovação automática está configurada pelo certbot
```

Após obter o certificado, descomente o bloco HTTPS no arquivo `nginx.conf`.

### 7. Gerenciar o Serviço

```bash
# Iniciar serviço
sudo systemctl start iqoptiontraderbot

# Parar serviço
sudo systemctl stop iqoptiontraderbot

# Reiniciar serviço
sudo systemctl restart iqoptiontraderbot

# Ver status
sudo systemctl status iqoptiontraderbot

# Ver logs
sudo journalctl -u iqoptiontraderbot -f

# Habilitar início automático
sudo systemctl enable iqoptiontraderbot
```

### 8. Gerenciar Nginx

```bash
# Testar configuração
sudo nginx -t

# Recarregar configuração
sudo systemctl reload nginx

# Reiniciar nginx
sudo systemctl restart nginx

# Ver logs
sudo tail -f /var/log/nginx/iqoptiontraderbot_error.log
```

## Estrutura de Arquivos

```
/caminho/do/projeto/
├── app.py                 # Aplicação Flask principal
├── wsgi.py                # Entry point WSGI para Gunicorn
├── gunicorn.conf.py       # Configuração do Gunicorn
├── nginx.conf             # Configuração do Nginx
├── iqoptiontraderbot.service   # Arquivo de serviço systemd
├── deploy.sh              # Script de deploy
├── requirements.txt       # Dependências Python
├── .env                   # Variáveis de ambiente (NÃO commitado)
├── logs/                  # Diretório de logs
│   ├── gunicorn_access.log
│   └── gunicorn_error.log
├── static/                # Arquivos estáticos
├── templates/             # Templates HTML
└── venv/                  # Ambiente virtual Python
```

## Troubleshooting

### Erro: "Connection refused"
- Verifique se o Gunicorn está rodando: `sudo systemctl status iqoptiontraderbot`
- Verifique se a porta 8000 está aberta: `sudo netstat -tlnp | grep 8000`

### Erro: "502 Bad Gateway"
- Verifique os logs do Nginx: `sudo tail -f /var/log/nginx/iqoptiontraderbot_error.log`
- Verifique os logs do Gunicorn: `sudo journalctl -u iqoptiontraderbot -f`
- Verifique se o Gunicorn está escutando na porta correta

### Erro: "Permission denied"
- Verifique permissões: `sudo chown -R www-data:www-data /caminho/do/projeto`
- Verifique se o usuário tem acesso ao diretório

### Erro: "Module not found"
- Ative o ambiente virtual: `source venv/bin/activate`
- Reinstale dependências: `pip install -r requirements.txt`

### Aplicação não atualiza após mudanças
- Reinicie o serviço: `sudo systemctl restart iqoptiontraderbot`
- O Gunicorn com `preload_app = True` pode precisar de restart completo

## Segurança

1. **Firewall**: Configure o firewall para permitir apenas portas necessárias (80, 443)
2. **SSL**: Sempre use HTTPS em produção
3. **Secret Key**: Use uma chave secreta forte e única
4. **Permissões**: Mantenha arquivos sensíveis (.env) com permissões restritas
5. **Logs**: Monitore logs regularmente para detectar problemas

## Monitoramento

- Logs do Gunicorn: `logs/gunicorn_error.log`
- Logs do Nginx: `/var/log/nginx/iqoptiontraderbot_error.log`
- Logs do Systemd: `sudo journalctl -u iqoptiontraderbot -f`
- Status do serviço: `sudo systemctl status iqoptiontraderbot`

## Atualizações

Para atualizar a aplicação:

```bash
# 1. Parar o serviço
sudo systemctl stop iqoptiontraderbot

# 2. Atualizar código (git pull ou scp)
git pull origin main

# 3. Atualizar dependências
source venv/bin/activate
pip install -r requirements.txt

# 4. Reiniciar serviço
sudo systemctl start iqoptiontraderbot
```

## Suporte

Em caso de problemas:
1. Verifique os logs
2. Verifique o status dos serviços
3. Revise as configurações
4. Consulte a documentação do Flask, Gunicorn e Nginx

