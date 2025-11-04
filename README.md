# Bot IQ Option API - Sistema de Trading Automatizado

Sistema completo de trading automatizado para IQ Option com interface web moderna, execução automática de sinais, proteção de stop loss e estratégia Martingale configurável.

## 🚀 Funcionalidades

- **Interface Web Moderna**: Dashboard intuitivo e responsivo
- **Execução Automática de Sinais**: Processa sinais de trading automaticamente
- **Proteção Stop Loss/Win**: Controle automático de risco
- **Estratégia Martingale**: Configurável com níveis Gale 0, 1 ou 2
- **Proteção Contra Perdas Consecutivas**: Pula sinais após 2 LOSS consecutivos
- **Histórico de Operações**: Registro completo de trades executados
- **Logs em Tempo Real**: Acompanhamento detalhado da execução

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Conta IQ Option (PRACTICE ou REAL)
- Navegador web moderno

## 🛠️ Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/bot-iqoption-api.git
cd bot-iqoption-api
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e configure:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais:

```
IQ_OPTION_EMAIL=seu-email@exemplo.com
IQ_OPTION_PASSWORD=sua-senha
IQ_OPTION_ACCOUNT_TYPE=PRACTICE
```

## 🎯 Uso Rápido

### Executar Interface Web Local

```bash
python app.py
```

Acesse `http://localhost:5000` no navegador.

### Executar Sinais Automaticamente

1. Faça login na interface web
2. Configure seus parâmetros na página de Configurações
3. Adicione sinais no formato: `M1;ATIVO;HH:MM;DIREÇÃO`
4. Inicie a execução automática

## 📁 Estrutura do Projeto

```
bot-iqoption-api/
├── app.py                 # Aplicação Flask principal
├── wsgi.py                # Entry point WSGI (produção)
├── sinais_processor.py    # Processador de sinais
├── stop_loss_protection.py # Proteção de stop loss
├── templates/             # Templates HTML
├── static/                # Arquivos estáticos (CSS, JS)
├── requirements.txt       # Dependências Python
├── sinais.txt            # Arquivo de sinais (formato: M1;ATIVO;HH:MM;DIREÇÃO)
└── README.md             # Este arquivo
```

## 🔧 Configurações

### Tipos de Entrada

- **PERCENT**: Entrada em porcentagem do saldo
- **FIXED**: Valor fixo em dólares

### Estratégia Martingale (Gale)

- **Sem Gale (0)**: Não reinveste após LOSS
- **Gale 1**: Reinveste 1 vez (multiplicador 2.15x)
- **Gale 2**: Reinveste 2 vezes (multiplicador 2.15x cada)

### Proteção Contra Perdas Consecutivas

Após 2 LOSS consecutivos (considerando o nível de Gale configurado), o sistema automaticamente pula os próximos 2 sinais.

## 📊 Formato de Sinais

Os sinais devem estar no arquivo `sinais.txt` no formato:

```
TIMEFRAME;ATIVO;HORA;DIREÇÃO
```

Exemplos:
```
M1;EURUSD-OTC;09:30;PUT
M5;GBPUSD;14:45;CALL
M1;BTCUSD;16:00;PUT
```

- **TIMEFRAME**: M1, M5, M15, etc.
- **ATIVO**: Par de moedas ou criptomoeda (ex: EURUSD-OTC, BTCUSD)
- **HORA**: Formato HH:MM (24 horas)
- **DIREÇÃO**: CALL ou PUT

## 🚀 Deploy em Produção

Para deploy em servidor com Nginx e Gunicorn, consulte o arquivo [README_DEPLOY.md](README_DEPLOY.md).

Resumo rápido:
```bash
# Execute o script de deploy
sudo bash deploy.sh

# Configure SSL (opcional mas recomendado)
sudo certbot --nginx -d seu-dominio.com
```

## 📝 Documentação Adicional

- [README_DEPLOY.md](README_DEPLOY.md) - Guia completo de deploy
- [WEB_INTERFACE.md](WEB_INTERFACE.md) - Documentação da interface web
- [GUIA_EXECUTAR.md](GUIA_EXECUTAR.md) - Guia de execução

## ⚠️ Avisos Importantes

1. **Use Conta DEMO**: Teste sempre em conta PRACTICE antes de usar REAL
2. **Gerencie Riscos**: Configure stop loss adequadamente
3. **Monitore Logs**: Acompanhe a execução regularmente
4. **Não Compartilhe Credenciais**: Mantenha o arquivo `.env` seguro

## 🐛 Troubleshooting

### Erro de Conexão
- Verifique suas credenciais no arquivo `.env`
- Confirme que a conta IQ Option está ativa

### Sinais Não Executam
- Verifique o formato do arquivo `sinais.txt`
- Confirme que a execução está ativa na interface web
- Verifique os logs na aba "Histórico Recente"

### Erro de Saldo Insuficiente
- Configure valores de entrada menores
- Verifique seu saldo na conta IQ Option

## 📄 Licença

Este projeto é fornecido "como está", sem garantias. Use por sua conta e risco.

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## 📧 Contato

Para suporte ou dúvidas, abra uma issue no GitHub.

---

**Desenvolvido com ❤️ para a comunidade de trading**
