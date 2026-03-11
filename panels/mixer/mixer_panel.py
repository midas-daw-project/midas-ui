from __future__ import annotations

from typing import Callable

from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QSpinBox,
    QDoubleSpinBox,
    QVBoxLayout,
    QWidget,
)

from viewmodels.mixer_viewmodel import MixerViewModel


class MixerPanel(QWidget):
    def __init__(
        self,
        on_apply_mute: Callable[[], None],
        on_apply_gain: Callable[[], None],
        on_refresh: Callable[[], None],
    ) -> None:
        super().__init__()
        self._on_apply_mute = on_apply_mute
        self._on_apply_gain = on_apply_gain
        self._on_refresh = on_refresh

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        control_box = QGroupBox("Mixer Channel")
        form = QFormLayout(control_box)
        self.channel_input = QSpinBox()
        self.channel_input.setRange(1, 2048)
        self.channel_input.setValue(1)
        self.mute_input = QCheckBox("Muted")
        self.gain_input = QDoubleSpinBox()
        self.gain_input.setRange(0.0, 2.0)
        self.gain_input.setSingleStep(0.05)
        self.gain_input.setValue(1.0)

        self.apply_mute_button = QPushButton("Apply Mute")
        self.apply_gain_button = QPushButton("Apply Gain")
        self.refresh_button = QPushButton("Refresh")

        form.addRow("Channel", self.channel_input)
        form.addRow("Mute", self.mute_input)
        form.addRow("Gain", self.gain_input)
        form.addRow(self.apply_mute_button)
        form.addRow(self.apply_gain_button)
        form.addRow(self.refresh_button)
        layout.addWidget(control_box)

        status_box = QGroupBox("Status")
        status_layout = QVBoxLayout(status_box)
        self.status_label = QLabel("Channel 1 | muted=false | gain=1.0")
        self.error_label = QLabel("Error: ")
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.error_label)
        layout.addWidget(status_box)

        self.apply_mute_button.clicked.connect(self._on_apply_mute)
        self.apply_gain_button.clicked.connect(self._on_apply_gain)
        self.refresh_button.clicked.connect(self._on_refresh)

    def selected_channel(self) -> int:
        return int(self.channel_input.value())

    def selected_mute(self) -> bool:
        return bool(self.mute_input.isChecked())

    def selected_gain(self) -> float:
        return float(self.gain_input.value())

    def render(self, vm: MixerViewModel) -> None:
        channel = vm.selected_channel_id
        state = None
        for item in vm.channels:
            if item.channel_id == channel:
                state = item
                break
        if state is None:
            self.status_label.setText(f"Channel {channel} | muted=false | gain=1.0")
        else:
            self.status_label.setText(
                f"Channel {state.channel_id} | muted={'true' if state.muted else 'false'} | gain={state.gain:.3f}"
            )
            self.mute_input.setChecked(state.muted)
            self.gain_input.setValue(state.gain)
        self.error_label.setText(f"Error: {vm.last_error}")
