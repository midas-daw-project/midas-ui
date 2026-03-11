from __future__ import annotations

import atexit
from typing import Callable, Dict

from bridge.protocol import (
    AudioStatus,
    BridgeClient,
    BridgeEvent,
    BridgeResult,
    MixerChannelStatus,
    SessionStatus,
)


class NativeBridgeClient(BridgeClient):
    """Thin Python wrapper over the compiled native bridge module."""

    def __init__(self) -> None:
        try:
            import midas_bridge_native as native_module  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "Native bridge module 'midas_bridge_native' is unavailable. "
                "Build/install the binding module (MIDAS_BUILD_PYTHON_NATIVE_MODULE=ON) "
                "with matching PYTHON_EXECUTABLE, or unset MIDAS_UI_USE_NATIVE_BRIDGE."
            ) from exc
        self._native = native_module
        self._handles: Dict[int, int] = {}
        self._next_local_handle = 1
        atexit.register(self._shutdown_dispatcher)

    def bridge_version(self) -> int:
        return int(self._native.bridge_version())

    def start_default_runtime_profile(self) -> BridgeResult:
        return _to_result(self._native.start_default_runtime_profile())

    def shutdown_runtime_profile(self) -> BridgeResult:
        return _to_result(self._native.shutdown_runtime_profile())

    def init_audio(self, device_id: str, sample_rate: int, buffer_size: int) -> BridgeResult:
        return _to_result(self._native.init_audio(device_id, sample_rate, buffer_size))

    def open_audio(self) -> BridgeResult:
        return _to_result(self._native.open_audio())

    def start_audio(self, track_channel: int, mixer_subsystem: int) -> BridgeResult:
        return _to_result(self._native.start_audio(track_channel, mixer_subsystem))

    def stop_audio(self) -> BridgeResult:
        return _to_result(self._native.stop_audio())

    def close_audio(self) -> BridgeResult:
        return _to_result(self._native.close_audio())

    def get_audio_status(self) -> AudioStatus:
        raw = self._native.get_audio_status()
        return AudioStatus(
            state=str(raw.get("state", "idle")),
            device_id=str(raw.get("device_id", "")),
            sample_rate=int(raw.get("sample_rate", 0)),
            buffer_size=int(raw.get("buffer_size", 0)),
            render_status=str(raw.get("render_status", "stopped")),
        )

    def drain_recent_events(self, max_events: int) -> list[BridgeEvent]:
        raw_events = self._native.drain_recent_events(max_events)
        events: list[BridgeEvent] = []
        for item in raw_events:
            events.append(
                BridgeEvent(
                    category=str(item.get("category", "unknown")),
                    emitter=int(item.get("emitter", 0)),
                    metadata=dict(item.get("metadata", {})),
                )
            )
        return events

    def subscribe_events(self, callback: Callable[[BridgeEvent], None]) -> int:
        def _wrapped(raw: dict) -> None:
            event = BridgeEvent(
                category=str(raw.get("category", "unknown")),
                emitter=int(raw.get("emitter", 0)),
                metadata=dict(raw.get("metadata", {})),
            )
            callback(event)

        native_handle = int(self._native.subscribe_events(_wrapped))
        local_handle = self._next_local_handle
        self._next_local_handle += 1
        self._handles[local_handle] = native_handle
        return local_handle

    def unsubscribe_events(self, handle: int) -> None:
        native_handle = self._handles.pop(handle, None)
        if native_handle is None:
            return
        self._native.unsubscribe_events(native_handle)

    def get_mixer_channels(self) -> list[MixerChannelStatus]:
        raw_channels = self._native.get_mixer_channels()
        channels: list[MixerChannelStatus] = []
        for item in raw_channels:
            values = dict(item.get("values", {}))
            channels.append(
                MixerChannelStatus(
                    channel_id=int(values.get("channel", "1")),
                    muted=str(values.get("muted", "false")).lower() == "true",
                    gain=float(values.get("gain", "1.0")),
                )
            )
        return channels

    def set_channel_mute(self, channel_id: int, muted: bool) -> BridgeResult:
        return _to_result(self._native.set_channel_mute(channel_id, bool(muted)))

    def set_channel_gain(self, channel_id: int, gain: float) -> BridgeResult:
        return _to_result(self._native.set_channel_gain(channel_id, float(gain)))

    def save_session(self) -> BridgeResult:
        return _to_result(self._native.save_session())

    def load_session(self) -> BridgeResult:
        return _to_result(self._native.load_session())

    def apply_session(self) -> BridgeResult:
        return _to_result(self._native.apply_session())

    def get_session_status(self) -> SessionStatus:
        raw = self._native.get_runtime_status()
        values = dict(raw.get("values", {}))
        return SessionStatus(
            status=str(values.get("status", "idle")),
            session_ref=str(values.get("session_ref", "default-session")),
        )

    def _shutdown_dispatcher(self) -> None:
        if hasattr(self._native, "shutdown_event_dispatcher"):
            self._native.shutdown_event_dispatcher()


def _to_result(raw: dict) -> BridgeResult:
    return BridgeResult(code=int(raw.get("code", 4)), message=str(raw.get("message", "")))
