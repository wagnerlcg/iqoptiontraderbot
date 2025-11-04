"""
Real-time Data Streaming Example - IQ Option API
Demonstrates live candle streaming, price updates, and real-time monitoring.

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
from datetime import datetime
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
    
    print("=== IQ Option API - Real-time Streaming Example ===\n")
    
    # Initialize and connect
    api = IQ_Option(EMAIL, PASSWORD)
    check, reason = api.connect()
    
    if not check:
        print(f"❌ Connection failed: {reason}")
        return
    
    print("✅ Connected successfully!\n")
    
    # Asset to monitor
    asset = "EURUSD"
    interval = 60  # 1-minute candles
    
    print(f"Monitoring {asset} with {interval}-second candles")
    print("Streaming data (press Ctrl+C to stop)...\n")
    
    try:
        # Subscribe to real-time candles
        api.start_candles_stream(asset, interval, 20)  # Keep last 20 candles
        time.sleep(3)  # Wait for initial data
        
        # Stream data
        for i in range(30):  # Run for ~30 iterations
            # Check connection
            if not api.check_connect():
                print("⚠️  Connection lost, attempting reconnect...")
                api.connect()
                time.sleep(2)
                continue
            
            # Get real-time candles
            candles = api.get_realtime_candles(asset, interval)
            
            if candles:
                # Sort by timestamp
                sorted_candles = sorted(candles.items(), reverse=True)
                
                # Get latest candle
                latest_timestamp, latest_candle = sorted_candles[0]
                
                # Format timestamp
                dt = datetime.fromtimestamp(latest_timestamp)
                time_str = dt.strftime("%H:%M:%S")
                
                # Display info
                print(f"[{time_str}] {asset}: "
                      f"Open={latest_candle.get('open', 0):.5f}, "
                      f"Close={latest_candle.get('close', 0):.5f}, "
                      f"High={latest_candle.get('max', 0):.5f}, "
                      f"Low={latest_candle.get('min', 0):.5f}")
                
                # Show candle count
                print(f"         Stored candles: {len(candles)}/20")
            else:
                print("No candles received yet...")
            
            time.sleep(5)  # Wait 5 seconds before next update
        
        # Stop streaming
        print("\nStopping stream...")
        api.stop_candles_stream(asset, interval)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Stream interrupted by user")
        if api.check_connect():
            api.stop_candles_stream(asset, interval)
    
    # Disconnect
    print("\nDisconnecting...")
    api.logout()
    print("✅ Disconnected")
    
    print("\n=== Streaming completed ===")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Program interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")

