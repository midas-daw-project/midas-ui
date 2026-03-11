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
