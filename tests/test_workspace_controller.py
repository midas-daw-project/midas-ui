from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bridge.fallback_bridge import FallbackBridgeClient
from controllers.audio_controller import AudioController
from controllers.browser_controller import BrowserController
from controllers.mixer_controller import MixerController
from controllers.workspace_controller import WorkspaceController
from viewmodels.audio_viewmodel import AudioViewModel
from viewmodels.browser_viewmodel import BrowserViewModel
from viewmodels.mixer_viewmodel import MixerViewModel
from viewmodels.workspace_viewmodel import WorkspaceViewModel


def test_workspace_overview_reflects_runtime_and_session():
    bridge = FallbackBridgeClient()
    audio_vm = AudioViewModel(device_id="dev-w", sample_rate=48000, buffer_size=256, track_channel=1, mixer_subsystem=2001)
    audio = AudioController(bridge, audio_vm)

    workspace_vm = WorkspaceViewModel()
    workspace = WorkspaceController(bridge, workspace_vm)
    workspace.set_bridge_identity("fallback", bridge.bridge_version())
    browser_vm = BrowserViewModel()
    browser = BrowserController(bridge, browser_vm)
    mixer_vm = MixerViewModel(selected_channel_id=1)
    mixer = MixerController(bridge, mixer_vm)

    assert audio.start_runtime_profile().ok
    assert audio.init_audio().ok
    assert audio.open_audio().ok
    assert audio.start_audio().ok

    workspace.refresh_overview()
    browser.load_registry()
    workspace.ingest_browser_state(browser_vm)
    assert mixer.insert_plugin(1, "midas.eq.basic", 0).ok
    assert mixer.request_insert_load(1, 0).ok
    workspace.refresh_overview()
    workspace.ingest_mixer_state(mixer_vm)
    assert workspace_vm.bridge_mode == "fallback"
    assert workspace_vm.bridge_version == 1
    assert workspace_vm.session_ref == "local-session"
    assert workspace_vm.session_phase in {"none", "modified", "saved", "loaded", "applied"}
    assert workspace_vm.session_storage_source == "fallback-memory"
    assert workspace_vm.audio_state == "started"
    assert workspace_vm.runtime_active is True
    assert workspace_vm.transport_state == "playing"
    assert workspace_vm.render_status in {"ok", "no_callback", "partial", "failed", "invalid_runtime_state"}
    assert workspace_vm.mixer_channel_count >= 1
    assert workspace_vm.plugin_count >= 1
    assert workspace_vm.available_plugin_count >= 1
    assert workspace_vm.inserted_plugin_count >= 1
    assert workspace_vm.managed_instance_count >= 1
    assert "stub-" in workspace_vm.selected_insert_summary
    assert "created" in workspace_vm.selected_managed_instance_summary
    assert "created:created" in workspace_vm.selected_managed_instance_summary
    assert "fallback_stub" in workspace_vm.selected_runtime_handle_summary
    assert "fallback-handle-" in workspace_vm.selected_runtime_handle_summary
    assert workspace.reconcile_all_inserts() is True
    workspace.refresh_overview()
    assert workspace_vm.reconcile_attempted >= 1
    assert workspace_vm.reconcile_resolved + workspace_vm.reconcile_failed >= 1
    assert workspace_vm.reconcile_policy_mode in {"manual", "immediate", "auto_after_load_apply", "manual_recommended"}
    assert workspace.new_session("workspace-home") is True
    assert workspace.open_session("workspace-home") is False
    assert bridge.save_session().ok
    workspace.refresh_overview()
    assert workspace_vm.recent_session_count >= 1
    assert workspace_vm.recent_sessions[0].session_ref == "workspace-home"
    assert workspace_vm.recent_session_summary.startswith("workspace-home")
    assert workspace_vm.discoverable_session_count >= 1
    assert workspace_vm.current_project_summary.startswith("workspace-home")
    assert "Resume" in workspace_vm.startup_hint
