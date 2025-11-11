"""Tela de login para a aplicação desktop."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class LoginPage(QWidget):
    """Tela de login moderna e intuitiva."""

    login_requested = Signal(str, str, str)  # email, senha, tipo de conta

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Configura a interface do usuário."""
        self.setObjectName("LoginPage")

        # Título principal
        title = QLabel("Bem-vindo ao IQ Option Bot")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title.setObjectName("LoginTitle")

        # Subtítulo
        subtitle = QLabel("Autentique-se com suas credenciais para começar a operar")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        subtitle.setObjectName("LoginSubtitle")
        subtitle.setWordWrap(True)

        # Campos de entrada
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email da IQ Option")
        self.email_input.setObjectName("EmailInput")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Senha")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setObjectName("PasswordInput")

        # ComboBox
        self.account_combo = QComboBox()
        self.account_combo.addItems(["PRACTICE", "REAL"])
        self.account_combo.setObjectName("AccountCombo")

        # Botão de login
        self.login_button = QPushButton("Entrar")
        self.login_button.setObjectName("LoginButton")
        self.login_button.clicked.connect(self._emit_login)

        # Rodapé
        footer = QLabel("🔒 Suas credenciais permanecem seguras apenas na sua máquina")
        footer.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        footer.setProperty("class", "caption")
        footer.setWordWrap(True)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(80, 50, 80, 50)
        layout.setSpacing(0)

        # Card centralizado
        card = QWidget()
        card.setObjectName("LoginCard")
        card.setMaximumWidth(500)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(56, 48, 56, 48)
        card_layout.setSpacing(24)

        # Adicionar widgets ao card
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(20)
        card_layout.addWidget(self.email_input)
        card_layout.addSpacing(6)
        card_layout.addWidget(self.password_input)
        card_layout.addSpacing(6)
        card_layout.addWidget(self.account_combo)
        card_layout.addSpacing(12)
        card_layout.addWidget(self.login_button)
        card_layout.addSpacing(8)
        card_layout.addWidget(footer)

        layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

    def _emit_login(self) -> None:
        """Emite o sinal de login com os dados preenchidos."""
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        account_type = self.account_combo.currentText()
        self.login_requested.emit(email, password, account_type)