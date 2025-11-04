"""
WSGI entry point para produção com Gunicorn
"""
import os
import sys
import types
import importlib.util

# Adicionar o diretório do projeto ao path ANTES de importar app
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

def load_module_recursive(module_name, file_path, package=None):
    """Carrega um módulo recursivamente e registra no sys.modules."""
    if module_name in sys.modules:
        return sys.modules[module_name]
    
    if os.path.exists(file_path):
        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                if package:
                    setattr(package, module_name.split('.')[-1], module)
                return module
        except Exception as e:
            print(f"Erro ao carregar {module_name}: {e}")
    return None

# CRÍTICO: Criar módulo virtual 'iqoptionapi' ANTES de importar app.py
# Isso permite que stable_api.py encontre iqoptionapi.api, iqoptionapi.constants, etc.
if 'iqoptionapi' not in sys.modules:
    iqoptionapi_module = types.ModuleType('iqoptionapi')
    iqoptionapi_module.__path__ = [current_dir]
    iqoptionapi_module.__file__ = os.path.join(current_dir, '__init__.py')
    sys.modules['iqoptionapi'] = iqoptionapi_module
    
    # Criar módulos http e ws como pacotes
    http_module = types.ModuleType('iqoptionapi.http')
    http_module.__path__ = [os.path.join(current_dir, 'http')]
    sys.modules['iqoptionapi.http'] = http_module
    setattr(iqoptionapi_module, 'http', http_module)
    
    ws_module = types.ModuleType('iqoptionapi.ws')
    ws_module.__path__ = [os.path.join(current_dir, 'ws')]
    sys.modules['iqoptionapi.ws'] = ws_module
    setattr(iqoptionapi_module, 'ws', ws_module)
    
    # Criar sub-módulos ws.chanels e ws.received
    ws_chanels_module = types.ModuleType('iqoptionapi.ws.chanels')
    ws_chanels_module.__path__ = [os.path.join(current_dir, 'ws', 'chanels')]
    sys.modules['iqoptionapi.ws.chanels'] = ws_chanels_module
    setattr(ws_module, 'chanels', ws_chanels_module)
    
    ws_received_module = types.ModuleType('iqoptionapi.ws.received')
    ws_received_module.__path__ = [os.path.join(current_dir, 'ws', 'received')]
    sys.modules['iqoptionapi.ws.received'] = ws_received_module
    setattr(ws_module, 'received', ws_received_module)
    
    # Carregar módulos principais primeiro
    modules_to_load = {
        'api': 'api.py',
        'constants': 'constants.py',
        'country_id': 'country_id.py',
        'global_value': 'global_value.py',
        'expiration': 'expiration.py',
        'version_control': 'version_control.py',
    }
    
    for module_name, file_name in modules_to_load.items():
        module_path = os.path.join(current_dir, file_name)
        load_module_recursive(f'iqoptionapi.{module_name}', module_path, iqoptionapi_module)

# Adicionar diretórios ao path
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# IMPORTANTE: Adicionar current_dir ao path DEPOIS de criar o módulo virtual
# Mas antes de importar app.py (que pode removê-lo)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Importar a aplicação Flask
# O app.py tentará remover current_dir do path, mas o módulo virtual já está criado
from app import app

# Se necessário, configurar variáveis de ambiente aqui
# os.environ['FLASK_ENV'] = 'production'

if __name__ == "__main__":
    app.run()

