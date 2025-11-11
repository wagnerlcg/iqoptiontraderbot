"""Camada de serviço independente de interface para o bot IQ Option.

Este módulo encapsula a lógica de negócio utilizada pela aplicação web (Flask)
e poderá ser reutilizado pela futura aplicação desktop. O objetivo é manter a
função-lógica (login, execução de sinais, controle de stop loss, histórico,
logs) desacoplada das camadas de apresentação.

Uso básico:

    service = BotService()
    service.load_config()  # carrega configurações do .env
    service.login(email, password, account_type="PRACTICE")
    service.start_signal_execution()  # executa com base nas configs atuais
    ...

Esta versão inicial foi extraída de `app.py` e mantém a maioria dos
comportamentos originais. Novas interfaces (web, desktop, CLI) devem apenas
instanciar `BotService` e orquestrar as chamadas públicas.
"""

from __future__ import annotations

import os
import sys
import time
import json
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Garantir que dependências internas possam ser importadas sem conflitos com
# o diretório local "http/". Reaproveita a lógica existente em app.py.
# ---------------------------------------------------------------------------

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)

if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

if CURRENT_DIR in sys.path:
    sys.path.remove(CURRENT_DIR)


import importlib.util

stop_loss_path = os.path.join(CURRENT_DIR, "stop_loss_protection.py")
spec_stop = importlib.util.spec_from_file_location("stop_loss_protection", stop_loss_path)
stop_loss_module = importlib.util.module_from_spec(spec_stop)
spec_stop.loader.exec_module(stop_loss_module)
create_stop_loss_protection = stop_loss_module.create_stop_loss_protection
StopLossProtection = stop_loss_module.StopLossProtection

sinais_processor_path = os.path.join(CURRENT_DIR, "sinais_processor.py")
spec_sinais = importlib.util.spec_from_file_location("sinais_processor", sinais_processor_path)
sinais_processor_module = importlib.util.module_from_spec(spec_sinais)
spec_sinais.loader.exec_module(sinais_processor_module)
SinaisProcessor = sinais_processor_module.SinaisProcessor
Sinal = sinais_processor_module.Sinal


# Importar IQ_Option com a mesma estratégia utilizada no app Flask
try:
    from iqoptionapi import IQ_Option  # type: ignore
except ImportError:
    stable_api_path = os.path.join(CURRENT_DIR, "stable_api.py")
    spec = importlib.util.spec_from_file_location("stable_api", stable_api_path)
    if spec and spec.loader:
        stable_api_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(stable_api_module)  # type: ignore[attr-defined]
        IQ_Option = stable_api_module.IQ_Option  # type: ignore[attr-defined]
    else:
        raise


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------


def parse_float_value(value: Any, default: Optional[float] = None, *, field_name: str = "valor") -> float:
    """Converte entradas em float, aceitando vírgula como separador decimal."""

    if value is None or (isinstance(value, str) and value.strip() == ""):
        if default is not None:
            return float(default)
        raise ValueError(f"{field_name} não informado")

    if isinstance(value, (int, float)):
        return float(value)

    value_str = str(value).strip().replace(",", ".")
    if value_str == "":
        if default is not None:
            return float(default)
        raise ValueError(f"{field_name} vazio")

    try:
        return float(value_str)
    except ValueError as exc:  # pragma: no cover - ajustado para robustez
        if default is not None:
            return float(default)
        raise ValueError(f"{field_name} inválido: {value}") from exc


def parse_int_value(value: Any, default: Optional[int] = None, *, field_name: str = "valor") -> int:
    """Converte entradas em int aceitando formatos com vírgula."""

    try:
        float_value = parse_float_value(value, default, field_name=field_name)
    except ValueError as exc:
        if default is not None:
            return int(default)
        raise exc

    try:
        return int(round(float(float_value)))
    except (TypeError, ValueError) as exc:
        if default is not None:
            return int(default)
        raise ValueError(f"{field_name} inválido: {value}") from exc


# ---------------------------------------------------------------------------
# Estruturas de dados
# ---------------------------------------------------------------------------


@dataclass
class TradeEntry:
    id: Any
    asset: str
    direction: str
    amount: float
    expiry: int
    timestamp: str
    status: str = "pending"
    profit: float = 0.0
    is_martingale: bool = False
    martingale_level: int = 0
    parent_trade_id: Optional[Any] = None
    sinal: Optional[str] = None


@dataclass
class LogEntry:
    timestamp: str
    message: str
    type: str = "info"  # info, success, warning, error


@dataclass
class BotConfig:
    stop_loss: float = 5.0
    stop_win: float = 100.0
    entry_type: str = "PERCENT"  # PERCENT ou FIXED
    entry_value: float = 1.0
    gale: int = 0
    account_type: str = "PRACTICE"


@dataclass
class BotStatus:
    running: bool
    processed_signals: int
    executed_signals: int
    next_signal: Optional[str]
    logs: List[LogEntry] = field(default_factory=list)
    trades: List[TradeEntry] = field(default_factory=list)
    balance: Optional[float] = None
    initial_balance: Optional[float] = None
    variation: Optional[float] = None
    variation_percent: Optional[float] = None
    stop_loss_status: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# Serviço principal
# ---------------------------------------------------------------------------


class ThreadSafeIQOption:
    """Wrapper que serializa chamadas à API original em múltiplas threads."""

    def __init__(self, api: IQ_Option) -> None:
        super().__setattr__("_api", api)
        super().__setattr__("_lock", threading.RLock())

    def __getattr__(self, name: str) -> Any:
        with self._lock:
            attr = getattr(self._api, name)
            if callable(attr):
                def _locked_call(*args: Any, **kwargs: Any) -> Any:
                    with self._lock:
                        return attr(*args, **kwargs)

                return _locked_call
            return attr

    def __setattr__(self, name: str, value: Any) -> None:
        if name in {"_api", "_lock"}:
            super().__setattr__(name, value)
        else:
            with self._lock:
                setattr(self._api, name, value)

    def run_locked(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        with self._lock:
            return func(*args, **kwargs)

    @property
    def raw(self) -> IQ_Option:
        return self._api


class BotService:
    """Gerencia ciclo de vida do bot IQ Option de forma independente de UI."""

    def __init__(self, base_dir: Optional[str] = None, env_path: Optional[str] = None) -> None:
        self.base_dir = base_dir or CURRENT_DIR
        self.env_path = env_path or os.path.join(self.base_dir, ".env")

        load_dotenv(self.env_path)

        self.config = BotConfig(
            stop_loss=parse_float_value(os.getenv("IQ_OPTION_STOP_LOSS"), default=5, field_name="Stop Loss"),
            stop_win=parse_float_value(os.getenv("IQ_OPTION_STOP_WIN"), default=100, field_name="Stop Win"),
            entry_type=os.getenv("IQ_OPTION_ENTRY_TYPE", "PERCENT").upper() or "PERCENT",
            entry_value=parse_float_value(os.getenv("IQ_OPTION_ENTRY_VALUE"), default=1, field_name="Valor da entrada"),
            gale=parse_int_value(os.getenv("IQ_OPTION_GALE"), default=0, field_name="Gale"),
        )

        self.email: Optional[str] = None
        self.password: Optional[str] = None
        self.api: Optional[ThreadSafeIQOption] = None
        self.stop_loss_protection: Optional[StopLossProtection] = None

        self.trade_history: List[TradeEntry] = []
        self.logs: List[LogEntry] = []
        self.processed_signals: int = 0
        self.executed_signals: int = 0
        self.next_signal: Optional[str] = None
        self.running: bool = False

        self.losses_state = {"count": 0, "skip_count": 0}

        self.initial_balance: Optional[float] = None
        self.last_balance: Optional[float] = None

        self._execution_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Registro de logs e histórico
    # ------------------------------------------------------------------

    def add_log(self, message: str, log_type: str = "info") -> None:
        entry = LogEntry(timestamp=datetime.now().isoformat(), message=message, type=log_type)
        self.logs.insert(0, entry)
        self.logs = self.logs[:100]
        print(f"[SINAIS] {message}")  # mantém comportamento para debug

    def _append_trade(self, trade: TradeEntry) -> None:
        self.trade_history.insert(0, trade)
        self.trade_history = self.trade_history[:50]

    # ------------------------------------------------------------------
    # Autenticação
    # ------------------------------------------------------------------

    def login(self, email: str, password: str, account_type: str = "PRACTICE") -> Tuple[bool, Optional[str]]:
        """Autentica e prepara a instância da API."""

        try:
            raw_api = IQ_Option(email, password, active_account_type=account_type)
            check, reason = raw_api.connect()

            if not check:
                error_message = self._parse_login_error(reason)
                return False, error_message

            raw_api.change_balance(account_type)
            api = ThreadSafeIQOption(raw_api)
            balance = float(api.get_balance())

            self.email = email
            self.password = password
            self.config.account_type = account_type
            self.api = api
            self.initial_balance = balance
            self.last_balance = balance

            self.stop_loss_protection = create_stop_loss_protection(
                api,
                self.config.stop_loss,
                auto_fetch_balance=False,
                initial_balance=balance,
            )
            self.add_log("Login realizado com sucesso", "success")
            return True, None

        except Exception as exc:  # pragma: no cover - comportamento original
            self.add_log(f"Erro ao conectar: {exc}", "error")
            return False, str(exc)

    def logout(self) -> None:
        if self.api:
            try:
                self.api.logout()
            except Exception:
                pass
        if self.stop_loss_protection:
            self.stop_loss_protection.stop_monitoring()
        self.api = None
        self.stop_loss_protection = None
        self.running = False
        self._stop_event.set()
        self.add_log("Sessão encerrada", "info")

    # ------------------------------------------------------------------
    # Configuração
    # ------------------------------------------------------------------

    def get_config(self) -> BotConfig:
        return self.config

    def update_config(self, **kwargs: Any) -> BotConfig:
        if "stop_loss" in kwargs:
            self.config.stop_loss = parse_float_value(kwargs["stop_loss"], field_name="Stop Loss")
        if "stop_win" in kwargs:
            self.config.stop_win = parse_float_value(kwargs["stop_win"], field_name="Stop Win")
        if "entry_type" in kwargs:
            self.config.entry_type = str(kwargs["entry_type"]).upper()
        if "entry_value" in kwargs:
            self.config.entry_value = parse_float_value(kwargs["entry_value"], field_name="Valor da entrada")
        if "gale" in kwargs:
            self.config.gale = parse_int_value(kwargs["gale"], field_name="Gale")

        self._persist_config()
        self.add_log("Configurações atualizadas", "success")
        return self.config

    def _persist_config(self) -> None:
        env_lines = []
        if os.path.exists(self.env_path):
            with open(self.env_path, "r", encoding="utf-8") as f_env:
                env_lines = [
                    line
                    for line in f_env
                    if not line.strip().startswith(
                        (
                            "IQ_OPTION_STOP_LOSS",
                            "IQ_OPTION_STOP_WIN",
                            "IQ_OPTION_ENTRY_TYPE",
                            "IQ_OPTION_ENTRY_VALUE",
                            "IQ_OPTION_GALE",
                            "IQ_OPTION_ACCOUNT_TYPE",
                        )
                    )
                ]

        env_lines.extend(
            [
                f"IQ_OPTION_STOP_LOSS={self.config.stop_loss}\n",
                f"IQ_OPTION_STOP_WIN={self.config.stop_win}\n",
                f"IQ_OPTION_ENTRY_TYPE={self.config.entry_type}\n",
                f"IQ_OPTION_ENTRY_VALUE={self.config.entry_value}\n",
                f"IQ_OPTION_GALE={self.config.gale}\n",
                f"IQ_OPTION_ACCOUNT_TYPE={self.config.account_type}\n",
            ]
        )

        with open(self.env_path, "w", encoding="utf-8") as f_env:
            f_env.writelines(env_lines)

    # ------------------------------------------------------------------
    # Execução de sinais
    # ------------------------------------------------------------------

    def start_signal_execution(self, sinais_file: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        if not self.api:
            return False, "É necessário autenticar-se antes de iniciar a execução"

        if self.running:
            return False, "Execução já está em andamento"

        sinais_path = sinais_file or os.path.join(CURRENT_DIR, "sinais.txt")
        self.running = True
        self._stop_event.clear()

        self._execution_thread = threading.Thread(
            target=self._signal_worker,
            kwargs={"sinais_path": sinais_path},
            daemon=True,
        )
        self._execution_thread.start()
        self.add_log("Execução de sinais iniciada", "info")
        return True, None

    def stop_signal_execution(self) -> None:
        self._stop_event.set()
        self.running = False
        self.add_log("Execução de sinais interrompida manualmente", "warning")

    # ------------------------------------------------------------------
    # Consulta de status
    # ------------------------------------------------------------------

    def get_status(self, *, fresh: bool = False) -> BotStatus:
        balance = self.last_balance
        stop_loss_status = None

        if (fresh or self.last_balance is None) and self.api:
            try:
                balance = float(self.api.get_balance())
                self.last_balance = balance
            except Exception:
                balance = self.last_balance

        if self.stop_loss_protection and balance is not None:
            self.stop_loss_protection.update_balance(balance)
            stop_loss_status = self.stop_loss_protection.get_status()

        variation = None
        variation_percent = None
        if balance is not None and self.initial_balance:
            variation = balance - self.initial_balance
            if self.initial_balance > 0:
                variation_percent = (variation / self.initial_balance) * 100

        return BotStatus(
            running=self.running,
            processed_signals=self.processed_signals,
            executed_signals=self.executed_signals,
            next_signal=self.next_signal,
            logs=list(self.logs),
            trades=list(self.trade_history),
            balance=balance,
            initial_balance=self.initial_balance,
            variation=variation,
            variation_percent=variation_percent,
            stop_loss_status=stop_loss_status,
        )

    # ------------------------------------------------------------------
    # Implementação interna da execução de sinais
    # ------------------------------------------------------------------

    def _signal_worker(self, *, sinais_path: str) -> None:
        try:
            processor = SinaisProcessor(sinais_path)
            if not processor.carregar_sinais():
                self.add_log("Nenhum sinal válido encontrado", "warning")
                self.running = False
                return

            self.processed_signals = 0
            self.executed_signals = 0
            self.losses_state = {"count": 0, "skip_count": 0}

            ultima_recarga = datetime.now()
            sinais_executados = set()

            self.add_log(f"Execução iniciada às {datetime.now().strftime('%H:%M:%S')}", "info")

            while not self._stop_event.is_set():
                hora_atual = datetime.now()
                hora_str = hora_atual.strftime("%H:%M")

                if (datetime.now() - ultima_recarga).total_seconds() >= 60:
                    try:
                        processor.carregar_sinais()
                        ultima_recarga = datetime.now()
                        sinais_executados.clear()
                    except Exception as exc:
                        self.add_log(f"Erro ao recarregar sinais: {exc}", "error")

                if self._stop_event.is_set():
                    break

                if hora_str not in sinais_executados:
                    sinais_para_hora = processor.obter_sinais_para_hora(hora_atual)
                    if sinais_para_hora:
                        segundos = hora_atual.second
                        if segundos >= 58 or segundos <= 2:
                            sinais_executados.add(hora_str)
                            for sinal in sinais_para_hora:
                                if self._stop_event.is_set():
                                    break
                                self._process_signal(sinal)

                proximos = processor.obter_proximos_sinais(1)
                self.next_signal = (
                    f"{proximos[0].hora} - {proximos[0].ativo} ({proximos[0].direcao})"
                    if proximos else "Nenhum sinal futuro"
                )

                time.sleep(0.1)

        except Exception as exc:  # pragma: no cover - manter debug consistente
            self.add_log(f"Erro na execução de sinais: {exc}", "error")
        finally:
            self.running = False
            self.add_log("Execução de sinais finalizada", "info")

    def _process_signal(self, sinal: Sinal) -> None:
        if not self.api:
            self.add_log("API indisponível ao processar sinal", "error")
            self.stop_signal_execution()
            return

        if self.stop_loss_protection and not self.stop_loss_protection.can_operate():
            self.add_log("Stop Loss acionado - execução interrompida", "warning")
            self.stop_signal_execution()
            return

        saldo_atual = self.api.get_balance()
        if self.config.entry_type == "PERCENT":
            valor_entrada = saldo_atual * (self.config.entry_value / 100.0)
        else:
            valor_entrada = self.config.entry_value

        if self.stop_loss_protection:
            if self.config.entry_type == "PERCENT":
                valor_entrada = self.stop_loss_protection.calculate_safe_entry_value(entry_percent=self.config.entry_value)
            else:
                valor_entrada = self.stop_loss_protection.calculate_safe_entry_value(entry_fixed=self.config.entry_value)

        if saldo_atual < valor_entrada:
            self.add_log(
                f"Saldo insuficiente para {sinal.ativo} {sinal.direcao} - necessário ${valor_entrada:.2f}, disponível ${saldo_atual:.2f}",
                "error",
            )
            return

        try:
            minutos = int(sinal.timeframe[1:]) if sinal.timeframe.startswith("M") else int(sinal.timeframe[1:]) * 60
        except Exception:
            self.add_log(f"Timeframe inválido para sinal: {sinal.timeframe}", "error")
            return

        self.add_log(
            f"Executando sinal: {sinal.timeframe};{sinal.ativo};{sinal.hora};{sinal.direcao} | Valor ${valor_entrada:.2f}",
            "info",
        )
        self.processed_signals += 1

        try:
            resultado, order_id = self.api.buy(valor_entrada, sinal.ativo, sinal.direcao.lower(), minutos)
        except Exception as exc:
            self.add_log(f"Erro ao enviar ordem: {exc}", "error")
            return

        if not resultado:
            self.add_log(f"Falha ao executar sinal {sinal.ativo} {sinal.direcao}", "error")
            return

        self.executed_signals += 1
        balance = self.api.get_balance()
        if self.stop_loss_protection:
            self.stop_loss_protection.update_balance(balance)

        trade = TradeEntry(
            id=order_id,
            asset=sinal.ativo,
            direction=sinal.direcao,
            amount=valor_entrada,
            expiry=minutos,
            timestamp=datetime.now().isoformat(),
            sinal=f"{sinal.timeframe};{sinal.ativo};{sinal.hora};{sinal.direcao}",
        )
        self._append_trade(trade)

        threading.Thread(
            target=self._check_trade_result,
            args=(trade, sinal, self.config.gale),
            daemon=True,
        ).start()

    def _check_trade_result(self, trade: TradeEntry, sinal: Sinal, gale_level: int) -> None:
        if not self.api:
            return

        time.sleep(trade.expiry * 60 + 5)

        try:
            win, profit = self.api.check_win_v4(trade.id)
        except Exception as exc:
            self.add_log(f"Erro ao verificar resultado (ordem {trade.id}): {exc}", "error")
            return

        for stored_trade in self.trade_history:
            if stored_trade.id == trade.id:
                if win == "win":
                    stored_trade.status = "win"
                    stored_trade.profit = float(profit) if profit else 0.0
                elif win == "loose":
                    stored_trade.status = "loss"
                    stored_trade.profit = float(profit) if profit else 0.0
                else:
                    stored_trade.status = "equal"
                    stored_trade.profit = float(profit) if profit else 0.0
                break

        # Atualiza stop loss e perdas consecutivas
        balance = self.api.get_balance()
        if self.stop_loss_protection:
            self.stop_loss_protection.update_balance(balance)

        self._update_losses(trade, gale_level)

        if stored_trade.status == "loss" and gale_level > 0:
            threading.Thread(
                target=self._execute_martingale,
                args=(stored_trade, sinal, gale_level),
                daemon=True,
            ).start()

    def _execute_martingale(self, trade: TradeEntry, sinal: Sinal, gale_level: int) -> None:
        if not self.api:
            return

        current_level = trade.martingale_level
        if current_level >= gale_level:
            return

        valor = trade.amount * 2.15
        if self.stop_loss_protection:
            saldo = self.api.get_balance()
            if saldo < valor:
                self.add_log("Saldo insuficiente para Martingale", "warning")
                return
        try:
            resultado, order_id = self.api.buy(valor, trade.asset, trade.direction.lower(), trade.expiry)
        except Exception as exc:
            self.add_log(f"Erro ao executar Martingale: {exc}", "error")
            return

        if not resultado:
            self.add_log("Falha ao executar Martingale", "error")
            return

        martingale_trade = TradeEntry(
            id=order_id,
            asset=trade.asset,
            direction=trade.direction,
            amount=valor,
            expiry=trade.expiry,
            timestamp=datetime.now().isoformat(),
            status="pending",
            is_martingale=True,
            martingale_level=trade.martingale_level + 1,
            parent_trade_id=trade.parent_trade_id or trade.id,
            sinal=trade.sinal,
        )
        self._append_trade(martingale_trade)

        time.sleep(martingale_trade.expiry * 60 + 5)
        try:
            win, profit = self.api.check_win_v4(order_id)
        except Exception as exc:
            self.add_log(f"Erro ao verificar Martingale: {exc}", "error")
            return

        for stored_trade in self.trade_history:
            if stored_trade.id == order_id:
                if win == "win":
                    stored_trade.status = "win"
                    stored_trade.profit = float(profit) if profit else 0.0
                elif win == "loose":
                    stored_trade.status = "loss"
                    stored_trade.profit = float(profit) if profit else 0.0
                else:
                    stored_trade.status = "equal"
                    stored_trade.profit = float(profit) if profit else 0.0
                break

        balance = self.api.get_balance()
        if self.stop_loss_protection:
            self.stop_loss_protection.update_balance(balance)

        self._update_losses(trade, gale_level)

        if stored_trade.status == "loss" and stored_trade.martingale_level < gale_level:
            stored_trade.martingale_level += 1
            self._execute_martingale(stored_trade, sinal, gale_level)

    def _update_losses(self, trade: TradeEntry, gale_level: int) -> None:
        if trade.status != "loss":
            if self.losses_state["count"] > 0:
                self.add_log("✅ WIN ou EQUAL detectado. Contador de perdas resetado", "info")
            self.losses_state["count"] = 0
            return

        self.losses_state["count"] += 1
        self.add_log(f"LOSS completo detectado. Perdas consecutivas: {self.losses_state['count']}", "warning")

        if self.losses_state["count"] >= 2:
            self.losses_state["skip_count"] = 2
            self.add_log("⚠️ 2 LOSS consecutivos! Próximos 2 sinais serão pulados automaticamente.", "warning")

    def _parse_login_error(self, reason: Any) -> str:
        error_msg = "Erro desconhecido"
        if not reason:
            return error_msg
        try:
            if isinstance(reason, str):
                try:
                    error_json = json.loads(reason)
                    if "message" in error_json:
                        return error_json["message"]
                    if "code" in error_json:
                        code = error_json["code"]
                        if code == "verify":
                            return "Autenticação de dois fatores necessária"
                        if code == "invalid_credentials":
                            return "Email ou senha incorretos"
                        return f"Código de erro: {code}"
                    return reason
                except json.JSONDecodeError:
                    return reason
            return str(reason)
        except Exception:
            return str(reason)


__all__ = [
    "BotService",
    "BotStatus",
    "BotConfig",
    "TradeEntry",
    "LogEntry",
]


