# Instruções para Publicar no GitHub

O projeto já está configurado com Git localmente. Siga estes passos para publicar no GitHub:

## Passo 1: Criar Repositório no GitHub

1. Acesse https://github.com e faça login com sua conta (wagnerlcg@gmail.com)
2. Clique no botão **"+"** no canto superior direito e selecione **"New repository"**
3. Configure o repositório:
   - **Repository name**: `iqoptiontraderbot` (ou outro nome de sua escolha)
   - **Description**: "Sistema completo de trading automatizado para IQ Option com interface web"
   - **Visibility**: Escolha **Public** ou **Private**
   - **NÃO marque** "Initialize this repository with a README" (já temos um)
   - **NÃO marque** "Add .gitignore" (já temos um)
   - **NÃO marque** "Choose a license" (já temos um)
4. Clique em **"Create repository"**

## Passo 2: Conectar ao Repositório GitHub

Após criar o repositório, GitHub mostrará instruções. Execute estes comandos no PowerShell:

```powershell
# Adicionar o repositório remoto (substitua SEU_USUARIO pelo seu usuário do GitHub)
git remote add origin https://github.com/SEU_USUARIO/iqoptiontraderbot.git

# Verificar que foi adicionado corretamente
git remote -v

# Renomear branch principal para main (se necessário)
git branch -M main

# Fazer push do código
git push -u origin main
```

## Passo 3: Autenticação

Se for solicitado login:
- **Username**: Seu usuário do GitHub
- **Password**: Use um **Personal Access Token** (não a senha da conta)

### Como criar Personal Access Token:

1. Vá em GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Clique em **"Generate new token"**
3. Dê um nome ao token (ex: "iqoptiontraderbot")
4. Selecione escopos: **repo** (acesso completo aos repositórios)
5. Clique em **"Generate token"**
6. **COPIE O TOKEN** (você não verá novamente)
7. Use este token como senha quando solicitado

## Alternativa: Usando GitHub CLI

Se você tiver o GitHub CLI instalado:

```powershell
# Instalar GitHub CLI (se não tiver)
winget install GitHub.cli

# Login
gh auth login

# Criar repositório e fazer push
gh repo create iqoptiontraderbot --public --source=. --remote=origin --push
```

## Verificar Publicação

Após o push, acesse:
```
https://github.com/SEU_USUARIO/iqoptiontraderbot
```

Você deve ver todos os arquivos do projeto lá!

## Próximos Passos

1. ✅ Adicione uma descrição no repositório
2. ✅ Configure topics/tags (ex: `python`, `flask`, `trading`, `iqoption`, `bot`)
3. ✅ Configure o README como página inicial (já está configurado)
4. ✅ Considere adicionar badges de status (opcional)

## Comandos Úteis

```powershell
# Ver status
git status

# Adicionar mudanças
git add .

# Fazer commit
git commit -m "Sua mensagem de commit"

# Fazer push
git push

# Ver histórico
git log --oneline

# Ver branches
git branch -a
```

## Problemas Comuns

### Erro: "remote origin already exists"
```powershell
# Remover origin existente
git remote remove origin

# Adicionar novamente
git remote add origin https://github.com/SEU_USUARIO/iqoptiontraderbot.git
```

### Erro: "authentication failed"
- Verifique se está usando Personal Access Token e não a senha
- Crie um novo token se necessário

### Erro: "branch main does not exist"
```powershell
# Criar branch main
git branch -M main

# Fazer push novamente
git push -u origin main
```

---

**Pronto!** Seu projeto está pronto para ser publicado no GitHub! 🚀

