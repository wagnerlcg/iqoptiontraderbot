"""
Script para executar sinais do arquivo sinais.txt
Processa e executa sinais de trading conforme programado.
"""

import sys
import os
import time
from datetime import datetime

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

# Importar módulos locais do diretório iqoptionapi usando importlib ou caminho direto
# Como não podemos adicionar project_dir ao sys.path (causa conflito com http/),
# vamos importar diretamente usando o caminho do arquivo
import importlib.util

# Importar sinais_processor
sinais_processor_path = os.path.join(project_dir, "sinais_processor.py")
spec_sinais = importlib.util.spec_from_file_location("sinais_processor", sinais_processor_path)
sinais_processor_module = importlib.util.module_from_spec(spec_sinais)
spec_sinais.loader.exec_module(sinais_processor_module)
SinaisProcessor = sinais_processor_module.SinaisProcessor
Sinal = sinais_processor_module.Sinal

# Importar stop_loss_protection
stop_loss_path = os.path.join(project_dir, "stop_loss_protection.py")
spec_stop = importlib.util.spec_from_file_location("stop_loss_protection", stop_loss_path)
stop_loss_module = importlib.util.module_from_spec(spec_stop)
spec_stop.loader.exec_module(stop_loss_module)
create_stop_loss_protection = stop_loss_module.create_stop_loss_protection
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]


def converter_timeframe_para_minutos(timeframe: str) -> int:
    """
    Converte timeframe (ex: M1, M5) para minutos.
    
    Args:
        timeframe: Timeframe no formato M<N> ou H<N>
        
    Returns:
        int: Minutos
    """
    timeframe = timeframe.upper()
    
    if timeframe.startswith('M'):
        return int(timeframe[1:])
    elif timeframe.startswith('H'):
        return int(timeframe[1:]) * 60
    else:
        raise ValueError(f"Timeframe invalido: {timeframe}")


def executar_sinal(api, sinal: Sinal, stop_loss_protection, valor_entrada: float):
    """
    Executa um sinal de trading.
    
    Args:
        api: Instância da API IQ Option
        sinal: Sinal a executar
        stop_loss_protection: Instância de proteção de stop loss
        valor_entrada: Valor a investir
        
    Returns:
        tuple: (sucesso: bool, order_id: int ou None, mensagem: str)
    """
    # VERIFICAÇÃO CRÍTICA: Stop Loss tem prioridade máxima
    if not stop_loss_protection.can_operate():
        return (False, None, "OPERACAO BLOQUEADA: Stop Loss foi acionado!")
    
    # Converter timeframe para minutos
    try:
        minutos = converter_timeframe_para_minutos(sinal.timeframe)
    except ValueError as e:
        return (False, None, f"Erro no timeframe: {e}")
    
    # Validar valor de entrada
    if valor_entrada <= 0:
        return (False, None, "Valor de entrada invalido")
    
    # Verificar saldo disponível
    saldo_atual = api.get_balance()
    if saldo_atual < valor_entrada:
        return (False, None, f"Saldo insuficiente. Disponivel: ${saldo_atual:.2f}, Necessario: ${valor_entrada:.2f}")
    
    # Executar operação
    try:
        print(f"  Executando: {sinal.direcao} em {sinal.ativo}, {sinal.timeframe}, ${valor_entrada:.2f}")
        # API buy: price, ACTIVES, ACTION, expirations (minutos)
        resultado, order_id = api.buy(valor_entrada, sinal.ativo, sinal.direcao.lower(), minutos)
        
        if resultado:
            # Atualizar saldo após operação
            novo_saldo = api.get_balance()
            stop_loss_protection.update_balance(novo_saldo)
            
            # Verificar se stop loss foi acionado após a operação
            if not stop_loss_protection.can_operate():
                return (True, order_id, f"Operacao executada (ID: {order_id}), mas STOP LOSS foi acionado!")
            
            return (True, order_id, f"Operacao executada com sucesso! ID: {order_id}")
        else:
            return (False, None, "Falha ao executar operacao na API")
            
    except Exception as e:
        return (False, None, f"Erro ao executar operacao: {e}")


def calcular_valor_entrada(entry_type: str, entry_value: str, saldo_atual: float) -> float:
    """
    Calcula o valor de entrada baseado no tipo configurado.
    
    Args:
        entry_type: PERCENT ou FIXED
        entry_value: Valor (porcentagem ou valor fixo)
        saldo_atual: Saldo atual da conta
        
    Returns:
        float: Valor calculado
    """
    try:
        value = float(entry_value)
        
        if entry_type == "PERCENT":
            return saldo_atual * (value / 100.0)
        elif entry_type == "FIXED":
            return value
        else:
            return saldo_atual * 0.01  # Padrão: 1% se tipo inválido
    except ValueError:
        return saldo_atual * 0.01  # Padrão: 1% se valor inválido


def main():
    # Carregar variáveis de ambiente
    load_dotenv()
    
    EMAIL = os.getenv("IQ_OPTION_EMAIL")
    PASSWORD = os.getenv("IQ_OPTION_PASSWORD")
    ACCOUNT_TYPE = os.getenv("IQ_OPTION_ACCOUNT_TYPE", "PRACTICE")
    
    # Configurações de entrada
    ENTRY_TYPE = os.getenv("IQ_OPTION_ENTRY_TYPE", "PERCENT")
    ENTRY_VALUE = os.getenv("IQ_OPTION_ENTRY_VALUE", "1")
    
    if not EMAIL or not PASSWORD:
        print("ERRO: Credenciais nao encontradas!")
        print("\nPor favor, configure IQ_OPTION_EMAIL e IQ_OPTION_PASSWORD no arquivo .env")
        return
    
    print("=" * 70)
    print("   EXECUTOR DE SINAIS - IQ Option API")
    print("=" * 70)
    print(f"\nTipo de Conta: {ACCOUNT_TYPE}")
    
    if ACCOUNT_TYPE == "REAL":
        print("*** ATENCAO: CONTA REAL SELECIONADA - DINHEIRO REAL! ***\n")
    
    # Carregar sinais
    # O arquivo sinais.txt deve estar no diretório raiz do projeto
    sinais_file = os.path.join(project_dir, "sinais.txt")
    print("\n1. Carregando sinais do arquivo sinais.txt...")
    processor = SinaisProcessor(sinais_file)
    
    if not os.path.exists(sinais_file):
        print("  Arquivo sinais.txt nao encontrado!")
        resposta = input("  Deseja criar um arquivo de exemplo? (S/N): ")
        if resposta.upper() == "S":
            if processor.criar_arquivo_exemplo():
                print("  Arquivo exemplo criado! Edite sinais.txt e execute novamente.")
            else:
                print("  Erro ao criar arquivo exemplo.")
        return
    
    if not processor.carregar_sinais():
        print("  ERRO: Nao foi possivel carregar sinais!")
        erros = processor.get_erros()
        if erros:
            print("\n  Erros encontrados:")
            for erro in erros:
                print(f"    - {erro}")
        return
    
    sinais = processor.obter_todos_sinais()
    erros = processor.get_erros()
    
    if erros:
        print(f"  AVISO: {len(erros)} erro(s) encontrado(s) (mas {len(sinais)} sinal(is) valido(s)):")
        for erro in erros[:5]:  # Mostrar apenas os 5 primeiros
            print(f"    - {erro}")
        if len(erros) > 5:
            print(f"    ... e mais {len(erros) - 5} erro(s)")
    
    print(f"  OK: {len(sinais)} sinal(is) carregado(s) com sucesso!")
    
    # Conectar na API
    print("\n2. Conectando na IQ Option...")
    api = IQ_Option(EMAIL, PASSWORD, active_account_type=ACCOUNT_TYPE)
    check, reason = api.connect()
    
    if not check:
        print(f"  ERRO: Conexao falhou: {reason}")
        return
    
    print("  OK: Conectado com sucesso!")
    
    # Obter saldo
    saldo_inicial = api.get_balance()
    print(f"\n3. Saldo Inicial: ${saldo_inicial:.2f}")
    
    # Ativar proteção de Stop Loss (PRIORIDADE MÁXIMA)
    print("\n4. Ativando protecao de Stop Loss...")
    stop_loss_protection = create_stop_loss_protection(api)
    
    if not stop_loss_protection:
        print("  ERRO: Nao foi possivel criar protecao de stop loss!")
        api.logout()
        return
    
    stop_loss_protection.start_monitoring()
    print("  OK: Protecao de Stop Loss ativada (PRIORIDADE MAXIMA)")
    
    # Mostrar configurações
    print("\n5. Configuracoes de Entrada:")
    print(f"   Tipo: {ENTRY_TYPE}")
    if ENTRY_TYPE == "PERCENT":
        print(f"   Valor: {ENTRY_VALUE}% da banca")
    else:
        print(f"   Valor: ${ENTRY_VALUE} por operacao")
    
    # Mostrar próximos sinais
    proximos = processor.obter_proximos_sinais(5)
    if proximos:
        print(f"\n6. Proximos {min(5, len(proximos))} sinais programados:")
        for sinal in proximos:
            print(f"   {sinal.hora} - {sinal.ativo} ({sinal.timeframe}) - {sinal.direcao}")
    
    # Loop de monitoramento contínuo de sinais
    print("\n7. Iniciando monitoramento de sinais...")
    print("   O script ficara aguardando os sinais programados.")
    print("   (Use Ctrl+C para parar)")
    print()
    
    ultima_hora_verificada = None
    ultima_execucao_hora = None
    ultimo_sinal_executado_hora = None
    tempo_espera_pos_sinais = 120  # Aguardar 2 minutos após último sinal antes de encerrar
    
    try:
        while True:
            # Verificar stop loss primeiro
            if stop_loss_protection and not stop_loss_protection.can_operate():
                print("\n   *** STOP LOSS ACIONADO - PARANDO EXECUCAO ***")
                break
            
            # Obter hora atual
            hora_atual = datetime.now()
            hora_str = hora_atual.strftime("%H:%M")
            segundo = hora_atual.second
            
            # Verificar se ainda há sinais futuros
            proximos = processor.obter_proximos_sinais(1)
            if not proximos:
                # Não há mais sinais futuros
                if ultimo_sinal_executado_hora:
                    # Já executamos algum sinal, verificar se passou tempo suficiente
                    tempo_decorrido = (hora_atual - ultimo_sinal_executado_hora).total_seconds()
                    if tempo_decorrido >= tempo_espera_pos_sinais:
                        print(f"\n[{hora_atual.strftime('%H:%M:%S')}] Nenhum sinal futuro encontrado.")
                        print(f"   Todos os sinais programados ja foram executados ou passaram.")
                        print(f"   Aguardou {tempo_espera_pos_sinais/60:.0f} minutos apos o ultimo sinal.")
                        print(f"   Encerrando monitoramento...")
                        break
                    else:
                        # Ainda está dentro do tempo de espera, continuar monitorando
                        tempo_restante = tempo_espera_pos_sinais - tempo_decorrido
                        if segundo <= 5 and hora_str != ultima_hora_verificada:
                            print(f"\r[{hora_str}] Aguardando... Nenhum sinal futuro. Encerrando em {tempo_restante:.0f}s... " + " " * 20, end="", flush=True)
                            ultima_hora_verificada = hora_str
                else:
                    # Nunca executamos nenhum sinal e não há sinais futuros
                    # Isso significa que todos os sinais já passaram antes de iniciar
                    print(f"\n[{hora_atual.strftime('%H:%M:%S')}] Nenhum sinal futuro encontrado.")
                    print(f"   Todos os sinais programados ja passaram antes do inicio do monitoramento.")
                    print(f"   Encerrando monitoramento...")
                    break
            
            # Executar sinais na hora exata (janela de 58s a 02s do próximo minuto)
            # Isso garante que executamos no momento certo, mesmo com pequenos atrasos
            if (segundo >= 58 or segundo <= 2) and hora_str != ultima_execucao_hora:
                sinais_agora = processor.obter_sinais_para_hora(hora_atual)
                
                if sinais_agora:
                    print(f"\n[{hora_atual.strftime('%H:%M:%S')}] *** {len(sinais_agora)} SINAL(IS) ENCONTRADO(S)! ***")
                    
                    # Registrar que executamos um sinal agora
                    ultimo_sinal_executado_hora = hora_atual
                    
                    for sinal in sinais_agora:
                        print(f"\n   Processando: {sinal}")
                        
                        # Verificar stop loss antes de cada operação
                        if stop_loss_protection and not stop_loss_protection.can_operate():
                            print("\n   *** STOP LOSS ACIONADO - PARANDO EXECUCAO ***")
                            break
                        
                        # Calcular valor de entrada
                        valor_entrada = calcular_valor_entrada(ENTRY_TYPE, ENTRY_VALUE, api.get_balance())
                        
                        # Usar cálculo seguro se stop loss protection estiver disponível
                        if stop_loss_protection:
                            if ENTRY_TYPE == "PERCENT":
                                valor_entrada = stop_loss_protection.calculate_safe_entry_value(entry_percent=float(ENTRY_VALUE))
                            else:
                                valor_entrada = stop_loss_protection.calculate_safe_entry_value(entry_fixed=float(ENTRY_VALUE))
                        
                        # Executar sinal
                        sucesso, order_id, mensagem = executar_sinal(api, sinal, stop_loss_protection, valor_entrada)
                        
                        if sucesso:
                            print(f"   OK: {mensagem}")
                            if order_id:
                                print(f"      Order ID: {order_id}")
                        else:
                            print(f"   ERRO: {mensagem}")
                        
                        # Pequena pausa entre operações
                        time.sleep(1)
                    
                    ultima_execucao_hora = hora_str
                    # Esperar alguns segundos para evitar re-execução no mesmo minuto
                    time.sleep(5)
            
            # Mostrar próximos sinais e status a cada minuto (apenas no segundo 0-5 para não poluir)
            if segundo <= 5 and hora_str != ultima_hora_verificada:
                ultima_hora_verificada = hora_str
                
                # Buscar próximos sinais novamente (pode ter mudado)
                proximos = processor.obter_proximos_sinais(3)
                if proximos:
                    print(f"\r[{hora_str}] Aguardando... Proximos: ", end="")
                    for i, sinal in enumerate(proximos[:3]):
                        print(f"{sinal.hora} {sinal.ativo} ", end="")
                    print(" " * 20, end="")  # Limpar resto da linha
                    print(end="", flush=True)
                # Se não houver próximos, a verificação acima já cuida do encerramento
            
            # Verificar a cada segundo (para pegar a hora exata dos sinais)
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n   *** Monitoramento interrompido pelo usuario ***")
    
    # Status final
    saldo_final = api.get_balance()
    print("\n" + "=" * 70)
    print("   RESUMO DA EXECUCAO")
    print("=" * 70)
    print(f"   Saldo Inicial: ${saldo_inicial:.2f}")
    print(f"   Saldo Final: ${saldo_final:.2f}")
    print(f"   Variacao: ${saldo_final - saldo_inicial:.2f}")
    
    if stop_loss_protection:
        status = stop_loss_protection.get_status()
        print(f"   Stop Loss Acionado: {'SIM' if status['is_triggered'] else 'NAO'}")
        print(f"   Perda Atual: {status['loss_percent']:.2f}%")
        stop_loss_protection.stop_monitoring()
    
    print("=" * 70)
    
    # Desconectar
    print("\n8. Desconectando...")
    api.logout()
    print("   OK: Desconectado com sucesso")
    
    print("\n=== Execucao concluida ===")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAVISO: Interrompido pelo usuario")
    except Exception as e:
        print(f"\n\nERRO: {e}")
        import traceback
        traceback.print_exc()

