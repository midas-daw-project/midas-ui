from __future__ import annotations

from PySide6.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget

from bridge.protocol import BridgeEvent


class DebugPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        root = QVBoxLayout(self)
        self.version_label = QLabel("Bridge Version: unknown")
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        root.addWidget(self.version_label)
        root.addWidget(self.log)

    def set_bridge_version(self, version: int) -> None:
        self.version_label.setText(f"Bridge Version: {version}")

    def append_event(self, event: BridgeEvent) -> None:
        self.log.append(
            f"[{event.category}] emitter={event.emitter} metadata={event.metadata}"
        )

    def append_result(self, operation: str, code: int, message: str) -> None:
        self.log.append(f"[result] {operation} code={code} message={message}")
