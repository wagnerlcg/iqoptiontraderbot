"""
Exemplo de uso do módulo de proteção de Stop Loss
Demonstra como implementar proteção máxima de stop loss em scripts de trading.

IMPORTANTE: O Stop Loss tem PRIORIDADE MÁXIMA e deve ser verificado
antes de TODAS as operações.
"""

import sys
import os

# Adicionar diretório do projeto ao PYTHONPATH
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
parent_dir = os.path.dirname(project_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from iqoptionapi import IQ_Option  # pyright: ignore[reportMissingImports]
from stop_loss_protection import create_stop_loss_protection, StopLossProtection
import time
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]


def main():
    # Carregar variáveis de ambiente
    load_dotenv()
    
    EMAIL = os.getenv("IQ_OPTION_EMAIL")
    PASSWORD = os.getenv("IQ_OPTION_PASSWORD")
    ACCOUNT_TYPE = os.getenv("IQ_OPTION_ACCOUNT_TYPE", "PRACTICE")
    
    if not EMAIL or not PASSWORD:
        print("ERRO: Credenciais nao encontradas!")
        return
    
    print("=== Exemplo de Protecao de Stop Loss ===")
    print(f"Tipo de Conta: {ACCOUNT_TYPE}\n")
    
    if ACCOUNT_TYPE == "REAL":
        print("*** ATENCAO: CONTA REAL SELECIONADA ***\n")
    
    # Inicializar API
    print("1. Conectando...")
    api = IQ_Option(EMAIL, PASSWORD, active_account_type=ACCOUNT_TYPE)
    check, reason = api.connect()
    
    if not check:
        print(f"ERRO: Conexao falhou: {reason}")
        return
    
    print("OK: Conectado!")
    
    # Obter saldo inicial
    initial_balance = api.get_balance()
    print(f"\n2. Saldo Inicial: ${initial_balance:.2f}")
    
    # Criar proteção de Stop Loss (PRIORIDADE MÁXIMA)
    print("\n3. Ativando protecao de Stop Loss...")
    stop_loss_protection = create_stop_loss_protection(api)
    
    if not stop_loss_protection:
        print("ERRO: Nao foi possivel criar protecao de stop loss!")
        api.logout()
        return
    
    # Iniciar monitoramento contínuo
    stop_loss_protection.start_monitoring()
    
    # Callback quando stop loss for acionado
    def on_stop_loss():
        print("\n*** CALLBACK: Stop Loss acionado - todas operacoes devem parar! ***")
        # Aqui você pode adicionar lógica adicional, como fechar posições abertas
    
    stop_loss_protection.on_stop_loss_triggered = on_stop_loss
    
    # Simular verificações antes de operações
    print("\n4. Simulando verificacoes de seguranca antes de operar...")
    
    for i in range(10):
        if not stop_loss_protection.can_operate():
            print(f"\n*** OPERACAO {i+1} BLOQUEADA: Stop Loss foi acionado! ***")
            print("Nenhuma operacao sera permitida ate que o problema seja resolvido.")
            break
        
        # Simular verificação de saldo
        current_balance = api.get_balance()
        updated = stop_loss_protection.update_balance(current_balance)
        
        if updated:
            print(f"\n*** STOP LOSS ACIONADO na verificacao {i+1}! ***")
            break
        
        status = stop_loss_protection.get_status()
        print(f"Verificacao {i+1}: Saldo=${current_balance:.2f}, "
              f"Perda={status['loss_percent']:.2f}%, "
              f"Pode operar={'SIM' if status['can_operate'] else 'NAO'}")
        
        time.sleep(1)
    
    # Parar monitoramento
    print("\n5. Parando monitoramento...")
    stop_loss_protection.stop_monitoring()
    
    # Status final
    status = stop_loss_protection.get_status()
    print("\n=== Status Final ===")
    print(f"Stop Loss Acionado: {'SIM' if status['is_triggered'] else 'NAO'}")
    print(f"Saldo Inicial: ${status['initial_balance']:.2f}")
    print(f"Saldo Atual: ${status['current_balance']:.2f}")
    print(f"Saldo Minimo: ${status['minimum_balance']:.2f}")
    print(f"Perda: {status['loss_percent']:.2f}%")
    print(f"Pode Operar: {'SIM' if status['can_operate'] else 'NAO'}")
    
    # Desconectar
    print("\n6. Desconectando...")
    api.logout()
    print("OK: Desconectado")
    
    print("\n=== Exemplo concluido ===")
    print("\nIMPORTANTE: Em um script real de trading, voce DEVE:")
    print("1. Verificar stop_loss_protection.can_operate() antes de CADA operacao")
    print("2. Chamar stop_loss_protection.update_balance() apos CADA operacao")
    print("3. NUNCA ignorar o resultado de can_operate() - ele tem PRIORIDADE MAXIMA")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAVISO: Interrompido pelo usuario")
    except Exception as e:
        print(f"\n\nERRO: {e}")
        import traceback
        traceback.print_exc()

