from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class MixerPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Mixer panel placeholder (phase 1)."))
