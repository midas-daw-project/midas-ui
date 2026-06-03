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

    def load_layout_version(self) -> int:
        return int(self._settings.value("window/layout_version", 0))

    def save_layout_version(self, version: int) -> None:
        self._settings.setValue("window/layout_version", int(version))

    def load_debug_filter(self) -> str:
        value = self._settings.value("debug/event_filter", "all")
        return str(value)

    def save_debug_filter(self, value: str) -> None:
        self._settings.setValue("debug/event_filter", value)

    def load_startup_sound_enabled(self) -> bool:
        value = self._settings.value("startup_sound/enabled", True)
        return str(value).lower() not in {"0", "false", "no"}

    def save_startup_sound_enabled(self, enabled: bool) -> None:
        self._settings.setValue("startup_sound/enabled", bool(enabled))

    def load_startup_sound_volume(self) -> float:
        value = float(self._settings.value("startup_sound/volume", 0.12))
        return max(0.0, min(1.0, value))

    def save_startup_sound_volume(self, volume: float) -> None:
        self._settings.setValue("startup_sound/volume", max(0.0, min(1.0, float(volume))))

    def load_startup_sound_path(self) -> str:
        return str(
            self._settings.value(
                "startup_sound/path",
                "/Users/matthewperalta/Documents/REAPER Media/MIDAS DAW Start Up Rumble.wav",
            )
        )

    def save_startup_sound_path(self, path: str) -> None:
        self._settings.setValue("startup_sound/path", path)
