from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AudioViewModel:
    state: str = "idle"
    device_id: str = ""
    sample_rate: int = 48000
    buffer_size: int = 256
    track_channel: int = 1
    mixer_subsystem: int = 2001
    render_status: str = "stopped"
    last_error: str = ""
