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
        self.manual_refresh_button = QPushButton("Manual Refresh")
        bridge_form.addRow(self.mode_label)
        bridge_form.addRow(self.version_label)
        bridge_form.addRow(self.subscription_label)
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

    def set_domain_statuses(self, *, audio: str, mixer: str, session: str, transport: str) -> None:
        self.audio_label.setText(f"Audio: {audio}")
        self.mixer_label.setText(f"Mixer: {mixer}")
        self.session_label.setText(f"Session: {session}")
        self.transport_label.setText(f"Transport: {transport}")

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
