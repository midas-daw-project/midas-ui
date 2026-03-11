from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class TransportPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Transport panel placeholder (phase 1)."))
