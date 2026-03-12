from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SessionViewModel:
    status: str = "idle"
    phase: str = "none"
    dirty: bool = False
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
