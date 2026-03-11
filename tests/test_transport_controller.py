from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bridge.fallback_bridge import FallbackBridgeClient
from controllers.audio_controller import AudioController
from controllers.transport_controller import TransportController
from viewmodels.audio_viewmodel import AudioViewModel
from viewmodels.transport_viewmodel import TransportViewModel


def test_transport_play_stop_flow():
    bridge = FallbackBridgeClient()
    audio_vm = AudioViewModel(device_id="dev-t", sample_rate=48000, buffer_size=256, track_channel=1, mixer_subsystem=2001)
    audio = AudioController(bridge, audio_vm)
    transport_vm = TransportViewModel(track_channel=1, mixer_subsystem=2001)
    transport = TransportController(bridge, transport_vm)

    assert audio.start_runtime_profile().ok
    assert audio.init_audio().ok
    assert audio.open_audio().ok

    assert transport.play().ok
    assert transport_vm.play_state == "playing"

    assert transport.stop().ok
    assert transport_vm.play_state == "stopped"
