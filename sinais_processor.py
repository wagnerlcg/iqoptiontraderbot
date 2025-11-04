"""
Processador de Sinais de Trading
Lê e processa sinais do arquivo sinais.txt

Formato esperado (4 campos separados por ponto e vírgula):
TIMEFRAME;ATIVO;HORA;DIREÇÃO

Exemplo:
M1;EURUSD-OTC;19:00;CALL
M5;EURUSD;14:30;PUT
"""

import os
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class Sinal:
    """Representa um sinal de trading."""
    timeframe: str  # Ex: M1, M5, M15
    ativo: str      # Ex: EURUSD, EURUSD-OTC
    hora: str      # Ex: 19:00
    direcao: str    # PUT ou CALL
    linha_original: int  # Número da linha no arquivo (para debug)
    
    def __str__(self):
        return f"{self.timeframe};{self.ativo};{self.hora};{self.direcao}"
    
    def __repr__(self):
        return f"Sinal(line={self.linha_original}, {self})"


class SinaisProcessor:
    """Processa arquivo de sinais e valida os dados."""
    
    def __init__(self, arquivo_sinais: str = "sinais.txt"):
        """
        Inicializa o processador de sinais.
        
        Args:
            arquivo_sinais: Caminho para o arquivo de sinais
        """
        self.arquivo_sinais = arquivo_sinais
        self.sinais: List[Sinal] = []
        self.erros: List[str] = []
    
    def carregar_sinais(self) -> bool:
        """
        Carrega e valida sinais do arquivo.
        
        Returns:
            bool: True se carregou com sucesso, False caso contrário
        """
        self.sinais = []
        self.erros = []
        
        if not os.path.exists(self.arquivo_sinais):
            self.erros.append(f"Arquivo '{self.arquivo_sinais}' nao encontrado!")
            return False
        
        try:
            with open(self.arquivo_sinais, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
        except Exception as e:
            self.erros.append(f"Erro ao ler arquivo: {e}")
            return False
        
        # Processar cada linha
        for num_linha, linha in enumerate(linhas, start=1):
            linha = linha.strip()
            
            # Ignorar linhas vazias e comentários
            if not linha or linha.startswith('#'):
                continue
            
            # Validar formato
            campos = linha.split(';')
            if len(campos) != 4:
                self.erros.append(f"Linha {num_linha}: Formato invalido. "
                                 f"Esperado: TIMEFRAME;ATIVO;HORA;DIREÇÃO. "
                                 f"Recebido: {linha}")
                continue
            
            timeframe, ativo, hora, direcao = [campo.strip() for campo in campos]
            
            # Validar campos
            erro_validacao = self._validar_sinal(timeframe, ativo, hora, direcao, num_linha)
            if erro_validacao:
                self.erros.append(erro_validacao)
                continue
            
            # Criar sinal válido
            sinal = Sinal(
                timeframe=timeframe.upper(),
                ativo=ativo.upper(),
                hora=hora,
                direcao=direcao.upper(),
                linha_original=num_linha
            )
            self.sinais.append(sinal)
        
        return len(self.sinais) > 0 or len(self.erros) == 0
    
    def _validar_sinal(self, timeframe: str, ativo: str, hora: str, direcao: str, num_linha: int) -> Optional[str]:
        """
        Valida os campos de um sinal.
        
        Returns:
            str: Mensagem de erro se inválido, None se válido
        """
        # Validar timeframe (deve começar com M e ter número)
        if not timeframe.upper().startswith('M'):
            return f"Linha {num_linha}: Timeframe invalido '{timeframe}'. Deve começar com 'M' (ex: M1, M5, M15)"
        
        try:
            tf_num = int(timeframe.upper()[1:])
            if tf_num <= 0:
                return f"Linha {num_linha}: Timeframe invalido '{timeframe}'. Numero deve ser maior que 0"
        except ValueError:
            return f"Linha {num_linha}: Timeframe invalido '{timeframe}'. Formato deve ser M<numero>"
        
        # Validar ativo (não pode estar vazio)
        if not ativo:
            return f"Linha {num_linha}: Ativo nao pode estar vazio"
        
        # Validar hora (formato HH:MM)
        try:
            hora_parts = hora.split(':')
            if len(hora_parts) != 2:
                raise ValueError
            h, m = int(hora_parts[0]), int(hora_parts[1])
            if h < 0 or h > 23 or m < 0 or m > 59:
                raise ValueError
        except (ValueError, IndexError):
            return f"Linha {num_linha}: Hora invalida '{hora}'. Formato esperado: HH:MM (ex: 19:00)"
        
        # Validar direção
        if direcao.upper() not in ['PUT', 'CALL']:
            return f"Linha {num_linha}: Direcao invalida '{direcao}'. Deve ser 'PUT' ou 'CALL'"
        
        return None  # Válido
    
    def obter_sinais_para_hora(self, hora_atual: Optional[datetime] = None) -> List[Sinal]:
        """
        Retorna sinais programados para a hora atual.
        
        Args:
            hora_atual: Hora atual (se None, usa hora do sistema)
            
        Returns:
            List[Sinal]: Lista de sinais para executar agora
        """
        if hora_atual is None:
            hora_atual = datetime.now()
        
        hora_str = hora_atual.strftime("%H:%M")
        sinais_agora = []
        
        for sinal in self.sinais:
            if sinal.hora == hora_str:
                sinais_agora.append(sinal)
        
        return sinais_agora
    
    def obter_proximos_sinais(self, quantidade: int = 5) -> List[Sinal]:
        """
        Retorna os próximos N sinais ordenados por hora.
        
        Args:
            quantidade: Quantidade de sinais a retornar
            
        Returns:
            List[Sinal]: Próximos sinais ordenados
        """
        hora_atual = datetime.now().strftime("%H:%M")
        
        # Filtrar sinais futuros
        sinais_futuros = []
        for sinal in self.sinais:
            if sinal.hora >= hora_atual:
                sinais_futuros.append(sinal)
        
        # Ordenar por hora
        sinais_futuros.sort(key=lambda x: x.hora)
        
        return sinais_futuros[:quantidade]
    
    def obter_todos_sinais(self) -> List[Sinal]:
        """Retorna todos os sinais carregados."""
        return self.sinais.copy()
    
    def get_erros(self) -> List[str]:
        """Retorna lista de erros encontrados durante o processamento."""
        return self.erros.copy()
    
    def criar_arquivo_exemplo(self) -> bool:
        """
        Cria um arquivo de exemplo com alguns sinais.
        
        Returns:
            bool: True se criado com sucesso
        """
        exemplo = """# Arquivo de Sinais - Formato
# Use apenas 4 campos separados por ponto e virgula:
# TIMEFRAME;ATIVO;HORA;DIREÇÃO
#
# Timeframes validos: M1, M5, M15, M30, H1, etc
# Direcoes validas: PUT ou CALL
# Formato de hora: HH:MM (ex: 19:00)

M1;EURUSD-OTC;19:00;CALL
M5;EURUSD;14:30;PUT
M1;GBPUSD-OTC;20:00;CALL
M5;EURUSD;15:45;PUT
"""
        try:
            with open(self.arquivo_sinais, 'w', encoding='utf-8') as f:
                f.write(exemplo)
            return True
        except Exception as e:
            self.erros.append(f"Erro ao criar arquivo exemplo: {e}")
            return False

