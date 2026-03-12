from __future__ import annotations

from bridge.protocol import BridgeClient
from viewmodels.browser_viewmodel import BrowserViewModel
from viewmodels.mixer_viewmodel import MixerViewModel
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
        self._vm.session_phase = session.phase
        self._vm.session_dirty = session.dirty
        self._vm.session_storage_path = session.storage_path
        self._vm.session_storage_source = session.storage_source
        self._vm.session_last_operation = session.last_operation
        self._vm.transport_state = transport.play_state
        self._vm.audio_state = runtime.audio.state
        self._vm.runtime_active = transport.runtime_active or runtime.runtime_started
        self._vm.render_status = runtime.audio.render_status
        self._vm.mixer_channel_count = len(channels)
        self._vm.muted_channel_count = sum(1 for channel in channels if channel.muted)

    def ingest_browser_state(self, browser_vm: BrowserViewModel) -> None:
        self._vm.plugin_count = len(browser_vm.plugins)
        self._vm.available_plugin_count = sum(1 for plugin in browser_vm.plugins if plugin.available)
        self._vm.selected_plugin_name = browser_vm.selected_name

    def ingest_mixer_state(self, mixer_vm: MixerViewModel) -> None:
        self._vm.inserted_plugin_count = len([slot for slot in mixer_vm.insert_chain if slot.plugin_id])
        if mixer_vm.insert_chain:
            first = mixer_vm.insert_chain[0]
            bypass = "bypassed" if first.bypassed else "active"
            self._vm.selected_insert_summary = (
                f"ch{first.channel_id}:slot{first.slot_index}:{first.plugin_name}:{bypass}:{first.load_state}:{first.host_lifecycle_state}"
            )
        else:
            self._vm.selected_insert_summary = ""
