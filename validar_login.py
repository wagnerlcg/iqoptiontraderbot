"""
Script para validar login no IQ Option
Retorna código de saída 0 se login for bem-sucedido, 1 caso contrário
"""

import sys
import os
import json
import traceback

# CRÍTICO: Mudar o diretório de trabalho ANTES de qualquer importação
# Isso evita que o Python adicione o diretório iqoptionapi/ ao sys.path automaticamente
# e assim evita o conflito com o diretório local http/
script_dir = os.path.dirname(os.path.abspath(__file__))
# script_dir é o diretório iqoptionapi/ (onde validar_login.py está)
parent_dir = os.path.dirname(script_dir)  # Diretório pai

# Salvar diretório atual e mudar para o pai
original_cwd = os.getcwd()
try:
    os.chdir(parent_dir)
except:
    pass

# Adicionar o diretório pai ao path para que Python encontre 'iqoptionapi' como módulo
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# IMPORTANTE: Remover o diretório atual (iqoptionapi/) do sys.path se estiver lá
# para evitar conflito com http/
if script_dir in sys.path:
    sys.path.remove(script_dir)

# Agora podemos importar sem conflito
from iqoptionapi import IQ_Option
from dotenv import load_dotenv

def main():
    # Carregar .env do diretório original (iqoptionapi/)
    env_path = os.path.join(script_dir, ".env")
    load_dotenv(env_path)
    
    EMAIL = os.getenv("IQ_OPTION_EMAIL")
    PASSWORD = os.getenv("IQ_OPTION_PASSWORD")
    
    if not EMAIL or not PASSWORD:
        print("ERRO: Credenciais nao encontradas no arquivo .env")
        print("Por favor, verifique se IQ_OPTION_EMAIL e IQ_OPTION_PASSWORD estao configurados.")
        return 1
    
    # Remover espaços em branco das credenciais
    EMAIL = EMAIL.strip()
    PASSWORD = PASSWORD.strip()
    
    if not EMAIL or not PASSWORD:
        print("ERRO: Email ou senha vazios no arquivo .env")
        return 1
    
    # Testar login (usar PRACTICE por padrão para teste)
    api = None
    try:
        print(f"Tentando conectar com email: {EMAIL[:3]}***@***")
        api = IQ_Option(EMAIL, PASSWORD, active_account_type="PRACTICE")
        check, reason = api.connect()
        
        if check:
            # Tentar obter saldo para confirmar que está realmente conectado
            try:
                balance = api.get_balance()
                api.logout()
                print(f"OK: Login bem-sucedido! Saldo: ${balance:.2f}")
                return 0
            except Exception as e:
                api.logout()
                print(f"AVISO: Conectado mas erro ao obter saldo: {e}")
                print("OK: Login validado (conexao estabelecida)")
                return 0
        else:
            # Tentar parsear a razão do erro
            error_msg = "Erro desconhecido"
            try:
                if reason:
                    if isinstance(reason, str):
                        try:
                            error_json = json.loads(reason)
                            if 'message' in error_json:
                                error_msg = error_json['message']
                            elif 'code' in error_json:
                                code = error_json['code']
                                if code == 'verify':
                                    error_msg = "Autenticacao de dois fatores (2FA) necessaria"
                                elif code == 'invalid_credentials':
                                    error_msg = "Email ou senha incorretos"
                                else:
                                    error_msg = f"Codigo de erro: {code}"
                            else:
                                error_msg = reason
                        except:
                            error_msg = reason
                    else:
                        error_msg = str(reason)
            except:
                error_msg = str(reason) if reason else "Erro desconhecido"
            
            print(f"ERRO: Falha no login")
            print(f"Detalhes: {error_msg}")
            
            if api:
                try:
                    api.logout()
                except:
                    pass
            
            return 1
            
    except KeyboardInterrupt:
        print("\nValidacao cancelada pelo usuario")
        if api:
            try:
                api.logout()
            except:
                pass
        return 1
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        
        print(f"ERRO: {error_type}")
        print(f"Detalhes: {error_msg}")
        
        # Mostrar traceback apenas se for um erro crítico
        if "ModuleNotFoundError" in error_type or "ImportError" in error_type:
            print("\nPossiveis solucoes:")
            print("1. Execute: pip install -r requirements.txt")
            print("2. Verifique se o ambiente virtual esta ativado")
        
        if api:
            try:
                api.logout()
            except:
                pass
        
        return 1

if __name__ == "__main__":
    sys.exit(main())

