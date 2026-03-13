from pathlib import Path
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog

from bridge.fallback_bridge import FallbackBridgeClient
from bridge.protocol import DiscoverableSessionEntry
from panels.workspace.open_existing_session_dialog import OpenExistingSessionDialog
from shell import main_window as main_window_module


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_open_existing_session_dialog_orders_entries_and_marks_current():
    _app()
    dialog = OpenExistingSessionDialog(
        sessions=[
            DiscoverableSessionEntry(session_ref="older", storage_path="C:/sessions/older.session", last_modified_epoch=10),
            DiscoverableSessionEntry(session_ref="active", storage_path="C:/sessions/active.session", last_modified_epoch=30),
            DiscoverableSessionEntry(session_ref="recent", storage_path="C:/sessions/recent.session", last_modified_epoch=20),
        ],
        active_session_ref="active",
        recent_session_refs=["recent", "active"],
    )

    assert dialog.session_list.count() == 3
    assert dialog.session_list.item(0).data(Qt.UserRole) == "active"
    assert "[current / recent]" in dialog.session_list.item(0).text()
    assert not bool(dialog.session_list.item(0).flags() & Qt.ItemIsEnabled)
    assert dialog.session_list.item(1).data(Qt.UserRole) == "recent"
    assert "[recent]" in dialog.session_list.item(1).text()
    assert dialog.selected_session_ref() == "recent"
    assert dialog.open_button.isEnabled()

    dialog.browse_button.click()
    assert dialog.browse_requested() is True


def test_open_existing_session_routes_selected_entry_through_open_session(monkeypatch):
    _app()
    bridge = FallbackBridgeClient()
    bridge.new_session("active-session")
    bridge.save_session()
    bridge.new_session("discoverable-a")
    bridge.save_session()
    window = main_window_module.MainWindow(bridge)

    selected_refs: list[str] = []

    class _FakeDialog:
        Accepted = QDialog.Accepted

        def __init__(self, sessions, active_session_ref, recent_session_refs, parent=None):
            assert any(entry.session_ref == "discoverable-a" for entry in sessions)
            assert active_session_ref == "discoverable-a"
            assert "discoverable-a" in recent_session_refs

        def exec(self):
            return self.Accepted

        def browse_requested(self):
            return False

        def selected_session_ref(self):
            return "active-session"

    monkeypatch.setattr(main_window_module, "OpenExistingSessionDialog", _FakeDialog)
    monkeypatch.setattr(window, "_open_session", lambda session_ref: selected_refs.append(session_ref))

    window._open_existing_session()

    assert selected_refs == ["active-session"]
    window.close()


def test_open_existing_session_browse_fallback_uses_file_picker(monkeypatch):
    _app()
    bridge = FallbackBridgeClient()
    window = main_window_module.MainWindow(bridge)

    class _FakeDialog:
        Accepted = QDialog.Accepted

        def __init__(self, sessions, active_session_ref, recent_session_refs, parent=None):
            pass

        def exec(self):
            return self.Accepted

        def browse_requested(self):
            return True

        def selected_session_ref(self):
            return ""

    opened_refs: list[str] = []
    monkeypatch.setattr(main_window_module, "OpenExistingSessionDialog", _FakeDialog)
    monkeypatch.setattr(main_window_module.QFileDialog, "getOpenFileName", lambda *args, **kwargs: ("C:/sessions/from-browse.session", "MIDAS Sessions (*.session)"))
    monkeypatch.setattr(window, "_open_session", lambda session_ref: opened_refs.append(session_ref))

    window._open_existing_session()

    assert opened_refs == ["from-browse"]
    window.close()


def test_open_existing_session_failure_updates_session_and_workspace_state(monkeypatch):
    _app()
    bridge = FallbackBridgeClient()
    window = main_window_module.MainWindow(bridge)

    class _FakeDialog:
        Accepted = QDialog.Accepted

        def __init__(self, sessions, active_session_ref, recent_session_refs, parent=None):
            pass

        def exec(self):
            return self.Accepted

        def browse_requested(self):
            return False

        def selected_session_ref(self):
            return "missing-session"

    monkeypatch.setattr(main_window_module, "OpenExistingSessionDialog", _FakeDialog)

    window._open_existing_session()

    assert window._session_vm.last_error == "session not found"
    assert window._workspace_vm.session_error_summary == "session not found"
    window.close()
