from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bridge.fallback_bridge import FallbackBridgeClient
from controllers.mixer_controller import MixerController
from viewmodels.mixer_viewmodel import MixerViewModel


def test_mixer_mute_gain_flow():
    bridge = FallbackBridgeClient()
    vm = MixerViewModel(selected_channel_id=1)
    controller = MixerController(bridge, vm)

    controller.refresh_channels()
    first = controller.channel(1)
    assert first.muted is False
    assert abs(first.gain - 1.0) < 1e-9

    assert controller.set_mute(1, True).ok
    assert controller.channel(1).muted is True

    assert controller.set_gain(1, 0.75).ok
    assert abs(controller.channel(1).gain - 0.75) < 1e-9
