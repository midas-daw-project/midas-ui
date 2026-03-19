from __future__ import annotations

from collections import deque
from datetime import datetime
from typing import Callable, Deque

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from bridge.protocol import BridgeEvent


class DebugPanel(QWidget):
    def __init__(self, on_manual_refresh: Callable[[], None]) -> None:
        super().__init__()
        self._on_manual_refresh = on_manual_refresh
        self._events: Deque[BridgeEvent] = deque(maxlen=300)

        root = QVBoxLayout(self)

        bridge_box = QGroupBox("Bridge")
        bridge_form = QFormLayout(bridge_box)
        self.mode_label = QLabel("Mode: unknown")
        self.version_label = QLabel("Version: unknown")
        self.subscription_label = QLabel("Subscription: inactive")
        self.backend_label = QLabel("Backend: -")
        self.capabilities_label = QLabel("Capabilities: -")
        self.scope_label = QLabel("Support Scope: -")
        self.catalog_label = QLabel("Catalog: -")
        self.slot_adapter_label = QLabel("Selected Slot Adapter: -")
        self.slot_runtime_label = QLabel("Selected Slot Runtime: -")
        self.manual_refresh_button = QPushButton("Manual Refresh")
        bridge_form.addRow(self.mode_label)
        bridge_form.addRow(self.version_label)
        bridge_form.addRow(self.subscription_label)
        bridge_form.addRow(self.backend_label)
        bridge_form.addRow(self.capabilities_label)
        bridge_form.addRow(self.scope_label)
        bridge_form.addRow(self.catalog_label)
        bridge_form.addRow(self.slot_adapter_label)
        bridge_form.addRow(self.slot_runtime_label)
        bridge_form.addRow(self.manual_refresh_button)

        summary_box = QGroupBox("Summary")
        summary_form = QFormLayout(summary_box)
        self.latest_result_label = QLabel("Latest Result: -")
        self.audio_label = QLabel("Audio: -")
        self.mixer_label = QLabel("Mixer: -")
        self.session_label = QLabel("Session: -")
        self.transport_label = QLabel("Transport: -")
        summary_form.addRow(self.latest_result_label)
        summary_form.addRow(self.audio_label)
        summary_form.addRow(self.mixer_label)
        summary_form.addRow(self.session_label)
        summary_form.addRow(self.transport_label)

        instance_box = QGroupBox("Managed Instances")
        instance_layout = QVBoxLayout(instance_box)
        self.instance_summary_label = QLabel("Managed Instances: active=0 selected=-")
        self.instance_log = QTextEdit()
        self.instance_log.setReadOnly(True)
        instance_layout.addWidget(self.instance_summary_label)
        instance_layout.addWidget(self.instance_log)

        transition_box = QGroupBox("Adapter Transition History")
        transition_layout = QVBoxLayout(transition_box)
        self.transition_summary_label = QLabel("Transitions: 0")
        self.transition_log = QTextEdit()
        self.transition_log.setReadOnly(True)
        transition_layout.addWidget(self.transition_summary_label)
        transition_layout.addWidget(self.transition_log)

        event_box = QGroupBox("Events")
        event_layout = QVBoxLayout(event_box)
        self.event_filter = QComboBox()
        self.event_filter.addItems(["all", "device", "transport", "mixer", "session", "state", "meter", "subsystem"])
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        event_layout.addWidget(self.event_filter)
        event_layout.addWidget(self.log)

        self.manual_refresh_button.clicked.connect(self._on_manual_refresh)
        self.event_filter.currentTextChanged.connect(self._render_log)

        root.addWidget(bridge_box)
        root.addWidget(summary_box)
        root.addWidget(instance_box)
        root.addWidget(transition_box)
        root.addWidget(event_box)

    def set_bridge_info(self, *, mode: str, version: int, subscription_active: bool, fallback_polling: bool) -> None:
        self.mode_label.setText(f"Mode: {mode}")
        self.version_label.setText(f"Version: {version}")
        label = "active" if subscription_active else "inactive"
        if fallback_polling:
            label += " (polling fallback)"
        self.subscription_label.setText(f"Subscription: {label}")

    def set_subscription_state(self, active: bool) -> None:
        current = self.subscription_label.text()
        fallback = "(polling fallback)" in current
        label = "active" if active else "inactive"
        if fallback:
            label += " (polling fallback)"
        self.subscription_label.setText(f"Subscription: {label}")

    def set_backend_summary(
        self,
        *,
        backend_name: str,
        supports_create: bool,
        supports_destroy: bool,
        supports_query: bool,
        support_scope: str,
        selected_slot_reason: str,
        selected_slot_message: str,
        selected_backend_name: str,
        selected_backend_handle: str,
        selected_handle_state: str,
        selected_terminal: bool,
        selected_retryable: bool,
        selected_reason_source: str,
        selected_descriptor_id: str,
        selected_descriptor_kind: str,
        selected_descriptor_ref: str,
        catalog_source_label: str,
        catalog_source_version: str,
        catalog_descriptor_count: int,
        catalog_valid_descriptor_count: int,
        catalog_policy_supported_descriptor_count: int,
    ) -> None:
        self.backend_label.setText(f"Backend: {backend_name or '-'}")
        self.capabilities_label.setText(
            "Capabilities: "
            f"create={'yes' if supports_create else 'no'}, "
            f"destroy={'yes' if supports_destroy else 'no'}, "
            f"query={'yes' if supports_query else 'no'}"
        )
        self.scope_label.setText(f"Support Scope: {support_scope or '-'}")
        self.catalog_label.setText(
            "Catalog: "
            f"source={catalog_source_label or '-'}"
            f"@{catalog_source_version or '-'} "
            f"descriptors={catalog_descriptor_count} "
            f"valid={catalog_valid_descriptor_count} "
            f"policy_supported={catalog_policy_supported_descriptor_count}"
        )
        if selected_slot_reason or selected_slot_message:
            self.slot_adapter_label.setText(
                f"Selected Slot Adapter: reason={selected_slot_reason or '-'} msg={selected_slot_message or '-'}"
            )
        else:
            self.slot_adapter_label.setText("Selected Slot Adapter: -")
        if (
            selected_backend_name
            or selected_backend_handle
            or selected_handle_state
            or selected_reason_source
            or selected_descriptor_id
            or selected_descriptor_kind
            or selected_descriptor_ref
        ):
            self.slot_runtime_label.setText(
                "Selected Slot Runtime: "
                f"backend={selected_backend_name or '-'} "
                f"handle={selected_backend_handle or '-'} "
                f"handle_state={selected_handle_state or '-'} "
                f"terminal={'yes' if selected_terminal else 'no'} "
                f"retryable={'yes' if selected_retryable else 'no'} "
                f"source={selected_reason_source or '-'} "
                f"descriptor={selected_descriptor_id or '-'} "
                f"({selected_descriptor_kind or '-'}:{selected_descriptor_ref or '-'})"
            )
        else:
            self.slot_runtime_label.setText("Selected Slot Runtime: -")

    def set_event_filter(self, value: str) -> None:
        index = self.event_filter.findText(value)
        if index >= 0:
            self.event_filter.setCurrentIndex(index)
        else:
            self.event_filter.setCurrentIndex(0)

    def event_filter_value(self) -> str:
        return self.event_filter.currentText()

    def set_domain_statuses(self, *, audio: str, mixer: str, session: str, transport: str) -> None:
        self.audio_label.setText(f"Audio: {audio}")
        self.mixer_label.setText(f"Mixer: {mixer}")
        self.session_label.setText(f"Session: {session}")
        self.transport_label.setText(f"Transport: {transport}")

    def set_managed_instance_status(self, *, summary: str, rows: list[str]) -> None:
        self.instance_summary_label.setText(f"Managed Instances: {summary}")
        self.instance_log.setPlainText("\n".join(rows))

    def set_transition_history(self, *, summary: str, rows: list[str]) -> None:
        self.transition_summary_label.setText(f"Transitions: {summary}")
        self.transition_log.setPlainText("\n".join(rows))

    def append_event(self, event: BridgeEvent) -> None:
        self._events.append(event)
        self._render_log()

    def append_result(self, operation: str, code: int, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.latest_result_label.setText(
            f"Latest Result: {timestamp} | {operation} | code={code} | {message or 'ok'}"
        )

    def _render_log(self) -> None:
        selected = self.event_filter.currentText()
        lines: list[str] = []
        for event in self._events:
            if selected != "all" and event.category != selected:
                continue
            timestamp = datetime.now().strftime("%H:%M:%S")
            lines.append(f"[{timestamp}] [{event.category}] emitter={event.emitter} metadata={event.metadata}")
        self.log.setPlainText("\n".join(lines))
        self.log.moveCursor(QTextCursor.End)
