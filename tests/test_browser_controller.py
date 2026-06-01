from pathlib import Path
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtWidgets import QApplication

from bridge.fallback_bridge import FallbackBridgeClient
from controllers.browser_controller import BrowserController
from panels.browser.browser_panel import BrowserPanel
from viewmodels.browser_viewmodel import BrowserViewModel


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


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


def test_browser_panel_renders_library_marketplace_and_registry():
    _app()
    panel = BrowserPanel(
        on_refresh_registry=lambda: None,
        on_select_plugin=lambda _plugin_id: None,
        on_insert_plugin=lambda: None,
    )
    bridge = FallbackBridgeClient()
    vm = BrowserViewModel(plugins=bridge.get_plugin_registry())
    controller = BrowserController(bridge, vm)
    controller.load_registry()

    panel.render(vm)

    assert panel.browser_search_input.placeholderText() == "Search sounds, plugins, presets"
    assert panel.category_list.count() == 7
    assert panel.category_list.currentItem().text() == "808s"
    assert panel.pack_list.count() == 3
    assert "Starter Kit" in panel.pack_list.item(0).text()
    assert panel.plugin_list.count() >= 1
