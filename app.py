"""
Aplicação Web Flask para IQ Option API
Interface moderna e responsiva para gerenciamento de trading
"""

import os
import sys
import json
import time
from datetime import datetime

# CRÍTICO: Configurar sys.path ANTES de importar Flask
# O diretório local 'http/' interfere no módulo padrão 'http' do Python
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# IMPORTANTE: Adicionar apenas o diretório pai ao path
# NÃO adicionar current_dir para evitar conflito com http/
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# IMPORTANTE: Remover current_dir do path se estiver lá
# Isso é CRÍTICO para evitar conflito com o diretório http/ que interfere
# no módulo padrão 'http' do Python
if __package__ in (None, "", "__main__") and current_dir in sys.path:
    sys.path.remove(current_dir)

# Agora podemos importar Flask sem conflito
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv

# Importar módulos do projeto usando importlib para evitar conflitos
import importlib.util

# Importar stop_loss_protection
stop_loss_path = os.path.join(current_dir, "stop_loss_protection.py")
spec_stop = importlib.util.spec_from_file_location("stop_loss_protection", stop_loss_path)
stop_loss_module = importlib.util.module_from_spec(spec_stop)
spec_stop.loader.exec_module(stop_loss_module)
create_stop_loss_protection = stop_loss_module.create_stop_loss_protection
StopLossProtection = stop_loss_module.StopLossProtection

# Importar sinais_processor
sinais_processor_path = os.path.join(current_dir, "sinais_processor.py")
spec_sinais = importlib.util.spec_from_file_location("sinais_processor", sinais_processor_path)
sinais_processor_module = importlib.util.module_from_spec(spec_sinais)
spec_sinais.loader.exec_module(sinais_processor_module)
SinaisProcessor = sinais_processor_module.SinaisProcessor
Sinal = sinais_processor_module.Sinal

# Importar IQ_Option
# Tentar importar de diferentes formas para compatibilidade
try:
    # Tentar importação relativa direta (quando rodando como pacote)
    from .stable_api import IQ_Option  # type: ignore[no-redef]
except ImportError:
    # Fallback: carregar manualmente via importlib, garantindo nome de módulo consistente
    import importlib.util

    stable_api_path = os.path.join(current_dir, "stable_api.py")
    if not os.path.exists(stable_api_path):
        raise ImportError(f"stable_api.py não encontrado em {stable_api_path}")

    module_name = "iqoptionapi.stable_api" if __package__ else "stable_api"
    spec = importlib.util.spec_from_file_location(module_name, stable_api_path)
    if spec and spec.loader:
        stable_api_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(stable_api_module)
        IQ_Option = stable_api_module.IQ_Option  # type: ignore[attr-defined]
    else:
        raise ImportError("Não foi possível carregar stable_api.py")

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Configurar APPLICATION_ROOT para funcionar em subpath /bot (apenas em produção)
# Isso permite que o Flask funcione corretamente quando está em nomadtradersystem.com/bot
# Em desenvolvimento local, não usar APPLICATION_ROOT
if os.getenv('FLASK_ENV') == 'production' or os.getenv('APPLICATION_ROOT'):
    app.config['APPLICATION_ROOT'] = '/bot'
else:
    # Em desenvolvimento, não usar APPLICATION_ROOT
    pass

# Configurar sessão permanente
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 horas

# Variáveis globais para gerenciar conexão
api_instances = {}
stop_loss_protections = {}

# Histórico de operações por sessão
trade_history = {}  # {session_id: [lista de operações]}
sinais_logs = {}  # {session_id: [lista de logs]}
losses_consecutivas = {}  # {session_id: {'count': int, 'skip_count': int}} - Controle de perdas consecutivas


def parse_float_value(value, default=None, field_name="valor"):
    """Converte entradas em float aceitando vírgula como separador decimal."""
    if value is None or (isinstance(value, str) and value.strip() == ""):
        if default is not None:
            return float(default)
        raise ValueError(f"{field_name} não informado")

    if isinstance(value, (int, float)):
        return float(value)

    value_str = str(value).strip().replace(',', '.')
    if value_str == "":
        if default is not None:
            return float(default)
        raise ValueError(f"{field_name} vazio")

    try:
        return float(value_str)
    except ValueError:
        if default is not None:
            return float(default)
        raise ValueError(f"{field_name} inválido: {value}")


def parse_int_value(value, default=None, field_name="valor"):
    """Converte entradas em int aceitando vírgula como separador decimal."""
    try:
        float_value = parse_float_value(value, default, field_name)
    except ValueError:
        if default is not None:
            return int(default)
        raise

    try:
        return int(round(float(float_value)))
    except (TypeError, ValueError):
        if default is not None:
            return int(default)
        raise ValueError(f"{field_name} inválido: {value}")


def resolve_numeric_setting(session_key, env_key, default, field_name, parser=parse_float_value):
    """Obtém configuração numérica da sessão ou .env com parsing seguro."""
    value = None

    if session_key:
        value = session.get(session_key)

    if value is None:
        env_value = os.getenv(env_key)
        if env_value is not None and env_value != "":
            value = env_value

    if value is None:
        value = default

    return parser(value, default=default, field_name=field_name)


def add_sinais_log(session_id, message, log_type='info'):
    """
    Adiciona um log de execução de sinais para a sessão.
    
    Args:
        session_id: ID da sessão
        message: Mensagem do log
        log_type: Tipo do log ('info', 'success', 'warning', 'error')
    """
    if session_id not in sinais_logs:
        sinais_logs[session_id] = []
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'message': message,
        'type': log_type
    }
    
    sinais_logs[session_id].insert(0, log_entry)
    
    # Limitar a 100 logs por sessão
    if len(sinais_logs[session_id]) > 100:
        sinais_logs[session_id] = sinais_logs[session_id][:100]
    
    # Também imprimir no terminal para debug
    print(f"[SINAIS] {message}")


def verificar_loss_completo(session_id, trade_id, gale_level):
    """
    Verifica se um trade completo (incluindo Martingales) resultou em LOSS.
    
    Args:
        session_id: ID da sessão
        trade_id: ID do trade principal
        gale_level: Nível de Gale configurado (0, 1 ou 2)
        
    Returns:
        bool: True se foi LOSS completo, False caso contrário
    """
    history = trade_history.get(session_id, [])
    
    # Encontrar o trade principal
    trade_principal = None
    for trade in history:
        if trade['id'] == trade_id:
            trade_principal = trade
            break
    
    if not trade_principal:
        return False
    
    # Encontrar todos os Martingales relacionados a este trade (cadeia completa)
    def encontrar_martingales_cadeia(trade_id_base):
        """Encontra todos os Martingales na cadeia, recursivamente."""
        martingales_diretos = []
        for trade in history:
            if trade.get('is_martingale') and trade.get('parent_trade_id') == trade_id_base:
                martingales_diretos.append(trade)
                # Buscar Martingales deste Martingale também
                martingales_diretos.extend(encontrar_martingales_cadeia(trade['id']))
        return martingales_diretos
    
    martingales = encontrar_martingales_cadeia(trade_id)
    
    # Ordenar por nível de Martingale
    martingales.sort(key=lambda x: x.get('martingale_level', 0))
    
    # Verificar se foi LOSS completo baseado no nível de Gale
    if gale_level == 0:
        # Sem Gale: qualquer LOSS na primeira entrada já conta como perda
        return trade_principal['status'] == 'loss'
    
    elif gale_level == 1:
        # Gale 1: só conta como LOSS se perder na primeira E na segunda entrada
        if trade_principal['status'] != 'loss':
            return False
        
        # Se não há Martingales, significa que não tentou Martingale ainda ou já tentou todos
        # Se já tentou todos os Martingales permitidos e todos perderam, é LOSS completo
        if len(martingales) == 0:
            # Não há Martingales - pode ser que ainda não tentou ou já tentou todos
            # Se o trade principal perdeu e não tem Martingale pendente, é LOSS completo para Gale 1
            # Mas precisamos verificar se realmente não vai ter mais Martingale
            # Por segurança, só consideramos LOSS completo se houver pelo menos 1 Martingale que perdeu
            return False
        
        # Verificar se o primeiro (e único) Martingale também perdeu
        if len(martingales) >= 1:
            primeiro_martingale = martingales[0]
            if primeiro_martingale['status'] == 'pending':
                return False  # Ainda pendente
            # Se o primeiro Martingale perdeu e não vai ter mais (gale_level == 1), é LOSS completo
            if primeiro_martingale['status'] == 'loss' and primeiro_martingale.get('martingale_level', 0) >= gale_level:
                return True
            return primeiro_martingale['status'] == 'loss'
    
    elif gale_level == 2:
        # Gale 2: só conta como LOSS se perder na primeira, segunda E terceira entrada
        if trade_principal['status'] != 'loss':
            return False
        
        if len(martingales) == 0:
            return False  # Ainda pode ter Martingales pendentes
        
        # Verificar se todos os Martingales perderam (deve ter pelo menos 2 para Gale 2)
        if len(martingales) < 2:
            # Se tem menos de 2 Martingales, ainda pode ter mais pendentes
            # Verificar se algum está pendente
            for m in martingales:
                if m['status'] == 'pending':
                    return False
            # Se não há pendentes mas tem menos de 2, ainda não completou toda a cadeia
            return False
        
        # Verificar se ambos os Martingales perderam
        primeiro_martingale = martingales[0]
        segundo_martingale = martingales[1]
        
        if primeiro_martingale['status'] == 'pending' or segundo_martingale['status'] == 'pending':
            return False  # Ainda pendente
        
        # Se ambos perderam e não vai ter mais (gale_level == 2), é LOSS completo
        if primeiro_martingale['status'] == 'loss' and segundo_martingale['status'] == 'loss':
            if segundo_martingale.get('martingale_level', 0) >= gale_level:
                return True
            return False
    
    return False


def verificar_e_atualizar_perdas_consecutivas(session_id, trade_id, gale_level):
    """
    Verifica se houve LOSS completo e atualiza o contador de perdas consecutivas.
    Se chegar a 2 perdas consecutivas, ativa o modo de pular 2 sinais.
    
    Args:
        session_id: ID da sessão
        trade_id: ID do trade principal
        gale_level: Nível de Gale configurado
    """
    if verificar_loss_completo(session_id, trade_id, gale_level):
        # Inicializar estrutura se não existir
        if session_id not in losses_consecutivas:
            losses_consecutivas[session_id] = {'count': 0, 'skip_count': 0}
        
        losses_consecutivas[session_id]['count'] += 1
        add_sinais_log(session_id, f"LOSS completo detectado! Perdas consecutivas: {losses_consecutivas[session_id]['count']}", 'warning')
        
        if losses_consecutivas[session_id]['count'] >= 2:
            losses_consecutivas[session_id]['skip_count'] = 2
            add_sinais_log(session_id, "⚠️ 2 LOSS consecutivos detectados! Próximos 2 sinais serão pulados automaticamente.", 'warning')
    else:
        # Se não foi LOSS completo (WIN ou EQUAL ou ainda pendente), resetar contador
        if session_id in losses_consecutivas:
            if losses_consecutivas[session_id]['count'] > 0:
                add_sinais_log(session_id, f"✅ WIN ou EQUAL detectado. Contador de perdas consecutivas resetado.", 'info')
            losses_consecutivas[session_id]['count'] = 0
            # Não resetar skip_count aqui, pois pode estar no meio de pular sinais


def get_api_instance():
    """Obtém ou cria instância da API para a sessão atual."""
    session_id = session.get('session_id')
    
    if not session_id:
        return None
    
    if session_id not in api_instances:
        return None
    
    return api_instances[session_id]


def create_api_instance(email, password, account_type="PRACTICE", session_id=None):
    """Cria uma nova instância da API."""
    if session_id is None:
        session_id = session.get('session_id')
        if not session_id:
            # Criar session_id baseado no email e timestamp
            session_id = f"{email}_{int(time.time())}"
            session['session_id'] = session_id
    
    try:
        api = IQ_Option(email, password, active_account_type=account_type)
        check, reason = api.connect()
        
        if not check:
            return None, reason
        
        api.change_balance(account_type)
        api_instances[session_id] = api
        
        return api, None
    except Exception as e:
        return None, str(e)


@app.route('/')
def index():
    """Página inicial."""
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    """Endpoint de login."""
    try:
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Content-Type deve ser application/json'}), 400
        
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        account_type = data.get('account_type', 'PRACTICE')
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email e senha são obrigatórios'}), 400
        
        # Criar session_id ANTES de criar a instância da API
        session_id = f"{email}_{int(time.time())}"
        session['session_id'] = session_id
        print(f"DEBUG: Criando sessão com session_id: {session_id}")
        app.logger.info(f"Recebi login para {email} (conta {account_type})")
        # Criar instância da API com o session_id
        api, error = create_api_instance(email, password, account_type, session_id)
        app.logger.info(f"Resultado login: api={'OK' if api else 'None'}, erro={error}")
        
        if api is None:
            print(f"DEBUG: Erro ao criar instância da API: {error}")
            return jsonify({'success': False, 'message': f'Erro ao conectar: {error}'}), 400
        
        # Salvar informações na sessão
        session['logged_in'] = True
        session['email'] = email
        session['account_type'] = account_type
        
        print(f"DEBUG: Login bem-sucedido. Session: {dict(session)}")
        print(f"DEBUG: api_instances keys após login: {list(api_instances.keys())}")
        
        # Obter saldo inicial
        try:
            balance = api.get_balance()
            session['initial_balance'] = balance
        except Exception as e:
            print(f"Erro ao obter saldo: {e}")
            session['initial_balance'] = 0
        
        # Forçar salvamento da sessão
        session.permanent = True
        
        return jsonify({
            'success': True,
            'message': 'Login realizado com sucesso',
            'balance': session['initial_balance']
        })
    except Exception as e:
        print(f"Erro no login: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500


@app.route('/logout', methods=['POST'])
def logout():
    """Endpoint de logout."""
    api = get_api_instance()
    if api:
        try:
            api.logout()
        except:
            pass
    
    session_id = session.get('session_id')
    if session_id in api_instances:
        del api_instances[session_id]
    if session_id in stop_loss_protections:
        del stop_loss_protections[session_id]
    
    session.clear()
    return jsonify({'success': True, 'message': 'Logout realizado com sucesso'})


@app.route('/dashboard')
def dashboard():
    """Dashboard principal."""
    print(f"DEBUG: Acessando dashboard. Session: {dict(session)}")
    
    if 'logged_in' not in session or not session.get('logged_in'):
        print("DEBUG: Usuário não está logado, redirecionando para index")
        return redirect(url_for('index'))
    
    # Verificar se session_id existe
    session_id = session.get('session_id')
    if not session_id:
        print("DEBUG: session_id não encontrado na sessão")
        session.clear()
        return redirect(url_for('index'))
    
    print(f"DEBUG: session_id encontrado: {session_id}")
    print(f"DEBUG: api_instances keys: {list(api_instances.keys())}")
    
    api = get_api_instance()
    if not api:
        print("DEBUG: Instância da API não encontrada")
        # Se não há instância da API, mas usuário está logado, limpar sessão e redirecionar
        # Isso pode acontecer se o servidor foi reiniciado
        session.clear()
        return redirect(url_for('index'))
    
    try:
        balance = api.get_balance()
        account_type = session.get('account_type', 'PRACTICE')
        initial_balance = session.get('initial_balance', balance)
        
        # Calcular variação
        variation = balance - initial_balance
        variation_percent = (variation / initial_balance * 100) if initial_balance > 0 else 0
        
        print(f"DEBUG: Dashboard renderizado com sucesso. Balance: {balance}")
        return render_template('dashboard.html', 
                             balance=balance,
                             initial_balance=initial_balance,
                             variation=variation,
                             variation_percent=variation_percent,
                             account_type=account_type)
    except Exception as e:
        print(f"DEBUG: Erro ao renderizar dashboard: {e}")
        import traceback
        traceback.print_exc()
        return render_template('error.html', error=str(e))


@app.route('/api/balance')
def api_balance():
    """API para obter saldo atual."""
    api = get_api_instance()
    if not api:
        return jsonify({'error': 'Não autenticado'}), 401
    
    try:
        balance = api.get_balance()
        initial_balance = session.get('initial_balance', balance)
        variation = balance - initial_balance
        variation_percent = (variation / initial_balance * 100) if initial_balance > 0 else 0
        
        # Verificar stop loss se estiver ativo
        session_id = session.get('session_id')
        stop_loss_status = None
        if session_id in stop_loss_protections:
            sl = stop_loss_protections[session_id]
            sl.update_balance(balance)
            stop_loss_status = sl.get_status()
        
        return jsonify({
            'balance': balance,
            'initial_balance': initial_balance,
            'variation': variation,
            'variation_percent': variation_percent,
            'stop_loss': stop_loss_status
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/config')
def config():
    """Página de configuração."""
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('index'))
    
    try:
        stop_loss = resolve_numeric_setting('stop_loss', 'IQ_OPTION_STOP_LOSS', 5.0, 'Stop Loss')
        stop_win = resolve_numeric_setting('stop_win', 'IQ_OPTION_STOP_WIN', 100.0, 'Stop Win')
        entry_type = session.get('entry_type', os.getenv('IQ_OPTION_ENTRY_TYPE', 'PERCENT'))
        entry_value = resolve_numeric_setting('entry_value', 'IQ_OPTION_ENTRY_VALUE', 1.0, 'Valor da entrada')
        gale = resolve_numeric_setting('gale', 'IQ_OPTION_GALE', 0, 'Gale', parser=parse_int_value)
    except ValueError as e:
        return render_template('error.html', error=str(e))
    
    return render_template('config.html',
                         stop_loss=stop_loss,
                         stop_win=stop_win,
                         entry_type=entry_type,
                         entry_value=entry_value,
                         gale=gale)


@app.route('/api/config', methods=['POST'])
def api_config():
    """API para salvar configurações."""
    if 'logged_in' not in session or not session['logged_in']:
        return jsonify({'error': 'Não autenticado'}), 401
    
    data = request.json
    stop_loss = float(data.get('stop_loss', 5))
    stop_win = float(data.get('stop_win', 100))
    entry_type = data.get('entry_type', 'PERCENT')
    entry_value = float(data.get('entry_value', 1))
    gale = int(data.get('gale', 0))
    
    # Validar
    if stop_loss <= 0 or stop_loss >= 100:
        return jsonify({'error': 'Stop Loss deve estar entre 0% e 100%'}), 400
    
    if gale not in [0, 1, 2]:
        return jsonify({'error': 'Gale deve ser 0, 1 ou 2'}), 400
    
    # Salvar na sessão
    session['stop_loss'] = stop_loss
    session['stop_win'] = stop_win
    session['entry_type'] = entry_type
    session['entry_value'] = entry_value
    session['gale'] = gale
    
    # Tentar salvar no .env também
    try:
        env_path = os.path.join(current_dir, '.env')
        env_lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                env_lines = [line for line in f if not line.strip().startswith(('IQ_OPTION_STOP_LOSS', 'IQ_OPTION_STOP_WIN', 'IQ_OPTION_ENTRY_TYPE', 'IQ_OPTION_ENTRY_VALUE', 'IQ_OPTION_GALE'))]
        
        env_lines.append(f'IQ_OPTION_STOP_LOSS={stop_loss}\n')
        env_lines.append(f'IQ_OPTION_STOP_WIN={stop_win}\n')
        env_lines.append(f'IQ_OPTION_ENTRY_TYPE={entry_type}\n')
        env_lines.append(f'IQ_OPTION_ENTRY_VALUE={entry_value}\n')
        env_lines.append(f'IQ_OPTION_GALE={gale}\n')
        
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(env_lines)
    except Exception as e:
        print(f"Erro ao salvar .env: {e}")
    
    return jsonify({'success': True, 'message': 'Configurações salvas com sucesso'})


@app.route('/stop-loss')
def stop_loss_page():
    """Página de gerenciamento de Stop Loss."""
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('index'))
    
    api = get_api_instance()
    if not api:
        return redirect(url_for('index'))
    
    try:
        stop_loss_percent = resolve_numeric_setting('stop_loss', 'IQ_OPTION_STOP_LOSS', 5.0, 'Stop Loss')
    except ValueError as e:
        return render_template('error.html', error=str(e))
    
    # Criar ou obter proteção de stop loss
    session_id = session.get('session_id')
    if session_id not in stop_loss_protections:
        try:
            initial_balance = session.get('initial_balance', api.get_balance())
            protection = create_stop_loss_protection(api, stop_loss_percent)
            if protection:
                protection.start_monitoring()
                stop_loss_protections[session_id] = protection
        except Exception as e:
            return render_template('error.html', error=f"Erro ao criar proteção: {e}")
    
    protection = stop_loss_protections.get(session_id)
    status = protection.get_status() if protection else None
    
    return render_template('stop_loss.html', status=status, stop_loss_percent=stop_loss_percent)


@app.route('/api/stop-loss/status')
def api_stop_loss_status():
    """API para obter status do Stop Loss."""
    if 'logged_in' not in session or not session['logged_in']:
        return jsonify({'error': 'Não autenticado'}), 401
    
    session_id = session.get('session_id')
    if session_id not in stop_loss_protections:
        return jsonify({'error': 'Stop Loss não inicializado'}), 400
    
    protection = stop_loss_protections[session_id]
    api = get_api_instance()
    
    if api:
        try:
            balance = api.get_balance()
            protection.update_balance(balance)
        except:
            pass
    
    return jsonify(protection.get_status())


@app.route('/sinais')
def sinais_page():
    """Página de gerenciamento de sinais."""
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('index'))
    
    sinais_file = os.path.join(current_dir, 'sinais.txt')
    processor = SinaisProcessor(sinais_file)
    
    sinais = []
    erros = []
    if os.path.exists(sinais_file):
        processor.carregar_sinais()
        sinais = processor.obter_todos_sinais()
        erros = processor.get_erros()
    
    return render_template('sinais.html', sinais=sinais, erros=erros)


@app.route('/api/sinais', methods=['GET', 'POST'])
def api_sinais():
    """API para gerenciar sinais."""
    if 'logged_in' not in session or not session['logged_in']:
        return jsonify({'error': 'Não autenticado'}), 401
    
    sinais_file = os.path.join(current_dir, 'sinais.txt')
    
    if request.method == 'GET':
        processor = SinaisProcessor(sinais_file)
        if os.path.exists(sinais_file):
            processor.carregar_sinais()
            sinais = processor.obter_todos_sinais()
            erros = processor.get_erros()
            return jsonify({
                'sinais': [{
                    'timeframe': s.timeframe,
                    'ativo': s.ativo,
                    'hora': s.hora,
                    'direcao': s.direcao,
                    'linha': s.linha_original
                } for s in sinais],
                'erros': erros
            })
        return jsonify({'sinais': [], 'erros': []})
    
    elif request.method == 'POST':
        data = request.json
        action = data.get('action')
        
        if action == 'save':
            content = data.get('content', '')
            try:
                with open(sinais_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                return jsonify({'success': True, 'message': 'Sinais salvos com sucesso'})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        elif action == 'add':
            sinal = data.get('sinal')
            try:
                with open(sinais_file, 'a', encoding='utf-8') as f:
                    f.write(f"{sinal['timeframe']};{sinal['ativo']};{sinal['hora']};{sinal['direcao']}\n")
                return jsonify({'success': True, 'message': 'Sinal adicionado com sucesso'})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        elif action == 'delete':
            index = data.get('index')
            try:
                processor = SinaisProcessor(sinais_file)
                if os.path.exists(sinais_file):
                    processor.carregar_sinais()
                    sinais = processor.obter_todos_sinais()
                    
                    if 0 <= index < len(sinais):
                        # Remover o sinal do índice especificado
                        sinais.pop(index)
                        
                        # Reescrever o arquivo sem o sinal removido
                        with open(sinais_file, 'w', encoding='utf-8') as f:
                            for s in sinais:
                                f.write(f"{s.timeframe};{s.ativo};{s.hora};{s.direcao}\n")
                        
                        return jsonify({'success': True, 'message': 'Sinal removido com sucesso'})
                    else:
                        return jsonify({'success': False, 'error': 'Índice inválido'}), 400
                else:
                    return jsonify({'success': False, 'error': 'Arquivo de sinais não encontrado'}), 404
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        return jsonify({'success': False, 'error': 'Ação inválida'}), 400


@app.route('/api/sinais/upload', methods=['POST'])
def api_upload_sinais():
    """API para fazer upload de arquivo de sinais."""
    if 'logged_in' not in session or not session['logged_in']:
        return jsonify({'error': 'Não autenticado'}), 401
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Nenhum arquivo selecionado'}), 400
    
    if not file.filename.endswith('.txt'):
        return jsonify({'success': False, 'error': 'Apenas arquivos .txt são permitidos'}), 400
    
    sinais_file = os.path.join(current_dir, 'sinais.txt')
    
    try:
        # Salvar o arquivo enviado
        file.save(sinais_file)
        
        # Validar o arquivo usando SinaisProcessor
        processor = SinaisProcessor(sinais_file)
        processor.carregar_sinais()
        
        # Verificar se há erros críticos
        if processor.get_erros():
            # Ainda assim salvar o arquivo, mas avisar sobre erros
            return jsonify({
                'success': True,
                'message': 'Arquivo enviado com sucesso, mas alguns erros foram encontrados',
                'errors': processor.get_erros()
            })
        
        return jsonify({
            'success': True,
            'message': 'Arquivo enviado e validado com sucesso',
            'sinais_count': len(processor.obter_todos_sinais())
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro ao processar arquivo: {str(e)}'}), 500


@app.route('/trading')
def trading_page():
    """Página de trading."""
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('index'))
    
    api = get_api_instance()
    if not api:
        return redirect(url_for('index'))
    
    return render_template('trading.html')


@app.route('/api/trade', methods=['POST'])
def api_trade():
    """API para executar trades."""
    if 'logged_in' not in session or not session['logged_in']:
        return jsonify({'error': 'Não autenticado'}), 401
    
    api = get_api_instance()
    if not api:
        return jsonify({'error': 'API não disponível'}), 400
    
    data = request.json
    asset = data.get('asset', '')
    direction = data.get('direction', 'call').lower()
    amount = parse_float_value(data.get('amount', 0), default=0.0, field_name='Valor da operação')
    expiry = int(data.get('expiry', 5))  # minutos
    is_martingale = data.get('is_martingale', False)
    parent_trade_id = data.get('parent_trade_id', None)
    
    # Verificar stop loss
    session_id = session.get('session_id')
    if session_id in stop_loss_protections:
        protection = stop_loss_protections[session_id]
        if not protection.can_operate():
            return jsonify({'success': False, 'error': 'Stop Loss acionado! Operação bloqueada.'}), 400
    
    if amount <= 0:
        return jsonify({'success': False, 'error': 'Valor inválido'}), 400
    
    try:
        result, order_id = api.buy(amount, asset, direction, expiry)
        
        if result:
            # Atualizar saldo após operação
            balance = api.get_balance()
            if session_id in stop_loss_protections:
                stop_loss_protections[session_id].update_balance(balance)
            
            # Adicionar ao histórico
            if session_id not in trade_history:
                trade_history[session_id] = []
            
            trade_entry = {
                'id': order_id,
                'asset': asset.upper(),
                'direction': direction.upper(),
                'amount': amount,
                'expiry': expiry,
                'timestamp': datetime.now().isoformat(),
                'status': 'pending',  # pending, win, loss
                'profit': 0,
                'is_martingale': is_martingale,
                'martingale_level': 0,
                'parent_trade_id': parent_trade_id,
                'sinal': None  # Para operações de sinais
            }
            
            # Se for martingale, calcular o nível
            if is_martingale and parent_trade_id:
                parent_trade = next((t for t in trade_history[session_id] if t['id'] == parent_trade_id), None)
                if parent_trade:
                    trade_entry['martingale_level'] = parent_trade.get('martingale_level', 0) + 1
            
            trade_history[session_id].insert(0, trade_entry)
            
            # Limitar histórico a 50 operações
            if len(trade_history[session_id]) > 50:
                trade_history[session_id] = trade_history[session_id][:50]
            
            # Capturar configurações antes de criar thread
            gale_level = int(os.getenv('IQ_OPTION_GALE', session.get('gale', 0)))
            
            # Iniciar verificação de resultado em background
            import threading
            def check_result():
                time.sleep(expiry * 60 + 5)  # Aguardar expiração + 5 segundos
                try:
                    win, profit = api.check_win_v4(order_id)
                    trade_updated = None
                    
                    # Atualizar histórico
                    for trade in trade_history.get(session_id, []):
                        if trade['id'] == order_id:
                            if win == "win":
                                trade['status'] = 'win'
                                trade['profit'] = float(profit) if profit else 0
                            elif win == "loose":
                                trade['status'] = 'loss'
                                trade['profit'] = float(profit) if profit else 0
                            else:
                                trade['status'] = 'equal'
                            
                            trade_updated = trade
                            break
                    
                    # Aplicar Martingale automático se configurado
                    if trade_updated and trade_updated['status'] == 'loss' and gale_level > 0:
                        # Verificar se ainda pode fazer retry
                        current_martingale_level = trade_updated.get('martingale_level', 0)
                        
                        if current_martingale_level < gale_level:
                            # Encontrar o trade original (não martingale) para calcular valor base
                            original_trade_id = trade_updated.get('parent_trade_id') or trade_updated['id']
                            
                            # Buscar trade original
                            original_trade = None
                            for t in trade_history.get(session_id, []):
                                if t['id'] == original_trade_id:
                                    original_trade = t
                                    break
                            
                            if not original_trade:
                                original_trade = trade_updated
                            
                            # Calcular valor do Martingale (último valor × 2.15)
                            martingale_amount = trade_updated['amount'] * 2.15
                            
                            # Executar Martingale automaticamente
                            try:
                                new_result, new_order_id = api.buy(
                                    martingale_amount,
                                    trade_updated['asset'],
                                    trade_updated['direction'].lower(),
                                    trade_updated['expiry']
                                )
                                
                                if new_result:
                                    # Atualizar saldo
                                    balance = api.get_balance()
                                    if session_id in stop_loss_protections:
                                        stop_loss_protections[session_id].update_balance(balance)
                                    
                                    # Adicionar novo trade ao histórico
                                    new_trade_entry = {
                                        'id': new_order_id,
                                        'asset': trade_updated['asset'],
                                        'direction': trade_updated['direction'],
                                        'amount': martingale_amount,
                                        'expiry': trade_updated['expiry'],
                                        'timestamp': datetime.now().isoformat(),
                                        'status': 'pending',
                                        'profit': 0,
                                        'is_martingale': True,
                                        'martingale_level': current_martingale_level + 1,
                                        'parent_trade_id': original_trade['id'],
                                        'sinal': trade_updated.get('sinal')
                                    }
                                    
                                    trade_history[session_id].insert(0, new_trade_entry)
                                    
                                    # Limitar histórico
                                    if len(trade_history[session_id]) > 50:
                                        trade_history[session_id] = trade_history[session_id][:50]
                                    
                                    # Verificar resultado do novo trade também
                                    def check_martingale_result():
                                        time.sleep(new_trade_entry['expiry'] * 60 + 5)
                                        try:
                                            win, profit = api.check_win_v4(new_order_id)
                                            trade_to_update = None
                                            
                                            for trade in trade_history.get(session_id, []):
                                                if trade['id'] == new_order_id:
                                                    if win == "win":
                                                        trade['status'] = 'win'
                                                        trade['profit'] = float(profit) if profit else 0
                                                    elif win == "loose":
                                                        trade['status'] = 'loss'
                                                        trade['profit'] = float(profit) if profit else 0
                                                    else:
                                                        trade['status'] = 'equal'
                                                    
                                                    trade_to_update = trade
                                                    break
                                            
                                            # Verificar se pode fazer mais um retry (Gale 2)
                                            if trade_to_update and trade_to_update['status'] == 'loss':
                                                if trade_to_update['martingale_level'] < gale_level:
                                                    # Calcular próximo valor
                                                    martingale_amount2 = trade_to_update['amount'] * 2.15
                                                    
                                                    # Executar mais um Martingale
                                                    try:
                                                        new_result2, new_order_id2 = api.buy(
                                                            martingale_amount2,
                                                            trade_to_update['asset'],
                                                            trade_to_update['direction'].lower(),
                                                            trade_to_update['expiry']
                                                        )
                                                        
                                                        if new_result2:
                                                            balance = api.get_balance()
                                                            if session_id in stop_loss_protections:
                                                                stop_loss_protections[session_id].update_balance(balance)
                                                            
                                                            new_trade_entry2 = {
                                                                'id': new_order_id2,
                                                                'asset': trade_to_update['asset'],
                                                                'direction': trade_to_update['direction'],
                                                                'amount': martingale_amount2,
                                                                'expiry': trade_to_update['expiry'],
                                                                'timestamp': datetime.now().isoformat(),
                                                                'status': 'pending',
                                                                'profit': 0,
                                                                'is_martingale': True,
                                                                'martingale_level': trade_to_update['martingale_level'] + 1,
                                                                'parent_trade_id': original_trade['id'],
                                                                'sinal': trade_to_update.get('sinal')
                                                            }
                                                            
                                                            trade_history[session_id].insert(0, new_trade_entry2)
                                                            
                                                            if len(trade_history[session_id]) > 50:
                                                                trade_history[session_id] = trade_history[session_id][:50]
                                                            
                                                            # Verificar resultado final (último nível)
                                                            def check_final_result():
                                                                time.sleep(new_trade_entry2['expiry'] * 60 + 5)
                                                                try:
                                                                    win, profit = api.check_win_v4(new_order_id2)
                                                                    for trade in trade_history.get(session_id, []):
                                                                        if trade['id'] == new_order_id2:
                                                                            if win == "win":
                                                                                trade['status'] = 'win'
                                                                                trade['profit'] = float(profit) if profit else 0
                                                                            elif win == "loose":
                                                                                trade['status'] = 'loss'
                                                                                trade['profit'] = float(profit) if profit else 0
                                                                            else:
                                                                                trade['status'] = 'equal'
                                                                            break
                                                                except:
                                                                    pass
                                                            
                                                            final_thread = threading.Thread(target=check_final_result, daemon=True)
                                                            final_thread.start()
                                                    except Exception as e:
                                                        print(f"Erro ao executar segundo Martingale: {e}")
                                        except:
                                            pass
                                    
                                    martingale_thread = threading.Thread(target=check_martingale_result, daemon=True)
                                    martingale_thread.start()
                            except Exception as e:
                                print(f"Erro ao executar Martingale automático: {e}")
                except:
                    pass
            
            thread = threading.Thread(target=check_result, daemon=True)
            thread.start()
            
            return jsonify({
                'success': True,
                'message': 'Operação executada com sucesso',
                'order_id': order_id,
                'balance': balance,
                'trade': trade_entry
            })
        else:
            return jsonify({'success': False, 'error': 'Falha ao executar operação'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/config', methods=['GET'])
def api_get_config():
    """API para obter configurações atuais."""
    if 'logged_in' not in session or not session.get('logged_in'):
        return jsonify({'error': 'Não autenticado'}), 401
    
    try:
        stop_loss = resolve_numeric_setting('stop_loss', 'IQ_OPTION_STOP_LOSS', 5.0, 'Stop Loss')
        stop_win = resolve_numeric_setting('stop_win', 'IQ_OPTION_STOP_WIN', 100.0, 'Stop Win')
        entry_type = session.get('entry_type', os.getenv('IQ_OPTION_ENTRY_TYPE', 'PERCENT'))
        entry_value = resolve_numeric_setting('entry_value', 'IQ_OPTION_ENTRY_VALUE', 1.0, 'Valor da entrada')
        gale = resolve_numeric_setting('gale', 'IQ_OPTION_GALE', 0, 'Gale', parser=parse_int_value)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
    return jsonify({
        'stop_loss': stop_loss,
        'stop_win': stop_win,
        'entry_type': entry_type,
        'entry_value': entry_value,
        'gale': gale
    })


# Variável global para gerenciar execução de sinais
sinais_execution = {
    'running': False,
    'thread': None,
    'processed': 0,
    'executed': 0,
    'next_sinal': None
}


@app.route('/api/sinais/executar', methods=['POST'])
def api_executar_sinais():
    """API para iniciar execução de sinais."""
    if 'logged_in' not in session or not session.get('logged_in'):
        return jsonify({'error': 'Não autenticado'}), 401
    
    if sinais_execution['running']:
        return jsonify({'success': False, 'error': 'Execução de sinais já está em andamento'}), 400
    
    api = get_api_instance()
    if not api:
        return jsonify({'success': False, 'error': 'API não disponível'}), 400
    
    # Importar threading para executar em background
    import threading
    
    # Obter valores da sessão ANTES de criar a thread
    session_id = session.get('session_id')
    entry_type = session.get('entry_type', os.getenv('IQ_OPTION_ENTRY_TYPE', 'PERCENT'))

    try:
        entry_value = resolve_numeric_setting('entry_value', 'IQ_OPTION_ENTRY_VALUE', 1.0, 'Valor da entrada')
        stop_loss_percent = resolve_numeric_setting('stop_loss', 'IQ_OPTION_STOP_LOSS', 5.0, 'Stop Loss')
        gale_level = resolve_numeric_setting('gale', 'IQ_OPTION_GALE', 0, 'Gale', parser=parse_int_value)
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    
    def executar_sinais_thread():
        try:
            sinais_execution['running'] = True
            sinais_execution['processed'] = 0
            sinais_execution['executed'] = 0
            
            # Carregar sinais
            sinais_file = os.path.join(current_dir, 'sinais.txt')
            processor = SinaisProcessor(sinais_file)
            
            if not os.path.exists(sinais_file):
                sinais_execution['running'] = False
                return
            
            if not processor.carregar_sinais():
                sinais_execution['running'] = False
                return
            
            sinais = processor.obter_todos_sinais()
            
            # Criar proteção de stop loss se não existir
            if session_id not in stop_loss_protections:
                protection = create_stop_loss_protection(api, stop_loss_percent)
                if protection:
                    protection.start_monitoring()
                    stop_loss_protections[session_id] = protection
            
            protection = stop_loss_protections.get(session_id)
            
            # Variáveis para controle de execução
            ultima_execucao_hora = None
            ultima_recarga_sinais = datetime.now()
            sinais_executados_hora = set()  # Para evitar execuções duplicadas na mesma hora
            ultimo_minuto_verificado = None
            
            # Resetar contador de perdas consecutivas ao iniciar execução
            if session_id not in losses_consecutivas:
                losses_consecutivas[session_id] = {'count': 0, 'skip_count': 0}
            else:
                # Manter skip_count se houver, mas resetar count (opcional)
                # losses_consecutivas[session_id]['count'] = 0
                pass
            
            add_sinais_log(session_id, f"Execução iniciada às {datetime.now().strftime('%H:%M:%S')}", 'info')
            
            # Loop de execução (simplificado - em produção use o código completo do executar_sinais.py)
            while sinais_execution['running']:
                hora_atual = datetime.now()
                hora_str = hora_atual.strftime("%H:%M")
                minuto_atual = hora_atual.minute
                segundo = hora_atual.second
                
                # Recarregar sinais a cada minuto para pegar atualizações do arquivo
                if (datetime.now() - ultima_recarga_sinais).total_seconds() >= 60:
                    try:
                        processor.carregar_sinais()
                        ultima_recarga_sinais = datetime.now()
                        # Resetar controles para permitir nova verificação
                        sinais_executados_hora = set()
                        ultimo_minuto_verificado = None  # Resetar para permitir verificação do minuto atual
                        # Log de sinais recarregados removido (não exibir)
                        pass
                    except Exception as e:
                        add_sinais_log(session_id, f"Erro ao recarregar sinais: {e}", 'error')
                
                # Verificar stop loss
                if protection and not protection.can_operate():
                    add_sinais_log(session_id, "Stop Loss acionado - parando execução", 'warning')
                    sinais_execution['running'] = False
                    break
                
                # Verificar flag antes de processar sinais
                if not sinais_execution['running']:
                    break
                
                # Verificar se mudou de minuto para processar sinais
                # Sempre verificar quando o minuto muda, mas executar apenas na janela segura (58s-02s)
                if ultimo_minuto_verificado != minuto_atual:
                    ultimo_minuto_verificado = minuto_atual
                    sinais_agora = processor.obter_sinais_para_hora(hora_atual)
                    
                    if sinais_agora:
                        # Verificar flag antes de processar sinais encontrados
                        if not sinais_execution['running']:
                            break
                        
                        hora_atual_key = hora_str
                        
                        # Verificar se já executou sinais nesta hora
                        if hora_atual_key not in sinais_executados_hora:
                            # Executar sinais apenas na janela segura (58s a 02s do próximo minuto)
                            # Isso garante que executamos no momento certo, mesmo com pequenos atrasos
                            if segundo >= 58 or segundo <= 2:
                                ultima_execucao_hora = hora_str
                                sinais_executados_hora.add(hora_atual_key)
                                
                                add_sinais_log(session_id, f"{len(sinais_agora)} sinal(is) encontrado(s) para {hora_str} (segundo: {segundo})", 'info')
                                
                                for sinal in sinais_agora:
                                    # Verificar flag antes de processar cada sinal
                                    if not sinais_execution['running']:
                                        break
                                    
                                    # Verificar se deve pular sinais devido a perdas consecutivas
                                    if session_id in losses_consecutivas and losses_consecutivas[session_id]['skip_count'] > 0:
                                        losses_consecutivas[session_id]['skip_count'] -= 1
                                        restantes = losses_consecutivas[session_id]['skip_count']
                                        add_sinais_log(session_id, f"⏭️ Sinal pulado devido a perdas consecutivas: {sinal.timeframe};{sinal.ativo};{sinal.hora};{sinal.direcao} | Sinais restantes a pular: {restantes}", 'warning')
                                        
                                        if restantes == 0:
                                            add_sinais_log(session_id, "✅ Período de pular sinais finalizado. Retomando execução normal.", 'info')
                                        continue
                                    
                                    add_sinais_log(session_id, f"Executando sinal: {sinal.timeframe};{sinal.ativo};{sinal.hora};{sinal.direcao}", 'info')
                                    sinais_execution['processed'] += 1
                                    
                                    if protection and not protection.can_operate():
                                        break
                                    
                                    # Verificar flag novamente antes de continuar
                                    if not sinais_execution['running']:
                                        break
                                    
                                    # Calcular valor de entrada
                                    saldo_atual = api.get_balance()
                                    if entry_type == "PERCENT":
                                        valor_entrada = saldo_atual * (entry_value / 100.0)
                                    else:
                                        valor_entrada = entry_value
                                    
                                    if protection:
                                        if entry_type == "PERCENT":
                                            valor_entrada = protection.calculate_safe_entry_value(entry_percent=entry_value)
                                        else:
                                            valor_entrada = protection.calculate_safe_entry_value(entry_fixed=entry_value)
                                    
                                    # Verificar saldo antes de executar
                                    if saldo_atual < valor_entrada:
                                        add_sinais_log(session_id, f"Saldo insuficiente! Necessário: ${valor_entrada:.2f} | Disponível: ${saldo_atual:.2f}", 'error')
                                        continue
                                    
                                    # Converter timeframe
                                    try:
                                        minutos = int(sinal.timeframe[1:]) if sinal.timeframe.startswith('M') else int(sinal.timeframe[1:]) * 60
                                    except:
                                        add_sinais_log(session_id, f"Erro ao converter timeframe: {sinal.timeframe}", 'error')
                                        continue
                                    
                                    # Executar
                                    try:
                                        add_sinais_log(session_id, f"Tentando executar: {sinal.ativo} {sinal.direcao} | Valor: ${valor_entrada:.2f} | Expiração: {minutos}min | Saldo: ${saldo_atual:.2f}", 'info')
                                        resultado, order_id = api.buy(valor_entrada, sinal.ativo, sinal.direcao.lower(), minutos)
                                        
                                        if resultado:
                                            add_sinais_log(session_id, f"Sinal executado com sucesso! Order ID: {order_id} | {sinal.ativo} {sinal.direcao} | Valor: ${valor_entrada:.2f}", 'success')
                                            sinais_execution['executed'] += 1
                                            balance = api.get_balance()
                                            if protection:
                                                protection.update_balance(balance)
                                            
                                            # Adicionar ao histórico
                                            if session_id not in trade_history:
                                                trade_history[session_id] = []
                                            
                                            trade_entry = {
                                                'id': order_id,
                                                'asset': sinal.ativo,
                                                'direction': sinal.direcao,
                                                'amount': valor_entrada,
                                                'expiry': minutos,
                                                'timestamp': datetime.now().isoformat(),
                                                'status': 'pending',
                                                'profit': 0,
                                                'is_martingale': False,
                                                'martingale_level': 0,
                                                'parent_trade_id': None,
                                                'sinal': f"{sinal.timeframe};{sinal.ativo};{sinal.hora};{sinal.direcao}"
                                            }
                                            
                                            trade_history[session_id].insert(0, trade_entry)
                                            if len(trade_history[session_id]) > 50:
                                                trade_history[session_id] = trade_history[session_id][:50]
                                            
                                            # Verificar resultado após expiração
                                            def check_sinal_result():
                                                time.sleep(minutos * 60 + 5)
                                                try:
                                                    win, profit = api.check_win_v4(order_id)
                                                    trade_updated = None
                                                    
                                                    for trade in trade_history.get(session_id, []):
                                                        if trade['id'] == order_id:
                                                            if win == "win":
                                                                trade['status'] = 'win'
                                                                trade['profit'] = float(profit) if profit else 0
                                                            elif win == "loose":
                                                                trade['status'] = 'loss'
                                                                trade['profit'] = float(profit) if profit else 0
                                                            else:
                                                                trade['status'] = 'equal'
                                                            
                                                            trade_updated = trade
                                                            break
                                                    
                                                    # Verificar perdas consecutivas após resultado (fora do loop)
                                                    if trade_updated:
                                                        # Para Gale 0: verificar imediatamente
                                                        # Para Gale 1 e 2: só verificar se não vai ter Martingale
                                                        current_martingale_level = trade_updated.get('martingale_level', 0)
                                                        
                                                        if gale_level == 0:
                                                            # Sem Gale: verificar imediatamente após resultado
                                                            verificar_e_atualizar_perdas_consecutivas(session_id, trade_updated['id'], gale_level)
                                                        elif trade_updated['status'] != 'loss' or current_martingale_level >= gale_level:
                                                            # Gale 1 ou 2: só verificar se não vai ter mais Martingales
                                                            verificar_e_atualizar_perdas_consecutivas(session_id, trade_updated['id'], gale_level)
                                                        
                                                        # Aplicar Martingale automático se configurado
                                                        if trade_updated['status'] == 'loss' and gale_level > 0:
                                                            if current_martingale_level < gale_level:
                                                                original_trade_id = trade_updated.get('parent_trade_id') or trade_updated['id']
                                                                original_trade = None
                                                                
                                                                for t in trade_history.get(session_id, []):
                                                                    if t['id'] == original_trade_id:
                                                                        original_trade = t
                                                                        break
                                                                
                                                                if not original_trade:
                                                                    original_trade = trade_updated
                                                                
                                                                martingale_amount = trade_updated['amount'] * 2.15
                                                                
                                                                try:
                                                                    new_result, new_order_id = api.buy(
                                                                        martingale_amount,
                                                                        trade_updated['asset'],
                                                                        trade_updated['direction'].lower(),
                                                                        trade_updated['expiry']
                                                                    )
                                                                    
                                                                    if new_result:
                                                                        balance = api.get_balance()
                                                                        if protection:
                                                                            protection.update_balance(balance)
                                                                        
                                                                        new_trade_entry = {
                                                                            'id': new_order_id,
                                                                            'asset': trade_updated['asset'],
                                                                            'direction': trade_updated['direction'],
                                                                            'amount': martingale_amount,
                                                                            'expiry': trade_updated['expiry'],
                                                                            'timestamp': datetime.now().isoformat(),
                                                                            'status': 'pending',
                                                                            'profit': 0,
                                                                            'is_martingale': True,
                                                                            'martingale_level': current_martingale_level + 1,
                                                                            'parent_trade_id': original_trade['id'],
                                                                            'sinal': trade_updated.get('sinal')
                                                                        }
                                                                        
                                                                        trade_history[session_id].insert(0, new_trade_entry)
                                                                        if len(trade_history[session_id]) > 50:
                                                                            trade_history[session_id] = trade_history[session_id][:50]
                                                                        
                                                                        # Verificar resultado do Martingale
                                                                        def check_martingale_sinal():
                                                                            time.sleep(new_trade_entry['expiry'] * 60 + 5)
                                                                            try:
                                                                                win, profit = api.check_win_v4(new_order_id)
                                                                                trade_to_update = None
                                                                                
                                                                                for trade in trade_history.get(session_id, []):
                                                                                    if trade['id'] == new_order_id:
                                                                                        if win == "win":
                                                                                            trade['status'] = 'win'
                                                                                            trade['profit'] = float(profit) if profit else 0
                                                                                        elif win == "loose":
                                                                                            trade['status'] = 'loss'
                                                                                            trade['profit'] = float(profit) if profit else 0
                                                                                        else:
                                                                                            trade['status'] = 'equal'
                                                                                        
                                                                                        trade_to_update = trade
                                                                                        break
                                                                                
                                                                                # Verificar perdas consecutivas após resultado do primeiro Martingale (Gale 1 ou se não vai ter mais)
                                                                                if trade_to_update:
                                                                                    if gale_level == 1:
                                                                                        # Para Gale 1: verificar se não vai ter mais Martingales
                                                                                        if trade_to_update['martingale_level'] >= gale_level or trade_to_update['status'] != 'loss':
                                                                                            verificar_e_atualizar_perdas_consecutivas(session_id, original_trade['id'], gale_level)
                                                                                    elif gale_level == 2:
                                                                                        # Para Gale 2: verificar se não vai ter mais Martingales (se WIN ou se não vai ter segundo Martingale)
                                                                                        if trade_to_update['status'] != 'loss' or trade_to_update['martingale_level'] >= gale_level:
                                                                                            verificar_e_atualizar_perdas_consecutivas(session_id, original_trade['id'], gale_level)
                                                                                
                                                                                # Verificar se pode fazer mais um retry (Gale 2)
                                                                                if trade_to_update and trade_to_update['status'] == 'loss':
                                                                                    if trade_to_update['martingale_level'] < gale_level:
                                                                                        martingale_amount2 = trade_to_update['amount'] * 2.15
                                                                                        
                                                                                        try:
                                                                                            new_result2, new_order_id2 = api.buy(
                                                                                                martingale_amount2,
                                                                                                trade_to_update['asset'],
                                                                                                trade_to_update['direction'].lower(),
                                                                                                trade_to_update['expiry']
                                                                                            )
                                                                                            
                                                                                            if new_result2:
                                                                                                balance = api.get_balance()
                                                                                                if protection:
                                                                                                    protection.update_balance(balance)
                                                                                                
                                                                                                new_trade_entry2 = {
                                                                                                    'id': new_order_id2,
                                                                                                    'asset': trade_to_update['asset'],
                                                                                                    'direction': trade_to_update['direction'],
                                                                                                    'amount': martingale_amount2,
                                                                                                    'expiry': trade_to_update['expiry'],
                                                                                                    'timestamp': datetime.now().isoformat(),
                                                                                                    'status': 'pending',
                                                                                                    'profit': 0,
                                                                                                    'is_martingale': True,
                                                                                                    'martingale_level': trade_to_update['martingale_level'] + 1,
                                                                                                    'parent_trade_id': original_trade['id'],
                                                                                                    'sinal': trade_to_update.get('sinal')
                                                                                                }
                                                                                                
                                                                                                trade_history[session_id].insert(0, new_trade_entry2)
                                                                                                if len(trade_history[session_id]) > 50:
                                                                                                    trade_history[session_id] = trade_history[session_id][:50]
                                                                                                
                                                                                                # Verificar resultado final
                                                                                                def check_final_sinal():
                                                                                                    time.sleep(new_trade_entry2['expiry'] * 60 + 5)
                                                                                                    try:
                                                                                                        win, profit = api.check_win_v4(new_order_id2)
                                                                                                        for trade in trade_history.get(session_id, []):
                                                                                                            if trade['id'] == new_order_id2:
                                                                                                                if win == "win":
                                                                                                                    trade['status'] = 'win'
                                                                                                                    trade['profit'] = float(profit) if profit else 0
                                                                                                                elif win == "loose":
                                                                                                                    trade['status'] = 'loss'
                                                                                                                    trade['profit'] = float(profit) if profit else 0
                                                                                                                else:
                                                                                                                    trade['status'] = 'equal'
                                                                                                                break
                                                                                                        
                                                                                                        # Verificar perdas consecutivas após resultado do segundo Martingale (Gale 2)
                                                                                                        verificar_e_atualizar_perdas_consecutivas(session_id, original_trade['id'], gale_level)
                                                                                                    except:
                                                                                                        pass
                                                                                                
                                                                                                final_thread = threading.Thread(target=check_final_sinal, daemon=True)
                                                                                                final_thread.start()
                                                                                        except Exception as e:
                                                                                            add_sinais_log(session_id, f"Erro ao executar segundo Martingale de sinal: {e}", 'error')
                                                                            except Exception as e:
                                                                                add_sinais_log(session_id, f"Erro ao verificar resultado do primeiro Martingale: {e}", 'error')
                                                                        
                                                                        martingale_thread = threading.Thread(target=check_martingale_sinal, daemon=True)
                                                                        martingale_thread.start()
                                                                except Exception as e:
                                                                    add_sinais_log(session_id, f"Erro ao executar Martingale automático de sinal: {e}", 'error')
                                                except Exception as e:
                                                    add_sinais_log(session_id, f"Erro ao verificar resultado do sinal: {e}", 'error')
                                            
                                            thread_check = threading.Thread(target=check_sinal_result, daemon=True)
                                            thread_check.start()
                                        else:
                                            # Tentar obter mais informações sobre o erro
                                            error_msg = f"Falha ao executar sinal: {sinal.timeframe};{sinal.ativo};{sinal.hora};{sinal.direcao}"
                                            if order_id:
                                                error_msg += f" | Resposta da API: {order_id}"
                                            else:
                                                error_msg += " | A API retornou False (sem order_id)"
                                            
                                            # Verificar possíveis causas
                                            if saldo_atual < valor_entrada:
                                                error_msg += f" | Saldo insuficiente (${saldo_atual:.2f})"
                                            
                                            add_sinais_log(session_id, error_msg, 'error')
                                    except Exception as e:
                                        add_sinais_log(session_id, f"Erro ao executar sinal {sinal.timeframe};{sinal.ativo};{sinal.hora};{sinal.direcao}: {str(e)}", 'error')
                
                # Verificar flag antes de atualizar próximo sinal
                if not sinais_execution['running']:
                    break
                
                # Atualizar próximo sinal
                proximos = processor.obter_proximos_sinais(1)
                if proximos:
                    sinais_execution['next_sinal'] = f"{proximos[0].hora} - {proximos[0].ativo} ({proximos[0].direcao})"
                else:
                    sinais_execution['next_sinal'] = "Nenhum sinal futuro"
                
                # Sleep curto para permitir resposta rápida ao comando de parar
                # Dividir em pequenos intervalos para verificar a flag mais frequentemente
                for _ in range(10):  # 10 x 0.1s = 1s total
                    if not sinais_execution['running']:
                        break
                    time.sleep(0.1)
                
        except Exception as e:
            add_sinais_log(session_id, f"Erro na execução de sinais: {e}", 'error')
        finally:
            add_sinais_log(session_id, "Execução de sinais finalizada", 'info')
            sinais_execution['running'] = False
    
    thread = threading.Thread(target=executar_sinais_thread, daemon=True)
    thread.start()
    sinais_execution['thread'] = thread
    
    add_sinais_log(session_id, "Solicitação de início de execução recebida", 'info')
    
    return jsonify({'success': True, 'message': 'Execução de sinais iniciada'})


@app.route('/api/sinais/stop', methods=['POST'])
def api_stop_sinais():
    """API para parar execução de sinais."""
    if 'logged_in' not in session or not session.get('logged_in'):
        return jsonify({'error': 'Não autenticado'}), 401
    
    session_id = session.get('session_id')
    add_sinais_log(session_id, "Parando execução de sinais...", 'warning')
    sinais_execution['running'] = False
    return jsonify({'success': True, 'message': 'Execução de sinais parada'})


@app.route('/api/sinais/status', methods=['GET'])
def api_sinais_status():
    """API para obter status da execução de sinais."""
    if 'logged_in' not in session or not session.get('logged_in'):
        return jsonify({'error': 'Não autenticado'}), 401
    
    return jsonify({
        'running': sinais_execution['running'],
        'processed': sinais_execution['processed'],
        'executed': sinais_execution['executed'],
        'next_sinal': sinais_execution['next_sinal']
    })


@app.route('/api/sinais/logs', methods=['GET'])
def api_sinais_logs():
    """API para obter logs de execução de sinais."""
    if 'logged_in' not in session or not session.get('logged_in'):
        return jsonify({'error': 'Não autenticado'}), 401
    
    session_id = session.get('session_id')
    logs = sinais_logs.get(session_id, [])
    
    return jsonify({'logs': logs})


@app.route('/api/trade/history', methods=['GET'])
def api_trade_history():
    if 'logged_in' not in session or not session.get('logged_in'):
        return jsonify({'error': 'Não autenticado'}), 401
    
    session_id = session.get('session_id')
    history = trade_history.get(session_id, [])
    
    # Verificar resultados de trades pendentes
    api = get_api_instance()
    if api:
        import threading
        def update_pending_trades():
            for trade in history:
                if trade['status'] == 'pending':
                    try:
                        win, profit = api.check_win_v4(trade['id'])
                        if win == "win":
                            trade['status'] = 'win'
                            trade['profit'] = float(profit) if profit else 0
                        elif win == "loose":
                            trade['status'] = 'loss'
                            trade['profit'] = float(profit) if profit else 0
                        elif win:
                            trade['status'] = 'equal'
                    except:
                        pass
        
        # Executar em thread separada para não bloquear
        thread = threading.Thread(target=update_pending_trades, daemon=True)
        thread.start()
    
    return jsonify({'history': history})


@app.route('/api/trade/check', methods=['POST'])
def api_check_trade():
    """API para verificar resultado de um trade específico."""
    if 'logged_in' not in session or not session.get('logged_in'):
        return jsonify({'error': 'Não autenticado'}), 401
    
    data = request.json
    order_id = data.get('order_id')
    
    if not order_id:
        return jsonify({'error': 'order_id é obrigatório'}), 400
    
    api = get_api_instance()
    if not api:
        return jsonify({'error': 'API não disponível'}), 400
    
    try:
        win, profit = api.check_win_v4(order_id)
        
        session_id = session.get('session_id')
        # Atualizar histórico
        for trade in trade_history.get(session_id, []):
            if trade['id'] == order_id:
                if win == "win":
                    trade['status'] = 'win'
                    trade['profit'] = float(profit) if profit else 0
                elif win == "loose":
                    trade['status'] = 'loss'
                    trade['profit'] = float(profit) if profit else 0
                else:
                    trade['status'] = 'equal'
                
                return jsonify({
                    'success': True,
                    'status': trade['status'],
                    'profit': trade['profit'],
                    'win': win
                })
        
        return jsonify({'success': False, 'error': 'Trade não encontrado no histórico'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

