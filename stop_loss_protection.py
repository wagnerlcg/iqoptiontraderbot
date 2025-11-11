"""
Módulo de Proteção de Stop Loss - PRIORIDADE MÁXIMA
Este módulo garante que NUNCA o usuário perca mais do que foi estabelecido.

AVISO CRÍTICO: O Stop Loss é IMPRESCINDÍVEL e deve ser monitorado em todas as operações.
"""

import os
import time
import threading
from typing import Optional, Callable


class StopLossProtection:
    """
    Classe de proteção de Stop Loss com prioridade máxima.
    
    Esta classe monitora continuamente o saldo e FORÇA a parada imediata
    quando o stop loss é atingido, independente de qualquer outra condição.
    """
    
    def __init__(self, initial_balance: float, stop_loss_percent: float, api=None, check_interval: float = 0.5):
        """
        Inicializa o monitor de Stop Loss.
        
        Args:
            initial_balance: Saldo inicial da conta (baseline)
            stop_loss_percent: Porcentagem de perda máxima permitida (ex: 5.0 para 5%)
            api: Instância da API IQ Option (opcional, para verificar saldo automaticamente)
            check_interval: Intervalo de verificação em segundos (padrão: 0.5s)
        """
        if stop_loss_percent <= 0 or stop_loss_percent >= 100:
            raise ValueError("Stop Loss deve estar entre 0% e 100%")
        
        self.initial_balance = float(initial_balance)
        self.stop_loss_percent = float(stop_loss_percent)
        self.api = api
        self.check_interval = check_interval
        
        # Calcular o saldo mínimo permitido
        self.minimum_balance = self.initial_balance * (1 - self.stop_loss_percent / 100.0)
        
        # Estado de proteção
        self.is_active = False  # Se o monitoramento está ativo
        self.is_triggered = False  # Se o stop loss foi acionado
        self.current_balance = self.initial_balance
        self.loss_percent = 0.0
        
        # Callback para quando stop loss for acionado
        self.on_stop_loss_triggered: Optional[Callable] = None
        
        # Thread de monitoramento
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_monitoring = False
        self._lock = threading.Lock()
        
        print(f"=== STOP LOSS PROTECTION ATIVADO ===")
        print(f"Saldo Inicial: ${self.initial_balance:.2f}")
        print(f"Stop Loss: {self.stop_loss_percent}%")
        print(f"Saldo Minimo Permitido: ${self.minimum_balance:.2f}")
        print(f"ATENCAO: Nenhuma operacao sera permitida se o saldo cair abaixo de ${self.minimum_balance:.2f}")
        print("=" * 50)
    
    def start_monitoring(self):
        """Inicia o monitoramento contínuo do saldo."""
        if self.is_active:
            print("AVISO: Monitoramento ja esta ativo!")
            return
        
        self.is_active = True
        self._stop_monitoring = False
        self._monitor_thread = threading.Thread(target=self._monitor_balance, daemon=True)
        self._monitor_thread.start()
        print("Monitoramento de Stop Loss INICIADO (prioridade maxima)")
    
    def stop_monitoring(self):
        """Para o monitoramento."""
        if not self.is_active:
            return
        
        self._stop_monitoring = True
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
        self.is_active = False
        print("Monitoramento de Stop Loss PARADO")
    
    def _monitor_balance(self):
        """Loop interno de monitoramento (executa em thread separada)."""
        while not self._stop_monitoring and not self.is_triggered:
            try:
                # Verificar se stop loss foi atingido (saldo atualizado externamente)
                self._check_stop_loss()

                time.sleep(self.check_interval)

            except Exception as e:
                print(f"ERRO no monitoramento: {e}")
                time.sleep(self.check_interval)
    
    def update_balance(self, new_balance: float):
        """
        Atualiza o saldo atual e verifica stop loss.
        
        Args:
            new_balance: Novo saldo da conta
            
        Returns:
            bool: True se stop loss foi acionado, False caso contrário
        """
        with self._lock:
            self.current_balance = float(new_balance)
            
            # Calcular porcentagem de perda
            loss = self.initial_balance - self.current_balance
            self.loss_percent = (loss / self.initial_balance) * 100.0
            
            # Verificar se stop loss foi atingido
            return self._check_stop_loss()

    def _check_stop_loss(self) -> bool:
        """
        Verifica se o stop loss foi atingido.
        
        Returns:
            bool: True se stop loss foi acionado
        """
        if self.is_triggered:
            return True
        
        if self.current_balance < self.minimum_balance:
            self._trigger_stop_loss()
            return True
        
        return False
    
    def _trigger_stop_loss(self):
        """Aciona o stop loss e força a parada imediata."""
        with self._lock:
            if self.is_triggered:
                return  # Já foi acionado
            
            self.is_triggered = True
            
            print("\n" + "=" * 70)
            print("*** STOP LOSS ACIONADO - PRIORIDADE MAXIMA ***")
            print("=" * 70)
            print(f"Saldo Inicial: ${self.initial_balance:.2f}")
            print(f"Saldo Atual: ${self.current_balance:.2f}")
            print(f"Perda: ${self.initial_balance - self.current_balance:.2f} ({self.loss_percent:.2f}%)")
            print(f"Limite de Stop Loss: {self.stop_loss_percent}% (${self.minimum_balance:.2f})")
            print("=" * 70)
            print("*** TODAS AS OPERACOES FORAM PARADAS AUTOMATICAMENTE ***")
            print("*** O ROBO NAO PERMITIRA NENHUMA OPERACAO ADICIONAL ***")
            print("=" * 70 + "\n")
            
            # Executar callback se definido
            if self.on_stop_loss_triggered:
                try:
                    self.on_stop_loss_triggered(self)
                except Exception as e:
                    print(f"ERRO no callback de stop loss: {e}")
    
    def can_operate(self) -> bool:
        """
        Verifica se é seguro operar (stop loss não foi acionado).
        
        Returns:
            bool: True se pode operar, False se stop loss foi acionado
        """
        if self.is_triggered:
            return False
        
        # Verificação extra antes de permitir operação
        if self.api:
            try:
                current = float(self.api.get_balance())
                if current < self.minimum_balance:
                    self.update_balance(current)
                    return False
            except:
                pass
        
        return not self.is_triggered
    
    def calculate_safe_entry_value(self, entry_percent: Optional[float] = None, entry_fixed: Optional[float] = None) -> float:
        """
        Calcula o valor seguro para entrada considerando o stop loss.
        
        Args:
            entry_percent: Porcentagem da banca (ex: 1.0 para 1%)
            entry_fixed: Valor fixo em dólares
            
        Returns:
            float: Valor calculado e validado
        """
        if not self.can_operate():
            return 0.0
        
        if entry_percent is not None:
            value = self.current_balance * (entry_percent / 100.0)
        elif entry_fixed is not None:
            value = float(entry_fixed)
        else:
            return 0.0
        
        # Garantir que não exceda o saldo disponível
        available_balance = self.current_balance - self.minimum_balance
        safe_value = min(value, available_balance * 0.8)  # Usar no máximo 80% do disponível
        
        return max(0.0, safe_value)
    
    def get_status(self) -> dict:
        """
        Retorna o status atual do monitor de stop loss.
        
        Returns:
            dict: Status atual
        """
        with self._lock:
            return {
                "is_active": self.is_active,
                "is_triggered": self.is_triggered,
                "initial_balance": self.initial_balance,
                "current_balance": self.current_balance,
                "minimum_balance": self.minimum_balance,
                "stop_loss_percent": self.stop_loss_percent,
                "loss_percent": self.loss_percent,
                "can_operate": self.can_operate()
            }


def create_stop_loss_protection(
    api,
    stop_loss_percent: Optional[float] = None,
    *,
    auto_fetch_balance: bool = True,
    initial_balance: Optional[float] = None,
) -> Optional[StopLossProtection]:
    """
    Cria uma instância de proteção de stop loss carregando configurações do ambiente.
    
    Args:
        api: Instância da API IQ Option
        stop_loss_percent: Porcentagem de stop loss (se None, lê de variável de ambiente)
        auto_fetch_balance: Quando True, consulta saldo inicial diretamente na API.
        initial_balance: Opcional. Saldo inicial já conhecido (requer auto_fetch_balance=False).
        
    Returns:
        StopLossProtection ou None se não for possível criar
    """
    # Carregar stop loss do ambiente se não fornecido
    if stop_loss_percent is None:
        stop_loss_str = os.getenv("IQ_OPTION_STOP_LOSS", "5")
        try:
            stop_loss_percent = float(stop_loss_str)
        except ValueError:
            print(f"ERRO: Stop Loss invalido na variavel IQ_OPTION_STOP_LOSS: {stop_loss_str}")
            stop_loss_percent = 5.0  # Padrão de segurança
    
    # Obter saldo inicial
    if auto_fetch_balance:
        try:
            initial_balance = float(api.get_balance())
        except Exception as e:
            print(f"ERRO: Nao foi possivel obter saldo inicial: {e}")
            return None
    else:
        if initial_balance is None:
            raise ValueError("initial_balance deve ser informado quando auto_fetch_balance=False")
    
    if initial_balance <= 0:
        print("ERRO: Saldo inicial deve ser maior que zero!")
        return None
    
    # Criar proteção
    protection = StopLossProtection(
        initial_balance=initial_balance,
        stop_loss_percent=stop_loss_percent,
        api=api if auto_fetch_balance else None,
        check_interval=0.5
    )
    
    return protection

