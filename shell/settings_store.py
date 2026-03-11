from __future__ import annotations

from PySide6.QtCore import QSettings, QByteArray


class ShellSettingsStore:
    def __init__(self) -> None:
        self._settings = QSettings("MIDAS", "MIDAS-UI")

    def load_geometry(self) -> QByteArray | None:
        value = self._settings.value("window/geometry")
        if isinstance(value, QByteArray) and not value.isEmpty():
            return value
        return None

    def save_geometry(self, geometry: QByteArray) -> None:
        self._settings.setValue("window/geometry", geometry)

    def load_window_state(self) -> QByteArray | None:
        value = self._settings.value("window/state")
        if isinstance(value, QByteArray) and not value.isEmpty():
            return value
        return None

    def save_window_state(self, state: QByteArray) -> None:
        self._settings.setValue("window/state", state)

    def load_debug_filter(self) -> str:
        value = self._settings.value("debug/event_filter", "all")
        return str(value)

    def save_debug_filter(self, value: str) -> None:
        self._settings.setValue("debug/event_filter", value)
