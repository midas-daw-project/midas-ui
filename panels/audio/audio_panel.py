from __future__ import annotations

from typing import Callable

from PySide6.QtWidgets import (
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from viewmodels.audio_viewmodel import AudioViewModel


class AudioPanel(QWidget):
    def __init__(
        self,
        on_start_runtime: Callable[[], None],
        on_shutdown_runtime: Callable[[], None],
        on_init: Callable[[], None],
        on_open: Callable[[], None],
        on_start: Callable[[], None],
        on_stop: Callable[[], None],
        on_close: Callable[[], None],
        on_refresh: Callable[[], None],
    ) -> None:
        super().__init__()
        self._on_start_runtime = on_start_runtime
        self._on_shutdown_runtime = on_shutdown_runtime
        self._on_init = on_init
        self._on_open = on_open
        self._on_start = on_start
        self._on_stop = on_stop
        self._on_close = on_close
        self._on_refresh = on_refresh

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)

        config_box = QGroupBox("Audio Config")
        form = QFormLayout(config_box)
        self.device_input = QLineEdit("default-device")
        self.sample_rate_input = QSpinBox()
        self.sample_rate_input.setRange(8000, 192000)
        self.sample_rate_input.setValue(48000)
        self.buffer_size_input = QSpinBox()
        self.buffer_size_input.setRange(32, 4096)
        self.buffer_size_input.setValue(256)
        self.channel_input = QSpinBox()
        self.channel_input.setRange(1, 2048)
        self.channel_input.setValue(1)
        form.addRow("Device ID", self.device_input)
        form.addRow("Sample Rate", self.sample_rate_input)
        form.addRow("Buffer Size", self.buffer_size_input)
        form.addRow("Track Channel", self.channel_input)
        root.addWidget(config_box)

        buttons_box = QGroupBox("Audio Lifecycle")
        grid = QGridLayout(buttons_box)
        self.start_runtime_button = QPushButton("Start Runtime")
        self.shutdown_runtime_button = QPushButton("Shutdown Runtime")
        self.init_button = QPushButton("Init")
        self.open_button = QPushButton("Open")
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.close_button = QPushButton("Close")
        self.refresh_button = QPushButton("Refresh")
        grid.addWidget(self.start_runtime_button, 0, 0)
        grid.addWidget(self.shutdown_runtime_button, 0, 1)
        grid.addWidget(self.init_button, 1, 0)
        grid.addWidget(self.open_button, 1, 1)
        grid.addWidget(self.start_button, 2, 0)
        grid.addWidget(self.stop_button, 2, 1)
        grid.addWidget(self.close_button, 3, 0)
        grid.addWidget(self.refresh_button, 3, 1)
        root.addWidget(buttons_box)

        status_box = QGroupBox("Status")
        status_layout = QVBoxLayout(status_box)
        self.state_label = QLabel("State: idle")
        self.render_status_label = QLabel("Render: stopped")
        self.error_label = QLabel("Error: ")
        status_layout.addWidget(self.state_label)
        status_layout.addWidget(self.render_status_label)
        status_layout.addWidget(self.error_label)
        root.addWidget(status_box)

        self.start_runtime_button.clicked.connect(self._on_start_runtime)
        self.shutdown_runtime_button.clicked.connect(self._on_shutdown_runtime)
        self.init_button.clicked.connect(self._on_init)
        self.open_button.clicked.connect(self._on_open)
        self.start_button.clicked.connect(self._on_start)
        self.stop_button.clicked.connect(self._on_stop)
        self.close_button.clicked.connect(self._on_close)
        self.refresh_button.clicked.connect(self._on_refresh)

    def read_config_into(self, vm: AudioViewModel) -> None:
        vm.device_id = self.device_input.text().strip()
        vm.sample_rate = int(self.sample_rate_input.value())
        vm.buffer_size = int(self.buffer_size_input.value())
        vm.track_channel = int(self.channel_input.value())

    def render(self, vm: AudioViewModel) -> None:
        self.state_label.setText(
            f"State: {vm.state} | Device: {vm.device_id or '-'} | "
            f"Rate: {vm.sample_rate} | Buffer: {vm.buffer_size}"
        )
        self.render_status_label.setText(f"Render: {vm.render_status}")
        self.error_label.setText(f"Error: {vm.last_error}")
