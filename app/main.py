from __future__ import annotations

import os
import sys

from PySide6.QtWidgets import QApplication

from bridge.fallback_bridge import FallbackBridgeClient
from bridge.native_bridge import NativeBridgeClient
from shell.main_window import MainWindow


def build_bridge():
    use_native = os.getenv("MIDAS_UI_USE_NATIVE_BRIDGE", "0") == "1"
    if use_native:
        return NativeBridgeClient()
    return FallbackBridgeClient()


def main() -> int:
    app = QApplication(sys.argv)
    bridge = build_bridge()
    window = MainWindow(bridge)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
