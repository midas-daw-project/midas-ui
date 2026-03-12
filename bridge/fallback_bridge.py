from __future__ import annotations

from typing import Callable, Dict
from typing import List

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


class FallbackBridgeClient(BridgeClient):
    """Development fallback until native bridge bindings are available."""

    def __init__(self) -> None:
        self._status = AudioStatus()
        self._events: List[BridgeEvent] = []
        self._runtime_started = False
        self._callbacks: Dict[int, Callable[[BridgeEvent], None]] = {}
        self._next_handle = 1
        self._mixer_channels: Dict[int, MixerChannelStatus] = {
            1: MixerChannelStatus(channel_id=1, muted=False, gain=1.0)
        }
        self._session = SessionStatus(status="idle", session_ref="local-session")
        self._transport = TransportStatus(play_state="stopped")
        self._track_channel = 0

    def bridge_version(self) -> int:
        return 1

    def start_default_runtime_profile(self) -> BridgeResult:
        self._runtime_started = True
        self._publish(BridgeEvent(category="session", emitter=0, metadata={"status": "runtime_started"}))
        return BridgeResult()

    def shutdown_runtime_profile(self) -> BridgeResult:
        self._runtime_started = False
        self._status = AudioStatus()
        self._publish(BridgeEvent(category="session", emitter=0, metadata={"status": "runtime_stopped"}))
        return BridgeResult()

    def init_audio(self, device_id: str, sample_rate: int, buffer_size: int) -> BridgeResult:
        if not self._runtime_started:
            return BridgeResult(code=3, message="runtime profile not started")
        self._status.state = "initialized"
        self._status.device_id = device_id
        self._status.sample_rate = sample_rate
        self._status.buffer_size = buffer_size
        self._publish(BridgeEvent(category="device", emitter=2002, metadata={"action": "init"}))
        return BridgeResult()

    def open_audio(self) -> BridgeResult:
        if self._status.state not in {"initialized", "closed"}:
            return BridgeResult(code=3, message="audio not initialized")
        self._status.state = "opened"
        self._publish(BridgeEvent(category="device", emitter=2002, metadata={"action": "open"}))
        return BridgeResult()

    def start_audio(self, track_channel: int, mixer_subsystem: int) -> BridgeResult:
        if self._status.state != "opened":
            return BridgeResult(code=3, message="audio not opened")
        self._status.state = "started"
        self._status.render_status = "no_callback"
        self._status.render_produced = False
        self._status.render_frames_produced = 0
        self._status.render_frames_requested = 0
        self._status.render_channel_count = 2
        self._status.track_channel = int(track_channel)
        self._status.tracked_muted = self._mixer_channels.get(track_channel, MixerChannelStatus()).muted
        self._status.tracked_gain = self._mixer_channels.get(track_channel, MixerChannelStatus()).gain
        self._track_channel = int(track_channel)
        self._transport.play_state = "playing"
        self._publish(
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
        self._status.render_produced = False
        self._status.render_frames_produced = 0
        self._status.render_frames_requested = 0
        self._status.render_channel_count = 0
        self._transport.play_state = "stopped"
        self._publish(BridgeEvent(category="transport", emitter=2002, metadata={"action": "stop"}))
        return BridgeResult()

    def close_audio(self) -> BridgeResult:
        if self._status.state not in {"opened", "initialized"}:
            return BridgeResult(code=3, message="audio not open")
        self._status.state = "idle"
        self._status.device_id = ""
        self._status.sample_rate = 0
        self._status.buffer_size = 0
        self._status.render_status = "stopped"
        self._status.render_produced = False
        self._status.render_frames_produced = 0
        self._status.render_frames_requested = 0
        self._status.render_channel_count = 0
        self._status.track_channel = 0
        self._status.tracked_muted = False
        self._status.tracked_gain = 1.0
        self._track_channel = 0
        self._publish(BridgeEvent(category="device", emitter=2002, metadata={"action": "close"}))
        return BridgeResult()

    def get_audio_status(self) -> AudioStatus:
        return AudioStatus(
            state=self._status.state,
            device_id=self._status.device_id,
            sample_rate=self._status.sample_rate,
            buffer_size=self._status.buffer_size,
            render_status=self._status.render_status,
            render_produced=self._status.render_produced,
            render_frames_produced=self._status.render_frames_produced,
            render_frames_requested=self._status.render_frames_requested,
            render_channel_count=self._status.render_channel_count,
            track_channel=self._status.track_channel,
            tracked_muted=self._status.tracked_muted,
            tracked_gain=self._status.tracked_gain,
        )

    def drain_recent_events(self, max_events: int) -> List[BridgeEvent]:
        if max_events <= 0:
            return []
        chunk = self._events[:max_events]
        self._events = self._events[max_events:]
        return chunk

    def subscribe_events(self, callback: Callable[[BridgeEvent], None]) -> int:
        handle = self._next_handle
        self._next_handle += 1
        self._callbacks[handle] = callback
        return handle

    def unsubscribe_events(self, handle: int) -> None:
        self._callbacks.pop(handle, None)

    def get_mixer_channels(self) -> List[MixerChannelStatus]:
        return [MixerChannelStatus(channel_id=c.channel_id, muted=c.muted, gain=c.gain)
                for c in self._mixer_channels.values()]

    def set_channel_mute(self, channel_id: int, muted: bool) -> BridgeResult:
        channel = self._mixer_channels.setdefault(channel_id, MixerChannelStatus(channel_id=channel_id))
        channel.muted = muted
        if int(channel_id) == self._track_channel:
            self._status.tracked_muted = muted
        self._publish(
            BridgeEvent(
                category="mixer",
                emitter=2001,
                metadata={"channel": str(channel_id), "muted": "true" if muted else "false"},
            )
        )
        return BridgeResult()

    def set_channel_gain(self, channel_id: int, gain: float) -> BridgeResult:
        channel = self._mixer_channels.setdefault(channel_id, MixerChannelStatus(channel_id=channel_id))
        channel.gain = float(gain)
        if int(channel_id) == self._track_channel:
            self._status.tracked_gain = float(gain)
        self._publish(
            BridgeEvent(
                category="mixer",
                emitter=2001,
                metadata={"channel": str(channel_id), "gain": f"{channel.gain:.6f}"},
            )
        )
        return BridgeResult()

    def save_session(self) -> BridgeResult:
        self._session.status = "saved"
        self._publish(
            BridgeEvent(
                category="session",
                emitter=2003,
                metadata={"action": "save", "status": self._session.status, "session_ref": self._session.session_ref},
            )
        )
        return BridgeResult()

    def load_session(self) -> BridgeResult:
        self._session.status = "loaded"
        self._publish(
            BridgeEvent(
                category="session",
                emitter=2003,
                metadata={"action": "load", "status": self._session.status, "session_ref": self._session.session_ref},
            )
        )
        return BridgeResult()

    def apply_session(self) -> BridgeResult:
        self._session.status = "applied"
        self._publish(
            BridgeEvent(
                category="session",
                emitter=2003,
                metadata={"action": "apply", "status": self._session.status, "session_ref": self._session.session_ref},
            )
        )
        return BridgeResult()

    def get_session_status(self) -> SessionStatus:
        return SessionStatus(status=self._session.status, session_ref=self._session.session_ref)

    def play_transport(self, track_channel: int, mixer_subsystem: int) -> BridgeResult:
        return self.start_audio(track_channel, mixer_subsystem)

    def stop_transport(self) -> BridgeResult:
        return self.stop_audio()

    def get_transport_status(self) -> TransportStatus:
        return TransportStatus(
            play_state=self._transport.play_state,
            runtime_active=self._status.state == "started",
            audio_lifecycle_state=self._status.state,
            render_status=self._status.render_status,
            render_produced=self._status.render_produced,
        )

    def get_runtime_status(self) -> RuntimeStatus:
        return RuntimeStatus(
            runtime_started=self._runtime_started,
            bridge_version=self.bridge_version(),
            audio=self.get_audio_status(),
        )

    def _publish(self, event: BridgeEvent) -> None:
        self._events.append(event)
        for callback in list(self._callbacks.values()):
            callback(event)
