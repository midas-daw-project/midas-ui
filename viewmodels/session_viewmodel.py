from __future__ import annotations

from dataclasses import dataclass, field

from bridge.protocol import DiscoverableSessionEntry, RecentSessionEntry


@dataclass(slots=True)
class SessionViewModel:
    status: str = "idle"
    phase: str = "none"
    dirty: bool = False
    restore_phase: str = "idle"
    runtime_hydrated: bool = False
    restore_guidance: str = "Create or load a session to begin."
    session_ref: str = "default-session"
    storage_path: str = ""
    storage_source: str = ""
    last_operation: str = "none"
    last_save_epoch: int = 0
    last_load_epoch: int = 0
    last_apply_epoch: int = 0
    last_save_status: str = ""
    last_load_status: str = ""
    last_apply_status: str = ""
    last_error: str = ""
    recent_sessions: list[RecentSessionEntry] = field(default_factory=list)
    discoverable_sessions: list[DiscoverableSessionEntry] = field(default_factory=list)
    storage_root: str = ""
