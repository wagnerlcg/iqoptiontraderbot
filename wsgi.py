"""
WSGI entry point para produção com Gunicorn
"""
import os
import sys

# Adicionar o diretório do projeto ao path ANTES de importar app
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# CRÍTICO: Adicionar o diretório pai ao path para que iqoptionapi seja encontrado
# O app.py espera que o diretório pai esteja no path para importar iqoptionapi
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Também adicionar o diretório atual (necessário para importar app.py)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Importar a aplicação Flask
from app import app

# Se necessário, configurar variáveis de ambiente aqui
# os.environ['FLASK_ENV'] = 'production'

if __name__ == "__main__":
    app.run()

