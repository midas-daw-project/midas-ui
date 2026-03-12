from __future__ import annotations

from typing import Callable

from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QListWidget,
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
        on_insert_plugin: Callable[[], None],
        on_remove_plugin: Callable[[], None],
        on_move_slot_up: Callable[[], None],
        on_move_slot_down: Callable[[], None],
        on_toggle_bypass: Callable[[], None],
        on_refresh: Callable[[], None],
    ) -> None:
        super().__init__()
        self._on_apply_mute = on_apply_mute
        self._on_apply_gain = on_apply_gain
        self._on_insert_plugin = on_insert_plugin
        self._on_remove_plugin = on_remove_plugin
        self._on_move_slot_up = on_move_slot_up
        self._on_move_slot_down = on_move_slot_down
        self._on_toggle_bypass = on_toggle_bypass
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
        self.slot_input = QSpinBox()
        self.slot_input.setRange(0, 32)
        self.slot_input.setValue(0)
        self.insert_button = QPushButton("Insert Selected Plugin")
        self.remove_button = QPushButton("Remove Slot Plugin")
        self.move_up_button = QPushButton("Move Slot Up")
        self.move_down_button = QPushButton("Move Slot Down")
        self.bypass_input = QCheckBox("Bypassed")
        self.apply_bypass_button = QPushButton("Apply Slot Bypass")
        self.refresh_button = QPushButton("Refresh")

        form.addRow("Channel", self.channel_input)
        form.addRow("Mute", self.mute_input)
        form.addRow("Gain", self.gain_input)
        form.addRow(self.apply_mute_button)
        form.addRow(self.apply_gain_button)
        form.addRow("Insert Slot", self.slot_input)
        form.addRow(self.insert_button)
        form.addRow(self.remove_button)
        form.addRow(self.move_up_button)
        form.addRow(self.move_down_button)
        form.addRow("Slot Bypass", self.bypass_input)
        form.addRow(self.apply_bypass_button)
        form.addRow(self.refresh_button)
        layout.addWidget(control_box)

        status_box = QGroupBox("Status")
        status_layout = QVBoxLayout(status_box)
        self.status_label = QLabel("Channel 1 | muted=false | gain=1.0")
        self.insert_status_label = QLabel("Insert Status: -")
        self.chain_list = QListWidget()
        self.error_label = QLabel("Error: ")
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.insert_status_label)
        status_layout.addWidget(self.chain_list)
        status_layout.addWidget(self.error_label)
        layout.addWidget(status_box)

        self.apply_mute_button.clicked.connect(self._on_apply_mute)
        self.apply_gain_button.clicked.connect(self._on_apply_gain)
        self.insert_button.clicked.connect(self._on_insert_plugin)
        self.remove_button.clicked.connect(self._on_remove_plugin)
        self.move_up_button.clicked.connect(self._on_move_slot_up)
        self.move_down_button.clicked.connect(self._on_move_slot_down)
        self.apply_bypass_button.clicked.connect(self._on_toggle_bypass)
        self.refresh_button.clicked.connect(self._on_refresh)

    def selected_channel(self) -> int:
        return int(self.channel_input.value())

    def selected_mute(self) -> bool:
        return bool(self.mute_input.isChecked())

    def selected_gain(self) -> float:
        return float(self.gain_input.value())

    def selected_slot_index(self) -> int:
        return int(self.slot_input.value())

    def selected_slot_bypass(self) -> bool:
        return bool(self.bypass_input.isChecked())

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
        self.insert_status_label.setText(f"Insert Status: {vm.last_insert_status or '-'}")
        self.chain_list.clear()
        for slot in vm.insert_chain:
            self.chain_list.addItem(
                f"slot {slot.slot_index}: {slot.plugin_name or '-'} [{slot.plugin_id or 'empty'}] "
                f"bypassed={'true' if slot.bypassed else 'false'} state={slot.load_state}"
            )
            if slot.slot_index == self.selected_slot_index():
                self.bypass_input.setChecked(slot.bypassed)
        self.error_label.setText(f"Error: {vm.last_error}")
