# Guia: Transferir Arquivos sem rsync no Windows

## Problema: rsync não disponível no Windows via winget

O Windows não tem rsync nativo, mas podemos usar alternativas:

## ✅ Solução Recomendada: Script PowerShell

Execute o script que já foi criado:

```powershell
.\transferir_para_servidor.ps1
```

O script oferece duas opções:
1. **SCP direto** - Transfere arquivo por arquivo
2. **ZIP + SCP** - Mais rápido para muitos arquivos

## 📋 Método Manual Alternativo

### Opção 1: Usar SCP diretamente

```powershell
# Navegar até o diretório do projeto
cd "C:\Users\conta\apps-python\Bot-MHI-IQ\API Funcional\iqoptionapi"

# Transferir arquivos principais (um por um ou em lote)
scp app.py root@10104:/var/www/iqoptiontraderbot/
scp wsgi.py root@10104:/var/www/iqoptiontraderbot/
scp requirements.txt root@10104:/var/www/iqoptiontraderbot/
scp gunicorn.conf.py root@10104:/var/www/iqoptiontraderbot/

# Transferir diretórios
scp -r templates root@10104:/var/www/iqoptiontraderbot/
scp -r static root@10104:/var/www/iqoptiontraderbot/
scp -r http root@10104:/var/www/iqoptiontraderbot/
scp -r ws root@10104:/var/www/iqoptiontraderbot/
```

### Opção 2: Criar ZIP e transferir

```powershell
# Criar ZIP manualmente
cd "C:\Users\conta\apps-python\Bot-MHI-IQ\API Funcional\iqoptionapi"

# Usar PowerShell para criar ZIP
Compress-Archive -Path app.py,wsgi.py,requirements.txt,gunicorn.conf.py,templates,static,http,ws -DestinationPath update.zip -Force

# Transferir ZIP
scp update.zip root@10104:/tmp/

# No servidor:
# cd /var/www/iqoptiontraderbot
# unzip -o /tmp/update.zip
# rm /tmp/update.zip
```

### Opção 3: Instalar Git Bash (que inclui rsync)

1. Baixe Git para Windows: https://git-scm.com/download/win
2. Durante instalação, certifique-se de marcar "Git Bash Here"
3. Após instalar, abra Git Bash e execute:

```bash
# Verificar se rsync está disponível
rsync --version

# Se não estiver, instale via pacote MSYS2 ou use o script PowerShell
```

### Opção 4: Usar WinSCP (Interface Gráfica)

1. Baixe WinSCP: https://winscp.net/eng/download.php
2. Instale e configure conexão:
   - Host: 10104
   - Usuário: root
   - Protocolo: SFTP
3. Arraste e solte arquivos diretamente

## 🚀 Recomendação Final

**Use o script PowerShell `transferir_para_servidor.ps1`** - ele já está configurado e funciona sem precisar instalar nada adicional!

```powershell
.\transferir_para_servidor.ps1
```

O script:
- ✅ Não precisa de rsync
- ✅ Usa SCP nativo do Windows
- ✅ Oferece opção ZIP para ser mais rápido
- ✅ Transfere automaticamente o script de atualização
- ✅ Mostra comandos para executar no servidor

