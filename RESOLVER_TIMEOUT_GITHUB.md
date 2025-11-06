# Resolver Problema de Conexão com GitHub no Servidor

## 🔴 Problema: Timeout ao conectar ao GitHub

```
fatal: unable to access 'https://github.com/wagnerlcg/iqoptiontraderbot.git/': 
Failed to connect to github.com port 443 after 129609 ms: Connection timed out
```

## ✅ Soluções

### Solução 1: Usar SSH ao invés de HTTPS (Recomendado)

```bash
cd /var/www/iqoptiontraderbot

# Verificar URL atual
git remote -v

# Alterar de HTTPS para SSH
git remote set-url origin git@github.com:wagnerlcg/iqoptiontraderbot.git

# Tentar pull novamente
git pull origin main
```

**Se não tiver chave SSH configurada:**
```bash
# Gerar chave SSH (se não tiver)
ssh-keygen -t ed25519 -C "seu-email@exemplo.com"

# Mostrar chave pública
cat ~/.ssh/id_ed25519.pub

# Copiar e adicionar no GitHub: Settings → SSH and GPG keys → New SSH key
```

---

### Solução 2: Usar rsync/SCP do Windows para o Servidor

**No Windows PowerShell:**

```powershell
# Navegar até o diretório do projeto
cd "C:\Users\conta\apps-python\Bot-MHI-IQ\API Funcional\iqoptionapi"

# Transferir arquivos via rsync (ou SCP)
rsync -avz --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='.env' --exclude='logs' ./ root@10104:/var/www/iqoptiontraderbot/
```

**Ou usando SCP:**
```powershell
scp -r -o "StrictHostKeyChecking=no" --exclude="venv" --exclude="__pycache__" --exclude=".env" * root@10104:/var/www/iqoptiontraderbot/
```

**Depois no servidor:**
```bash
cd /var/www/iqoptiontraderbot
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart iqoptiontraderbot
```

---

### Solução 3: Configurar Proxy (se necessário)

Se o servidor precisa de proxy para acessar a internet:

```bash
# Configurar proxy temporário
export https_proxy=http://proxy:porta
export http_proxy=http://proxy:porta

# Tentar pull novamente
git pull origin main

# Ou configurar Git para usar proxy
git config --global http.proxy http://proxy:porta
git config --global https.proxy http://proxy:porta
```

---

### Solução 4: Verificar Conectividade

```bash
# Testar conexão com GitHub
ping github.com

# Testar DNS
nslookup github.com

# Testar HTTPS
curl -I https://github.com

# Verificar porta 443
telnet github.com 443
```

---

### Solução 5: Usar Mirror Local ou Zip

**No Windows:**
```powershell
# Criar arquivo ZIP sem venv e arquivos desnecessários
Compress-Archive -Path * -Exclude venv,__pycache__,.env,logs -DestinationPath update.zip
```

**Transferir para servidor:**
```powershell
scp update.zip root@10104:/tmp/
```

**No servidor:**
```bash
cd /var/www/iqoptiontraderbot
unzip -o /tmp/update.zip
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart iqoptiontraderbot
```

---

## 🚀 Solução Rápida Recomendada

**Opção Mais Rápida: Usar rsync do Windows**

1. **No Windows PowerShell:**
```powershell
# Instalar rsync (se não tiver)
winget install rsync

# Transferir arquivos
cd "C:\Users\conta\apps-python\Bot-MHI-IQ\API Funcional\iqoptionapi"
rsync -avz --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='.env' --exclude='logs' --exclude='.git' ./ root@10104:/var/www/iqoptiontraderbot/
```

2. **No servidor (10104):**
```bash
cd /var/www/iqoptiontraderbot
source venv/bin/activate
pip install -r requirements.txt
sudo chown -R www-data:www-data /var/www/iqoptiontraderbot
sudo systemctl restart iqoptiontraderbot
sudo systemctl status iqoptiontraderbot
```

---

## 📝 Script Automatizado para o Servidor

Crie um arquivo `atualizar_local.sh` no servidor:

```bash
#!/bin/bash
# Atualizar sem usar Git

cd /var/www/iqoptiontraderbot

echo "Ativando ambiente virtual..."
source venv/bin/activate

echo "Atualizando dependências..."
pip install -r requirements.txt

echo "Ajustando permissões..."
sudo chown -R www-data:www-data /var/www/iqoptiontraderbot

echo "Reiniciando serviço..."
sudo systemctl restart iqoptiontraderbot

echo "Status:"
sudo systemctl status iqoptiontraderbot --no-pager | head -n 10
```

Execute após transferir arquivos:
```bash
chmod +x atualizar_local.sh
bash atualizar_local.sh
```

---

## ⚠️ Importante

- **NUNCA sobrescreva o arquivo `.env`** - contém credenciais
- **Faça backup antes de atualizar** se for produção
- **Verifique logs após atualização**: `sudo journalctl -u iqoptiontraderbot -f`

