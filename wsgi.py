"""
WSGI entry point para produção com Gunicorn
"""
import os
import sys
import types

# Adicionar o diretório do projeto ao path ANTES de importar app
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# CRÍTICO: Criar módulo virtual 'iqoptionapi' ANTES de importar app.py
# Isso permite que stable_api.py encontre iqoptionapi.api, iqoptionapi.constants, etc.
if 'iqoptionapi' not in sys.modules:
    iqoptionapi_module = types.ModuleType('iqoptionapi')
    iqoptionapi_module.__path__ = [current_dir]
    iqoptionapi_module.__file__ = os.path.join(current_dir, '__init__.py')
    sys.modules['iqoptionapi'] = iqoptionapi_module
    
    # Também criar sub-módulos que stable_api.py precisa
    sys.modules['iqoptionapi.api'] = types.ModuleType('iqoptionapi.api')
    sys.modules['iqoptionapi.api'].__file__ = os.path.join(current_dir, 'api.py')
    sys.modules['iqoptionapi.constants'] = types.ModuleType('iqoptionapi.constants')
    sys.modules['iqoptionapi.constants'].__file__ = os.path.join(current_dir, 'constants.py')
    sys.modules['iqoptionapi.country_id'] = types.ModuleType('iqoptionapi.country_id')
    sys.modules['iqoptionapi.country_id'].__file__ = os.path.join(current_dir, 'country_id.py')
    sys.modules['iqoptionapi.global_value'] = types.ModuleType('iqoptionapi.global_value')
    sys.modules['iqoptionapi.global_value'].__file__ = os.path.join(current_dir, 'global_value.py')
    sys.modules['iqoptionapi.expiration'] = types.ModuleType('iqoptionapi.expiration')
    sys.modules['iqoptionapi.expiration'].__file__ = os.path.join(current_dir, 'expiration.py')
    sys.modules['iqoptionapi.version_control'] = types.ModuleType('iqoptionapi.version_control')
    sys.modules['iqoptionapi.version_control'].__file__ = os.path.join(current_dir, 'version_control.py')

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

