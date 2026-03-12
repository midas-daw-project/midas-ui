from __future__ import annotations

import atexit
from typing import Callable, Dict

from bridge.protocol import (
    AudioStatus,
    BridgeClient,
    BridgeEvent,
    BridgeResult,
    MixerChannelStatus,
    RuntimeStatus,
    SessionStatus,
    TransportStatus,
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
            render_produced=bool(raw.get("render_produced", False)),
            render_frames_produced=int(raw.get("render_frames_produced", 0)),
            render_frames_requested=int(raw.get("render_frames_requested", 0)),
            render_channel_count=int(raw.get("render_channel_count", 0)),
            track_channel=int(raw.get("track_channel", 0)),
            tracked_muted=bool(raw.get("tracked_muted", False)),
            tracked_gain=float(raw.get("tracked_gain", 1.0)),
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
        raw = self._native.get_session_status()
        values = dict(raw.get("values", {}))
        return SessionStatus(
            status=str(values.get("status", "idle")),
            session_ref=str(values.get("session_ref", "default-session")),
        )

    def play_transport(self, track_channel: int, mixer_subsystem: int) -> BridgeResult:
        return self.start_audio(track_channel, mixer_subsystem)

    def stop_transport(self) -> BridgeResult:
        return self.stop_audio()

    def get_transport_status(self) -> TransportStatus:
        runtime = self.get_runtime_status()
        return TransportStatus(
            play_state="playing" if runtime.audio.state == "started" else "stopped",
            runtime_active=runtime.audio.state == "started",
            audio_lifecycle_state=runtime.audio.state,
            render_status=runtime.audio.render_status,
            render_produced=runtime.audio.render_produced,
        )

    def get_runtime_status(self) -> RuntimeStatus:
        raw = self._native.get_runtime_status()
        values = dict(raw.get("values", {}))

        def _as_int(key: str, fallback: int = 0) -> int:
            try:
                return int(values.get(key, str(fallback)))
            except (TypeError, ValueError):
                return fallback

        def _as_float(key: str, fallback: float = 0.0) -> float:
            try:
                return float(values.get(key, str(fallback)))
            except (TypeError, ValueError):
                return fallback

        def _as_bool(key: str, fallback: bool = False) -> bool:
            raw_value = str(values.get(key, "true" if fallback else "false")).strip().lower()
            return raw_value in {"1", "true", "yes", "on"}

        audio = AudioStatus(
            state=str(values.get("state", "idle")),
            device_id=str(values.get("device_id", "")),
            sample_rate=_as_int("sample_rate", 0),
            buffer_size=_as_int("buffer_size", 0),
            render_status=str(values.get("render_status", "stopped")),
            render_produced=_as_bool("render_produced", False),
            render_frames_produced=_as_int("render_frames_produced", 0),
            render_frames_requested=_as_int("render_frames_requested", 0),
            render_channel_count=_as_int("render_channel_count", 0),
            track_channel=_as_int("track_channel", 0),
            tracked_muted=_as_bool("muted", False),
            tracked_gain=_as_float("gain", 1.0),
        )
        return RuntimeStatus(
            runtime_started=_as_bool("runtime_started", False),
            bridge_version=_as_int("bridge_version", self.bridge_version()),
            audio=audio,
        )

    def _shutdown_dispatcher(self) -> None:
        if hasattr(self._native, "shutdown_event_dispatcher"):
            self._native.shutdown_event_dispatcher()


def _to_result(raw: dict) -> BridgeResult:
    return BridgeResult(code=int(raw.get("code", 4)), message=str(raw.get("message", "")))
