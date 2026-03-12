from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Protocol


@dataclass(slots=True)
class BridgeResult:
    code: int = 0
    message: str = ""

    @property
    def ok(self) -> bool:
        return self.code == 0


@dataclass(slots=True)
class AudioStatus:
    state: str = "idle"
    device_id: str = ""
    sample_rate: int = 0
    buffer_size: int = 0
    render_status: str = "stopped"
    render_produced: bool = False
    render_frames_produced: int = 0
    render_frames_requested: int = 0
    render_channel_count: int = 0
    track_channel: int = 0
    tracked_muted: bool = False
    tracked_gain: float = 1.0


@dataclass(slots=True)
class MixerChannelStatus:
    channel_id: int = 1
    muted: bool = False
    gain: float = 1.0


@dataclass(slots=True)
class SessionStatus:
    status: str = "idle"
    session_ref: str = ""


@dataclass(slots=True)
class TransportStatus:
    play_state: str = "stopped"
    runtime_active: bool = False
    audio_lifecycle_state: str = "idle"
    render_status: str = "stopped"
    render_produced: bool = False


@dataclass(slots=True)
class RuntimeStatus:
    runtime_started: bool = False
    bridge_version: int = 0
    audio: AudioStatus = field(default_factory=AudioStatus)


@dataclass(slots=True)
class PluginRegistryEntry:
    plugin_id: str
    name: str
    category: str
    vendor: str
    available: bool = True
    source: str = "builtin"


@dataclass(slots=True)
class BridgeEvent:
    category: str
    emitter: int
    metadata: Dict[str, str] = field(default_factory=dict)


class BridgeClient(Protocol):
    def bridge_version(self) -> int:
        ...

    def start_default_runtime_profile(self) -> BridgeResult:
        ...

    def shutdown_runtime_profile(self) -> BridgeResult:
        ...

    def init_audio(self, device_id: str, sample_rate: int, buffer_size: int) -> BridgeResult:
        ...

    def open_audio(self) -> BridgeResult:
        ...

    def start_audio(self, track_channel: int, mixer_subsystem: int) -> BridgeResult:
        ...

    def stop_audio(self) -> BridgeResult:
        ...

    def close_audio(self) -> BridgeResult:
        ...

    def get_audio_status(self) -> AudioStatus:
        ...

    def drain_recent_events(self, max_events: int) -> List[BridgeEvent]:
        ...

    def subscribe_events(self, callback: Callable[[BridgeEvent], None]) -> int:
        ...

    def unsubscribe_events(self, handle: int) -> None:
        ...

    def get_mixer_channels(self) -> List[MixerChannelStatus]:
        ...

    def set_channel_mute(self, channel_id: int, muted: bool) -> BridgeResult:
        ...

    def set_channel_gain(self, channel_id: int, gain: float) -> BridgeResult:
        ...

    def save_session(self) -> BridgeResult:
        ...

    def load_session(self) -> BridgeResult:
        ...

    def apply_session(self) -> BridgeResult:
        ...

    def get_session_status(self) -> SessionStatus:
        ...

    def play_transport(self, track_channel: int, mixer_subsystem: int) -> BridgeResult:
        ...

    def stop_transport(self) -> BridgeResult:
        ...

    def get_transport_status(self) -> TransportStatus:
        ...

    def get_runtime_status(self) -> RuntimeStatus:
        ...

    def get_plugin_registry(self) -> List[PluginRegistryEntry]:
        ...

    def refresh_plugin_registry(self) -> BridgeResult:
        ...
