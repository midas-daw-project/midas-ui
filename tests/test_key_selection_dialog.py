from pathlib import Path
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtWidgets import QApplication

from panels.workspace.key_selection_dialog import KeySelectionWheelDialog, normalize_project_key


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_key_selection_wheel_resolves_a_major_scale():
    _app()
    dialog = KeySelectionWheelDialog("A Major")

    assert dialog.selected_key() == "A Major"
    assert dialog.selected_scale_notes() == ["A", "B", "C#", "D", "E", "F#", "G#", "A"]
    assert normalize_project_key("a major") == "A Major"
    assert normalize_project_key("A") == "A Major"

    dialog.close()
