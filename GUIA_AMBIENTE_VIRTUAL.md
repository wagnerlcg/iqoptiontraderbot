# 🔧 Guia de Ambiente Virtual - IQ Option API

Guia completo para configurar e usar um ambiente virtual limpo.

## 🎯 Por que usar Ambiente Virtual?

- ✅ **Isolamento**: Não interfere com outras instalações Python
- ✅ **Limpeza**: Ambiente novo sem conflitos de dependências
- ✅ **Segurança**: Evita problemas como `http.client` não encontrado
- ✅ **Reproduzibilidade**: Mesmo ambiente em diferentes máquinas

## 🚀 Configuração Rápida

### Opção 1: Script Automático (Recomendado)

**Windows PowerShell:**
```powershell
.\setup_venv.ps1
```

**Windows CMD:**
```cmd
setup_venv.bat
```

O script faz tudo automaticamente:
1. Cria ambiente virtual
2. Ativa o ambiente
3. Atualiza pip
4. Instala dependências
5. Configura .env
6. Testa instalação

### Opção 2: Manual

```bash
# 1. Criar ambiente virtual
python -m venv venv

# 2. Ativar ambiente virtual

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Windows (CMD):
venv\Scripts\activate.bat

# Linux/Mac:
source venv/bin/activate

# 3. Atualizar pip
python -m pip install --upgrade pip

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Configurar .env (se não existe)
cp .env.example .env
# Edite .env com suas credenciais
```

## 📝 Usando o Ambiente Virtual

### Ativar o Ambiente

**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows CMD:**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

Você deve ver `(venv)` no início do prompt quando estiver ativo.

### Executar Scripts

Depois de ativar o ambiente virtual:

```bash
# Teste rápido
python TESTE_RAPIDO.py

# Exemplos
python examples/basic_trading.py
python examples/market_analysis.py
```

### Desativar o Ambiente

Quando terminar de usar:

```bash
deactivate
```

## 🔍 Verificando Instalação

Teste se tudo está funcionando:

```bash
# No ambiente virtual ativado:
python -c "from iqoptionapi import IQ_Option; print('✅ Funcionando!')"
```

## 🐛 Problemas Comuns

### Erro: "cannot be loaded because running scripts is disabled"

**Solução PowerShell:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Erro: "ModuleNotFoundError"

**Solução:**
1. Certifique-se de que o ambiente virtual está ativado
2. Reinstale as dependências: `pip install -r requirements.txt`

### Erro: "http.client not found"

**Solução:** 
Use ambiente virtual limpo. Este erro geralmente ocorre em instalações Python corrompidas.

### Limpar e Recriar Ambiente

```bash
# Desativar ambiente atual
deactivate

# Remover ambiente antigo
rmdir /s /q venv    # Windows
rm -rf venv         # Linux/Mac

# Recriar
python -m venv venv
# ... seguir passos de ativação e instalação
```

## 📋 Checklist

- [ ] Ambiente virtual criado
- [ ] Ambiente virtual ativado (vejo `(venv)` no prompt)
- [ ] Dependências instaladas (`pip list` mostra os pacotes)
- [ ] Arquivo `.env` configurado com credenciais
- [ ] Teste de importação passou
- [ ] Scripts executam sem erros

## 💡 Dicas

1. **Sempre ative o ambiente virtual** antes de trabalhar no projeto
2. **Commit apenas código**, não o ambiente virtual (já está no `.gitignore`)
3. **Recrie o ambiente** se tiver problemas estranhos de dependências
4. **Use versão fixa do Python** se possível (ex: Python 3.11)

## 🎉 Pronto!

Agora você tem um ambiente virtual limpo e configurado. Comece a usar!

```bash
# Ativar ambiente
.\venv\Scripts\Activate.ps1

# Executar exemplo
python examples/basic_trading.py
```

