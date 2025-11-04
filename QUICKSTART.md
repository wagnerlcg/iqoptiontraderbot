# 🚀 Guia Rápido de Execução

Passo a passo simplificado para executar a IQ Option API.

## ⚡ Execução Rápida (5 minutos)

### 1️⃣ Configurar Ambiente (Recomendado)

**⚠️ RECOMENDADO: Use Ambiente Virtual (venv)**

Para evitar conflitos e problemas de dependências, é altamente recomendado usar um ambiente virtual:

**Windows (PowerShell):**
```bash
# Execute o script de configuração automática
.\setup_venv.ps1
```

**Windows (CMD):**
```bash
setup_venv.bat
```

**Manual (qualquer sistema):**
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Linux/Mac)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

O script de setup faz tudo automaticamente:
- ✅ Cria ambiente virtual limpo
- ✅ Instala todas as dependências
- ✅ Verifica/cria arquivo .env
- ✅ Testa se tudo está funcionando

**⚠️ IMPORTANTE:** Sempre ative o ambiente virtual antes de executar os scripts:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac  
source venv/bin/activate
```

**Opção Alternativa (sem venv):**
```bash
python setup_env.py --auto
```

### 2️⃣ Configurar Credenciais (Arquivo .env)

**IMPORTANTE**: As credenciais agora são gerenciadas através de um arquivo `.env` para maior segurança.

1. Crie um arquivo chamado `.env` na raiz do projeto
2. Adicione suas credenciais:

```bash
# .env
IQ_OPTION_EMAIL=seu_email@example.com
IQ_OPTION_PASSWORD=sua_senha_aqui
```

⚠️ **IMPORTANTE**: 
- O arquivo `.env` está no `.gitignore` e não será commitado
- NUNCA compartilhe suas credenciais
- Use `.env.example` como referência (se disponível)

### 3️⃣ Criar Arquivo de Teste

Crie um arquivo chamado `meu_teste.py`:

```python
# meu_teste.py
from iqoptionapi import IQ_Option
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Obter credenciais do arquivo .env
EMAIL = os.getenv("IQ_OPTION_EMAIL")
PASSWORD = os.getenv("IQ_OPTION_PASSWORD")

# Inicializar API
api = IQ_Option(EMAIL, PASSWORD)

# Conectar
print("Conectando...")
check, reason = api.connect()

if check:
    print("✅ Conectado com sucesso!")
    
    # Mudar para conta prática (demo)
    api.change_balance("PRACTICE")
    
    # Ver saldo
    balance = api.get_balance()
    print(f"Saldo: ${balance:.2f}")
    
    # Pegar candles
    candles = api.get_candles("EURUSD", 60, 10, api.get_server_timestamp())
    print(f"Peguei {len(candles)} candles!")
    
    # Desconectar
    api.logout()
    print("Desconectado!")
else:
    print(f"❌ Erro: {reason}")
```

### 4️⃣ Executar

```bash
python meu_teste.py
```

**Pronto!** Se funcionou, você está conectado! 🎉

---

## 📚 Exemplos Prontos

O projeto vem com exemplos prontos para executar:

### Exemplo Básico
```bash
cd examples
python basic_trading.py
```

**⚠️ Importante**: Antes de executar, certifique-se de ter configurado o arquivo `.env` com suas credenciais:
1. Crie ou edite o arquivo `.env` na raiz do projeto
2. Adicione suas credenciais:
   ```bash
   IQ_OPTION_EMAIL=seu_email@example.com
   IQ_OPTION_PASSWORD=sua_senha
   ```
3. Salve o arquivo `.env`
4. Execute os exemplos

### Todos os Exemplos Disponíveis

```bash
# Trading básico
python examples/basic_trading.py

# Análise de mercado
python examples/market_analysis.py

# Streaming de dados
python examples/streaming_data.py

# Gestão de portfólio
python examples/portfolio_management.py
```

---

## 🔧 Solução de Problemas Rápidos

### Erro: "ModuleNotFoundError: No module named 'requests'"
**Solução:**
```bash
pip install requests websocket-client
```

### Erro: "Authentication failed"
**Soluções:**
- Verifique se email e senha estão corretos
- Se tiver 2FA habilitado, veja seção abaixo
- Tente fazer login manual no site iqoption.com

### Erro: "Connection timeout"
**Soluções:**
- Verifique sua internet
- Aguarde alguns minutos e tente novamente
- Os servidores do IQ Option podem estar indisponíveis

### Erro de SSL/TLS
**Solução:**
```bash
pip install --upgrade websocket-client requests
```

### Erro: "dependency conflicts" ou conflito com websocket-client
**Problema:** Se você tem o pacote antigo `iqoptionapi` do PyPI instalado, pode haver conflito de versões.

**Solução:**
```bash
# Desinstalar o pacote antigo do PyPI
pip uninstall iqoptionapi

# Reinstalar apenas as dependências necessárias
pip install -r requirements.txt
```

**Nota:** Este projeto usa código-fonte local, não o pacote do PyPI. Por isso, é seguro desinstalar a versão antiga.

---

## 🔐 Conta com Autenticação de 2 Fatores (2FA)

Se sua conta tem 2FA habilitado:

```python
from iqoptionapi import IQ_Option
import os
from dotenv import load_dotenv

load_dotenv()
EMAIL = os.getenv("IQ_OPTION_EMAIL")
PASSWORD = os.getenv("IQ_OPTION_PASSWORD")

api = IQ_Option(EMAIL, PASSWORD)

# Primeira tentativa
check, reason = api.connect()

if reason == "2FA":
    print("2FA detectado! Digite o código do SMS:")
    sms_code = input("Código: ")
    
    # Segunda tentativa com código
    check, reason = api.connect(sms_code)
    
    if check:
        print("✅ Conectado!")
        # Seu código aqui...
```

---

## 📖 Próximos Passos

Após conseguir executar:

1. ✅ Leia o `README.md` completo
2. ✅ Explore os exemplos em `examples/`
3. ✅ Teste no PRACTICE account
4. ✅ Crie suas próprias estratégias
5. ✅ Leia `INDEX.md` para mais recursos

---

## 💡 Dicas Importantes

### ⚠️ SEMPRE use PRACTICE primeiro!
```python
api.change_balance("PRACTICE")  # Demo - SEM DINHEIRO REAL
```

### ⚠️ NUNCA commite suas senhas
- ✅ Use arquivo `.env` (RECOMENDADO)
- ✅ Adicione `.env` ao `.gitignore`
- ❌ Nunca commite credenciais no código
- ❌ Nunca compartilhe seu arquivo `.env`

### ⚠️ Trading envolve risco
- Teste muito antes de usar dinheiro real
- Use apenas o que pode perder
- Este software é educativo

---

## 📞 Ainda com Problemas?

1. Veja `SETUP.md` para instruções detalhadas
2. Consulte `README.md` para documentação completa
3. Verifique `examples/` para exemplos funcionais
4. Abra uma issue no GitHub

---

**Boa sorte com seu trading! 🚀📈**

