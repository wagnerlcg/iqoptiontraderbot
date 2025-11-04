"""
Portfolio Management Example - IQ Option API
Demonstrates position management, order history, and portfolio monitoring.

WARNING: This is for educational purposes only.
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

from iqoptionapi import IQ_Option
import time
from dotenv import load_dotenv

def main():
    # Carregar variáveis de ambiente do arquivo .env
    load_dotenv()
    
    # Obter credenciais do arquivo .env
    EMAIL = os.getenv("IQ_OPTION_EMAIL")
    PASSWORD = os.getenv("IQ_OPTION_PASSWORD")
    
    # Verificar se as credenciais foram carregadas
    if not EMAIL or not PASSWORD:
        print("❌ ERRO: Credenciais não encontradas!")
        print("\nPor favor:")
        print("1. Copie o arquivo .env.example para .env")
        print("2. Preencha IQ_OPTION_EMAIL e IQ_OPTION_PASSWORD no arquivo .env")
        return
    
    print("=== IQ Option API - Portfolio Management Example ===\n")
    
    # Initialize and connect
    api = IQ_Option(EMAIL, PASSWORD)
    check, reason = api.connect()
    
    if not check:
        print(f"❌ Connection failed: {reason}")
        return
    
    print("✅ Connected successfully!\n")
    
    # Ensure PRACTICE account
    if api.get_balance_mode() != "PRACTICE":
        api.change_balance("PRACTICE")
        time.sleep(1)
    
    # 1. Account Overview
    print("1. Account Overview")
    print("-" * 50)
    
    balance = api.get_balance()
    currency = api.get_currency()
    account_mode = api.get_balance_mode()
    
    print(f"   Account Type: {account_mode}")
    print(f"   Balance: {balance:.2f} {currency}")
    print(f"   Balance ID: {api.get_balance_id()}")
    
    # 2. Recent Trading History
    print("\n2. Recent Trading History")
    print("-" * 50)
    
    try:
        # Get recent closed positions
        options = api.get_optioninfo_v2(10)  # Last 10 positions
        
        if options and options.get('msg', {}).get('closed_options'):
            closed_options = options['msg']['closed_options']
            print(f"   Found {len(closed_options)} recent closed positions")
            
            # Show last 5
            for i, opt in enumerate(closed_options[:5], 1):
                opt_info = opt['id']
                win = opt.get('win', 'unknown')
                profit = opt.get('win_amount', 0) - opt.get('amount', 0)
                amount = opt.get('amount', 0)
                
                result_emoji = "🎉" if win == "win" else "💸" if win == "loose" else "⚖️"
                
                print(f"   {i}. {result_emoji} Result: {win.upper()}, "
                      f"Amount: ${amount:.2f}, P&L: ${profit:.2f}")
        else:
            print("   No closed positions found")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 3. Get Open Positions (Digital Options)
    print("\n3. Open Positions Check")
    print("-" * 50)
    
    try:
        # Get digital positions
        check, positions_data = api.get_positions("digital-option")
        
        if check and positions_data and positions_data.get('positions'):
            positions = positions_data['positions']
            print(f"   Found {len(positions)} open digital option positions")
            
            for i, pos in enumerate(positions[:5], 1):
                asset = pos.get('instrument_underlying', 'N/A')
                amount = pos.get('invest', 0)
                profit = pos.get('profit', 0)
                status = pos.get('status', 'unknown')
                
                print(f"   {i}. Asset: {asset}, Amount: ${amount:.2f}, "
                      f"P&L: ${profit:.2f}, Status: {status}")
        else:
            print("   No open digital positions")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 4. Commission Information
    print("\n4. Commission Information")
    print("-" * 50)
    
    try:
        # Subscribe to commission changes
        api.subscribe_commission_changed("turbo-option")
        time.sleep(2)
        
        commission = api.get_commission_change("turbo-option")
        if commission:
            print(f"   Commission data available")
            print(f"   Details: {commission}")
        else:
            print("   No commission data")
        
        api.unsubscribe_commission_changed("turbo-option")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 5. Account Statistics (if available)
    print("\n5. Account Statistics")
    print("-" * 50)
    
    try:
        # Get profile data
        profile = api.get_profile_ansyc()
        if profile:
            user_id = profile.get('user_id', 'N/A')
            username = profile.get('username', 'N/A')
            country = profile.get('country', 'N/A')
            
            print(f"   User ID: {user_id}")
            print(f"   Username: {username}")
            print(f"   Country: {country}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 6. Instrument Information
    print("\n6. Available Instruments")
    print("-" * 50)
    
    try:
        # Get list of available assets
        actives = api.get_all_ACTIVES_OPCODE()
        print(f"   Total available instruments: {len(actives)}")
        print(f"   Sample instruments:")
        
        for i, (name, active_id) in enumerate(list(actives.items())[:10], 1):
            print(f"   {i}. {name} (ID: {active_id})")
        
        print(f"   ... and {len(actives) - 10} more")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Disconnect
    print("\n7. Disconnecting...")
    api.logout()
    print("✅ Done!")
    
    print("\n=== Portfolio review completed ===")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")

