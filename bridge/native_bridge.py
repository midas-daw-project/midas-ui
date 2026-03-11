from __future__ import annotations

from bridge.protocol import AudioStatus, BridgeClient, BridgeEvent, BridgeResult


class NativeBridgeClient(BridgeClient):
    """Thin Python wrapper over the compiled native bridge module."""

    def __init__(self) -> None:
        try:
            import midas_bridge_native as native_module  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "Native bridge module 'midas_bridge_native' is unavailable. "
                "Build/install the binding module or unset MIDAS_UI_USE_NATIVE_BRIDGE."
            ) from exc
        self._native = native_module

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


def _to_result(raw: dict) -> BridgeResult:
    return BridgeResult(code=int(raw.get("code", 4)), message=str(raw.get("message", "")))
