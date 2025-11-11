"""Camada de controle entre UI (PySide6) e BotService."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QObject, QThreadPool, Signal, QTimer

from ...bot_service import BotService, BotStatus
from .workers import Worker


class AppController(QObject):
    """Encapsula interações com BotService e expõe sinais para a UI."""

    login_succeeded = Signal()
    login_failed = Signal(str)
    logout_completed = Signal()
    status_updated = Signal(object)  # emite BotStatus
    execution_started = Signal()
    execution_stopped = Signal()
    error_occurred = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.service = BotService()
        self.thread_pool = QThreadPool()

    # ------------------------------------------------------------------
    # Autenticação
    # ------------------------------------------------------------------

    def login(self, email: str, password: str, account_type: str) -> None:
        worker = Worker(self.service.login, email, password, account_type)

        def handle_result(result: tuple[bool, Optional[str]]) -> None:
            success, error = result
            if success:
                print("[CONTROLLER] login_succeeded")
                self.login_succeeded.emit()
                QTimer.singleShot(500, lambda: self.request_status_update(fresh=True))
            else:
                self.login_failed.emit(error or "Erro desconhecido")

        worker.signals.result.connect(handle_result)
        worker.signals.error.connect(lambda msg: self.login_failed.emit(msg))
        self.thread_pool.start(worker)

    def logout(self) -> None:
        worker = Worker(self.service.logout)
        worker.signals.finished.connect(self.logout_completed.emit)
        worker.signals.error.connect(lambda msg: self.error_occurred.emit(msg))
        self.thread_pool.start(worker)

    # ------------------------------------------------------------------
    # Execução de sinais
    # ------------------------------------------------------------------

    def start_execution(self, sinais_file: Optional[str] = None) -> None:
        worker = Worker(self.service.start_signal_execution, sinais_file)

        def handle_result(result: tuple[bool, Optional[str]]) -> None:
            success, error = result
            if success:
                self.execution_started.emit()
            else:
                self.error_occurred.emit(error or "Não foi possível iniciar a execução")

        worker.signals.result.connect(handle_result)
        worker.signals.error.connect(lambda msg: self.error_occurred.emit(msg))
        self.thread_pool.start(worker)

    def stop_execution(self) -> None:
        worker = Worker(self.service.stop_signal_execution)
        worker.signals.finished.connect(self.execution_stopped.emit)
        worker.signals.error.connect(lambda msg: self.error_occurred.emit(msg))
        self.thread_pool.start(worker)

    # ------------------------------------------------------------------
    # Status / Config
    # ------------------------------------------------------------------

    def request_status_update(self, *, fresh: bool = False) -> None:
        worker = Worker(self.service.get_status, fresh=fresh)

        worker.signals.result.connect(
            lambda status: print(f"[CONTROLLER] status atualizado (fresh={fresh})")
            or self.status_updated.emit(status)
        )
        worker.signals.error.connect(lambda msg: self.error_occurred.emit(msg))
        self.thread_pool.start(worker)

    def get_config(self):  # noqa: D401 - simples proxy
        """Retorna a configuração atual (BotConfig)."""

        return self.service.get_config()

    def update_config(self, **kwargs) -> None:
        worker = Worker(self.service.update_config, **kwargs)
        worker.signals.result.connect(lambda _: self.request_status_update())
        worker.signals.error.connect(lambda msg: self.error_occurred.emit(msg))
        self.thread_pool.start(worker)


