from __future__ import annotations

from typing import Callable

from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from viewmodels.transport_viewmodel import TransportViewModel


class TransportPanel(QWidget):
    def __init__(
        self,
        on_play: Callable[[], None],
        on_stop: Callable[[], None],
        on_refresh: Callable[[], None],
    ) -> None:
        super().__init__()
        self._on_play = on_play
        self._on_stop = on_stop
        self._on_refresh = on_refresh

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        controls = QGroupBox("Transport")
        form = QFormLayout(controls)
        self.track_channel_input = QSpinBox()
        self.track_channel_input.setRange(1, 2048)
        self.track_channel_input.setValue(1)
        self.play_button = QPushButton("Play")
        self.stop_button = QPushButton("Stop")
        self.refresh_button = QPushButton("Refresh")
        form.addRow("Track Channel", self.track_channel_input)
        form.addRow(self.play_button)
        form.addRow(self.stop_button)
        form.addRow(self.refresh_button)
        layout.addWidget(controls)

        status_box = QGroupBox("Status")
        status_layout = QVBoxLayout(status_box)
        self.status_label = QLabel("Play state: stopped")
        self.error_label = QLabel("Error: ")
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.error_label)
        layout.addWidget(status_box)

        self.play_button.clicked.connect(self._on_play)
        self.stop_button.clicked.connect(self._on_stop)
        self.refresh_button.clicked.connect(self._on_refresh)

    def selected_track_channel(self) -> int:
        return int(self.track_channel_input.value())

    def render(self, vm: TransportViewModel) -> None:
        self.status_label.setText(f"Play state: {vm.play_state}")
        self.error_label.setText(f"Error: {vm.last_error}")
