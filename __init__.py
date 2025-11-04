"""A python wrapper for IQ Option API."""

import logging

def _prepare_logging():
    """Prepare logger for module IQ Option API."""
    logger = logging.getLogger(__name__)
    #https://github.com/Lu-Yi-Hsun/iqoptionapi_private/issues/1
    #try to fix this problem
    #logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.NullHandler())

    websocket_logger = logging.getLogger("websocket")
    websocket_logger.setLevel(logging.DEBUG)
    websocket_logger.addHandler(logging.NullHandler())

_prepare_logging()

# Exportar a classe principal para uso simplificado
# Precisamos garantir que o módulo iqoptionapi possa ser encontrado antes de importar stable_api
# porque stable_api.py importa outros módulos de iqoptionapi
import sys
import os

# Obter diretório deste arquivo (iqoptionapi/)
_current_dir = os.path.dirname(os.path.abspath(__file__))
# Obter diretório pai (onde iqoptionapi está como diretório)
_parent_dir = os.path.dirname(_current_dir)

# CRÍTICO: Adicionar apenas o diretório pai ao path
# NÃO adicionar o diretório atual (_current_dir) para evitar conflito
# com o diretório local 'http/' que interfere no módulo padrão 'http' do Python
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)
# NÃO adicionar _current_dir ao path para evitar conflito com http/

# Função para importar IQ_Option dinamicamente
def _import_iq_option():
    """Importa IQ_Option usando diferentes métodos."""
    try:
        # Método 1: Importação relativa (quando instalado como pacote)
        from .stable_api import IQ_Option
        return IQ_Option
    except ImportError:
        try:
            # Método 2: Importação absoluta (quando diretório pai está no path)
            from iqoptionapi.stable_api import IQ_Option
            return IQ_Option
        except ImportError:
            try:
                # Método 3: Importação direta do arquivo (último recurso)
                if _current_dir not in sys.path:
                    sys.path.insert(0, _current_dir)
                from stable_api import IQ_Option
                return IQ_Option
            except ImportError:
                return None

# Tentar importar imediatamente
IQ_Option = _import_iq_option()

# Se falhou, criar uma classe proxy que importa quando chamada
if IQ_Option is None:
    class _IQ_Option_Proxy:
        """Proxy que tenta importar IQ_Option quando instanciado."""
        def __new__(cls, *args, **kwargs):
            # Tentar importar novamente
            import traceback
            try:
                IQ_Option = _import_iq_option()
                if IQ_Option is None:
                    # Capturar o último erro
                    try:
                        from iqoptionapi.stable_api import IQ_Option
                    except Exception as e:
                        error_msg = str(e)
                        raise ImportError(
                            f"Não foi possível importar IQ_Option.\n"
                            f"Erro: {error_msg}\n\n"
                            f"Soluções possíveis:\n"
                            f"1. Execute do diretório pai: cd .. && python iqoptionapi/examples/basic_trading.py\n"
                            f"2. Instale o pacote: pip install -e .\n"
                            f"3. Verifique se todas as dependências estão instaladas: pip install -r requirements.txt"
                        )
                    if IQ_Option is None:
                        raise ImportError("IQ_Option ainda é None após tentativas")
            except Exception as e:
                # Se o erro não for ImportError, relançar
                if not isinstance(e, ImportError):
                    raise
                # Mostrar traceback completo para debug
                import sys
                if hasattr(sys, '_getframe'):
                    raise type(e)(str(e) + "\n\nTraceback completo:\n" + "".join(traceback.format_exc()))
                raise
            
            # Substituir a classe proxy pela classe real no módulo
            import iqoptionapi
            iqoptionapi.IQ_Option = IQ_Option
            # Criar instância da classe real
            return IQ_Option(*args, **kwargs)
    
    IQ_Option = _IQ_Option_Proxy

__all__ = ['IQ_Option']
