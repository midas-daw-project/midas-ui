from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bridge.fallback_bridge import FallbackBridgeClient
from controllers.audio_controller import AudioController
from viewmodels.audio_viewmodel import AudioViewModel


def test_audio_lifecycle_flow():
    bridge = FallbackBridgeClient()
    vm = AudioViewModel(device_id="dev-a", sample_rate=48000, buffer_size=256, track_channel=1, mixer_subsystem=2001)
    controller = AudioController(bridge, vm)

    assert controller.start_runtime_profile().ok
    assert controller.init_audio().ok
    assert controller.open_audio().ok
    assert controller.start_audio().ok
    assert vm.state == "started"
    assert controller.stop_audio().ok
    assert controller.close_audio().ok
