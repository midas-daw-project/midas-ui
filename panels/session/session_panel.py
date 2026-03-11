from __future__ import annotations

from typing import Callable

from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from viewmodels.session_viewmodel import SessionViewModel


class SessionPanel(QWidget):
    def __init__(
        self,
        on_save: Callable[[], None],
        on_load: Callable[[], None],
        on_apply: Callable[[], None],
        on_refresh: Callable[[], None],
    ) -> None:
        super().__init__()
        self._on_save = on_save
        self._on_load = on_load
        self._on_apply = on_apply
        self._on_refresh = on_refresh

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        control_box = QGroupBox("Session Actions")
        form = QFormLayout(control_box)
        self.session_ref_input = QLineEdit("default-session")
        self.save_button = QPushButton("Save")
        self.load_button = QPushButton("Load")
        self.apply_button = QPushButton("Apply")
        self.refresh_button = QPushButton("Refresh")
        form.addRow("Session Ref", self.session_ref_input)
        form.addRow(self.save_button)
        form.addRow(self.load_button)
        form.addRow(self.apply_button)
        form.addRow(self.refresh_button)
        layout.addWidget(control_box)

        status_box = QGroupBox("Status")
        status_layout = QVBoxLayout(status_box)
        self.status_label = QLabel("Status: idle")
        self.last_actions_label = QLabel("Save=- Load=- Apply=-")
        self.error_label = QLabel("Error: ")
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.last_actions_label)
        status_layout.addWidget(self.error_label)
        layout.addWidget(status_box)

        self.save_button.clicked.connect(self._on_save)
        self.load_button.clicked.connect(self._on_load)
        self.apply_button.clicked.connect(self._on_apply)
        self.refresh_button.clicked.connect(self._on_refresh)

    def render(self, vm: SessionViewModel) -> None:
        self.status_label.setText(f"Status: {vm.status} | Session: {vm.session_ref}")
        self.last_actions_label.setText(
            f"Save={vm.last_save_status or '-'} "
            f"Load={vm.last_load_status or '-'} "
            f"Apply={vm.last_apply_status or '-'}"
        )
        self.error_label.setText(f"Error: {vm.last_error}")
