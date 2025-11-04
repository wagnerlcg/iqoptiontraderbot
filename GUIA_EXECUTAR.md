# 🚀 Guia de Uso - executar.bat

Guia completo para usar o script `executar.bat` que permite escolher entre conta PRACTICE e REAL.

## 📋 Funcionalidades

- ✅ **Seleção de Conta**: Escolha entre PRACTICE (demo) ou REAL (dinheiro real)
- ✅ **Menu Interativo**: Interface fácil de usar
- ✅ **Múltiplos Scripts**: Execute qualquer script do projeto
- ✅ **Verificações**: Verifica ambiente virtual e arquivo .env automaticamente
- ✅ **Segurança**: Aviso especial ao usar conta REAL

## 🎯 Como Usar

### Execução Básica

1. **Abra o prompt de comando** no diretório do projeto

2. **Execute o script:**
   ```cmd
   executar.bat
   ```

3. **Escolha as opções no menu:**
   - **Opção 1**: PRACTICE (Conta Demo)
   - **Opção 2**: REAL (Conta Real - com confirmação de segurança)
   - **Opções 3-7**: Scripts disponíveis

### Exemplo de Uso

```
============================================================
   IQ Option API - Seletor de Conta e Script
============================================================

Tipo de Conta:
  1. PRACTICE (Conta Demo - Sem dinheiro real)
  2. REAL (Conta Real - DINHEIRO REAL)

Scripts Disponiveis:
  3. TESTE_RAPIDO.py - Teste rapido de conexao
  4. examples/basic_trading.py - Exemplo basico de trading
  5. examples/market_analysis.py - Analise de mercado
  6. examples/streaming_data.py - Streaming de dados em tempo real
  7. examples/portfolio_management.py - Gerenciamento de portfolio

  0. Sair

Escolha uma opcao (1-7, 0 para sair): 1
```

Depois escolha o script (3-7) que deseja executar.

## ⚠️ Importante - Conta REAL

Ao selecionar **Opção 2 (REAL)**, o script exibirá um aviso:

```
============================================================
   ATENCAO: CONTA REAL SELECIONADA
============================================================

Voce esta prestes a usar a conta REAL com DINHEIRO REAL!
Operacoes nesta conta envolvem risco de perda financeira.

Tem certeza que deseja continuar? (SIM para confirmar):
```

**Você deve digitar `SIM` (em maiúsculas) para confirmar.**

## 🔧 Scripts Disponíveis

| Opção | Script | Descrição |
|-------|--------|-----------|
| 3 | `TESTE_RAPIDO.py` | Teste rápido de conexão e funcionalidades básicas |
| 4 | `examples/basic_trading.py` | Exemplo básico de trading |
| 5 | `examples/market_analysis.py` | Análise técnica de mercado |
| 6 | `examples/streaming_data.py` | Streaming de dados em tempo real |
| 7 | `examples/portfolio_management.py` | Gerenciamento de portfólio |

## 🛠️ Funcionalidades Automáticas

O script faz automaticamente:

1. **Verifica ambiente virtual**
   - Se não existir, oferece para criar

2. **Ativa ambiente virtual**
   - Se existir, ativa automaticamente

3. **Verifica arquivo .env**
   - Se não existir, cria a partir do `.env.example`

4. **Define variável de ambiente**
   - Define `IQ_OPTION_ACCOUNT_TYPE` antes de executar
   - Remove após execução

## 📝 Configuração no .env

Você também pode definir o tipo de conta diretamente no arquivo `.env`:

```bash
IQ_OPTION_EMAIL=seu_email@example.com
IQ_OPTION_PASSWORD=sua_senha
IQ_OPTION_ACCOUNT_TYPE=PRACTICE  # ou REAL
```

Se definido no `.env`, esse valor será usado como padrão quando não selecionar via menu.

## 🔄 Fluxo de Execução

```
executar.bat
    ↓
Verifica ambiente virtual
    ↓
Verifica/cria .env
    ↓
Menu de seleção
    ↓
Escolhe tipo de conta (1 ou 2)
    ↓
Escolhe script (3-7)
    ↓
Confirmação (se REAL)
    ↓
Executa script com conta selecionada
    ↓
Mostra resultado
    ↓
Pergunta se deseja executar novamente
```

## 💡 Dicas

1. **Sempre use PRACTICE primeiro** para testar
2. **Confira as credenciais** no `.env` antes de executar
3. **Selecione REAL apenas** quando tiver certeza
4. **O script pode ser executado múltiplas vezes** sem reiniciar

## 🐛 Problemas Comuns

### "Ambiente virtual não encontrado"
- O script oferece criar automaticamente
- Ou execute `setup_venv.bat` primeiro

### "Arquivo .env não encontrado"
- O script cria automaticamente
- Edite com suas credenciais depois

### "Tipo de conta não aplicado"
- Certifique-se de escolher a opção no menu
- Ou defina no arquivo `.env`

## 🎉 Pronto!

Agora você pode executar os scripts de forma segura e fácil, escolhendo sempre o tipo de conta antes de executar!

