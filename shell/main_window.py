from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QDockWidget, QMainWindow

from bridge.protocol import BridgeClient
from controllers.audio_controller import AudioController
from panels.audio.audio_panel import AudioPanel
from panels.debug.debug_panel import DebugPanel
from panels.mixer.mixer_panel import MixerPanel
from panels.session.session_panel import SessionPanel
from panels.transport.transport_panel import TransportPanel
from panels.workspace.workspace_panel import WorkspacePanel
from viewmodels.audio_viewmodel import AudioViewModel


class MainWindow(QMainWindow):
    def __init__(self, bridge: BridgeClient) -> None:
        super().__init__()
        self._bridge = bridge
        self.setWindowTitle("MIDAS - Phase 1 Shell")
        self.resize(1280, 780)

        self._audio_vm = AudioViewModel()
        self._audio_controller = AudioController(bridge, self._audio_vm)
        self._debug_panel = DebugPanel()
        self._mixer_panel = MixerPanel()
        self._session_panel = SessionPanel()
        self._transport_panel = TransportPanel()
        self._workspace_panel = WorkspacePanel()
        self._debug_panel.set_bridge_version(self._bridge.bridge_version())

        self._audio_panel = AudioPanel(
            on_start_runtime=self._start_runtime,
            on_shutdown_runtime=self._shutdown_runtime,
            on_init=self._init_audio,
            on_open=self._open_audio,
            on_start=self._start_audio,
            on_stop=self._stop_audio,
            on_close=self._close_audio,
            on_refresh=self._refresh_audio,
        )

        self._mount_docks()
        self._refresh_audio()

        self._event_timer = QTimer(self)
        self._event_timer.timeout.connect(self._poll_events)
        self._event_timer.start(150)

    def _mount_docks(self) -> None:
        self.setCentralWidget(self._workspace_panel)

        audio_dock = QDockWidget("Audio", self)
        audio_dock.setWidget(self._audio_panel)
        self.addDockWidget(Qt.LeftDockWidgetArea, audio_dock)

        debug_dock = QDockWidget("Debug / Events", self)
        debug_dock.setWidget(self._debug_panel)
        self.addDockWidget(Qt.BottomDockWidgetArea, debug_dock)

        mixer_dock = QDockWidget("Mixer", self)
        mixer_dock.setWidget(self._mixer_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, mixer_dock)

        session_dock = QDockWidget("Session", self)
        session_dock.setWidget(self._session_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, session_dock)

        transport_dock = QDockWidget("Transport", self)
        transport_dock.setWidget(self._transport_panel)
        self.addDockWidget(Qt.TopDockWidgetArea, transport_dock)

    def _start_runtime(self) -> None:
        result = self._audio_controller.start_runtime_profile()
        self._debug_panel.append_result("start_default_runtime_profile", result.code, result.message)

    def _shutdown_runtime(self) -> None:
        result = self._audio_controller.shutdown_runtime_profile()
        self._debug_panel.append_result("shutdown_runtime_profile", result.code, result.message)
        self._refresh_audio()

    def _init_audio(self) -> None:
        self._audio_panel.read_config_into(self._audio_vm)
        result = self._audio_controller.init_audio()
        self._debug_panel.append_result("init_audio", result.code, result.message)
        self._refresh_audio()

    def _open_audio(self) -> None:
        result = self._audio_controller.open_audio()
        self._debug_panel.append_result("open_audio", result.code, result.message)
        self._refresh_audio()

    def _start_audio(self) -> None:
        self._audio_panel.read_config_into(self._audio_vm)
        result = self._audio_controller.start_audio()
        self._debug_panel.append_result("start_audio", result.code, result.message)
        self._refresh_audio()

    def _stop_audio(self) -> None:
        result = self._audio_controller.stop_audio()
        self._debug_panel.append_result("stop_audio", result.code, result.message)
        self._refresh_audio()

    def _close_audio(self) -> None:
        result = self._audio_controller.close_audio()
        self._debug_panel.append_result("close_audio", result.code, result.message)
        self._refresh_audio()

    def _refresh_audio(self) -> None:
        self._audio_controller.refresh_status()
        self._audio_panel.render(self._audio_vm)

    def _poll_events(self) -> None:
        events = self._bridge.drain_recent_events(32)
        if not events:
            return
        for event in events:
            self._debug_panel.append_event(event)
        # Event model for phase 1: notify first, then re-query authoritative state.
        self._refresh_audio()


# Keep Qt imports grouped with UI shell to avoid accidental backend coupling in modules.
from PySide6.QtCore import Qt  # noqa: E402
