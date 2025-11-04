"""
WSGI entry point para produção com Gunicorn
"""
import os
import sys

# Adicionar o diretório do projeto ao path ANTES de importar app
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# CRÍTICO: Adicionar APENAS o diretório pai ao path
# NÃO adicionar current_dir para evitar conflito com o diretório http/
# que interfere no módulo padrão 'http' do Python
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# NÃO adicionar current_dir ao path - isso causaria conflito com http/
# Em vez disso, vamos importar os módulos usando o caminho completo

# Importar módulo iqoptionapi diretamente
# Como estamos no diretório iqoptionapi, precisamos importar como pacote
try:
    import importlib
    # Tentar importar iqoptionapi como pacote do diretório pai
    iqoptionapi_module = importlib.import_module('iqoptionapi')
    sys.modules['iqoptionapi'] = iqoptionapi_module
except Exception as e:
    # Se falhar, tentar importar usando importlib.util
    try:
        import importlib.util
        init_path = os.path.join(current_dir, '__init__.py')
        if os.path.exists(init_path):
            spec = importlib.util.spec_from_file_location('iqoptionapi', init_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules['iqoptionapi'] = module
                spec.loader.exec_module(module)
    except Exception as e2:
        pass

# Importar a aplicação Flask
from app import app

# Se necessário, configurar variáveis de ambiente aqui
# os.environ['FLASK_ENV'] = 'production'

if __name__ == "__main__":
    app.run()

