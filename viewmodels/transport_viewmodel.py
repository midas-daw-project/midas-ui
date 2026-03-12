from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TransportViewModel:
    play_state: str = "stopped"
    runtime_active: bool = False
    audio_lifecycle_state: str = "idle"
    render_status: str = "stopped"
    render_produced: bool = False
    track_channel: int = 1
    mixer_subsystem: int = 2001
    last_error: str = ""
