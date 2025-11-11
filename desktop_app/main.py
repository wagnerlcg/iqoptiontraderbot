"""Ponto de entrada da aplicação desktop (PySide6)."""

from __future__ import annotations

import os
import sys

try:
    from PySide6.QtWidgets import QApplication
except ModuleNotFoundError as exc:  # pragma: no cover - feedback claro
    raise ModuleNotFoundError(
        "PySide6 não está instalado. Execute 'pip install PySide6' antes de iniciar a versão desktop.") from exc

from .controllers.app_controller import AppController
from .ui.main_window import MainWindow


def main() -> int:
    """Inicializa QApplication, controladores e exibe a janela principal."""

    app = QApplication(sys.argv)

    qss_path = os.path.join(os.path.dirname(__file__), "resources", "style.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f_style:
            app.setStyleSheet(f_style.read())

    controller = AppController()
    window = MainWindow(controller)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())


