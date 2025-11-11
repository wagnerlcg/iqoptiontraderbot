"""Workers utilitários para execução assíncrona na UI."""

from __future__ import annotations

from typing import Any, Callable, Tuple

from PySide6.QtCore import QObject, QRunnable, Signal


class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(str)
    result = Signal(object)


class Worker(QRunnable):
    """Executa uma função em thread separada usando QThreadPool."""

    def __init__(self, fn: Callable, *args: Tuple[Any, ...], **kwargs: Any) -> None:
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self) -> None:  # pragma: no cover - executado em thread separada
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as exc:  # noqa: BLE001
            self.signals.error.emit(str(exc))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


