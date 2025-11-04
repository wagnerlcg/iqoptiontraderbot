"""
WSGI entry point para produção com Gunicorn
"""
import os
import sys

# Adicionar o diretório do projeto ao path ANTES de importar app
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# CRÍTICO: Adicionar o diretório pai ao path para que iqoptionapi seja encontrado
# O código espera que o diretório pai esteja no path
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# IMPORTANTE: Garantir que current_dir está no path
# Isso permite que os módulos sejam encontrados
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Importar __init__.py do iqoptionapi que já tem lógica de importação
# Isso carrega o módulo iqoptionapi corretamente
try:
    import __init__ as iqoptionapi_init
    sys.modules['iqoptionapi'] = iqoptionapi_init
except:
    pass

# Importar a aplicação Flask
from app import app

# Se necessário, configurar variáveis de ambiente aqui
# os.environ['FLASK_ENV'] = 'production'

if __name__ == "__main__":
    app.run()

