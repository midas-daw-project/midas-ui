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
    runtime_started: bool = False
    render_produced: bool = False
    render_frames_produced: int = 0
    render_frames_requested: int = 0
    render_channel_count: int = 0
    tracked_channel: int = 0
    tracked_muted: bool = False
    tracked_gain: float = 1.0
    last_error: str = ""
