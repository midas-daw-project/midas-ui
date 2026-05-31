from pathlib import Path
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

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

    assert not window._browser_dock.isHidden()
    assert not window._mixer_dock.isHidden()
    assert window._transport_dock.isHidden()
    assert window._debug_dock.isHidden()
    assert window.centralWidget() is not None
    assert "Browser -> Arrange/Channel Rack -> Mixer" in window._hint_status_label.text()

    window.close()
