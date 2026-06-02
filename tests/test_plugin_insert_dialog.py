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


def test_plugin_insert_dialog_hides_local_sources_that_are_not_inserts():
    _app()
    plugins = FallbackBridgeClient().get_plugin_registry()
    dialog = PluginInsertDialog(plugins=plugins, selected_plugin_id="midas.comp.basic", channel_id=1)

    category_names = {dialog.category_list.item(row).text() for row in range(dialog.category_list.count())}
    assert "Host App" not in category_names
    assert "Host Extension" not in category_names
    assert "Sample Pack" not in category_names
    assert "Plugin Shell" not in category_names
    assert "Audio Interface Utility" not in category_names
    assert "Spatial Utility" not in category_names
    assert "Drum Instrument" not in category_names
    assert "Sample Library" not in category_names
    assert "Automation Source" not in category_names
    assert "Performance Host" not in category_names
    assert "Skin Design Tool" not in category_names
    assert "Reference Source" not in category_names

    visible_text = "\n".join(dialog.plugin_list.item(row).text() for row in range(dialog.plugin_list.count()))
    assert "MIDAS Phrygian Gate" not in visible_text
    assert "MIDAS Inferno Shaper" not in visible_text
    assert "MIDAS Poseidon WaveShell" not in visible_text
    assert "MIDAS Argus Head Tracker" not in visible_text
    assert "MIDAS Scarlett Hearth" not in visible_text
    assert "MIDAS Anvil Drumforge" not in visible_text
    assert "MIDAS Thread Library" not in visible_text
    assert "MIDAS Helios Decks" not in visible_text
    assert "MIDAS Athena Font Vault" not in visible_text
    assert "MIDAS Muse Board" not in visible_text
