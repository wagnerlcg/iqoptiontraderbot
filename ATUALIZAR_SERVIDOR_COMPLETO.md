# Guia Completo - Atualizar Mudanças no Servidor

Este guia apresenta duas formas de atualizar as mudanças no servidor.

## 📋 Pré-requisitos

1. **Servidor Linux** com acesso SSH
2. **Caminho do projeto no servidor**: `/var/www/iqoptiontraderbot`
3. **Usuário do servidor**: Com permissões sudo

---

## 🚀 Opção 1: Via Git (Recomendado)

### Passo 1: Inicializar Git Localmente (se necessário)

```powershell
# No diretório do projeto (Windows)
cd "C:\Users\conta\apps-python\Bot-MHI-IQ\API Funcional\iqoptionapi"

# Inicializar Git (se ainda não foi feito)
git init

# Adicionar todos os arquivos
git add .

# Fazer commit inicial
git commit -m "Atualização do projeto IQ Option API"
```

### Passo 2: Configurar Repositório Remoto

**Se você já tem um repositório GitHub:**

```powershell
# Adicionar remote
git remote add origin https://github.com/SEU_USUARIO/iqoptiontraderbot.git

# Ou se já existe, atualizar URL
git remote set-url origin https://github.com/SEU_USUARIO/iqoptiontraderbot.git
```

**Se não tem repositório GitHub ainda:**

1. Crie um repositório no GitHub (veja `GITHUB_SETUP.md`)
2. Depois adicione o remote conforme acima

### Passo 3: Fazer Push para GitHub

```powershell
# Renomear branch para main (se necessário)
git branch -M main

# Fazer push para GitHub
git push -u origin main
```

### Passo 4: Atualizar no Servidor

**Conecte-se ao servidor via SSH:**

```bash
ssh usuario@seu-servidor.com
```

**No servidor, execute:**

```bash
# 1. Acessar diretório do projeto
cd /var/www/iqoptiontraderbot

# 2. Verificar status atual
git status

# 3. Atualizar do GitHub
git pull origin main

# 4. Se houver conflitos locais, descartar alterações locais:
git reset --hard origin/main
git pull origin main

# 5. Atualizar dependências (se necessário)
source venv/bin/activate
pip install -r requirements.txt

# 6. Reiniciar serviço
sudo systemctl restart iqoptiontraderbot

# 7. Verificar status
sudo systemctl status iqoptiontraderbot
```

---

## 🔄 Opção 2: Via Transferência Direta (SCP/rsync)

### Usando SCP (Windows PowerShell)

```powershell
# No Windows PowerShell
# 1. Navegar até o diretório do projeto
cd "C:\Users\conta\apps-python\Bot-MHI-IQ\API Funcional\iqoptionapi"

# 2. Transferir arquivos para o servidor (excluindo venv e __pycache__)
scp -r -o "StrictHostKeyChecking=no" `
    --exclude="venv" `
    --exclude="__pycache__" `
    --exclude="*.pyc" `
    --exclude=".env" `
    --exclude="logs/*" `
    * usuario@seu-servidor.com:/var/www/iqoptiontraderbot/

# Ou usando rsync (se disponível no Windows)
# Instalar rsync: winget install rsync
rsync -avz --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='.env' --exclude='logs' ./ usuario@seu-servidor.com:/var/www/iqoptiontraderbot/
```

### Depois da Transferência (no servidor)

```bash
# 1. Conectar ao servidor
ssh usuario@seu-servidor.com

# 2. Acessar diretório
cd /var/www/iqoptiontraderbot

# 3. Ativar ambiente virtual e atualizar dependências
source venv/bin/activate
pip install -r requirements.txt

# 4. Ajustar permissões
sudo chown -R www-data:www-data /var/www/iqoptiontraderbot
sudo chmod +x wsgi.py

# 5. Reiniciar serviço
sudo systemctl restart iqoptiontraderbot

# 6. Verificar logs
sudo journalctl -u iqoptiontraderbot -f
```

---

## 🛠️ Script Automatizado para Windows

Execute o script `atualizar_servidor.ps1` (será criado) para automatizar o processo.

---

## 📝 Checklist de Atualização

Antes de atualizar, verifique:

- [ ] Todos os arquivos locais estão salvos
- [ ] Arquivo `.env` não será sobrescrito (contém credenciais)
- [ ] Backup do servidor foi feito (recomendado)
- [ ] Serviço pode ser reiniciado sem problemas

---

## ⚠️ Importante

1. **Nunca faça commit do arquivo `.env`** - contém credenciais sensíveis
2. **Sempre faça backup antes de atualizar** em produção
3. **Teste em ambiente de desenvolvimento primeiro** (se possível)
4. **Verifique os logs após atualização** para garantir que tudo está funcionando

---

## 🐛 Troubleshooting

### Erro: "permission denied" no servidor
```bash
sudo chown -R www-data:www-data /var/www/iqoptiontraderbot
```

### Erro: "git pull failed"
```bash
# Verificar status
git status

# Descartar alterações locais (CUIDADO!)
git reset --hard origin/main
git pull origin main
```

### Serviço não inicia após atualização
```bash
# Ver logs detalhados
sudo journalctl -u iqoptiontraderbot -n 50

# Verificar se todas as dependências estão instaladas
source venv/bin/activate
pip install -r requirements.txt

# Reiniciar serviço
sudo systemctl restart iqoptiontraderbot
```

---

## 📞 Comandos Úteis

### Verificar status no servidor
```bash
sudo systemctl status iqoptiontraderbot
```

### Ver logs em tempo real
```bash
sudo journalctl -u iqoptiontraderbot -f
```

### Ver último commit
```bash
cd /var/www/iqoptiontraderbot
git log --oneline -1
```

### Ver diferenças locais
```bash
cd /var/www/iqoptiontraderbot
git diff HEAD origin/main
```

