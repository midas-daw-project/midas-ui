from __future__ import annotations

from datetime import datetime
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
        on_new: Callable[[str], None],
        on_open: Callable[[str], None],
        on_save: Callable[[], None],
        on_load: Callable[[], None],
        on_apply: Callable[[], None],
        on_refresh: Callable[[], None],
    ) -> None:
        super().__init__()
        self._on_new = on_new
        self._on_open = on_open
        self._on_save = on_save
        self._on_load = on_load
        self._on_apply = on_apply
        self._on_refresh = on_refresh

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        control_box = QGroupBox("Session Actions")
        form = QFormLayout(control_box)
        self.session_ref_input = QLineEdit("default-session")
        self.new_button = QPushButton("New")
        self.open_button = QPushButton("Open")
        self.save_button = QPushButton("Save")
        self.load_button = QPushButton("Load")
        self.apply_button = QPushButton("Apply")
        self.refresh_button = QPushButton("Refresh")
        form.addRow("Session Ref", self.session_ref_input)
        form.addRow(self.new_button)
        form.addRow(self.open_button)
        form.addRow(self.save_button)
        form.addRow(self.load_button)
        form.addRow(self.apply_button)
        form.addRow(self.refresh_button)
        layout.addWidget(control_box)

        status_box = QGroupBox("Status")
        status_layout = QVBoxLayout(status_box)
        self.session_heading_label = QLabel("No active session")
        self.session_heading_label.setStyleSheet("font-weight: 600; font-size: 15px;")
        self.status_label = QLabel("Status: idle")
        self.identity_label = QLabel("Phase: none | Dirty: clean")
        self.storage_label = QLabel("Storage: -")
        self.storage_root_label = QLabel("Storage Root: -")
        self.last_ops_label = QLabel("Last op: none")
        self.last_actions_label = QLabel("Save=- Load=- Apply=-")
        self.recent_label = QLabel("Recent Sessions: -")
        self.discoverable_label = QLabel("Discoverable Sessions: 0")
        self.error_label = QLabel("Error: -")
        self.error_label.setWordWrap(True)
        status_layout.addWidget(self.session_heading_label)
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.identity_label)
        status_layout.addWidget(self.storage_label)
        status_layout.addWidget(self.storage_root_label)
        status_layout.addWidget(self.last_ops_label)
        status_layout.addWidget(self.last_actions_label)
        status_layout.addWidget(self.recent_label)
        status_layout.addWidget(self.discoverable_label)
        status_layout.addWidget(self.error_label)
        layout.addWidget(status_box)

        self.new_button.clicked.connect(lambda: self._on_new(self.session_ref_input.text()))
        self.open_button.clicked.connect(lambda: self._on_open(self.session_ref_input.text()))
        self.save_button.clicked.connect(self._on_save)
        self.load_button.clicked.connect(self._on_load)
        self.apply_button.clicked.connect(self._on_apply)
        self.refresh_button.clicked.connect(self._on_refresh)

    def render(self, vm: SessionViewModel) -> None:
        self.session_ref_input.setText(vm.session_ref)
        self.session_heading_label.setText(vm.session_ref or "No active session")
        self.status_label.setText(f"Status: {vm.status}")
        self.identity_label.setText(f"Phase: {vm.phase} | Dirty: {'dirty' if vm.dirty else 'clean'}")
        storage = vm.storage_path if vm.storage_path else "-"
        source = vm.storage_source if vm.storage_source else "-"
        self.storage_label.setText(f"{storage} | Source: {source}")
        self.storage_root_label.setText(f"Storage Root: {vm.storage_root or '-'}")
        self.last_ops_label.setText(
            f"Last op: {vm.last_operation} | "
            f"save={self._fmt_epoch(vm.last_save_epoch)} "
            f"load={self._fmt_epoch(vm.last_load_epoch)} "
            f"apply={self._fmt_epoch(vm.last_apply_epoch)}"
        )
        self.last_actions_label.setText(
            f"Save={vm.last_save_status or '-'} "
            f"Load={vm.last_load_status or '-'} "
            f"Apply={vm.last_apply_status or '-'}"
        )
        if vm.recent_sessions:
            summary = ", ".join(
                f"{entry.session_ref} ({self._fmt_epoch(entry.last_touched_epoch)})"
                for entry in vm.recent_sessions[:3]
            )
        else:
            summary = "-"
        self.recent_label.setText(f"Recent Sessions: {summary}")
        self.discoverable_label.setText(f"Discoverable Sessions: {len(vm.discoverable_sessions)}")
        self.error_label.setText(f"{vm.last_error or '-'}")

    @staticmethod
    def _fmt_epoch(value: int) -> str:
        if value <= 0:
            return "-"
        return datetime.fromtimestamp(value).strftime("%H:%M:%S")
