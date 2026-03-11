from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TransportViewModel:
    play_state: str = "stopped"
    track_channel: int = 1
    mixer_subsystem: int = 2001
    last_error: str = ""
