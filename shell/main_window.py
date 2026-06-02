from __future__ import annotations

from PySide6.QtCore import QObject, Qt, QTimer, Signal
from PySide6.QtGui import QAction, QGuiApplication, QKeySequence
from PySide6.QtWidgets import (
    QCompleter,
    QComboBox,
    QDockWidget,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from bridge.protocol import BridgeClient
from controllers.audio_controller import AudioController
from controllers.browser_controller import BrowserController
from controllers.mixer_controller import MixerController
from controllers.session_controller import SessionController
from controllers.transport_controller import TransportController
from controllers.workspace_controller import WorkspaceController
from panels.audio.audio_panel import AudioPanel
from panels.browser.browser_panel import BrowserPanel
from panels.debug.debug_panel import DebugPanel
from panels.mixer.mixer_panel import MixerPanel
from panels.mixer.plugin_insert_dialog import PluginInsertDialog
from panels.session.session_panel import SessionPanel
from panels.transport.transport_panel import TransportPanel
from panels.workspace.open_existing_session_dialog import OpenExistingSessionDialog
from panels.workspace.key_selection_dialog import (
    MAJOR_SCALES,
    KeySelectionWheelDialog,
    normalize_project_key,
)
from panels.workspace.onboarding_dialog import DawOnboardingDialog
from panels.workspace.workspace_panel import WorkspacePanel
from shell.settings_store import ShellSettingsStore
from viewmodels.audio_viewmodel import AudioViewModel
from viewmodels.browser_viewmodel import BrowserViewModel
from viewmodels.mixer_viewmodel import MixerViewModel
from viewmodels.session_viewmodel import SessionViewModel
from viewmodels.transport_viewmodel import TransportViewModel
from viewmodels.workspace_viewmodel import WorkspaceViewModel


class MainWindow(QMainWindow):
    DEFAULT_WIDTH = 1060
    DEFAULT_HEIGHT = 680
    MIN_WIDTH = 720
    MIN_HEIGHT = 500
    SCREEN_MARGIN = 72
    LAYOUT_VERSION = 10

    def __init__(self, bridge: BridgeClient) -> None:
        super().__init__()
        self._bridge = bridge
        self._settings = ShellSettingsStore()
        self.setWindowTitle("MIDAS - Phase 1 Shell")
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.resize(*self._default_window_size())

        self._audio_vm = AudioViewModel()
        self._mixer_vm = MixerViewModel()
        self._session_vm = SessionViewModel()
        self._transport_vm = TransportViewModel()
        self._browser_vm = BrowserViewModel()
        self._workspace_vm = WorkspaceViewModel()
        self._audio_controller = AudioController(bridge, self._audio_vm)
        self._browser_controller = BrowserController(bridge, self._browser_vm)
        self._mixer_controller = MixerController(bridge, self._mixer_vm)
        self._session_controller = SessionController(bridge, self._session_vm)
        self._transport_controller = TransportController(bridge, self._transport_vm)
        self._workspace_controller = WorkspaceController(bridge, self._workspace_vm)
        self._debug_panel = DebugPanel(on_manual_refresh=self._manual_refresh_all)
        self._mixer_panel = MixerPanel(
            on_apply_mute=self._apply_mixer_mute,
            on_apply_gain=self._apply_mixer_gain,
            on_insert_plugin=self._insert_selected_plugin,
            on_remove_plugin=self._remove_selected_slot_plugin,
            on_move_slot_up=self._move_selected_slot_up,
            on_move_slot_down=self._move_selected_slot_down,
            on_move_slot_top=self._move_selected_slot_top,
            on_move_slot_bottom=self._move_selected_slot_bottom,
            on_toggle_bypass=self._toggle_selected_slot_bypass,
            on_toggle_channel_bypass=self._toggle_channel_insert_bypass,
            on_clear_chain=self._clear_channel_insert_chain,
            on_refresh_runtime_state=self._refresh_channel_insert_runtime_state,
            on_request_slot_load=self._request_slot_host_load,
            on_request_slot_unload=self._request_slot_host_unload,
            on_refresh=self._refresh_mixer,
        )
        self._session_panel = SessionPanel(
            on_new=self._new_session,
            on_open=self._open_session,
            on_save=self._save_session,
            on_load=self._load_session,
            on_apply=self._apply_session,
            on_refresh=self._refresh_session,
        )
        self._transport_panel = TransportPanel(
            on_play=self._play_transport,
            on_stop=self._stop_transport,
            on_refresh=self._refresh_transport,
        )
        self._browser_panel = BrowserPanel(
            on_refresh_registry=self._refresh_plugin_registry,
            on_select_plugin=self._select_plugin,
            on_insert_plugin=self._insert_selected_plugin,
        )
        self._workspace_panel = WorkspacePanel(
            on_refresh_all=self._manual_refresh_all,
            on_new_session=self._new_session,
            on_open_session=self._open_session,
            on_open_existing_session=self._open_existing_session,
            on_open_recent=self._open_recent_session,
            on_save_session=self._save_session,
            on_load_session=self._load_session,
            on_apply_session=self._apply_session,
            on_reconcile_inserts=self._reconcile_all_inserts,
            on_midi_notes_changed=self._midi_notes_changed,
        )
        bridge_mode = "native" if self._bridge.__class__.__name__ == "NativeBridgeClient" else "fallback"
        self._workspace_controller.set_bridge_identity(mode=bridge_mode, version=self._bridge.bridge_version())
        self._project_tempo_bpm = 120.0
        self._project_key = "C Major"
        self._project_key_source = "Manual"
        self._project_key_notes = MAJOR_SCALES[self._project_key]
        self._debug_panel.set_bridge_info(
            mode=bridge_mode,
            version=self._bridge.bridge_version(),
            subscription_active=False,
            fallback_polling=False,
        )

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

        self._mount_header()
        self._mount_docks()
        self._mount_commands()
        self._restore_shell_state()
        self._refresh_audio()
        self._refresh_mixer()
        self._refresh_session()
        self._refresh_transport()
        self._refresh_browser()
        self._refresh_workspace()

        self._event_relay = _UiEventRelay()
        self._event_relay.event_received.connect(self._handle_bridge_event)
        self._event_subscription_handle = -1
        self._using_polling_fallback = False

        self._attach_event_flow()

        self._event_timer = QTimer(self)
        if self._using_polling_fallback:
            self._event_timer.timeout.connect(self._poll_events)
            self._event_timer.start(150)
        self._debug_panel.set_bridge_info(
            mode=bridge_mode,
            version=self._bridge.bridge_version(),
            subscription_active=(self._event_subscription_handle != -1),
            fallback_polling=self._using_polling_fallback,
        )
        self._refresh_debug_summary()
        self._onboarding_dialog: DawOnboardingDialog | None = None
        QTimer.singleShot(0, self._show_onboarding_dialog)

    def _mount_header(self) -> None:
        self._header_toolbar = QToolBar("MIDAS Header", self)
        self._header_toolbar.setObjectName("midasHeader")
        self._header_toolbar.setMovable(False)
        self._header_toolbar.setFloatable(False)
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(10, 7, 10, 7)
        header_layout.setSpacing(6)
        cockpit_row = QHBoxLayout()
        cockpit_row.setSpacing(10)
        self._project_title_label = QLabel("MIDAS")
        self._project_title_label.setObjectName("headerProjectTitle")
        self._command_search_input = QLineEdit()
        self._command_search_input.setObjectName("headerSearch")
        self._command_search_input.setPlaceholderText("Search commands, add tracks, set BPM, change key")
        self._command_search_input.returnPressed.connect(self._execute_command_search)
        self._header_play_button = QPushButton("Play")
        self._header_play_button.setObjectName("transportPrimary")
        self._header_stop_button = QPushButton("Stop")
        self._header_stop_button.setObjectName("transportButton")
        self._header_record_button = QPushButton("Record")
        self._header_record_button.setObjectName("transportRecordButton")
        self._header_loop_button = QPushButton("Loop")
        self._header_loop_button.setObjectName("transportButton")
        self._header_loop_button.setCheckable(True)
        self._header_metronome_button = QPushButton("Metro")
        self._header_metronome_button.setObjectName("transportButton")
        self._header_metronome_button.setCheckable(True)
        self._tempo_input = QDoubleSpinBox()
        self._tempo_input.setObjectName("tempoInput")
        self._tempo_input.setRange(20.0, 300.0)
        self._tempo_input.setDecimals(2)
        self._tempo_input.setSingleStep(1.0)
        self._tempo_input.setSuffix(" BPM")
        self._tempo_input.setValue(self._project_tempo_bpm)
        self._tempo_input.valueChanged.connect(self._set_project_tempo)
        self._key_button = QPushButton(self._project_key)
        self._key_button.setObjectName("keyButton")
        self._key_notes_label = QLabel(" ".join(self._project_key_notes))
        self._key_notes_label.setObjectName("keyNotesLabel")
        self._time_signature_input = QComboBox()
        self._time_signature_input.setObjectName("meterCombo")
        self._time_signature_input.addItems(["4 / 4", "3 / 4", "6 / 8", "12 / 8", "5 / 4", "7 / 8"])
        self._snap_input = QComboBox()
        self._snap_input.setObjectName("snapCombo")
        self._snap_input.addItems(["Grid 1/4", "Grid 1/8", "Grid 1/16", "Grid 1/32"])
        self._device_status_label = QLabel("Audio")
        self._device_status_label.setObjectName("deviceStatusLabel")
        self._sample_rate_input = QSpinBox()
        self._sample_rate_input.setObjectName("sampleRateInput")
        self._sample_rate_input.setRange(8000, 192000)
        self._sample_rate_input.setSingleStep(1000)
        self._sample_rate_input.setSuffix(" Hz")
        self._sample_rate_input.setValue(self._audio_vm.sample_rate or 48000)
        self._sample_rate_input.setToolTip("Project audio sample rate")
        self._buffer_size_input = QSpinBox()
        self._buffer_size_input.setObjectName("bufferSizeInput")
        self._buffer_size_input.setRange(32, 4096)
        self._buffer_size_input.setSingleStep(32)
        self._buffer_size_input.setSuffix(" spls")
        self._buffer_size_input.setValue(self._audio_vm.buffer_size or 256)
        self._buffer_size_input.setToolTip("Audio block size / buffer size")
        self._runtime_status_label = QLabel("Runtime: offline")
        self._runtime_status_label.setObjectName("runtimeStatusLabel")
        self._hint_status_label = QLabel("Hint: Browser -> Arrangement/Editor -> Mixer")
        self._hint_status_label.setObjectName("headerHint")
        self._status_chip = QLabel("Offline")
        self._status_chip.setObjectName("statusChip")
        cockpit_row.addWidget(self._project_title_label)
        cockpit_row.addWidget(self._command_search_input, 1)
        cockpit_row.addWidget(self._header_play_button)
        cockpit_row.addWidget(self._header_stop_button)
        cockpit_row.addWidget(self._header_record_button)
        cockpit_row.addWidget(self._header_loop_button)
        cockpit_row.addWidget(self._header_metronome_button)
        cockpit_row.addWidget(self._tempo_input)
        cockpit_row.addWidget(self._key_button)
        cockpit_row.addWidget(self._time_signature_input)
        cockpit_row.addWidget(self._snap_input)
        cockpit_row.addWidget(self._status_chip)
        cockpit_row.addWidget(self._device_status_label)
        cockpit_row.addWidget(self._sample_rate_input)
        cockpit_row.addWidget(self._buffer_size_input)
        cockpit_row.addWidget(self._runtime_status_label)
        header_layout.addLayout(cockpit_row)
        key_row = QHBoxLayout()
        key_row.setSpacing(8)
        self._header_mode_buttons: list[QPushButton] = []
        for mode_name in ("Start", "Arrange", "Record", "Mix", "Browse"):
            mode_button = QPushButton(mode_name)
            mode_button.setObjectName("headerModeButton")
            mode_button.setCheckable(True)
            mode_button.setChecked(mode_name == "Arrange")
            mode_button.clicked.connect(
                lambda _checked=False, selected_mode=mode_name: self._select_header_mode(selected_mode)
            )
            self._header_mode_buttons.append(mode_button)
            key_row.addWidget(mode_button)
        key_row.addWidget(self._key_notes_label, 1)
        header_layout.addLayout(key_row)
        session_separator = QFrame()
        session_separator.setObjectName("headerSeparator")
        session_separator.setFrameShape(QFrame.HLine)
        header_layout.addWidget(session_separator)
        session_row = QHBoxLayout()
        session_row.setSpacing(6)
        self._header_session_ref_input = QLineEdit("local-session")
        self._header_session_ref_input.setObjectName("headerSessionRef")
        self._header_session_ref_input.setPlaceholderText("session name")
        self._header_new_button = QPushButton("New")
        self._header_open_button = QPushButton("Open")
        self._header_save_button = QPushButton("Save")
        self._header_load_button = QPushButton("Load")
        self._header_apply_button = QPushButton("Apply")
        self._header_refresh_button = QPushButton("Refresh")
        self._header_mixer_button = QPushButton("Mixer")
        self._header_mixer_button.setCheckable(True)
        self._header_mixer_button.setChecked(False)
        self._workspace_preset_input = QComboBox()
        self._workspace_preset_input.setObjectName("workspacePresetCombo")
        self._workspace_preset_input.addItems(
            ["Beginner", "Producer", "Engineer", "Recording", "Performance", "Master", "Advanced"]
        )
        self._left_panel_button = QPushButton("Left")
        self._left_panel_button.setObjectName("panelToggleButton")
        self._left_panel_button.setCheckable(True)
        self._right_panel_button = QPushButton("Right")
        self._right_panel_button.setObjectName("panelToggleButton")
        self._right_panel_button.setCheckable(True)
        self._bottom_panel_button = QPushButton("Bottom")
        self._bottom_panel_button.setObjectName("panelToggleButton")
        self._bottom_panel_button.setCheckable(True)
        self._focus_mode_button = QPushButton("Focus")
        self._focus_mode_button.setObjectName("panelToggleButton")
        self._focus_mode_button.setCheckable(True)
        self._reset_layout_button = QPushButton("Reset Layout")
        self._reset_layout_button.setObjectName("panelToggleButton")
        session_row.addWidget(QLabel("Session"))
        session_row.addWidget(self._header_session_ref_input, 1)
        session_row.addWidget(self._header_new_button)
        session_row.addWidget(self._header_open_button)
        session_row.addWidget(self._header_save_button)
        session_row.addWidget(self._header_load_button)
        session_row.addWidget(self._header_apply_button)
        session_row.addWidget(self._header_refresh_button)
        session_row.addWidget(self._header_mixer_button)
        session_row.addWidget(QLabel("Workspace"))
        session_row.addWidget(self._workspace_preset_input)
        session_row.addWidget(self._left_panel_button)
        session_row.addWidget(self._right_panel_button)
        session_row.addWidget(self._bottom_panel_button)
        session_row.addWidget(self._focus_mode_button)
        session_row.addWidget(self._reset_layout_button)
        header_layout.addLayout(session_row)
        header_layout.addWidget(self._hint_status_label)
        self._header_play_button.clicked.connect(self._play_transport)
        self._header_stop_button.clicked.connect(self._stop_transport)
        self._header_record_button.clicked.connect(lambda: self._workspace_controller.mark_action("Record armed from header"))
        self._header_loop_button.clicked.connect(
            lambda checked: self._workspace_controller.mark_action("Loop on" if checked else "Loop off")
        )
        self._header_metronome_button.clicked.connect(
            lambda checked: self._workspace_controller.mark_action("Metronome on" if checked else "Metronome off")
        )
        self._key_button.clicked.connect(self._open_key_selection_wheel)
        self._sample_rate_input.valueChanged.connect(self._set_audio_sample_rate)
        self._buffer_size_input.valueChanged.connect(self._set_audio_buffer_size)
        self._header_new_button.clicked.connect(lambda: self._new_session(self._header_session_ref_input.text()))
        self._header_open_button.clicked.connect(lambda: self._open_session(self._header_session_ref_input.text()))
        self._header_save_button.clicked.connect(self._save_session)
        self._header_load_button.clicked.connect(self._load_session)
        self._header_apply_button.clicked.connect(self._apply_session)
        self._header_refresh_button.clicked.connect(self._manual_refresh_all)
        self._header_mixer_button.clicked.connect(self._toggle_mixer_dock)
        self._workspace_preset_input.currentTextChanged.connect(self._apply_workspace_preset)
        self._left_panel_button.clicked.connect(lambda checked: self._set_left_panel_visible(checked))
        self._right_panel_button.clicked.connect(lambda checked: self._set_right_panel_visible(checked))
        self._bottom_panel_button.clicked.connect(lambda checked: self._set_bottom_panel_visible(checked))
        self._focus_mode_button.clicked.connect(self._set_focus_mode)
        self._reset_layout_button.clicked.connect(self._reset_layout)
        self._header_toolbar.addWidget(header)
        self.addToolBar(Qt.TopToolBarArea, self._header_toolbar)

    def _mount_docks(self) -> None:
        self.setCentralWidget(self._scrollable_panel(self._workspace_panel))

        self._audio_dock = QDockWidget("Audio", self)
        self._audio_dock.setObjectName("dock.audio")
        self._audio_dock.setWidget(self._scrollable_panel(self._audio_panel))
        self.addDockWidget(Qt.LeftDockWidgetArea, self._audio_dock)

        self._debug_dock = QDockWidget("Debug / Events", self)
        self._debug_dock.setObjectName("dock.debug")
        self._debug_dock.setWidget(self._scrollable_panel(self._debug_panel))
        self.addDockWidget(Qt.BottomDockWidgetArea, self._debug_dock)

        self._mixer_dock = QDockWidget("Mixer", self)
        self._mixer_dock.setObjectName("dock.mixer")
        self._mixer_dock.setMinimumHeight(240)
        self._mixer_dock.setWidget(self._scrollable_panel(self._mixer_panel))
        self.addDockWidget(Qt.BottomDockWidgetArea, self._mixer_dock)

        self._session_dock = QDockWidget("Session", self)
        self._session_dock.setObjectName("dock.session")
        self._session_dock.setWidget(self._scrollable_panel(self._session_panel))
        self.addDockWidget(Qt.RightDockWidgetArea, self._session_dock)

        self._transport_dock = QDockWidget("Transport", self)
        self._transport_dock.setObjectName("dock.transport")
        self._transport_dock.setWidget(self._scrollable_panel(self._transport_panel))
        self.addDockWidget(Qt.TopDockWidgetArea, self._transport_dock)

        self._browser_dock = QDockWidget("Browser", self)
        self._browser_dock.setObjectName("dock.browser")
        self._browser_dock.setMinimumWidth(210)
        self._browser_dock.setWidget(self._scrollable_panel(self._browser_panel))
        self.addDockWidget(Qt.RightDockWidgetArea, self._browser_dock)
        self._mount_view_menu()

    def _start_runtime(self) -> None:
        result = self._audio_controller.start_runtime_profile()
        self._debug_panel.append_result("start_default_runtime_profile", result.code, result.message)
        self._workspace_controller.mark_action("Started runtime profile")
        self._refresh_workspace()

    def _shutdown_runtime(self) -> None:
        result = self._audio_controller.shutdown_runtime_profile()
        self._debug_panel.append_result("shutdown_runtime_profile", result.code, result.message)
        self._workspace_controller.mark_action("Shutdown runtime profile")
        self._refresh_audio()

    def _init_audio(self) -> None:
        self._sync_header_audio_config_to_panel()
        self._audio_panel.read_config_into(self._audio_vm)
        result = self._audio_controller.init_audio()
        self._debug_panel.append_result("init_audio", result.code, result.message)
        self._workspace_controller.mark_action("Initialized audio")
        self._refresh_audio()

    def _open_audio(self) -> None:
        result = self._audio_controller.open_audio()
        self._debug_panel.append_result("open_audio", result.code, result.message)
        self._workspace_controller.mark_action("Opened audio")
        self._refresh_audio()

    def _start_audio(self) -> None:
        self._sync_header_audio_config_to_panel()
        self._audio_panel.read_config_into(self._audio_vm)
        result = self._audio_controller.start_audio()
        self._debug_panel.append_result("start_audio", result.code, result.message)
        self._workspace_controller.mark_action("Started audio")
        self._refresh_audio()

    def _stop_audio(self) -> None:
        result = self._audio_controller.stop_audio()
        self._debug_panel.append_result("stop_audio", result.code, result.message)
        self._workspace_controller.mark_action("Stopped audio")
        self._refresh_audio()

    def _close_audio(self) -> None:
        result = self._audio_controller.close_audio()
        self._debug_panel.append_result("close_audio", result.code, result.message)
        self._workspace_controller.mark_action("Closed audio")
        self._refresh_audio()

    def _refresh_audio(self) -> None:
        self._audio_controller.refresh_status()
        self._audio_panel.render(self._audio_vm)
        self._refresh_debug_summary()
        self._refresh_workspace()

    def _refresh_mixer(self) -> None:
        self._mixer_vm.selected_channel_id = self._mixer_panel.selected_channel()
        self._mixer_vm.selected_slot_index = self._mixer_panel.selected_slot_index()
        self._mixer_controller.refresh_channels()
        self._mixer_panel.render(self._mixer_vm)
        self._refresh_debug_summary()
        self._refresh_workspace()

    def _refresh_session(self) -> None:
        self._session_controller.refresh_status()
        self._session_panel.render(self._session_vm)
        self._refresh_debug_summary()
        self._refresh_workspace()

    def _refresh_transport(self) -> None:
        self._transport_vm.track_channel = self._transport_panel.selected_track_channel()
        self._transport_controller.refresh_status()
        self._transport_panel.render(self._transport_vm)
        self._refresh_header()
        self._refresh_debug_summary()
        self._refresh_workspace()

    def _refresh_browser(self) -> None:
        self._browser_controller.load_registry()
        self._browser_panel.render(self._browser_vm)
        self._refresh_workspace()

    def _refresh_plugin_registry(self) -> None:
        result = self._browser_controller.refresh_registry()
        self._debug_panel.append_result("refresh_plugin_registry", result.code, result.message)
        self._workspace_controller.mark_action("Refreshed plugin registry")
        self._browser_panel.render(self._browser_vm)
        self._refresh_workspace()

    def _select_plugin(self, plugin_id: str) -> None:
        self._browser_controller.select_plugin(plugin_id, queue_if_insert=True)
        self._workspace_controller.mark_action(f"Selected plugin {plugin_id}")
        self._browser_panel.render(self._browser_vm)
        self._refresh_workspace()

    def _insert_selected_plugin(self) -> None:
        channel = self._mixer_panel.selected_channel()
        slot = self._mixer_panel.selected_slot_index()
        self._browser_controller.load_registry()
        dialog = PluginInsertDialog(
            plugins=list(self._browser_vm.plugins),
            selected_plugin_id=self._browser_vm.selected_plugin_id,
            channel_id=channel,
            parent=self,
        )
        if dialog.exec() != dialog.Accepted:
            self._workspace_controller.mark_action("Add FX cancelled")
            self._refresh_workspace()
            return
        plugin_id = dialog.selected_plugin_id().strip()
        if not plugin_id:
            self._debug_panel.append_result("insert_plugin", 3, "No plugin selected")
            return
        self._browser_controller.select_plugin(plugin_id)
        result = self._mixer_controller.insert_plugin(channel, plugin_id, slot)
        self._browser_controller.mark_insert_result(result)
        self._debug_panel.append_result("insert_plugin", result.code, result.message)
        if result.ok:
            self._workspace_controller.mark_action(f"Inserted {plugin_id} at ch{channel}:slot{slot}")
            self._mark_session_modified()
        self._browser_panel.render(self._browser_vm)
        self._refresh_mixer()

    def _remove_selected_slot_plugin(self) -> None:
        channel = self._mixer_panel.selected_channel()
        slot = self._mixer_panel.selected_slot_index()
        result = self._mixer_controller.remove_plugin(channel, slot)
        self._debug_panel.append_result("remove_plugin", result.code, result.message)
        if result.ok:
            self._workspace_controller.mark_action(f"Removed plugin at ch{channel}:slot{slot}")
            self._mark_session_modified()
        self._refresh_mixer()

    def _move_selected_slot_up(self) -> None:
        channel = self._mixer_panel.selected_channel()
        slot = self._mixer_panel.selected_slot_index()
        target_slot = max(0, slot - 1)
        result = self._mixer_controller.move_plugin(channel, slot, target_slot)
        self._debug_panel.append_result("move_plugin_up", result.code, result.message)
        if result.ok:
            self._workspace_controller.mark_action(f"Moved slot ch{channel}:{slot}->{target_slot}")
            self._mark_session_modified()
            self._mixer_panel.slot_input.setValue(target_slot)
        self._refresh_mixer()

    def _move_selected_slot_down(self) -> None:
        channel = self._mixer_panel.selected_channel()
        slot = self._mixer_panel.selected_slot_index()
        target_slot = slot + 1
        result = self._mixer_controller.move_plugin(channel, slot, target_slot)
        self._debug_panel.append_result("move_plugin_down", result.code, result.message)
        if result.ok:
            self._workspace_controller.mark_action(f"Moved slot ch{channel}:{slot}->{target_slot}")
            self._mark_session_modified()
            self._mixer_panel.slot_input.setValue(target_slot)
        self._refresh_mixer()

    def _move_selected_slot_top(self) -> None:
        channel = self._mixer_panel.selected_channel()
        slot = self._mixer_panel.selected_slot_index()
        result = self._mixer_controller.move_plugin_to_top(channel, slot)
        self._debug_panel.append_result("move_plugin_top", result.code, result.message)
        if result.ok:
            self._workspace_controller.mark_action(f"Moved slot ch{channel}:{slot} to top")
            self._mark_session_modified()
        self._refresh_mixer()

    def _move_selected_slot_bottom(self) -> None:
        channel = self._mixer_panel.selected_channel()
        slot = self._mixer_panel.selected_slot_index()
        result = self._mixer_controller.move_plugin_to_bottom(channel, slot)
        self._debug_panel.append_result("move_plugin_bottom", result.code, result.message)
        if result.ok:
            self._workspace_controller.mark_action(f"Moved slot ch{channel}:{slot} to bottom")
            self._mark_session_modified()
        self._refresh_mixer()

    def _toggle_selected_slot_bypass(self) -> None:
        channel = self._mixer_panel.selected_channel()
        slot = self._mixer_panel.selected_slot_index()
        bypassed = self._mixer_panel.selected_slot_bypass()
        result = self._mixer_controller.set_plugin_bypass(channel, slot, bypassed)
        self._debug_panel.append_result("set_plugin_bypass", result.code, result.message)
        if result.ok:
            self._workspace_controller.mark_action(
                f"{'Bypassed' if bypassed else 'Enabled'} slot ch{channel}:{slot}"
            )
            self._mark_session_modified()
        self._refresh_mixer()

    def _toggle_channel_insert_bypass(self) -> None:
        channel = self._mixer_panel.selected_channel()
        bypassed = self._mixer_panel.selected_channel_bypass()
        result = self._mixer_controller.set_channel_insert_bypass(channel, bypassed)
        self._debug_panel.append_result("set_channel_insert_bypass", result.code, result.message)
        if result.ok:
            self._workspace_controller.mark_action(
                f"{'Bypassed' if bypassed else 'Enabled'} all inserts on ch{channel}"
            )
            self._mark_session_modified()
        self._refresh_mixer()

    def _clear_channel_insert_chain(self) -> None:
        channel = self._mixer_panel.selected_channel()
        response = QMessageBox.question(
            self,
            "Clear Insert Chain",
            f"Clear all inserts on channel {channel}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if response != QMessageBox.StandardButton.Yes:
            return
        result = self._mixer_controller.clear_insert_chain(channel)
        self._debug_panel.append_result("clear_insert_chain", result.code, result.message)
        if result.ok:
            self._workspace_controller.mark_action(f"Cleared insert chain on ch{channel}")
            self._mark_session_modified()
        self._refresh_mixer()

    def _refresh_channel_insert_runtime_state(self) -> None:
        channel = self._mixer_panel.selected_channel()
        result = self._mixer_controller.refresh_insert_runtime_state(channel)
        self._debug_panel.append_result("refresh_insert_runtime_state", result.code, result.message)
        if result.ok:
            self._workspace_controller.mark_action(f"Refreshed insert runtime state on ch{channel}")
        self._refresh_mixer()

    def _request_slot_host_load(self) -> None:
        channel = self._mixer_panel.selected_channel()
        slot = self._mixer_panel.selected_slot_index()
        result = self._mixer_controller.request_insert_load(channel, slot)
        self._debug_panel.append_result("request_insert_load", result.code, result.message)
        if result.ok:
            self._workspace_controller.mark_action(f"Requested host load for ch{channel}:slot{slot}")
        self._refresh_mixer()

    def _request_slot_host_unload(self) -> None:
        channel = self._mixer_panel.selected_channel()
        slot = self._mixer_panel.selected_slot_index()
        result = self._mixer_controller.request_insert_unload(channel, slot)
        self._debug_panel.append_result("request_insert_unload", result.code, result.message)
        if result.ok:
            self._workspace_controller.mark_action(f"Requested host unload for ch{channel}:slot{slot}")
        self._refresh_mixer()

    def _refresh_workspace(self) -> None:
        self._workspace_controller.refresh_overview()
        self._workspace_controller.ingest_browser_state(self._browser_vm)
        self._workspace_controller.ingest_mixer_state(self._mixer_vm)
        self._workspace_panel.render(self._workspace_vm)
        self._refresh_header()

    def _select_header_mode(self, mode_name: str) -> None:
        if hasattr(self, "_focus_mode_button") and self._focus_mode_button.isChecked() and mode_name != "Arrange":
            self._focus_mode_button.setChecked(False)
        for button in getattr(self, "_header_mode_buttons", []):
            button.setChecked(button.text() == mode_name)
        if mode_name == "Start":
            self._workspace_controller.mark_action("Opened start workspace")
        elif mode_name == "Arrange":
            self._workspace_panel.show_arrangement()
            self._workspace_controller.mark_action("Opened arrangement")
        elif mode_name == "Record":
            self._workspace_panel.show_drum_machine()
            self._workspace_controller.mark_action("Opened record workspace")
        elif mode_name == "Mix":
            self._set_mixer_visible(True)
            return
        elif mode_name == "Browse":
            self._browser_dock.setVisible(True)
            self._workspace_controller.mark_action("Opened browser")
        self._refresh_workspace()

    def _apply_workspace_preset(self, preset_name: str) -> None:
        if not preset_name or not hasattr(self, "_browser_dock"):
            return
        if hasattr(self, "_focus_mode_button") and self._focus_mode_button.isChecked():
            self._focus_mode_button.blockSignals(True)
            self._focus_mode_button.setChecked(False)
            self._focus_mode_button.blockSignals(False)
        preset = preset_name.strip().lower()
        if preset == "beginner":
            self._workspace_panel.show_arrangement()
            self._set_left_panel_visible(False, refresh=False)
            self._set_right_panel_visible(True, refresh=False)
            self._set_bottom_panel_visible(False, refresh=False)
            self._session_dock.hide()
            self._transport_dock.hide()
            self._debug_dock.hide()
        elif preset == "producer":
            self._workspace_panel.show_drum_machine()
            self._set_left_panel_visible(False, refresh=False)
            self._set_right_panel_visible(True, refresh=False)
            self._set_bottom_panel_visible(False, refresh=False)
            self._session_dock.hide()
            self._transport_dock.hide()
            self._debug_dock.hide()
        elif preset == "engineer":
            self._workspace_panel.show_arrangement()
            self._set_left_panel_visible(False, refresh=False)
            self._set_right_panel_visible(False, refresh=False)
            self._set_bottom_panel_visible(True, refresh=False)
            self._session_dock.hide()
            self._transport_dock.hide()
            self._debug_dock.hide()
        elif preset == "recording":
            self._workspace_panel.show_arrangement()
            self._set_left_panel_visible(True, refresh=False)
            self._set_right_panel_visible(False, refresh=False)
            self._set_bottom_panel_visible(True, refresh=False)
            self._session_dock.hide()
            self._transport_dock.show()
            self._debug_dock.hide()
        elif preset == "performance":
            self._workspace_panel.show_drum_machine()
            self._set_left_panel_visible(False, refresh=False)
            self._set_right_panel_visible(False, refresh=False)
            self._set_bottom_panel_visible(False, refresh=False)
            self._session_dock.hide()
            self._transport_dock.show()
            self._debug_dock.hide()
        elif preset == "master":
            self._workspace_panel.show_arrangement()
            self._set_left_panel_visible(False, refresh=False)
            self._set_right_panel_visible(True, refresh=False)
            self._set_bottom_panel_visible(True, refresh=False)
            self._session_dock.hide()
            self._transport_dock.hide()
            self._debug_dock.hide()
        elif preset == "advanced":
            self._workspace_panel.show_arrangement()
            self._set_left_panel_visible(True, refresh=False)
            self._set_right_panel_visible(True, refresh=False)
            self._set_bottom_panel_visible(True, refresh=False)
            self._session_dock.show()
            self._transport_dock.show()
            self._debug_dock.hide()
        self._workspace_controller.mark_action(f"Workspace preset: {preset_name}")
        self._refresh_workspace()

    def _set_left_panel_visible(self, should_show: bool, *, refresh: bool = True) -> None:
        self._audio_dock.setVisible(should_show)
        self._left_panel_button.setChecked(should_show)
        if should_show:
            self._audio_dock.raise_()
        if refresh:
            self._workspace_controller.mark_action("Opened left panel" if should_show else "Closed left panel")
            self._refresh_header()

    def _set_right_panel_visible(self, should_show: bool, *, refresh: bool = True) -> None:
        self._browser_dock.setVisible(should_show)
        self._right_panel_button.setChecked(should_show)
        if should_show:
            self._browser_dock.raise_()
        if refresh:
            self._workspace_controller.mark_action("Opened right browser" if should_show else "Closed right browser")
            self._refresh_header()

    def _set_bottom_panel_visible(self, should_show: bool, *, refresh: bool = True) -> None:
        self._set_mixer_visible(should_show, refresh=refresh)

    def _set_focus_mode(self, enabled: bool) -> None:
        if enabled:
            self._set_left_panel_visible(False, refresh=False)
            self._set_right_panel_visible(False, refresh=False)
            self._set_bottom_panel_visible(False, refresh=False)
            self._session_dock.hide()
            self._transport_dock.hide()
            self._debug_dock.hide()
            self._workspace_controller.mark_action("Focus mode on")
            self._refresh_workspace()
            return
        self._apply_workspace_preset(self._workspace_preset_input.currentText() or "Beginner")

    def _reset_layout(self) -> None:
        self._focus_mode_button.setChecked(False)
        self._workspace_preset_input.blockSignals(True)
        self._workspace_preset_input.setCurrentText("Beginner")
        self._workspace_preset_input.blockSignals(False)
        self._apply_default_dock_layout()
        self._workspace_panel.show_arrangement()
        self._workspace_controller.mark_action("Reset layout")
        self._refresh_workspace()

    def _focus_tempo_control(self) -> None:
        self._tempo_input.setFocus()
        self._tempo_input.selectAll()
        self._workspace_controller.mark_action("Editing tempo")
        self._refresh_header()

    def _show_mix_workspace(self) -> None:
        self._select_header_mode("Mix")

    def _show_browse_workspace(self) -> None:
        self._select_header_mode("Browse")

    def _show_onboarding_dialog(self) -> None:
        if self._onboarding_dialog is not None and self._onboarding_dialog.isVisible():
            self._onboarding_dialog.raise_()
            self._onboarding_dialog.activateWindow()
            return
        self._onboarding_dialog = DawOnboardingDialog(self)
        self._onboarding_dialog.show()

    def _set_project_tempo(self, tempo_bpm: float) -> None:
        self._project_tempo_bpm = float(tempo_bpm)
        self._workspace_controller.mark_action(f"Tempo set to {self._project_tempo_bpm:.2f} BPM")
        self._refresh_header()

    def _set_project_key(self, key_name: str) -> bool:
        normalized = normalize_project_key(key_name)
        if normalized is None:
            return False
        self._project_key = normalized
        self._project_key_source = "Manual"
        self._project_key_notes = MAJOR_SCALES[normalized]
        self._workspace_controller.mark_action(
            f"Key set to {normalized}: {' '.join(self._project_key_notes)}"
        )
        self._refresh_header()
        return True

    def _set_audio_sample_rate(self, sample_rate: int) -> None:
        self._audio_vm.sample_rate = int(sample_rate)
        self._sync_header_audio_config_to_panel()
        self._workspace_controller.mark_action(f"Sample rate set to {self._format_sample_rate(int(sample_rate))}")
        self._refresh_header()

    def _set_audio_buffer_size(self, buffer_size: int) -> None:
        self._audio_vm.buffer_size = int(buffer_size)
        self._sync_header_audio_config_to_panel()
        self._workspace_controller.mark_action(f"Block size set to {int(buffer_size)} samples")
        self._refresh_header()

    def _sync_header_audio_config_to_panel(self) -> None:
        if not hasattr(self, "_audio_panel"):
            return
        sample_rate = int(getattr(self, "_sample_rate_input", self._audio_panel.sample_rate_input).value())
        buffer_size = int(getattr(self, "_buffer_size_input", self._audio_panel.buffer_size_input).value())
        self._audio_vm.sample_rate = sample_rate
        self._audio_vm.buffer_size = buffer_size
        self._audio_panel.sample_rate_input.blockSignals(True)
        self._audio_panel.buffer_size_input.blockSignals(True)
        self._audio_panel.sample_rate_input.setValue(sample_rate)
        self._audio_panel.buffer_size_input.setValue(buffer_size)
        self._audio_panel.sample_rate_input.blockSignals(False)
        self._audio_panel.buffer_size_input.blockSignals(False)

    def _sync_audio_config_controls_from_vm(self) -> None:
        sample_rate = int(self._audio_vm.sample_rate or 48000)
        buffer_size = int(self._audio_vm.buffer_size or 256)
        if hasattr(self, "_sample_rate_input") and not self._sample_rate_input.hasFocus():
            self._sample_rate_input.blockSignals(True)
            self._sample_rate_input.setValue(sample_rate)
            self._sample_rate_input.blockSignals(False)
        if hasattr(self, "_buffer_size_input") and not self._buffer_size_input.hasFocus():
            self._buffer_size_input.blockSignals(True)
            self._buffer_size_input.setValue(buffer_size)
            self._buffer_size_input.blockSignals(False)

    def _format_sample_rate(self, sample_rate: int) -> str:
        if sample_rate % 1000 == 0:
            return f"{sample_rate // 1000}kHz"
        return f"{sample_rate / 1000:.1f}kHz"

    def _open_key_selection_wheel(self) -> None:
        dialog = KeySelectionWheelDialog(self._project_key, self)
        if dialog.exec() != dialog.Accepted:
            self._workspace_controller.mark_action("Key selection cancelled")
            self._refresh_workspace()
            return
        self._project_key = dialog.selected_key()
        self._project_key_source = "Manual"
        self._project_key_notes = dialog.selected_scale_notes()
        self._workspace_controller.mark_action(
            f"Key set to {self._project_key}: {' '.join(self._project_key_notes)}"
        )
        self._refresh_workspace()

    def _refresh_header(self) -> None:
        if not hasattr(self, "_runtime_status_label"):
            return
        session_ref = self._session_vm.session_ref or self._workspace_vm.session_ref or "Untitled Beat"
        project_title = session_ref if session_ref != "default-session" else "Untitled Beat"
        self._project_title_label.setText(f"MIDAS  |  {project_title}")
        if hasattr(self, "_header_session_ref_input") and not self._header_session_ref_input.hasFocus():
            self._header_session_ref_input.setText(session_ref if session_ref != "Untitled Beat" else "")
        sample_rate = self._audio_vm.sample_rate or 48000
        buffer_size = self._audio_vm.buffer_size or 256
        self._device_status_label.setText(f"{self._format_sample_rate(int(sample_rate))} / {buffer_size}")
        self._sync_audio_config_controls_from_vm()
        runtime = "active" if self._workspace_vm.runtime_active or self._transport_vm.runtime_active else "offline"
        self._status_chip.setText("Online" if runtime == "active" else "Offline")
        self._status_chip.setProperty("online", runtime == "active")
        self._status_chip.style().unpolish(self._status_chip)
        self._status_chip.style().polish(self._status_chip)
        self._runtime_status_label.setText(
            f"{self._workspace_vm.bridge_mode.title()} Bridge | {self._transport_vm.play_state}"
        )
        if hasattr(self, "_tempo_input") and not self._tempo_input.hasFocus():
            self._tempo_input.blockSignals(True)
            self._tempo_input.setValue(self._project_tempo_bpm)
            self._tempo_input.blockSignals(False)
        if hasattr(self, "_key_button"):
            self._key_button.setText(self._project_key)
        if hasattr(self, "_key_notes_label"):
            self._key_notes_label.setText(
                f"Scale: {'  '.join(self._project_key_notes)} | Source: {self._project_key_source}"
            )
        self._hint_status_label.setText(
            f"{self._workspace_vm.startup_hint} | "
            f"Browser -> Arrangement/Editor -> Mixer | Last: {self._workspace_vm.last_action}"
        )
        if hasattr(self, "_header_mixer_button"):
            self._header_mixer_button.setChecked(not self._mixer_dock.isHidden())
        if hasattr(self, "_left_panel_button"):
            self._left_panel_button.setChecked(not self._audio_dock.isHidden())
        if hasattr(self, "_right_panel_button"):
            self._right_panel_button.setChecked(not self._browser_dock.isHidden())
        if hasattr(self, "_bottom_panel_button"):
            self._bottom_panel_button.setChecked(not self._mixer_dock.isHidden())

    def _toggle_mixer_dock(self) -> None:
        self._set_mixer_visible(self._header_mixer_button.isChecked())

    def _set_mixer_visible(self, should_show: bool, *, refresh: bool = True) -> None:
        self._mixer_dock.setVisible(should_show)
        self._header_mixer_button.setChecked(should_show)
        if hasattr(self, "_bottom_panel_button"):
            self._bottom_panel_button.setChecked(should_show)
        if refresh:
            self._workspace_controller.mark_action("Opened mixer" if should_show else "Closed mixer")
            self._refresh_header()

    def _toggle_dock(self, dock: QDockWidget, label: str) -> None:
        dock.setVisible(dock.isHidden())
        self._workspace_controller.mark_action(f"{'Opened' if not dock.isHidden() else 'Closed'} {label}")
        self._refresh_header()

    def _mount_commands(self) -> None:
        self._command_actions: dict[str, QAction] = {}

        def register(label: str, callback, shortcut: str = "") -> None:
            action = QAction(label, self)
            if shortcut:
                action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(callback)
            self.addAction(action)
            self._command_actions[label] = action

        register("New Session", lambda: self._new_session(self._header_session_ref_input.text()), "Ctrl+N")
        register("Open Session", lambda: self._open_session(self._header_session_ref_input.text()), "Ctrl+O")
        register("Save Session", self._save_session, "Ctrl+S")
        register("Load Session", self._load_session, "Ctrl+L")
        register("Apply Session", self._apply_session, "Ctrl+Return")
        register("Refresh All", self._manual_refresh_all, "Ctrl+R")
        register("Play", self._play_transport, "Space")
        register("Stop", self._stop_transport, "Shift+Space")
        register("Add Track", self._workspace_panel.add_arrangement_track_button.click, "Ctrl+T")
        register("Show Arrangement", self._workspace_panel.show_arrangement, "Ctrl+1")
        register("Show Drum Machine", self._workspace_panel.show_drum_machine, "Ctrl+2")
        register("Show Piano Roll", self._workspace_panel.show_piano_roll, "Ctrl+3")
        register("Show Mix", self._show_mix_workspace, "Ctrl+4")
        register("Show Browse", self._show_browse_workspace, "Ctrl+5")
        register("Edit BPM", self._focus_tempo_control, "Ctrl+Shift+B")
        register("Open Key Wheel", self._open_key_selection_wheel, "Ctrl+K")
        register("Show Navigation Help", self._show_onboarding_dialog, "Ctrl+/")
        register("Toggle Browser", lambda: self._toggle_dock(self._browser_dock, "browser"), "Ctrl+B")
        register("Toggle Audio", lambda: self._toggle_dock(self._audio_dock, "audio"), "Ctrl+Shift+A")
        register("Toggle Mixer", lambda: self._set_mixer_visible(self._mixer_dock.isHidden()), "Ctrl+M")
        register("Toggle Session", lambda: self._toggle_dock(self._session_dock, "session"), "Ctrl+Shift+S")
        register("Toggle Transport", lambda: self._toggle_dock(self._transport_dock, "transport"), "Ctrl+Shift+T")
        register("Toggle Debug", lambda: self._toggle_dock(self._debug_dock, "debug"), "Ctrl+Shift+D")
        register("Add FX", self._insert_selected_plugin, "Ctrl+Shift+F")
        register("Focus Mode", lambda: self._focus_mode_button.click(), "Ctrl+Shift+0")
        register("Reset Layout", self._reset_layout, "Ctrl+Shift+R")

        self._command_completer = QCompleter(sorted(self._command_actions), self)
        self._command_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._command_search_input.setCompleter(self._command_completer)

    def _execute_command_search(self) -> None:
        query = self._command_search_input.text().strip()
        if not query:
            return
        if self._execute_project_command(query):
            self._command_search_input.clear()
            return
        exact = {name.lower(): action for name, action in self._command_actions.items()}
        action = exact.get(query.lower())
        if action is None:
            action = next(
                (candidate for name, candidate in self._command_actions.items() if query.lower() in name.lower()),
                None,
            )
        if action is None:
            self._workspace_controller.mark_action(f"Command not found: {query}")
            self._refresh_workspace()
            return
        self._command_search_input.clear()
        action.trigger()

    def _execute_project_command(self, query: str) -> bool:
        lowered = query.lower().strip()
        tempo_prefixes = ("set bpm", "bpm", "tempo", "set tempo")
        for prefix in tempo_prefixes:
            if lowered.startswith(prefix):
                value_text = lowered.removeprefix(prefix).replace("to", "").strip()
                try:
                    tempo = float(value_text)
                except ValueError:
                    self._workspace_controller.mark_action(f"Tempo command needs a number: {query}")
                    self._refresh_workspace()
                    return True
                self._tempo_input.setValue(max(self._tempo_input.minimum(), min(self._tempo_input.maximum(), tempo)))
                return True
        key_prefixes = ("change key to", "set key to", "key")
        for prefix in key_prefixes:
            if lowered.startswith(prefix):
                key_text = query[len(prefix):].strip() if query.lower().startswith(prefix) else ""
                if not key_text:
                    self._workspace_controller.mark_action("Key command needs a key name")
                    self._refresh_workspace()
                    return True
                if not self._set_project_key(key_text):
                    self._workspace_controller.mark_action(f"Unknown key: {key_text}")
                    self._refresh_workspace()
                return True
        sample_rate_prefixes = ("set sample rate", "sample rate")
        for prefix in sample_rate_prefixes:
            if lowered.startswith(prefix):
                value_text = lowered.removeprefix(prefix).replace("to", "").strip()
                multiplier = 1000 if "khz" in value_text else 1
                value_text = value_text.replace("khz", "").replace("hz", "").strip()
                try:
                    sample_rate = int(float(value_text) * multiplier)
                except ValueError:
                    self._workspace_controller.mark_action(f"Sample rate command needs a number: {query}")
                    self._refresh_workspace()
                    return True
                self._sample_rate_input.setValue(
                    max(self._sample_rate_input.minimum(), min(self._sample_rate_input.maximum(), sample_rate))
                )
                return True
        buffer_prefixes = ("set block size", "block size", "set buffer", "buffer")
        for prefix in buffer_prefixes:
            if lowered.startswith(prefix):
                value_text = lowered.removeprefix(prefix).replace("to", "").replace("samples", "").strip()
                try:
                    buffer_size = int(float(value_text))
                except ValueError:
                    self._workspace_controller.mark_action(f"Block size command needs a number: {query}")
                    self._refresh_workspace()
                    return True
                self._buffer_size_input.setValue(
                    max(self._buffer_size_input.minimum(), min(self._buffer_size_input.maximum(), buffer_size))
                )
                return True
        return False

    def _apply_mixer_mute(self) -> None:
        channel = self._mixer_panel.selected_channel()
        self._mixer_vm.selected_channel_id = channel
        result = self._mixer_controller.set_mute(channel, self._mixer_panel.selected_mute())
        self._debug_panel.append_result("set_channel_mute", result.code, result.message)
        self._workspace_controller.mark_action(f"Set channel {channel} mute")
        if result.ok:
            self._mark_session_modified()
        self._refresh_mixer()

    def _apply_mixer_gain(self) -> None:
        channel = self._mixer_panel.selected_channel()
        self._mixer_vm.selected_channel_id = channel
        result = self._mixer_controller.set_gain(channel, self._mixer_panel.selected_gain())
        self._debug_panel.append_result("set_channel_gain", result.code, result.message)
        self._workspace_controller.mark_action(f"Set channel {channel} gain")
        if result.ok:
            self._mark_session_modified()
        self._refresh_mixer()

    def _save_session(self) -> None:
        result = self._session_controller.save_session()
        self._debug_panel.append_result("save_session", result.code, result.message)
        self._workspace_controller.mark_action("Saved session")
        self._refresh_session()

    def _new_session(self, session_ref: str) -> None:
        result = self._session_controller.new_session(session_ref)
        self._debug_panel.append_result("new_session", result.code, result.message)
        self._workspace_controller.mark_action(f"New session {session_ref.strip() or '-'}")
        self._refresh_session()
        self._refresh_mixer()

    def _open_session(self, session_ref: str) -> None:
        result = self._session_controller.open_session(session_ref)
        self._debug_panel.append_result("open_session", result.code, result.message)
        self._workspace_controller.mark_action(f"Open session {session_ref.strip() or '-'}")
        self._refresh_session()
        self._refresh_mixer()
        self._refresh_workspace()

    def _open_existing_session(self) -> None:
        self._session_controller.refresh_status()
        dialog = OpenExistingSessionDialog(
            sessions=list(self._session_vm.discoverable_sessions),
            active_session_ref=self._session_vm.session_ref,
            recent_session_refs=[entry.session_ref for entry in self._session_vm.recent_sessions],
            parent=self,
        )
        if dialog.exec() != dialog.Accepted:
            self._workspace_controller.mark_action("Open existing session cancelled")
            self._refresh_workspace()
            return
        if dialog.browse_requested():
            self._browse_existing_session_file()
            return
        session_ref = dialog.selected_session_ref().strip()
        if not session_ref:
            self._debug_panel.append_result("open_existing_session", 3, "No discoverable session selected")
            self._workspace_controller.mark_action("Open existing session failed")
            self._refresh_workspace()
            return
        self._debug_panel.append_result("open_existing_session_pick", 0, session_ref)
        self._open_session(session_ref)

    def _browse_existing_session_file(self) -> None:
        storage_root = self._bridge.get_session_storage_root()
        selected_path, _ = QFileDialog.getOpenFileName(
            self,
            "Browse Existing Session",
            storage_root,
            "MIDAS Sessions (*.session)",
        )
        if not selected_path:
            self._workspace_controller.mark_action("Browse existing session cancelled")
            self._refresh_workspace()
            return
        session_ref = Path(selected_path).stem
        self._debug_panel.append_result("browse_existing_session_pick", 0, selected_path)
        self._open_session(session_ref)

    def _open_recent_session(self, session_ref: str) -> None:
        if not session_ref:
            self._debug_panel.append_result("open_recent_session", 3, "No recent session selected")
            return
        self._open_session(session_ref)

    def _load_session(self) -> None:
        result = self._session_controller.load_session()
        self._debug_panel.append_result("load_session", result.code, result.message)
        self._workspace_controller.mark_action("Loaded session")
        self._refresh_session()
        self._refresh_mixer()

    def _apply_session(self) -> None:
        result = self._session_controller.apply_session()
        self._debug_panel.append_result("apply_session", result.code, result.message)
        self._workspace_controller.mark_action("Applied session")
        self._refresh_session()
        self._refresh_mixer()

    def _reconcile_all_inserts(self) -> None:
        ok = self._workspace_controller.reconcile_all_inserts()
        self._debug_panel.append_result("reconcile_all_inserts", 0 if ok else 4, "" if ok else "reconcile failed")
        self._workspace_controller.mark_action("Reconciled inserts")
        self._refresh_mixer()
        self._refresh_workspace()

    def _play_transport(self) -> None:
        self._transport_vm.track_channel = self._transport_panel.selected_track_channel()
        result = self._transport_controller.play()
        self._debug_panel.append_result("play_transport", result.code, result.message)
        self._workspace_controller.mark_action("Play transport")
        self._refresh_transport()

    def _stop_transport(self) -> None:
        result = self._transport_controller.stop()
        self._debug_panel.append_result("stop_transport", result.code, result.message)
        self._workspace_controller.mark_action("Stop transport")
        self._refresh_transport()

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
            self._debug_panel.set_subscription_state(True)
            return
        except Exception:
            self._using_polling_fallback = True
            self._debug_panel.set_subscription_state(False)

    def _on_bridge_event(self, event) -> None:
        # Bridge callbacks can arrive off the Qt UI thread; signal marshals safely.
        self._event_relay.event_received.emit(event)

    def _handle_bridge_event(self, event) -> None:
        self._debug_panel.append_event(event)
        # Event model for phase 1: notify first, then re-query authoritative state.
        self._refresh_audio()
        if getattr(event, "category", "") == "mixer":
            self._refresh_mixer()
        if getattr(event, "category", "") == "session":
            self._refresh_session()
        if getattr(event, "category", "") == "transport":
            self._refresh_transport()

    def closeEvent(self, event) -> None:  # noqa: N802
        self._save_shell_state()
        if self._event_subscription_handle != -1:
            try:
                self._bridge.unsubscribe_events(self._event_subscription_handle)
                self._debug_panel.set_subscription_state(False)
            except Exception:
                pass
        super().closeEvent(event)

    def _manual_refresh_all(self) -> None:
        self._workspace_controller.mark_action("Manual refresh")
        self._refresh_audio()
        self._refresh_mixer()
        self._refresh_session()
        self._refresh_transport()
        self._refresh_browser()

    def _mark_session_modified(self) -> None:
        self._session_controller.mark_dirty()

    def _midi_notes_changed(self, track_name: str, note_count: int) -> None:
        detected_key = self._infer_project_key_from_midi(self._workspace_panel.midi_pitches_for_track(track_name))
        if detected_key is not None:
            self._project_key = detected_key
            self._project_key_notes = MAJOR_SCALES[detected_key]
            self._project_key_source = f"MIDI: {track_name}"
            self._workspace_controller.mark_action(
                f"MIDI notes updated on {track_name} ({note_count}); detected {detected_key}"
            )
        else:
            self._workspace_controller.mark_action(f"MIDI notes updated on {track_name} ({note_count})")
        self._mark_session_modified()
        self._refresh_session()

    def _infer_project_key_from_midi(self, pitches: list[str]) -> str | None:
        pitch_classes = [self._normalize_pitch_class(pitch) for pitch in pitches]
        pitch_classes = [pitch for pitch in pitch_classes if pitch]
        if not pitch_classes:
            return None
        counts: dict[str, int] = {}
        for pitch in pitch_classes:
            counts[pitch] = counts.get(pitch, 0) + 1
        tonic_hint = pitch_classes[0]
        best_key = None
        best_score = -1
        for key_name, scale_notes in MAJOR_SCALES.items():
            tonic = self._normalize_pitch_class(scale_notes[0])
            scale = {self._normalize_pitch_class(note) for note in scale_notes[:-1]}
            score = sum(count for pitch, count in counts.items() if pitch in scale)
            score -= sum(count for pitch, count in counts.items() if pitch not in scale) * 2
            if tonic in counts:
                score += counts[tonic] * 2
            if tonic == tonic_hint:
                score += 1
            if score > best_score:
                best_key = key_name
                best_score = score
        return best_key if best_score > 0 else None

    @staticmethod
    def _normalize_pitch_class(pitch: str) -> str:
        cleaned = "".join(ch for ch in pitch.strip() if not ch.isdigit()).replace("♯", "#").replace("♭", "b")
        aliases = {
            "A#": "Bb",
            "B#": "C",
            "Cb": "B",
            "C#": "Db",
            "D#": "Eb",
            "E#": "F",
            "Fb": "E",
            "F#": "Gb",
            "G#": "Ab",
        }
        return aliases.get(cleaned, cleaned)

    def _refresh_debug_summary(self) -> None:
        runtime_status = self._bridge.get_runtime_status()
        mixer_channel = self._mixer_controller.channel(self._mixer_vm.selected_channel_id)
        managed_instances = self._bridge.get_managed_instances()
        transition_history = self._bridge.get_managed_instance_history()
        managed_rows = [
            (
                f"{item.managed_instance_id} | {item.plugin_id or '-'} | "
                f"ch{item.channel_id}:slot{item.slot_index} | "
                f"placeholder={item.placeholder_instance_id or '-'} | "
                f"state={item.managed_instance_state or '-'} | "
                f"adapter={item.managed_instance_adapter_state or '-'} | "
                f"reason={item.managed_instance_adapter_reason_code or '-'} | "
                f"backend={item.managed_instance_backend_name or '-'} | "
                f"handle={item.managed_instance_backend_handle or '-'} | "
                f"handle_state={item.managed_instance_handle_state or '-'} | "
                f"terminal={'yes' if item.managed_instance_terminal else 'no'} | "
                f"retryable={'yes' if item.managed_instance_retryable else 'no'} | "
                f"reason_source={item.managed_instance_reason_source or '-'} | "
                f"loader_strategy={item.managed_instance_loader_strategy or '-'} | "
                f"validator={item.managed_instance_validator_path or '-'} | "
                f"attribution={item.managed_instance_failure_attribution or '-'} | "
                f"descriptor_id={item.managed_instance_descriptor_id or '-'} | "
                f"descriptor={item.managed_instance_descriptor_kind or '-'}:{item.managed_instance_descriptor_ref or '-'} | "
                f"seq={item.managed_instance_created_sequence} | "
                f"msg={item.managed_instance_message or '-'}"
            )
            for item in managed_instances
        ]
        transition_rows = [
            (
                f"seq={item.sequence} | ch{item.channel_id}:slot{item.slot_index} | "
                f"{item.from_adapter_state}->{item.to_adapter_state} | "
                f"reason={item.reason_code or '-'} | "
                f"applied={'yes' if item.applied else 'no'} | "
                f"retry_allowed={'yes' if item.retry_allowed else 'no'} | "
                f"msg={item.message or '-'}"
            )
            for item in transition_history
        ]
        selected_slot = next(
            (slot for slot in self._mixer_vm.insert_chain if slot.slot_index == self._mixer_vm.selected_slot_index),
            None,
        )
        selected_summary = (
            f"{selected_slot.managed_instance_id or '-'} / "
            f"{selected_slot.managed_instance_state or '-'} / "
            f"{selected_slot.managed_instance_adapter_state or '-'} / "
            f"{selected_slot.managed_instance_handle_state or '-'} / "
            f"{selected_slot.managed_instance_reason_source or '-'} / "
            f"{selected_slot.managed_instance_loader_strategy or '-'} / "
            f"{selected_slot.managed_instance_validator_path or '-'} / "
            f"{selected_slot.managed_instance_failure_attribution or '-'} / "
            f"{'retryable' if selected_slot.managed_instance_retryable else 'terminal'}"
            if selected_slot is not None
            else "-"
        )
        selected_backend_name = selected_slot.managed_instance_backend_name if selected_slot is not None else ""
        selected_backend_handle = selected_slot.managed_instance_backend_handle if selected_slot is not None else ""
        selected_handle_state = selected_slot.managed_instance_handle_state if selected_slot is not None else ""
        selected_terminal = selected_slot.managed_instance_terminal if selected_slot is not None else False
        selected_retryable = selected_slot.managed_instance_retryable if selected_slot is not None else False
        selected_reason_source = selected_slot.managed_instance_reason_source if selected_slot is not None else ""
        selected_descriptor_id = selected_slot.managed_instance_descriptor_id if selected_slot is not None else ""
        selected_descriptor_kind = selected_slot.managed_instance_descriptor_kind if selected_slot is not None else ""
        selected_descriptor_ref = selected_slot.managed_instance_descriptor_ref if selected_slot is not None else ""
        selected_reason = runtime_status.selected_slot_adapter_reason_code or runtime_status.selected_slot_loader_reason_code
        selected_message = runtime_status.selected_slot_adapter_message or runtime_status.selected_slot_loader_message
        if selected_slot is not None:
            selected_message = (
                f"{selected_message or '-'} | "
                f"strategy={selected_slot.managed_instance_loader_strategy or '-'} | "
                f"validator={selected_slot.managed_instance_validator_path or '-'} | "
                f"attribution={selected_slot.managed_instance_failure_attribution or '-'}"
            )
        self._debug_panel.set_domain_statuses(
            audio=(
                f"runtime={'on' if self._audio_vm.runtime_started else 'off'}, "
                f"state={self._audio_vm.state}, "
                f"render={self._audio_vm.render_status}, "
                f"frames={self._audio_vm.render_frames_produced}/{self._audio_vm.render_frames_requested}"
            ),
            mixer=f"ch={mixer_channel.channel_id}, muted={mixer_channel.muted}, gain={mixer_channel.gain:.3f}",
            session=f"status={self._session_vm.status}, ref={self._session_vm.session_ref}",
            transport=(
                f"control={self._transport_vm.play_state}, "
                f"runtime={'on' if self._transport_vm.runtime_active else 'off'}, "
                f"audio={self._transport_vm.audio_lifecycle_state}, "
                f"render={self._transport_vm.render_status}"
            ),
        )
        self._debug_panel.set_backend_summary(
            backend_name=runtime_status.backend_name,
            supports_create=runtime_status.supports_create,
            supports_destroy=runtime_status.supports_destroy,
            supports_query=runtime_status.supports_query,
            support_scope=runtime_status.support_scope_summary,
            selected_slot_reason=selected_reason,
            selected_slot_message=selected_message,
            selected_backend_name=selected_backend_name,
            selected_backend_handle=selected_backend_handle,
            selected_handle_state=selected_handle_state,
            selected_terminal=selected_terminal,
            selected_retryable=selected_retryable,
            selected_reason_source=selected_reason_source,
            selected_descriptor_id=selected_descriptor_id,
            selected_descriptor_kind=selected_descriptor_kind,
            selected_descriptor_ref=selected_descriptor_ref,
            catalog_source_label=runtime_status.catalog_source_label,
            catalog_source_version=runtime_status.catalog_source_version,
            catalog_descriptor_count=runtime_status.catalog_descriptor_count,
            catalog_valid_descriptor_count=runtime_status.catalog_valid_descriptor_count,
            catalog_policy_supported_descriptor_count=runtime_status.catalog_policy_supported_descriptor_count,
        )
        self._debug_panel.set_managed_instance_status(
            summary=f"active={len(managed_instances)} selected={selected_summary}",
            rows=managed_rows or ["No managed instances"],
        )
        self._debug_panel.set_transition_history(
            summary=f"count={len(transition_history)}",
            rows=transition_rows or ["No adapter transitions"],
        )

    def _restore_shell_state(self) -> None:
        geometry = self._settings.load_geometry()
        if geometry is not None:
            self.restoreGeometry(geometry)
        if self._settings.load_layout_version() == self.LAYOUT_VERSION:
            state = self._settings.load_window_state()
            if state is not None:
                self.restoreState(state)
        else:
            self._apply_default_dock_layout()
        self._fit_to_screen()
        self._debug_panel.set_event_filter(self._settings.load_debug_filter())

    def _save_shell_state(self) -> None:
        self._settings.save_geometry(self.saveGeometry())
        self._settings.save_window_state(self.saveState())
        self._settings.save_layout_version(self.LAYOUT_VERSION)
        self._settings.save_debug_filter(self._debug_panel.event_filter_value())

    def _mount_view_menu(self) -> None:
        view_menu = self.menuBar().addMenu("View")
        for dock in (
            self._browser_dock,
            self._audio_dock,
            self._mixer_dock,
            self._session_dock,
            self._transport_dock,
            self._debug_dock,
        ):
            view_menu.addAction(dock.toggleViewAction())

    def _apply_default_dock_layout(self) -> None:
        self._audio_dock.hide()
        self._browser_dock.show()
        self._browser_dock.raise_()
        self._mixer_dock.raise_()
        self._session_dock.hide()
        self._mixer_dock.hide()
        self._transport_dock.hide()
        self._debug_dock.hide()
        available = self._available_screen_geometry()
        browser_width = 230 if available is None else max(210, min(260, int(available.width() * 0.22)))
        mixer_height = 280 if available is None else max(240, min(320, int(available.height() * 0.34)))
        self.resizeDocks([self._browser_dock], [browser_width], Qt.Horizontal)
        self.resizeDocks([self._mixer_dock], [mixer_height], Qt.Vertical)

    def _default_window_size(self) -> tuple[int, int]:
        available = self._available_screen_geometry()
        if available is None:
            return self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT
        width = min(self.DEFAULT_WIDTH, max(self.MIN_WIDTH, int(available.width() * 0.92)))
        height = min(self.DEFAULT_HEIGHT, max(self.MIN_HEIGHT, int(available.height() * 0.88)))
        return width, height

    def _fit_to_screen(self) -> None:
        available = self._available_screen_geometry()
        if available is None:
            return
        max_width = max(self.MIN_WIDTH, available.width() - self.SCREEN_MARGIN)
        max_height = max(self.MIN_HEIGHT, available.height() - self.SCREEN_MARGIN)
        if self.width() > max_width or self.height() > max_height:
            self.resize(min(self.width(), max_width), min(self.height(), max_height))
        frame = self.frameGeometry()
        if not available.contains(frame):
            frame.moveCenter(available.center())
            self.move(frame.topLeft())

    @staticmethod
    def _available_screen_geometry():
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return None
        return screen.availableGeometry()

    @staticmethod
    def _scrollable_panel(widget: QWidget) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        return scroll


# Keep Qt imports grouped with UI shell to avoid accidental backend coupling in modules.
from pathlib import Path  # noqa: E402
from PySide6.QtCore import Qt  # noqa: E402


class _UiEventRelay(QObject):
    event_received = Signal(object)
