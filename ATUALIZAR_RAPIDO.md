# 🚀 Atualização Rápida no Servidor

## ⚡ Método Rápido (Recomendado)

### No Windows (PowerShell):

```powershell
# Execute o script automatizado
.\atualizar_servidor.ps1
```

O script irá guiá-lo através do processo!

### No Servidor (Linux):

```bash
# Copie o script para o servidor primeiro
scp atualizar_servidor.sh usuario@servidor:/var/www/iqoptiontraderbot/

# Depois execute no servidor
ssh usuario@servidor
cd /var/www/iqoptiontraderbot
chmod +x atualizar_servidor.sh
bash atualizar_servidor.sh
```

---

## 📋 Método Manual

### Opção 1: Via Git (se já configurado)

**No Windows:**
```powershell
git add .
git commit -m "Atualização"
git push origin main
```

**No Servidor:**
```bash
cd /var/www/iqoptiontraderbot
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart iqoptiontraderbot
```

### Opção 2: Via Transferência Direta

**No Windows:**
```powershell
# Instalar rsync (se não tiver)
winget install rsync

# Transferir arquivos
rsync -avz --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='.env' ./ usuario@servidor:/var/www/iqoptiontraderbot/
```

**No Servidor:**
```bash
cd /var/www/iqoptiontraderbot
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart iqoptiontraderbot
```

---

## ✅ Verificação

Após atualizar, verifique:

```bash
# Status do serviço
sudo systemctl status iqoptiontraderbot

# Logs em tempo real
sudo journalctl -u iqoptiontraderbot -f
```

---

📖 **Documentação completa**: Veja `ATUALIZAR_SERVIDOR_COMPLETO.md`

