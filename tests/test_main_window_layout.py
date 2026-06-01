from pathlib import Path
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from bridge.fallback_bridge import FallbackBridgeClient
from shell.main_window import MainWindow


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_main_window_default_layout_prioritizes_workspace():
    _app()
    window = MainWindow(FallbackBridgeClient())
    window.show()
    QApplication.processEvents()

    assert not window._browser_dock.isHidden()
    assert window._mixer_dock.isHidden()
    assert window.dockWidgetArea(window._mixer_dock) == Qt.BottomDockWidgetArea
    assert window._session_dock.isHidden()
    assert window._transport_dock.isHidden()
    assert window._debug_dock.isHidden()
    assert window._header_save_button.text() == "Save"
    assert window._header_load_button.text() == "Load"
    assert not window._header_mixer_button.isChecked()
    window._header_mixer_button.click()
    assert not window._mixer_dock.isHidden()
    assert window._header_mixer_button.isChecked()
    window._header_mixer_button.click()
    assert window._mixer_dock.isHidden()
    assert window.centralWidget() is not None
    assert "Browser -> Arrangement/Editor -> Mixer" in window._hint_status_label.text()

    window.close()


def test_main_window_command_search_executes_window_and_workspace_commands():
    _app()
    window = MainWindow(FallbackBridgeClient())
    window.show()
    QApplication.processEvents()

    assert "Toggle Mixer" in window._command_actions
    assert "Show Drum Machine" in window._command_actions
    assert "Add Track" in window._command_actions

    window._command_search_input.setText("toggle mixer")
    window._execute_command_search()
    assert not window._mixer_dock.isHidden()

    window._command_search_input.setText("show drum")
    window._execute_command_search()
    assert window._workspace_panel.current_editor_name() == "Drum Machine"

    assert window._workspace_panel.arrangement_track_count() == 11
    window._command_search_input.setText("add track")
    window._execute_command_search()
    assert window._workspace_panel.arrangement_track_count() == 12

    window.close()
