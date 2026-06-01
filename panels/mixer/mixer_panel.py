from __future__ import annotations

import math
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDial,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSlider,
    QTabWidget,
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
        on_move_slot_top: Callable[[], None],
        on_move_slot_bottom: Callable[[], None],
        on_toggle_bypass: Callable[[], None],
        on_toggle_channel_bypass: Callable[[], None],
        on_clear_chain: Callable[[], None],
        on_refresh_runtime_state: Callable[[], None],
        on_request_slot_load: Callable[[], None],
        on_request_slot_unload: Callable[[], None],
        on_refresh: Callable[[], None],
    ) -> None:
        super().__init__()
        self._on_apply_mute = on_apply_mute
        self._on_apply_gain = on_apply_gain
        self._on_insert_plugin = on_insert_plugin
        self._on_remove_plugin = on_remove_plugin
        self._on_move_slot_up = on_move_slot_up
        self._on_move_slot_down = on_move_slot_down
        self._on_move_slot_top = on_move_slot_top
        self._on_move_slot_bottom = on_move_slot_bottom
        self._on_toggle_bypass = on_toggle_bypass
        self._on_toggle_channel_bypass = on_toggle_channel_bypass
        self._on_clear_chain = on_clear_chain
        self._on_refresh_runtime_state = on_refresh_runtime_state
        self._on_request_slot_load = on_request_slot_load
        self._on_request_slot_unload = on_request_slot_unload
        self._on_refresh = on_refresh

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        strip_box = QGroupBox("Mixer")
        strip_layout = QGridLayout(strip_box)
        strip_layout.setContentsMargins(8, 8, 8, 8)
        strip_layout.setHorizontalSpacing(6)
        strip_layout.setVerticalSpacing(6)
        self.channel_strip_labels: list[QLabel] = []
        for name in ["Kick", "Snare", "Hi Hats", "Melody", "Bass", "Master"]:
            label = QLabel(f"{name}\n- dB\nidle")
            label.setObjectName("mixerStrip")
            label.setProperty("mixerStrip", True)
            label.setWordWrap(True)
            index = len(self.channel_strip_labels)
            strip_layout.addWidget(label, index // 3, index % 3)
            self.channel_strip_labels.append(label)
        layout.addWidget(strip_box)

        self.mixer_tabs = QTabWidget()
        self.mixer_tabs.setObjectName("mixerTabs")
        layout.addWidget(self.mixer_tabs, 1)

        channel_page = QWidget()
        control_layout = QVBoxLayout(channel_page)
        control_layout.setContentsMargins(0, 0, 0, 0)
        form = QFormLayout()
        self.channel_input = QSlider(Qt.Horizontal)
        self.channel_input.setRange(1, 16)
        self.channel_input.setValue(1)
        self.channel_value_label = QLabel("1")
        self.mute_input = QCheckBox("Muted")
        self.gain_input = QSlider(Qt.Horizontal)
        self.gain_input.setRange(0, 200)
        self.gain_input.setValue(100)
        self.gain_value_label = QLabel("0.0 dB")

        self.apply_mute_button = QPushButton("Mute")
        self.apply_gain_button = QPushButton("Gain")
        self.slot_input = QSlider(Qt.Horizontal)
        self.slot_input.setRange(0, 32)
        self.slot_input.setValue(0)
        self.slot_value_label = QLabel("0")
        self.channel_input.valueChanged.connect(lambda value: self.channel_value_label.setText(str(value)))
        self.gain_input.valueChanged.connect(
            lambda value: self.gain_value_label.setText(self._gain_to_db_label(value / 100.0))
        )
        self.slot_input.valueChanged.connect(lambda value: self.slot_value_label.setText(str(value)))
        self.insert_button = QPushButton("Insert")
        self.remove_button = QPushButton("Remove")
        self.move_up_button = QPushButton("Move Up")
        self.move_down_button = QPushButton("Move Down")
        self.move_top_button = QPushButton("Move Top")
        self.move_bottom_button = QPushButton("Move Bottom")
        self.bypass_input = QCheckBox("Bypassed")
        self.apply_bypass_button = QPushButton("Slot Bypass")
        self.channel_bypass_input = QCheckBox("Bypass All Inserts")
        self.apply_channel_bypass_button = QPushButton("Chain Bypass")
        self.clear_chain_button = QPushButton("Clear Chain")
        self.refresh_runtime_button = QPushButton("Runtime")
        self.request_load_button = QPushButton("Load")
        self.request_unload_button = QPushButton("Unload")
        self.refresh_button = QPushButton("Refresh")

        form.addRow("Channel", self._with_value_label(self.channel_input, self.channel_value_label))
        form.addRow("Mute", self.mute_input)
        form.addRow("Volume", self._with_value_label(self.gain_input, self.gain_value_label))
        form.addRow("Insert Slot", self._with_value_label(self.slot_input, self.slot_value_label))
        form.addRow("Slot Bypass", self.bypass_input)
        form.addRow("Channel Bypass", self.channel_bypass_input)
        control_layout.addLayout(form)

        action_grid = QGridLayout()
        action_grid.setHorizontalSpacing(6)
        action_grid.setVerticalSpacing(6)
        action_buttons = [
            self.apply_mute_button,
            self.apply_gain_button,
            self.insert_button,
            self.remove_button,
            self.apply_bypass_button,
            self.refresh_button,
        ]
        for index, button in enumerate(action_buttons):
            action_grid.addWidget(button, index // 2, index % 2)
        control_layout.addLayout(action_grid)

        self.status_label = QLabel("Channel 1 | muted=false | gain=1.0")
        self.selected_strip_label = QLabel("Selected Strip: Channel 1")
        self.status_label.setWordWrap(True)
        self.selected_strip_label.setWordWrap(True)
        control_layout.addWidget(self.status_label)
        control_layout.addWidget(self.selected_strip_label)
        control_layout.addStretch(1)
        self.mixer_tabs.addTab(channel_page, "Channel")

        inserts_page = QWidget()
        status_layout = QVBoxLayout(inserts_page)
        status_layout.setContentsMargins(0, 0, 0, 0)
        self.insert_status_label = QLabel("Insert Status: -")
        self.plugin_stack_label = QLabel("Plugin Stack: no inserts")
        self.plugin_stack_label.setWordWrap(True)
        self.chain_list = QListWidget()
        self.chain_list.setMinimumHeight(72)
        self.chain_list.setMaximumHeight(104)
        self.error_label = QLabel("Error: ")
        self.effect_macro_box = QGroupBox("Effect Macros")
        macro_grid = QGridLayout(self.effect_macro_box)
        self.effect_macro_dials: list[QDial] = []
        for index, (name, value) in enumerate(
            [
                ("Mix", 70),
                ("Tone", 55),
                ("Rate", 30),
                ("Feedback", 40),
            ]
        ):
            dial = QDial()
            dial.setRange(0, 100)
            dial.setValue(value)
            dial.setNotchesVisible(True)
            dial.setObjectName("effectMacroDial")
            label = QLabel(name)
            label.setAlignment(Qt.AlignCenter)
            label.setObjectName("effectMacroLabel")
            macro_grid.addWidget(dial, 0, index)
            macro_grid.addWidget(label, 1, index)
            self.effect_macro_dials.append(dial)
        insert_tools = QGridLayout()
        insert_tools.setHorizontalSpacing(6)
        insert_tools.setVerticalSpacing(6)
        advanced_buttons = [
            self.move_up_button,
            self.move_down_button,
            self.move_top_button,
            self.move_bottom_button,
            self.apply_channel_bypass_button,
            self.clear_chain_button,
            self.refresh_runtime_button,
            self.request_load_button,
            self.request_unload_button,
        ]
        for index, button in enumerate(advanced_buttons):
            insert_tools.addWidget(button, index // 2, index % 2)
        status_layout.addWidget(self.insert_status_label)
        status_layout.addWidget(self.plugin_stack_label)
        status_layout.addWidget(self.chain_list)
        status_layout.addWidget(self.effect_macro_box)
        status_layout.addLayout(insert_tools)
        status_layout.addWidget(self.error_label)
        self.mixer_tabs.addTab(inserts_page, "Inserts")

        self.apply_mute_button.clicked.connect(self._on_apply_mute)
        self.apply_gain_button.clicked.connect(self._on_apply_gain)
        self.insert_button.clicked.connect(self._on_insert_plugin)
        self.remove_button.clicked.connect(self._on_remove_plugin)
        self.move_up_button.clicked.connect(self._on_move_slot_up)
        self.move_down_button.clicked.connect(self._on_move_slot_down)
        self.move_top_button.clicked.connect(self._on_move_slot_top)
        self.move_bottom_button.clicked.connect(self._on_move_slot_bottom)
        self.apply_bypass_button.clicked.connect(self._on_toggle_bypass)
        self.apply_channel_bypass_button.clicked.connect(self._on_toggle_channel_bypass)
        self.clear_chain_button.clicked.connect(self._on_clear_chain)
        self.refresh_runtime_button.clicked.connect(self._on_refresh_runtime_state)
        self.request_load_button.clicked.connect(self._on_request_slot_load)
        self.request_unload_button.clicked.connect(self._on_request_slot_unload)
        self.refresh_button.clicked.connect(self._on_refresh)

    def selected_channel(self) -> int:
        return int(self.channel_input.value())

    def selected_mute(self) -> bool:
        return bool(self.mute_input.isChecked())

    def selected_gain(self) -> float:
        return float(self.gain_input.value()) / 100.0

    def selected_slot_index(self) -> int:
        return int(self.slot_input.value())

    def selected_slot_bypass(self) -> bool:
        return bool(self.bypass_input.isChecked())

    def selected_channel_bypass(self) -> bool:
        return bool(self.channel_bypass_input.isChecked())

    def render(self, vm: MixerViewModel) -> None:
        channel = vm.selected_channel_id
        state = None
        for item in vm.channels:
            if item.channel_id == channel:
                state = item
                break
        if state is None:
            self.status_label.setText(f"Channel {channel} | muted=false | volume=0.0 dB")
            self.selected_strip_label.setText(f"Selected Strip: Channel {channel} | clean | volume=0.0 dB")
        else:
            db_label = self._gain_to_db_label(state.gain)
            self.status_label.setText(
                f"Channel {state.channel_id} | muted={'true' if state.muted else 'false'} | volume={db_label}"
            )
            self.selected_strip_label.setText(
                f"Selected Strip: Channel {state.channel_id} | "
                f"{'muted' if state.muted else 'active'} | volume={db_label}"
            )
            self.mute_input.setChecked(state.muted)
            self.gain_input.setValue(round(state.gain * 100))
        self._render_channel_strips(vm)
        self.insert_status_label.setText(f"Insert Status: {vm.last_insert_status or '-'}")
        self.chain_list.clear()
        all_bypassed = bool(vm.insert_chain) and all(slot.bypassed for slot in vm.insert_chain)
        self.channel_bypass_input.setChecked(all_bypassed)
        self.plugin_stack_label.setText(
            f"Plugin Stack: {len(vm.insert_chain)} insert{'s' if len(vm.insert_chain) != 1 else ''} | "
            f"{'all bypassed' if all_bypassed else 'active path'}"
        )
        for slot in vm.insert_chain:
            self.chain_list.addItem(
                f"Slot {slot.slot_index}: {slot.plugin_name or slot.plugin_id or 'Empty'}\n"
                f"Intent: {'bypassed' if slot.bypassed else 'active'} | "
                f"Runtime: {slot.load_state} | Host: {slot.host_lifecycle_state}\n"
                f"Instance: {slot.managed_instance_id or slot.placeholder_instance_id or '-'} | "
                f"Handle: {slot.managed_instance_backend_handle or '-'} | "
                f"Reason: {slot.loader_reason_code or slot.managed_instance_adapter_reason_code or '-'}"
            )
            if slot.slot_index == self.selected_slot_index():
                self.bypass_input.setChecked(slot.bypassed)
        self.error_label.setText(f"Error: {vm.last_error}")

    @staticmethod
    def _with_value_label(control: QWidget, label: QLabel) -> QWidget:
        wrapper = QWidget()
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(control, 1)
        label.setMinimumWidth(42)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(label)
        return wrapper

    def _render_channel_strips(self, vm: MixerViewModel) -> None:
        channel_map = {channel.channel_id: channel for channel in vm.channels}
        names = ["Kick", "Snare", "Hi Hats", "Melody", "Bass", "Master"]
        for index, label in enumerate(self.channel_strip_labels, start=1):
            channel = channel_map.get(index)
            name = names[index - 1]
            if channel is None:
                label.setText(f"{name}\n- dB\nidle")
                continue
            db_hint = self._gain_to_db_label(channel.gain)
            state = "muted" if channel.muted else "active"
            label.setText(f"{name}\n{db_hint}\n{state}")

    @staticmethod
    def _gain_to_db_label(gain: float) -> str:
        if gain <= 0:
            return "-inf dB"
        db_value = 20 * math.log10(gain)
        return f"{db_value:+.1f} dB"
