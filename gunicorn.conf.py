# Configuração do Gunicorn para produção
import multiprocessing
import os

# Diretório base da aplicação
basedir = os.path.abspath(os.path.dirname(__file__))

# Número de workers (processos)
# Recomendado: (2 x CPU cores) + 1
workers = multiprocessing.cpu_count() * 2 + 1

# Número de threads por worker
threads = 2

# Endereço e porta (será usado pelo nginx via socket)
bind = "127.0.0.1:8000"

# Timeout em segundos
timeout = 120

# Modo de trabalho (sync, gevent, eventlet, etc)
worker_class = "sync"

# Máximo de requisições por worker antes de reciclar
max_requests = 1000
max_requests_jitter = 50

# Logs
accesslog = os.path.join(basedir, "logs", "gunicorn_access.log")
errorlog = os.path.join(basedir, "logs", "gunicorn_error.log")
loglevel = "info"

# Usuário e grupo (configure conforme necessário)
# user = "www-data"
# group = "www-data"

# Preload da aplicação (melhora performance)
preload_app = True

# Worker temp directory
worker_tmp_dir = "/dev/shm"

# Configurações adicionais
keepalive = 5
graceful_timeout = 30

