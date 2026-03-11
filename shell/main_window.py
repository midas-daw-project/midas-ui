from __future__ import annotations

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtWidgets import QDockWidget, QMainWindow

from bridge.protocol import BridgeClient
from controllers.audio_controller import AudioController
from controllers.mixer_controller import MixerController
from panels.audio.audio_panel import AudioPanel
from panels.debug.debug_panel import DebugPanel
from panels.mixer.mixer_panel import MixerPanel
from panels.session.session_panel import SessionPanel
from panels.transport.transport_panel import TransportPanel
from panels.workspace.workspace_panel import WorkspacePanel
from viewmodels.audio_viewmodel import AudioViewModel
from viewmodels.mixer_viewmodel import MixerViewModel


class MainWindow(QMainWindow):
    def __init__(self, bridge: BridgeClient) -> None:
        super().__init__()
        self._bridge = bridge
        self.setWindowTitle("MIDAS - Phase 1 Shell")
        self.resize(1280, 780)

        self._audio_vm = AudioViewModel()
        self._mixer_vm = MixerViewModel()
        self._audio_controller = AudioController(bridge, self._audio_vm)
        self._mixer_controller = MixerController(bridge, self._mixer_vm)
        self._debug_panel = DebugPanel()
        self._mixer_panel = MixerPanel(
            on_apply_mute=self._apply_mixer_mute,
            on_apply_gain=self._apply_mixer_gain,
            on_refresh=self._refresh_mixer,
        )
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
        self._refresh_mixer()

        self._event_relay = _UiEventRelay()
        self._event_relay.event_received.connect(self._handle_bridge_event)
        self._event_subscription_handle = -1
        self._using_polling_fallback = False

        self._attach_event_flow()

        self._event_timer = QTimer(self)
        if self._using_polling_fallback:
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

    def _refresh_mixer(self) -> None:
        self._mixer_vm.selected_channel_id = self._mixer_panel.selected_channel()
        self._mixer_controller.refresh_channels()
        self._mixer_panel.render(self._mixer_vm)

    def _apply_mixer_mute(self) -> None:
        channel = self._mixer_panel.selected_channel()
        self._mixer_vm.selected_channel_id = channel
        result = self._mixer_controller.set_mute(channel, self._mixer_panel.selected_mute())
        self._debug_panel.append_result("set_channel_mute", result.code, result.message)
        self._refresh_mixer()

    def _apply_mixer_gain(self) -> None:
        channel = self._mixer_panel.selected_channel()
        self._mixer_vm.selected_channel_id = channel
        result = self._mixer_controller.set_gain(channel, self._mixer_panel.selected_gain())
        self._debug_panel.append_result("set_channel_gain", result.code, result.message)
        self._refresh_mixer()

    def _poll_events(self) -> None:
        events = self._bridge.drain_recent_events(32)
        if not events:
            return
        for event in events:
            self._handle_bridge_event(event)

    def _attach_event_flow(self) -> None:
        try:
            self._event_subscription_handle = self._bridge.subscribe_events(self._on_bridge_event)
            self._using_polling_fallback = False
            return
        except Exception:
            self._using_polling_fallback = True

    def _on_bridge_event(self, event) -> None:
        # Bridge callbacks can arrive off the Qt UI thread; signal marshals safely.
        self._event_relay.event_received.emit(event)

    def _handle_bridge_event(self, event) -> None:
        self._debug_panel.append_event(event)
        # Event model for phase 1: notify first, then re-query authoritative state.
        self._refresh_audio()
        if getattr(event, "category", "") == "mixer":
            self._refresh_mixer()

    def closeEvent(self, event) -> None:  # noqa: N802
        if self._event_subscription_handle != -1:
            try:
                self._bridge.unsubscribe_events(self._event_subscription_handle)
            except Exception:
                pass
        super().closeEvent(event)


# Keep Qt imports grouped with UI shell to avoid accidental backend coupling in modules.
from PySide6.QtCore import Qt  # noqa: E402


class _UiEventRelay(QObject):
    event_received = Signal(object)
