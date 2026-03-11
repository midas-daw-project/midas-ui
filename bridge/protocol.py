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
