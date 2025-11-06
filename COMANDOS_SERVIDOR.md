# Comandos para Executar Diretamente no Servidor

## 📋 Execute estes comandos no servidor (copie e cole)

```bash
cd /var/www/iqoptiontraderbot

# 1. Ativar ambiente virtual
source venv/bin/activate

# 2. Atualizar dependências
pip install --upgrade pip
pip install -r requirements.txt

# 3. Ajustar permissões
sudo chown -R www-data:www-data /var/www/iqoptiontraderbot
sudo chmod +x wsgi.py

# 4. Reiniciar serviço
sudo systemctl restart iqoptiontraderbot

# 5. Verificar status
sudo systemctl status iqoptiontraderbot

# 6. Ver logs (opcional)
sudo journalctl -u iqoptiontraderbot -f
```

## 🚀 Ou criar o script inline no servidor

Execute no servidor:

```bash
cd /var/www/iqoptiontraderbot

# Criar script inline
cat > atualizar.sh << 'EOF'
#!/bin/bash
set -e
cd /var/www/iqoptiontraderbot
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
sudo chown -R www-data:www-data /var/www/iqoptiontraderbot
sudo chmod +x wsgi.py
sudo systemctl restart iqoptiontraderbot
sleep 2
sudo systemctl status iqoptiontraderbot --no-pager | head -n 15
echo ""
echo "✅ Atualização concluída!"
echo "Ver logs: sudo journalctl -u iqoptiontraderbot -f"
EOF

chmod +x atualizar.sh
bash atualizar.sh
```

## 📤 Ou transferir o script do Windows

No Windows PowerShell:

```powershell
cd "C:\Users\conta\apps-python\Bot-MHI-IQ\API Funcional\iqoptionapi"
scp atualizar_sem_git.sh root@10104:/var/www/iqoptiontraderbot/
```

Depois no servidor:

```bash
cd /var/www/iqoptiontraderbot
chmod +x atualizar_sem_git.sh
bash atualizar_sem_git.sh
```

