from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class WorkspaceViewModel:
    workspace_title: str = "MIDAS Workspace"
    workspace_mode: str = "Shell / Runtime Overview"
    bridge_mode: str = "unknown"
    bridge_version: int = 0
    session_ref: str = "default-session"
    session_status: str = "idle"
    audio_state: str = "idle"
    transport_state: str = "stopped"
    runtime_active: bool = False
    render_status: str = "stopped"
    mixer_channel_count: int = 0
    muted_channel_count: int = 0
    plugin_count: int = 0
    available_plugin_count: int = 0
    selected_plugin_name: str = ""
    last_action: str = "Ready"
