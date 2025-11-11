"""Tela de login para a aplicação desktop."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class LoginPage(QWidget):
    login_requested = Signal(str, str, str)  # email, senha, tipo de conta

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setObjectName("LoginPage")

        title = QLabel("Bem-vindo ao IQ Option Bot")
        title.setAlignment(Qt.AlignHCenter)
        title.setObjectName("LoginTitle")

        subtitle = QLabel("Autentique-se com suas credenciais para começar a operar")
        subtitle.setAlignment(Qt.AlignHCenter)
        subtitle.setObjectName("LoginSubtitle")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email da IQ Option")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Senha")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.account_combo = QComboBox()
        self.account_combo.addItems(["PRACTICE", "REAL"])

        form_layout = QFormLayout()
        form_layout.setSpacing(18)
        form_layout.addRow("Email", self.email_input)
        form_layout.addRow("Senha", self.password_input)
        form_layout.addRow("Tipo de conta", self.account_combo)

        self.login_button = QPushButton("Entrar")
        self.login_button.setObjectName("LoginButton")
        self.login_button.clicked.connect(self._emit_login)

        footer = QLabel("As credenciais permanecem apenas na sua máquina.")
        footer.setAlignment(Qt.AlignHCenter)
        footer.setProperty("class", "caption")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(80, 50, 80, 50)
        layout.setSpacing(0)

        card = QWidget()
        card.setObjectName("LoginCard")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(28)
        card_layout.setContentsMargins(56, 48, 56, 48)
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addLayout(form_layout)
        card_layout.addWidget(self.login_button, alignment=Qt.AlignRight)
        card_layout.addWidget(footer)

        layout.addWidget(card, alignment=Qt.AlignCenter)

    def _emit_login(self) -> None:
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        account_type = self.account_combo.currentText()
        self.login_requested.emit(email, password, account_type)


