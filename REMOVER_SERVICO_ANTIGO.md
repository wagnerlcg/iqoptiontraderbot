# Comandos para Parar e Remover o Serviço Antigo

## 1. Parar o serviço antigo

```bash
sudo systemctl stop bot-iqoption
```

## 2. Desabilitar o serviço antigo (para não iniciar automaticamente)

```bash
sudo systemctl disable bot-iqoption
```

## 3. Verificar status

```bash
sudo systemctl status bot-iqoption
```

## 4. Remover o arquivo de serviço antigo

```bash
sudo rm /etc/systemd/system/bot-iqoption.service
```

## 5. Remover configuração do Nginx antiga (se existir)

```bash
sudo rm /etc/nginx/sites-enabled/bot-iqoption
sudo rm /etc/nginx/sites-available/bot-iqoption
```

## 6. Recarregar systemd

```bash
sudo systemctl daemon-reload
```

## 7. Verificar se o serviço foi removido

```bash
sudo systemctl list-units | grep bot-iqoption
# Não deve retornar nada
```

## 8. Instalar o novo serviço iqoptiontraderbot

Depois de fazer `git pull` para atualizar os arquivos:

```bash
cd /var/www/iqoptiontraderbot

# Copiar arquivo de serviço
sudo cp iqoptiontraderbot.service /etc/systemd/system/

# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar e iniciar
sudo systemctl enable iqoptiontraderbot
sudo systemctl start iqoptiontraderbot

# Verificar status
sudo systemctl status iqoptiontraderbot
```

## Comandos rápidos (copie e cole)

```bash
# Parar e remover serviço antigo
sudo systemctl stop bot-iqoption
sudo systemctl disable bot-iqoption
sudo rm /etc/systemd/system/bot-iqoption.service
sudo rm -f /etc/nginx/sites-enabled/bot-iqoption
sudo rm -f /etc/nginx/sites-available/bot-iqoption
sudo systemctl daemon-reload

# Verificar se foi removido
sudo systemctl list-units | grep bot-iqoption
```

