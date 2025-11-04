"""
Script wrapper para executar scripts IQ Option com tipo de conta selecionado.
Permite escolher entre PRACTICE e REAL antes de executar.
"""

import sys
import os

# Adicionar diretório do projeto ao PYTHONPATH
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def main():
    if len(sys.argv) < 3:
        print("Uso: python executar_com_conta.py <TIPO_CONTA> <SCRIPT>")
        print("  TIPO_CONTA: PRACTICE ou REAL")
        print("  SCRIPT: caminho do script a executar")
        print("\nExemplo:")
        print("  python executar_com_conta.py PRACTICE TESTE_RAPIDO.py")
        sys.exit(1)
    
    account_type = sys.argv[1].upper()
    script_path = sys.argv[2]
    
    if account_type not in ['PRACTICE', 'REAL']:
        print(f"ERRO: Tipo de conta invalido: {account_type}")
        print("Use PRACTICE ou REAL")
        sys.exit(1)
    
    if not os.path.exists(script_path):
        print(f"ERRO: Script nao encontrado: {script_path}")
        sys.exit(1)
    
    # Definir variável de ambiente
    os.environ['IQ_OPTION_ACCOUNT_TYPE'] = account_type
    
    print("=" * 60)
    print(f"Executando com conta: {account_type}")
    print(f"Script: {script_path}")
    print("=" * 60)
    print()
    
    if account_type == 'REAL':
        print("ATENCAO: Usando conta REAL com DINHEIRO REAL!")
        print("Operacoes nesta conta envolvem risco de perda financeira.")
        print()
    
    # Executar o script
    try:
        # Ler e executar o script
        with open(script_path, 'r', encoding='utf-8') as f:
            script_code = f.read()
        
        # Criar namespace para execução
        namespace = {
            '__name__': '__main__',
            '__file__': script_path,
            'os': os,
            'sys': sys,
        }
        
        # Executar o script no namespace
        exec(compile(script_code, script_path, 'exec'), namespace)
        
    except KeyboardInterrupt:
        print("\n\nAVISO: Interrompido pelo usuario")
    except Exception as e:
        print(f"\n\nERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

