# Interface Web - IQ Option Trading Bot

Interface web moderna e responsiva para gerenciar o bot de trading IQ Option.

## 🚀 Como Executar

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com suas credenciais:

```env
IQ_OPTION_EMAIL=seu_email@example.com
IQ_OPTION_PASSWORD=sua_senha
IQ_OPTION_ACCOUNT_TYPE=PRACTICE
IQ_OPTION_STOP_LOSS=5
IQ_OPTION_STOP_WIN=100
IQ_OPTION_ENTRY_TYPE=PERCENT
IQ_OPTION_ENTRY_VALUE=1
FLASK_SECRET_KEY=sua_chave_secreta_aqui
```

### 3. Executar a Aplicação

```bash
python app.py
```

A interface estará disponível em: `http://localhost:5000`

## 📋 Funcionalidades

### Dashboard
- Visualização do saldo atual e inicial
- Variação de ganhos/perdas
- Status da conexão
- Acesso rápido às principais funcionalidades

### Configurações
- Configurar Stop Loss (prioridade máxima)
- Configurar Stop Win
- Definir tipo de entrada (percentual ou fixo)
- Configurar valor de entrada

### Stop Loss
- Monitoramento em tempo real do Stop Loss
- Visualização de saldo mínimo permitido
- Status de proteção ativo/acionado
- Bloqueio automático de operações quando acionado

### Sinais
- Gerenciar sinais de trading
- Visualizar lista de sinais
- Adicionar novos sinais
- Editar arquivo de sinais diretamente
- Validação automática de formato

### Trading
- Executar operações de trading
- Selecionar ativo, direção e valor
- Escolher tempo de expiração
- Histórico de operações recentes

## 🎨 Design

- Interface moderna e limpa
- Design responsivo (funciona em desktop, tablet e mobile)
- Cores e ícones intuitivos
- Feedback visual imediato
- Animações suaves

## 🔒 Segurança

- Sessões com Flask
- Validação de autenticação em todas as rotas
- Proteção de Stop Loss integrada
- Validação de dados de entrada

## 📱 Responsividade

A interface é totalmente responsiva e funciona bem em:
- Desktop (1920px+)
- Laptop (1366px - 1920px)
- Tablet (768px - 1366px)
- Mobile (320px - 768px)

## ⚠️ Notas Importantes

1. **Stop Loss**: O Stop Loss tem PRIORIDADE MÁXIMA e será aplicado automaticamente em todas as operações.

2. **Conta Real**: Use com extrema cautela ao selecionar conta REAL. Operações envolvem dinheiro real.

3. **Sessões**: Cada login cria uma nova sessão. Faça logout ao terminar.

4. **Atualização em Tempo Real**: O dashboard atualiza automaticamente a cada 5 segundos.

## 🛠️ Desenvolvimento

### Estrutura de Arquivos

```
.
├── app.py                 # Aplicação Flask principal
├── templates/             # Templates HTML
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── config.html
│   ├── stop_loss.html
│   ├── sinais.html
│   ├── trading.html
│   └── error.html
├── static/
│   ├── css/
│   │   └── style.css      # Estilos principais
│   └── js/
│       └── main.js        # JavaScript principal
└── requirements.txt       # Dependências
```

### Personalização

Você pode personalizar:
- Cores: Edite as variáveis CSS em `static/css/style.css`
- Layout: Modifique os templates em `templates/`
- Funcionalidades: Adicione novas rotas em `app.py`

## 📞 Suporte

Em caso de problemas:
1. Verifique se todas as dependências estão instaladas
2. Verifique se o arquivo `.env` está configurado corretamente
3. Verifique os logs do Flask no terminal

