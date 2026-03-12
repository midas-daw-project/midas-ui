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
        recents = self._bridge.get_recent_sessions()
        discoverable = self._bridge.get_discoverable_sessions()
        transport = self._bridge.get_transport_status()
        runtime = self._bridge.get_runtime_status()
        reconcile = self._bridge.get_reconcile_status()
        channels = self._bridge.get_mixer_channels()

        self._vm.session_ref = session.session_ref or self._vm.session_ref
        self._vm.session_status = session.status
        self._vm.session_phase = session.phase
        self._vm.session_dirty = session.dirty
        self._vm.session_storage_path = session.storage_path
        self._vm.session_storage_source = session.storage_source
        self._vm.session_last_operation = session.last_operation
        self._vm.recent_sessions = recents
        self._vm.recent_session_count = len(recents)
        self._vm.recent_session_summary = (
            f"{recents[0].session_ref} ({recents[0].last_operation})" if recents else "none"
        )
        self._vm.discoverable_sessions = discoverable
        self._vm.discoverable_session_count = len(discoverable)
        self._vm.current_project_summary = (
            f"{session.session_ref} | {session.phase} | {'dirty' if session.dirty else 'clean'}"
            if session.session_ref
            else "No active session"
        )
        self._vm.startup_hint = (
            "Resume a recent session or open an existing .session file."
            if recents or discoverable
            else "Create a new session or save one to start building a recent list."
        )
        self._vm.session_error_summary = session.last_error_message
        self._vm.transport_state = transport.play_state
        self._vm.audio_state = runtime.audio.state
        self._vm.runtime_active = transport.runtime_active or runtime.runtime_started
        self._vm.render_status = runtime.audio.render_status
        self._vm.mixer_channel_count = len(channels)
        self._vm.muted_channel_count = sum(1 for channel in channels if channel.muted)
        self._vm.reconcile_attempted = reconcile.attempted
        self._vm.reconcile_resolved = reconcile.resolved
        self._vm.reconcile_failed = reconcile.failed
        self._vm.reconcile_created = reconcile.created
        self._vm.reconcile_cleared = reconcile.cleared
        self._vm.reconcile_last_message = reconcile.last_message
        self._vm.reconcile_policy_mode = reconcile.policy_mode
        self._vm.reconcile_policy_action = reconcile.policy_action
        self._vm.reconcile_pending_manual = reconcile.pending_manual_reconcile

    def ingest_browser_state(self, browser_vm: BrowserViewModel) -> None:
        self._vm.plugin_count = len(browser_vm.plugins)
        self._vm.available_plugin_count = sum(1 for plugin in browser_vm.plugins if plugin.available)
        self._vm.selected_plugin_name = browser_vm.selected_name

    def ingest_mixer_state(self, mixer_vm: MixerViewModel) -> None:
        self._vm.inserted_plugin_count = len([slot for slot in mixer_vm.insert_chain if slot.plugin_id])
        if mixer_vm.insert_chain:
            first = mixer_vm.insert_chain[0]
            bypass = "bypassed" if first.bypassed else "active"
            placeholder = first.placeholder_instance_id or "none"
            loader = first.loader_outcome or "none"
            self._vm.selected_insert_summary = (
                f"ch{first.channel_id}:slot{first.slot_index}:{first.plugin_name}:{bypass}:"
                f"{first.load_state}:{first.host_lifecycle_state}:ph={placeholder}:loader={loader}"
            )
        else:
            self._vm.selected_insert_summary = ""

    def reconcile_channel_inserts(self, channel_id: int) -> bool:
        result = self._bridge.reconcile_channel_inserts(channel_id)
        return result.ok

    def reconcile_all_inserts(self) -> bool:
        result = self._bridge.reconcile_all_inserts()
        return result.ok

    def new_session(self, session_ref: str) -> bool:
        return self._bridge.new_session(session_ref).ok

    def open_session(self, session_ref: str) -> bool:
        return self._bridge.open_session(session_ref).ok
