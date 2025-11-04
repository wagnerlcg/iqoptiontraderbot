"""
Basic Trading Example - IQ Option API
Demonstrates how to connect, check balance, and place simple binary option trades.

WARNING: This is for educational purposes only. Trading involves risk.
"""

import sys
import os

# Adicionar diretório do projeto ao PYTHONPATH para importação
# IMPORTANTE: Adicionar apenas o diretório PAI, não o diretório atual
# para evitar conflito com diretório local 'http/' que interfere no módulo padrão 'http'
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)  # Diretório iqoptionapi
parent_dir = os.path.dirname(project_dir)  # Diretório pai

# Adicionar o diretório pai ao path para que Python encontre 'iqoptionapi' como módulo
# NÃO adicionar project_dir ao path para evitar conflito com http/
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from iqoptionapi import IQ_Option  # pyright: ignore[reportMissingImports]
import time
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]

def main():
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
        return
    
    print("=== IQ Option API - Basic Trading Example ===")
    print(f"Tipo de Conta: {ACCOUNT_TYPE}\n")
    
    if ACCOUNT_TYPE == "REAL":
        print("*** ATENCAO: CONTA REAL SELECIONADA ***")
        print("Voce esta usando dinheiro REAL. Operacoes envolvem risco!\n")
    
    # Initialize API
    print("1. Initializing API...")
    api = IQ_Option(EMAIL, PASSWORD, active_account_type=ACCOUNT_TYPE)
    
    # Connect
    print("2. Connecting to IQ Option...")
    check, reason = api.connect()
    
    if not check:
        print(f"ERRO: Connection failed: {reason}")
        return
    
        print("OK: Connected successfully!")
    
    # Check connection status
    print("\n3. Connection status:")
    print(f"   Connected: {api.check_connect()}")
    
    # Get account info
    print("\n4. Account information:")
    balance = api.get_balance()
    print(f"   Balance: ${balance:.2f}")
    
    account_mode = api.get_balance_mode()
    print(f"   Account Type: {account_mode}")
    
    # Switch to selected account type (if not already)
    if account_mode != ACCOUNT_TYPE:
        print(f"\n5. Switching to {ACCOUNT_TYPE} account...")
        api.change_balance(ACCOUNT_TYPE)
        time.sleep(2)
        print(f"   New Balance: ${api.get_balance():.2f}")
    
    # Get server time
    print("\n6. Server synchronization:")
    server_time = api.get_server_timestamp()
    print(f"   Server Time: {server_time}")
    
    # Example: Get candles
    print("\n7. Fetching market data...")
    try:
        candles = api.get_candles("EURUSD", 60, 10, server_time)
        if candles:
            print(f"   Retrieved {len(candles)} candles for EURUSD")
            print(f"   Latest Close Price: {candles[-1]['close']}")
    except Exception as e:
        print(f"   Error fetching candles: {e}")
    
    # Example: Place a trade (optional - commented out for safety)
    print("\n8. Trade example (DISABLED by default):")
    print("   To place trades, uncomment the code below")
    
    """
    # Place a CALL order on EURUSD for 5 minutes
    print("   Placing EURUSD CALL order...")
    result, order_id = api.buy(10, "EURUSD", "call", 5)
    
    if result:
        print(f"   ✅ Order placed! ID: {order_id}")
        print("   Waiting for expiration...")
        
        # Check result after some time
        time.sleep(320)  # Wait ~5 minutes for expiration
        
        # Check win/loss
        win, profit = api.check_win_v4(order_id)
        if win == "win":
            print(f"   🎉 Trade won! Profit: ${profit:.2f}")
        elif win == "loose":
            print(f"   💸 Trade lost. Loss: ${abs(profit):.2f}")
        else:
            print(f"   ⚖️  Trade equaled. No profit/loss")
    else:
        print(f"   ERRO: Order failed")
    """
    
    # Disconnect
    print("\n9. Disconnecting...")
    api.logout()
    print("OK: Disconnected successfully")
    
    print("\n=== Example completed ===")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAVISO: Interrupted by user")
    except Exception as e:
        print(f"\n\nERRO: {e}")

