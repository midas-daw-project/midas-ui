from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bridge.fallback_bridge import FallbackBridgeClient
from controllers.browser_controller import BrowserController
from viewmodels.browser_viewmodel import BrowserViewModel


def test_browser_registry_load_and_selection():
    bridge = FallbackBridgeClient()
    vm = BrowserViewModel()
    controller = BrowserController(bridge, vm)

    controller.load_registry()
    assert len(vm.plugins) >= 1
    assert vm.selected_plugin_id != ""
    assert vm.selected_name != ""

    selected = vm.plugins[-1].plugin_id
    controller.select_plugin(selected)
    assert vm.selected_plugin_id == selected


def test_browser_registry_refresh():
    bridge = FallbackBridgeClient()
    vm = BrowserViewModel()
    controller = BrowserController(bridge, vm)

    result = controller.refresh_registry()
    assert result.ok
    assert vm.last_refresh_status == "ok"
    assert len(vm.plugins) >= 1
