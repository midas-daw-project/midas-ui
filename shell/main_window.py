from __future__ import annotations

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtWidgets import QDockWidget, QFileDialog, QMainWindow, QMessageBox

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
from panels.session.session_panel import SessionPanel
from panels.transport.transport_panel import TransportPanel
from panels.workspace.open_existing_session_dialog import OpenExistingSessionDialog
from panels.workspace.workspace_panel import WorkspacePanel
from shell.settings_store import ShellSettingsStore
from viewmodels.audio_viewmodel import AudioViewModel
from viewmodels.browser_viewmodel import BrowserViewModel
from viewmodels.mixer_viewmodel import MixerViewModel
from viewmodels.session_viewmodel import SessionViewModel
from viewmodels.transport_viewmodel import TransportViewModel
from viewmodels.workspace_viewmodel import WorkspaceViewModel


class MainWindow(QMainWindow):
    def __init__(self, bridge: BridgeClient) -> None:
        super().__init__()
        self._bridge = bridge
        self._settings = ShellSettingsStore()
        self.setWindowTitle("MIDAS - Phase 1 Shell")
        self.resize(1280, 780)

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
        )
        bridge_mode = "native" if self._bridge.__class__.__name__ == "NativeBridgeClient" else "fallback"
        self._workspace_controller.set_bridge_identity(mode=bridge_mode, version=self._bridge.bridge_version())
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

        self._mount_docks()
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

    def _mount_docks(self) -> None:
        self.setCentralWidget(self._workspace_panel)

        audio_dock = QDockWidget("Audio", self)
        audio_dock.setObjectName("dock.audio")
        audio_dock.setWidget(self._audio_panel)
        self.addDockWidget(Qt.LeftDockWidgetArea, audio_dock)

        debug_dock = QDockWidget("Debug / Events", self)
        debug_dock.setObjectName("dock.debug")
        debug_dock.setWidget(self._debug_panel)
        self.addDockWidget(Qt.BottomDockWidgetArea, debug_dock)

        mixer_dock = QDockWidget("Mixer", self)
        mixer_dock.setObjectName("dock.mixer")
        mixer_dock.setWidget(self._mixer_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, mixer_dock)

        session_dock = QDockWidget("Session", self)
        session_dock.setObjectName("dock.session")
        session_dock.setWidget(self._session_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, session_dock)

        transport_dock = QDockWidget("Transport", self)
        transport_dock.setObjectName("dock.transport")
        transport_dock.setWidget(self._transport_panel)
        self.addDockWidget(Qt.TopDockWidgetArea, transport_dock)

        browser_dock = QDockWidget("Browser", self)
        browser_dock.setObjectName("dock.browser")
        browser_dock.setWidget(self._browser_panel)
        self.addDockWidget(Qt.LeftDockWidgetArea, browser_dock)

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
        self._browser_controller.select_plugin(plugin_id)
        self._workspace_controller.mark_action(f"Selected plugin {plugin_id}")
        self._browser_panel.render(self._browser_vm)
        self._refresh_workspace()

    def _insert_selected_plugin(self) -> None:
        channel = self._mixer_panel.selected_channel()
        slot = self._mixer_panel.selected_slot_index()
        plugin_id = self._browser_vm.selected_plugin_id.strip()
        if not plugin_id:
            self._debug_panel.append_result("insert_plugin", 3, "No plugin selected")
            return
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
        state = self._settings.load_window_state()
        if state is not None:
            self.restoreState(state)
        self._debug_panel.set_event_filter(self._settings.load_debug_filter())

    def _save_shell_state(self) -> None:
        self._settings.save_geometry(self.saveGeometry())
        self._settings.save_window_state(self.saveState())
        self._settings.save_debug_filter(self._debug_panel.event_filter_value())


# Keep Qt imports grouped with UI shell to avoid accidental backend coupling in modules.
from pathlib import Path  # noqa: E402
from PySide6.QtCore import Qt  # noqa: E402


class _UiEventRelay(QObject):
    event_received = Signal(object)
