from __future__ import annotations

from typing import List

from bridge.protocol import AudioStatus, BridgeClient, BridgeEvent, BridgeResult


class FallbackBridgeClient(BridgeClient):
    """Development fallback until native bridge bindings are available."""

    def __init__(self) -> None:
        self._status = AudioStatus()
        self._events: List[BridgeEvent] = []
        self._runtime_started = False

    def bridge_version(self) -> int:
        return 1

    def start_default_runtime_profile(self) -> BridgeResult:
        self._runtime_started = True
        self._events.append(BridgeEvent(category="session", emitter=0, metadata={"status": "runtime_started"}))
        return BridgeResult()

    def shutdown_runtime_profile(self) -> BridgeResult:
        self._runtime_started = False
        self._status = AudioStatus()
        self._events.append(BridgeEvent(category="session", emitter=0, metadata={"status": "runtime_stopped"}))
        return BridgeResult()

    def init_audio(self, device_id: str, sample_rate: int, buffer_size: int) -> BridgeResult:
        if not self._runtime_started:
            return BridgeResult(code=3, message="runtime profile not started")
        self._status.state = "initialized"
        self._status.device_id = device_id
        self._status.sample_rate = sample_rate
        self._status.buffer_size = buffer_size
        self._events.append(BridgeEvent(category="device", emitter=2002, metadata={"action": "init"}))
        return BridgeResult()

    def open_audio(self) -> BridgeResult:
        if self._status.state not in {"initialized", "closed"}:
            return BridgeResult(code=3, message="audio not initialized")
        self._status.state = "opened"
        self._events.append(BridgeEvent(category="device", emitter=2002, metadata={"action": "open"}))
        return BridgeResult()

    def start_audio(self, track_channel: int, mixer_subsystem: int) -> BridgeResult:
        if self._status.state != "opened":
            return BridgeResult(code=3, message="audio not opened")
        self._status.state = "started"
        self._status.render_status = "no_callback"
        self._events.append(
            BridgeEvent(
                category="device",
                emitter=2002,
                metadata={
                    "action": "start",
                    "track_channel": str(track_channel),
                    "mixer_subsystem": str(mixer_subsystem),
                },
            )
        )
        return BridgeResult()

    def stop_audio(self) -> BridgeResult:
        if self._status.state != "started":
            return BridgeResult(code=3, message="audio not started")
        self._status.state = "opened"
        self._status.render_status = "stopped"
        self._events.append(BridgeEvent(category="transport", emitter=2002, metadata={"action": "stop"}))
        return BridgeResult()

    def close_audio(self) -> BridgeResult:
        if self._status.state not in {"opened", "initialized"}:
            return BridgeResult(code=3, message="audio not open")
        self._status.state = "idle"
        self._status.device_id = ""
        self._status.sample_rate = 0
        self._status.buffer_size = 0
        self._status.render_status = "stopped"
        self._events.append(BridgeEvent(category="device", emitter=2002, metadata={"action": "close"}))
        return BridgeResult()

    def get_audio_status(self) -> AudioStatus:
        return AudioStatus(
            state=self._status.state,
            device_id=self._status.device_id,
            sample_rate=self._status.sample_rate,
            buffer_size=self._status.buffer_size,
            render_status=self._status.render_status,
        )

    def drain_recent_events(self, max_events: int) -> List[BridgeEvent]:
        if max_events <= 0:
            return []
        chunk = self._events[:max_events]
        self._events = self._events[max_events:]
        return chunk
