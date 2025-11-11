"""Janela principal do aplicativo desktop."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from ..controllers.app_controller import AppController
from ...bot_service import BotStatus
from .pages.dashboard_page import DashboardPage
from .pages.login_page_improved import LoginPage


class MainWindow(QMainWindow):
    """Container principal com stack de páginas e toolbar."""

    def __init__(self, controller: AppController, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("IQ Option Bot Desktop")
        self.setMinimumSize(960, 600)
        self.setWindowState(Qt.WindowMaximized)
        self.controller = controller

        self._setup_ui()
        self._connect_signals()
        self._setup_status_timer()

    # ------------------------------------------------------------------
    def _setup_ui(self) -> None:
        self.stack = QStackedWidget()
        self.login_page = LoginPage()
        self.dashboard_page = DashboardPage()

        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.dashboard_page)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.stack)
        self.setCentralWidget(central_widget)

        self._build_toolbar()

    def _build_toolbar(self) -> None:
        self.toolbar = QToolBar("Ações")
        self.toolbar.setMovable(False)
        self.toolbar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        self.status_label = QLabel("Pronto")

        self.start_button = QPushButton("Iniciar Sinais")
        self.stop_button = QPushButton("Parar")
        self.logout_button = QPushButton("Sair")

        toolbar_container = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_container)
        toolbar_layout.setContentsMargins(8, 4, 8, 4)
        toolbar_layout.setSpacing(10)

        toolbar_layout.addWidget(self.start_button)
        toolbar_layout.addWidget(self.stop_button)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.status_label)
        toolbar_layout.addWidget(self.logout_button)

        self.toolbar.addWidget(toolbar_container)
        self._set_controls_enabled(False)

    def _connect_signals(self) -> None:
        self.login_page.login_requested.connect(self._handle_login_request)

        self.start_button.clicked.connect(lambda: self.controller.start_execution())
        self.stop_button.clicked.connect(lambda: self.controller.stop_execution())
        self.logout_button.clicked.connect(self._confirm_logout)

        self.controller.login_succeeded.connect(self._on_login_success)
        self.controller.login_failed.connect(self._display_error)
        self.controller.status_updated.connect(self._update_status)
        self.controller.execution_started.connect(lambda: self._set_status("Execução iniciada"))
        self.controller.execution_stopped.connect(lambda: self._set_status("Execução parada"))
        self.controller.logout_completed.connect(self._on_logout)
        self.controller.error_occurred.connect(self._display_error)

    def _setup_status_timer(self) -> None:
        self.status_timer = QTimer(self)
        self.status_timer.setInterval(3000)  # 3 segundos
        self.status_timer.timeout.connect(self._request_cached_status)

    # ------------------------------------------------------------------
    # Slots / callbacks
    # ------------------------------------------------------------------

    def _handle_login_request(self, email: str, password: str, account_type: str) -> None:
        self._set_status("Conectando...")
        self.controller.login(email, password, account_type)

    def _on_login_success(self) -> None:
        print("[DESKTOP] on_login_success acionado")
        self.stack.setCurrentWidget(self.dashboard_page)
        self._set_controls_enabled(True)
        self._set_status("Conectado")
        self.controller.request_status_update(fresh=True)

    def _request_initial_status(self) -> None:
        self.controller.request_status_update(fresh=True)

    def _request_cached_status(self) -> None:
        self.controller.request_status_update(fresh=False)

    def _on_logout(self) -> None:
        self._set_controls_enabled(False)
        self.stack.setCurrentWidget(self.login_page)
        self._set_status("Sessão encerrada")
        self.status_timer.stop()

    def _confirm_logout(self) -> None:
        reply = QMessageBox.question(
            self,
            "Confirmar saída",
            "Tem certeza que deseja encerrar a sessão?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.controller.logout()

    def _display_error(self, message: str) -> None:
        QMessageBox.critical(self, "Erro", message)
        self._set_status("Erro")

    def _set_controls_enabled(self, enabled: bool) -> None:
        self.start_button.setEnabled(enabled)
        self.stop_button.setEnabled(enabled)
        self.logout_button.setEnabled(enabled)

    def _set_status(self, message: str) -> None:
        self.status_label.setText(message)

    def _update_status(self, status: BotStatus) -> None:
        self.dashboard_page.update_from_status(status)
        self._set_status("Atualizado")


