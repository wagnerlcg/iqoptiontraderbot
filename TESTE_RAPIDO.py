"""
Teste Rápido - IQ Option API
Execute este arquivo para testar sua conexão rapidamente.

INSTRUÇÕES:
1. Copie o arquivo .env.example para .env
2. Preencha suas credenciais no arquivo .env
3. Execute: python TESTE_RAPIDO.py
"""

import sys
import os

# Adicionar diretório do projeto ao PYTHONPATH para importação
# IMPORTANTE: Adicionar apenas o diretório PAI, não o diretório atual
# para evitar conflito com diretório local 'http/' que interfere no módulo padrão 'http'
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = script_dir  # Estamos no diretório iqoptionapi
parent_dir = os.path.dirname(project_dir)  # Diretório pai

# Adicionar o diretório pai ao path para que Python encontre 'iqoptionapi' como módulo
# NÃO adicionar project_dir ao path para evitar conflito com http/
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from iqoptionapi import IQ_Option
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Obter credenciais do arquivo .env
EMAIL = os.getenv("IQ_OPTION_EMAIL")
PASSWORD = os.getenv("IQ_OPTION_PASSWORD")
# Obter tipo de conta (PRACTICE ou REAL) - padrão: PRACTICE
ACCOUNT_TYPE = os.getenv("IQ_OPTION_ACCOUNT_TYPE", "PRACTICE")

# Verificar se as credenciais foram carregadas
if not EMAIL or not PASSWORD:
    print("ERRO: Credenciais nao encontradas!")
    print("\nPor favor:")
    print("1. Copie o arquivo .env.example para .env")
    print("2. Preencha IQ_OPTION_EMAIL e IQ_OPTION_PASSWORD no arquivo .env")
    exit(1)

print("=" * 50)
print("IQ Option API - Teste de Conexao")
print(f"Tipo de Conta: {ACCOUNT_TYPE}")
print("=" * 50)

if ACCOUNT_TYPE == "REAL":
    print("\n*** ATENCAO: CONTA REAL SELECIONADA ***")
    print("Voce esta usando dinheiro REAL. Operacoes envolvem risco!")
    print()

# Inicializar
print("\n[1/5] Inicializando API...")
api = IQ_Option(EMAIL, PASSWORD, active_account_type=ACCOUNT_TYPE)

# Conectar
print("[2/5] Conectando ao IQ Option...")
check, reason = api.connect()

if not check:
    print(f"\n❌ FALHA: {reason}")
    print("\nPossíveis causas:")
    print("- Email ou senha incorretos")
    print("- Problema de conexão com internet")
    print("- Servidores IQ Option indisponíveis")
    exit()

print("[3/5] ✅ Conectado com sucesso!")

# Mudar para conta selecionada
print(f"[4/5] Configurando conta {ACCOUNT_TYPE}...")
api.change_balance(ACCOUNT_TYPE)

# Pegar saldo
balance = api.get_balance()
print(f"\n💵 Saldo na conta: ${balance:.2f}")

# Pegar server time
server_time = api.get_server_timestamp()
print(f"🕐 Tempo do servidor: {server_time}")

# Testar pegar candles
print("\n[5/5] Testando busca de dados do mercado...")
try:
    candles = api.get_candles("EURUSD", 60, 5, server_time)
    print(f"✅ Dados recebidos: {len(candles)} candles do EURUSD")
    
    # Mostrar última vela
    if candles:
        ultima = candles[-1]
        print(f"\n📊 Última vela:")
        print(f"   Abertura:  ${ultima['open']:.5f}")
        print(f"   Fechamento: ${ultima['close']:.5f}")
        print(f"   Máxima:    ${ultima['max']:.5f}")
        print(f"   Mínima:    ${ultima['min']:.5f}")
except Exception as e:
    print(f"⚠️  Erro ao buscar candles: {e}")

# Desconectar
print("\n🔌 Desconectando...")
api.logout()

print("\n" + "=" * 50)
print("✅ TESTE COMPLETO! Tudo funcionando perfeitamente!")
print("=" * 50)
print("\n📚 Próximos passos:")
print("   1. Execute: python examples/basic_trading.py")
print("   2. Leia: QUICKSTART.md")
print("   3. Explore: examples/")
print("\n🚀 Boa sorte com seu trading!\n")

