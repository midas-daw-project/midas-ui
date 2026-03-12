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
    workspace.ingest_mixer_state(mixer_vm)
    assert workspace_vm.bridge_mode == "fallback"
    assert workspace_vm.bridge_version == 1
    assert workspace_vm.session_ref == "local-session"
    assert workspace_vm.audio_state == "started"
    assert workspace_vm.runtime_active is True
    assert workspace_vm.transport_state == "playing"
    assert workspace_vm.render_status in {"ok", "no_callback", "partial", "failed", "invalid_runtime_state"}
    assert workspace_vm.mixer_channel_count >= 1
    assert workspace_vm.plugin_count >= 1
    assert workspace_vm.available_plugin_count >= 1
    assert workspace_vm.inserted_plugin_count >= 1
