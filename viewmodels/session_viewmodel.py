from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SessionViewModel:
    status: str = "idle"
    session_ref: str = "default-session"
    last_save_status: str = ""
    last_load_status: str = ""
    last_apply_status: str = ""
    last_error: str = ""
