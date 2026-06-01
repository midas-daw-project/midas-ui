from pathlib import Path
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from bridge.fallback_bridge import FallbackBridgeClient
from panels.mixer.plugin_insert_dialog import PluginInsertDialog


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_plugin_insert_dialog_filters_scrollable_registry():
    _app()
    bridge = FallbackBridgeClient()
    plugins = bridge.get_plugin_registry()
    dialog = PluginInsertDialog(plugins=plugins, selected_plugin_id="midas.comp.basic", channel_id=1)

    assert dialog.windowTitle() == "Add FX to Track 1"
    assert dialog.category_list.count() >= 2
    assert dialog.plugin_list.verticalScrollBarPolicy() == Qt.ScrollBarAsNeeded
    assert dialog.selected_plugin_id() == "midas.comp.basic"

    dialog.filter_input.setText("compressor")
    assert dialog.plugin_list.count() >= 1
    assert "Compressor" in dialog.plugin_list.currentItem().text()
    assert dialog.add_button.isEnabled()
