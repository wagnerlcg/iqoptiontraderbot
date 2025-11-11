"""Dashboard simplificado para exibir status do bot."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ....bot_service import BotStatus


class DashboardPage(QWidget):
    """Layout inicial mostrando status geral, saldo e logs."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.status_label = QLabel("Status: aguardando login")
        self.balance_label = QLabel("Saldo: -")
        self.variation_label = QLabel("Variação: -")
        self.next_signal_label = QLabel("Próximo sinal: -")

        form = QFormLayout()
        form.addRow("Status", self.status_label)
        form.addRow("Saldo", self.balance_label)
        form.addRow("Variação", self.variation_label)
        form.addRow("Próximo sinal", self.next_signal_label)

        self.logs_list = QListWidget()
        self.logs_list.setSelectionMode(QListWidget.NoSelection)

        self.trades_list = QListWidget()
        self.trades_list.setSelectionMode(QListWidget.NoSelection)

        splitter = QSplitter()
        logs_container = QWidget()
        logs_layout = QVBoxLayout(logs_container)
        logs_layout.addWidget(QLabel("Logs"))
        logs_layout.addWidget(self.logs_list)

        trades_container = QWidget()
        trades_layout = QVBoxLayout(trades_container)
        trades_layout.addWidget(QLabel("Operações"))
        trades_layout.addWidget(self.trades_list)

        splitter.addWidget(logs_container)
        splitter.addWidget(trades_container)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(splitter)

    def update_from_status(self, status: BotStatus) -> None:
        status_text = "Rodando" if status.running else "Parado"
        self.status_label.setText(status_text)

        if status.balance is not None:
            self.balance_label.setText(f"${status.balance:.2f}")
        else:
            self.balance_label.setText("-")

        if status.variation is not None and status.variation_percent is not None:
            self.variation_label.setText(f"${status.variation:.2f} ({status.variation_percent:.2f}%)")
        else:
            self.variation_label.setText("-")

        self.next_signal_label.setText(status.next_signal or "Nenhum")

        self.logs_list.clear()
        for log in status.logs[:50]:
            item = QListWidgetItem(f"[{log.timestamp[-8:]}] {log.message}")
            if log.type == "error":
                item.setForeground(Qt.red)
            elif log.type == "warning":
                item.setForeground(Qt.darkYellow)
            elif log.type == "success":
                item.setForeground(Qt.darkGreen)
            self.logs_list.addItem(item)

        self.trades_list.clear()
        for trade in status.trades[:50]:
            text = (
                f"[{trade.timestamp[-8:]}] {trade.asset} {trade.direction} "
                f"${trade.amount:.2f} ({trade.status.upper()})"
            )
            item = QListWidgetItem(text)
            if trade.status == "loss":
                item.setForeground(Qt.red)
            elif trade.status == "win":
                item.setForeground(Qt.darkGreen)
            self.trades_list.addItem(item)


