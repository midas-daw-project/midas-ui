from __future__ import annotations

from bridge.protocol import BridgeClient
from viewmodels.workspace_viewmodel import WorkspaceViewModel


class WorkspaceController:
    def __init__(self, bridge: BridgeClient, viewmodel: WorkspaceViewModel) -> None:
        self._bridge = bridge
        self._vm = viewmodel

    @property
    def viewmodel(self) -> WorkspaceViewModel:
        return self._vm

    def set_bridge_identity(self, mode: str, version: int) -> None:
        self._vm.bridge_mode = mode
        self._vm.bridge_version = int(version)

    def mark_action(self, action: str) -> None:
        self._vm.last_action = action

    def refresh_overview(self) -> None:
        session = self._bridge.get_session_status()
        transport = self._bridge.get_transport_status()
        runtime = self._bridge.get_runtime_status()
        channels = self._bridge.get_mixer_channels()

        self._vm.session_ref = session.session_ref or self._vm.session_ref
        self._vm.session_status = session.status
        self._vm.transport_state = transport.play_state
        self._vm.audio_state = runtime.audio.state
        self._vm.runtime_active = transport.runtime_active or runtime.runtime_started
        self._vm.render_status = runtime.audio.render_status
        self._vm.mixer_channel_count = len(channels)
        self._vm.muted_channel_count = sum(1 for channel in channels if channel.muted)
