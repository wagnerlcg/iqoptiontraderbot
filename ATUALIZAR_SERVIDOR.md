# Comandos para Atualizar o Projeto no Servidor

## Atualizar arquivos do GitHub

```bash
# 1. Acessar o diretório do projeto
cd /var/www/iqoptiontraderbot

# 2. Atualizar do GitHub (baixar alterações)
git pull origin main
```

Isso vai baixar todas as alterações do GitHub, incluindo o `deploy.sh` atualizado.

## Se houver conflitos

Se você tiver alterações locais no servidor que entrem em conflito:

```bash
# Verificar status
git status

# Opção 1: Descartar alterações locais e usar as do GitHub
git reset --hard origin/main
git pull origin main

# Opção 2: Salvar alterações locais primeiro
git stash
git pull origin main
git stash pop  # Reaplica suas alterações locais
```

## Verificar se atualizou

```bash
# Ver último commit
git log --oneline -1

# Ver alterações no deploy.sh
git diff HEAD~1 deploy.sh
```

## Atualizar apenas o deploy.sh (se necessário)

Se quiser atualizar apenas esse arquivo específico:

```bash
git checkout origin/main -- deploy.sh
```

---

**Resumo rápido:**
```bash
cd /var/www/iqoptiontraderbot && git pull origin main
```

