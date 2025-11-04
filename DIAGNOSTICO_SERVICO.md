# Diagnosticar Problema do Serviço iqoptiontraderbot

## 1. Ver logs detalhados do erro

```bash
sudo journalctl -u iqoptiontraderbot -n 50 --no-pager
```

## 2. Ver logs em tempo real

```bash
sudo journalctl -u iqoptiontraderbot -f
```

## 3. Verificar se o ambiente virtual existe

```bash
ls -la /var/www/iqoptiontraderbot/venv/bin/gunicorn
```

## 4. Verificar se o arquivo wsgi.py existe

```bash
ls -la /var/www/iqoptiontraderbot/wsgi.py
```

## 5. Verificar se o arquivo gunicorn.conf.py existe

```bash
ls -la /var/www/iqoptiontraderbot/gunicorn.conf.py
```

## 6. Testar manualmente (como usuário www-data)

```bash
sudo -u www-data /var/www/iqoptiontraderbot/venv/bin/gunicorn --config /var/www/iqoptiontraderbot/gunicorn.conf.py wsgi:app
```

## 7. Verificar permissões

```bash
# Verificar propriedade dos arquivos
ls -la /var/www/iqoptiontraderbot/

# Corrigir permissões se necessário
sudo chown -R www-data:www-data /var/www/iqoptiontraderbot
sudo chmod +x /var/www/iqoptiontraderbot/venv/bin/gunicorn
```

## 8. Verificar se o diretório de logs existe

```bash
mkdir -p /var/www/iqoptiontraderbot/logs
chown www-data:www-data /var/www/iqoptiontraderbot/logs
```

## Problemas Comuns e Soluções

### Erro: "No module named 'app'"
- Verificar se está no diretório correto
- Verificar se o arquivo app.py existe

### Erro: "Permission denied"
- Corrigir permissões: `sudo chown -R www-data:www-data /var/www/iqoptiontraderbot`

### Erro: "No such file or directory"
- Verificar se todos os caminhos no arquivo .service estão corretos
- Verificar se o ambiente virtual está criado

### Erro: "ImportError"
- Ativar venv e reinstalar dependências:
```bash
cd /var/www/iqoptiontraderbot
source venv/bin/activate
pip install -r requirements.txt
```

