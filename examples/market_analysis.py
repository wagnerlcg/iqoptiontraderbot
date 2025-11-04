"""
Market Analysis Example - IQ Option API
Demonstrates technical analysis, real-time data streaming, and market indicators.

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
    
    print("=== IQ Option API - Market Analysis Example ===\n")
    
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
    
    # Example asset
    asset = "EURUSD"
    
    # 1. Get historical candles
    print(f"1. Historical Data Analysis for {asset}")
    print("-" * 50)
    
    server_time = api.get_server_timestamp()
    candles = api.get_candles(asset, 60, 100, server_time)  # 100 candles, 1-minute
    
    if candles:
        # Simple technical analysis
        closes = [c['close'] for c in candles]
        highs = [c['max'] for c in candles]
        lows = [c['min'] for c in candles]
        
        # Calculate SMA
        sma_20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else 0
        sma_50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else 0
        
        print(f"   Last 100 candles retrieved")
        print(f"   Current Price: {closes[-1]:.5f}")
        print(f"   Highest Price (100): {max(highs):.5f}")
        print(f"   Lowest Price (100): {min(lows):.5f}")
        print(f"   SMA 20: {sma_20:.5f}")
        print(f"   SMA 50: {sma_50:.5f}")
        
        # Trend detection
        if sma_20 > sma_50:
            print("   📈 Trend: BULLISH (SMA 20 > SMA 50)")
        elif sma_20 < sma_50:
            print("   📉 Trend: BEARISH (SMA 20 < SMA 50)")
        else:
            print("   ➡️  Trend: NEUTRAL")
    
    print()
    
    # 2. Get technical indicators
    print(f"2. Technical Indicators for {asset}")
    print("-" * 50)
    
    try:
        indicators = api.get_technical_indicators(asset)
        if indicators and 'indicators' in indicators:
            for ind in indicators['indicators'][:5]:  # Show first 5
                name = ind.get('name', 'Unknown')
                value = ind.get('value', 0)
                print(f"   {name}: {value:.2f}")
        else:
            print("   No indicators available")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # 3. Get traders' sentiment
    print(f"3. Traders' Market Sentiment for {asset}")
    print("-" * 50)
    
    try:
        # Start sentiment stream if not already started
        api.start_mood_stream(asset, "turbo-option")
        time.sleep(2)
        
        # get_traders_mood retorna um float com a porcentagem de "higher" (call)
        mood_higher = api.get_traders_mood(asset)
        
        # Verificar se retornou um valor válido
        if mood_higher is None:
            print("   Traders' Sentiment: Dados nao disponiveis")
        else:
            # Converter para float se necessário
            try:
                higher_percent = float(mood_higher)
                lower_percent = 100.0 - higher_percent
                
                print(f"   Traders' Sentiment:")
                print(f"   - Higher (Call): {higher_percent:.1f}%")
                print(f"   - Lower (Put): {lower_percent:.1f}%")
                
                # Determine sentiment
                if higher_percent > 60:
                    print("   📊 Market is very optimistic")
                elif lower_percent > 60:
                    print("   📊 Market is very pessimistic")
                else:
                    print("   📊 Market sentiment is balanced")
            except (ValueError, TypeError):
                print(f"   Traders' Sentiment: Valor invalido recebido: {mood_higher}")
            
        api.stop_mood_stream(asset, "turbo-option")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # 4. Real-time candle streaming
    print(f"4. Real-time Candle Streaming for {asset}")
    print("-" * 50)
    print("   Starting stream (5 seconds)...")
    
    try:
        # Subscribe to real-time candles
        api.start_candles_stream(asset, 60, 10)  # 1-min candles, max 10
        
        # Wait a bit for data
        time.sleep(2)
        
        # Get latest candles
        realtime_candles = api.get_realtime_candles(asset, 60)
        
        if realtime_candles:
            # Get the latest candle
            latest = sorted(realtime_candles.items(), reverse=True)[0][1]
            print(f"   Latest candle:")
            print(f"   - Open: {latest.get('open', 0):.5f}")
            print(f"   - Close: {latest.get('close', 0):.5f}")
            print(f"   - High: {latest.get('max', 0):.5f}")
            print(f"   - Low: {latest.get('min', 0):.5f}")
            print(f"   - Volume: {latest.get('volume', 0)}")
        
        # Stop streaming
        api.stop_candles_stream(asset, 60)
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # 5. Get financial information
    print(f"5. Financial Information for {asset}")
    print("-" * 50)
    
    try:
        financial_info = api.get_financial_information(api.get_all_ACTIVES_OPCODE()[asset])
        if financial_info and financial_info.get('msg', {}).get('data', {}).get('active', {}):
            active_info = financial_info['msg']['data']['active']
            print(f"   Asset Name: {active_info.get('name', 'N/A')}")
            print(f"   Asset ID: {active_info.get('id', 'N/A')}")
            print(f"   State: {active_info.get('state', 'N/A')}")
            print(f"   Schedule: {active_info.get('schedule', [])}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Disconnect
    print("\n6. Disconnecting...")
    api.logout()
    print("✅ Done!")
    
    print("\n=== Analysis completed ===")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")

