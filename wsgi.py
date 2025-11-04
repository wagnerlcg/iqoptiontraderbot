"""
WSGI entry point para produção com Gunicorn
"""
import os
import sys

# Adicionar o diretório do projeto ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Importar a aplicação Flask
from app import app

# Se necessário, configurar variáveis de ambiente aqui
# os.environ['FLASK_ENV'] = 'production'

if __name__ == "__main__":
    app.run()

