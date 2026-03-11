from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bridge.fallback_bridge import FallbackBridgeClient
from controllers.session_controller import SessionController
from viewmodels.session_viewmodel import SessionViewModel


def test_session_save_load_apply_flow():
    bridge = FallbackBridgeClient()
    vm = SessionViewModel()
    controller = SessionController(bridge, vm)

    controller.refresh_status()
    assert vm.status == "idle"

    assert controller.save_session().ok
    assert vm.status == "saved"
    assert vm.last_save_status == "ok"

    assert controller.load_session().ok
    assert vm.status == "loaded"
    assert vm.last_load_status == "ok"

    assert controller.apply_session().ok
    assert vm.status == "applied"
    assert vm.last_apply_status == "ok"
