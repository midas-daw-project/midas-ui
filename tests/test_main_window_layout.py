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
    assert window._onboarding_dialog is not None
    assert window._onboarding_dialog.windowTitle() == "Welcome to MIDAS"
    onboarding_text = " ".join(label.text() for label in window._onboarding_dialog.findChildren(type(window._hint_status_label)))
    assert "Poseidon Wave Harbor" in onboarding_text
    assert "Hephaestus Interface Forge" in onboarding_text
    assert "Daedalus Automation Labyrinth" in onboarding_text
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
    assert "Edit BPM" in window._command_actions
    assert "Open Key Wheel" in window._command_actions
    assert "Show Navigation Help" in window._command_actions

    window._command_search_input.setText("toggle mixer")
    window._execute_command_search()
    assert not window._mixer_dock.isHidden()

    window._command_search_input.setText("show drum")
    window._execute_command_search()
    assert window._workspace_panel.current_editor_name() == "Drum Machine"

    window._command_search_input.setText("show piano")
    window._execute_command_search()
    assert window._workspace_panel.current_editor_name() == "Piano Roll"

    assert window._workspace_panel.arrangement_track_count() == 11
    window._command_search_input.setText("add track")
    window._execute_command_search()
    assert window._workspace_panel.arrangement_track_count() == 12

    window.close()


def test_main_window_project_controls_update_tempo_and_key():
    _app()
    window = MainWindow(FallbackBridgeClient())
    window.show()
    QApplication.processEvents()

    assert window._tempo_input.value() == 120.0
    assert window._key_button.text() == "C Major"

    window._tempo_input.setValue(98.5)
    assert window._project_tempo_bpm == 98.5

    window._command_search_input.setText("set bpm 104")
    window._execute_command_search()
    assert window._tempo_input.value() == 104.0

    window._command_search_input.setText("change key to a major")
    window._execute_command_search()
    assert window._key_button.text() == "A Major"
    assert window._project_key_notes == ["A", "B", "C#", "D", "E", "F#", "G#", "A"]
    assert "A  B  C#  D  E  F#  G#  A" in window._key_notes_label.text()

    window.close()
