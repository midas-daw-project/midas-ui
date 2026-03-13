from __future__ import annotations

from datetime import datetime
from typing import Callable

from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidgetItem,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from viewmodels.workspace_viewmodel import WorkspaceViewModel


class WorkspacePanel(QWidget):
    def __init__(
        self,
        on_refresh_all: Callable[[], None],
        on_new_session: Callable[[str], None],
        on_open_session: Callable[[str], None],
        on_open_existing_session: Callable[[], None],
        on_open_recent: Callable[[str], None],
        on_save_session: Callable[[], None],
        on_load_session: Callable[[], None],
        on_apply_session: Callable[[], None],
        on_reconcile_inserts: Callable[[], None],
    ) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        self.title_label = QLabel("MIDAS Workspace")
        self.mode_label = QLabel("Shell / Runtime Overview")
        layout.addWidget(self.title_label)
        layout.addWidget(self.mode_label)

        overview_box = QGroupBox("Current Project")
        overview_form = QFormLayout(overview_box)
        self.project_heading_label = QLabel("No active session")
        self.project_heading_label.setStyleSheet("font-weight: 600; font-size: 16px;")
        self.project_summary_label = QLabel("Open or create a session to begin.")
        self.project_summary_label.setWordWrap(True)
        self.session_status_label = QLabel("Status: idle")
        self.session_identity_label = QLabel("Phase: none | Dirty: clean | Last: none")
        self.session_storage_label = QLabel("Storage: -")
        self.session_error_label = QLabel("Session Error: -")
        self.session_error_label.setWordWrap(True)
        self.startup_hint_label = QLabel("Create a new session or open an existing one.")
        self.startup_hint_label.setWordWrap(True)
        self.bridge_label = QLabel("Bridge: unknown v0")
        self.recent_summary_label = QLabel("Recent Sessions: none")
        self.discoverable_summary_label = QLabel("Discoverable Sessions: 0")
        overview_form.addRow(self.project_heading_label)
        overview_form.addRow(self.project_summary_label)
        overview_form.addRow("Session", self.session_status_label)
        overview_form.addRow("Identity", self.session_identity_label)
        overview_form.addRow("Storage", self.session_storage_label)
        overview_form.addRow("Recent", self.recent_summary_label)
        overview_form.addRow("Discoverable", self.discoverable_summary_label)
        overview_form.addRow("Next", self.startup_hint_label)
        overview_form.addRow("Error", self.session_error_label)
        overview_form.addRow("Bridge", self.bridge_label)
        layout.addWidget(overview_box)

        runtime_box = QGroupBox("Runtime Snapshot")
        runtime_form = QFormLayout(runtime_box)
        self.audio_label = QLabel("Audio: idle")
        self.transport_label = QLabel("Transport: stopped")
        self.runtime_label = QLabel("Runtime Active: no")
        self.render_label = QLabel("Render: stopped")
        self.mixer_label = QLabel("Mixer: channels=0, muted=0")
        self.plugin_label = QLabel("Plugins: total=0, available=0")
        self.selected_plugin_label = QLabel("Selected Plugin: -")
        self.inserted_plugin_label = QLabel("Inserted Plugins: 0")
        self.selected_insert_label = QLabel("Selected Insert: -")
        self.instance_label = QLabel("Managed Instances: active=0 failed=0")
        self.selected_instance_label = QLabel("Selected Managed Instance: -")
        self.reconcile_label = QLabel("Reconcile: attempted=0 resolved=0 failed=0 created=0 cleared=0")
        self.reconcile_policy_label = QLabel("Reconcile Policy: mode=none action=none pending_manual=no")
        runtime_form.addRow(self.audio_label)
        runtime_form.addRow(self.transport_label)
        runtime_form.addRow(self.runtime_label)
        runtime_form.addRow(self.render_label)
        runtime_form.addRow(self.mixer_label)
        runtime_form.addRow(self.plugin_label)
        runtime_form.addRow(self.selected_plugin_label)
        runtime_form.addRow(self.inserted_plugin_label)
        runtime_form.addRow(self.selected_insert_label)
        runtime_form.addRow(self.instance_label)
        runtime_form.addRow(self.selected_instance_label)
        runtime_form.addRow(self.reconcile_label)
        runtime_form.addRow(self.reconcile_policy_label)
        layout.addWidget(runtime_box)

        home_box = QGroupBox("Workspace Home")
        home_layout = QVBoxLayout(home_box)
        self.home_intro_label = QLabel("Start a new session, open a known session ref, or resume from recent work.")
        self.home_intro_label.setWordWrap(True)
        self.new_section_label = QLabel("New Session")
        self.session_ref_input = QLineEdit("default-session")
        self.session_ref_input.setPlaceholderText("session-ref")
        self.new_session_button = QPushButton("New Session")
        self.open_section_label = QLabel("Open Existing Session")
        self.open_session_button = QPushButton("Open By Ref")
        self.open_existing_button = QPushButton("Open Existing Session")
        self.recent_section_label = QLabel("Recent Sessions")
        self.recent_hint_label = QLabel("Open the selected recent session or use Open Existing Session for discovered entries.")
        self.recent_hint_label.setWordWrap(True)
        self.recent_list = QListWidget()
        self.open_recent_button = QPushButton("Open Selected Recent")
        self.recent_summary_card_label = QLabel("No recent session history yet.")
        self.recent_summary_card_label.setWordWrap(True)
        action_row = QHBoxLayout()
        action_row.addWidget(self.new_session_button)
        action_row.addWidget(self.open_session_button)
        action_row.addWidget(self.open_existing_button)
        home_layout.addWidget(self.home_intro_label)
        home_layout.addWidget(self.new_section_label)
        home_layout.addWidget(self.session_ref_input)
        home_layout.addLayout(action_row)
        home_layout.addWidget(self.open_section_label)
        home_layout.addWidget(self.recent_summary_card_label)
        home_layout.addWidget(self.recent_section_label)
        home_layout.addWidget(self.recent_hint_label)
        home_layout.addWidget(self.recent_list)
        home_layout.addWidget(self.open_recent_button)
        layout.addWidget(home_box)

        actions_box = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout(actions_box)
        self.refresh_button = QPushButton("Refresh All")
        self.save_button = QPushButton("Save Session")
        self.load_button = QPushButton("Load Session")
        self.apply_button = QPushButton("Apply Session")
        self.reconcile_button = QPushButton("Reconcile Inserts")
        self.last_action_label = QLabel("Last Action: Ready")
        actions_layout.addWidget(self.refresh_button)
        actions_layout.addWidget(self.save_button)
        actions_layout.addWidget(self.load_button)
        actions_layout.addWidget(self.apply_button)
        actions_layout.addWidget(self.reconcile_button)
        actions_layout.addWidget(self.last_action_label)
        layout.addWidget(actions_box)

        self.new_session_button.clicked.connect(lambda: on_new_session(self.session_ref_input.text()))
        self.open_session_button.clicked.connect(lambda: on_open_session(self.session_ref_input.text()))
        self.open_existing_button.clicked.connect(on_open_existing_session)
        self.refresh_button.clicked.connect(on_refresh_all)
        self.save_button.clicked.connect(on_save_session)
        self.load_button.clicked.connect(on_load_session)
        self.apply_button.clicked.connect(on_apply_session)
        self.reconcile_button.clicked.connect(on_reconcile_inserts)
        self.open_recent_button.clicked.connect(lambda: on_open_recent(self.selected_recent_session_ref()))

    def render(self, vm: WorkspaceViewModel) -> None:
        self.title_label.setText(vm.workspace_title)
        self.mode_label.setText(vm.workspace_mode)
        self.session_ref_input.setText(vm.session_ref)
        self.project_heading_label.setText(vm.session_ref or "No active session")
        self.session_status_label.setText(vm.session_status)
        self.session_identity_label.setText(
            f"Phase: {vm.session_phase} | Dirty: {'dirty' if vm.session_dirty else 'clean'} | Last: {vm.session_last_operation}"
        )
        self.session_storage_label.setText(
            f"{(vm.session_storage_path or '-')} | Source: {(vm.session_storage_source or '-')}"
        )
        self.project_summary_label.setText(vm.current_project_summary or "No active session")
        self.startup_hint_label.setText(vm.startup_hint)
        self.session_error_label.setText(vm.session_error_summary or "-")
        self.bridge_label.setText(f"Bridge: {vm.bridge_mode} v{vm.bridge_version}")
        self.recent_summary_label.setText(
            f"{vm.recent_session_count} total | Latest: {vm.recent_session_summary or 'none'}"
        )
        self.discoverable_summary_label.setText(
            f"{vm.discoverable_session_count} available from storage root"
        )
        self.recent_summary_card_label.setText(
            f"Current: {vm.session_ref or '-'} | Recent: {vm.recent_session_count} | Discoverable: {vm.discoverable_session_count}"
        )
        self.audio_label.setText(f"Audio: {vm.audio_state}")
        self.transport_label.setText(f"Transport: {vm.transport_state}")
        self.runtime_label.setText(f"Runtime Active: {'yes' if vm.runtime_active else 'no'}")
        self.render_label.setText(f"Render: {vm.render_status}")
        self.mixer_label.setText(f"Mixer: channels={vm.mixer_channel_count}, muted={vm.muted_channel_count}")
        self.plugin_label.setText(
            f"Plugins: total={vm.plugin_count}, available={vm.available_plugin_count}"
        )
        self.selected_plugin_label.setText(f"Selected Plugin: {vm.selected_plugin_name or '-'}")
        self.inserted_plugin_label.setText(f"Inserted Plugins: {vm.inserted_plugin_count}")
        self.selected_insert_label.setText(f"Selected Insert: {vm.selected_insert_summary or '-'}")
        self.instance_label.setText(
            f"Managed Instances: active={vm.managed_instance_count} failed={vm.failed_instance_count}"
        )
        self.selected_instance_label.setText(
            f"Selected Managed Instance: {vm.selected_managed_instance_summary or '-'}"
        )
        self.reconcile_label.setText(
            "Reconcile: "
            f"attempted={vm.reconcile_attempted} "
            f"resolved={vm.reconcile_resolved} "
            f"failed={vm.reconcile_failed} "
            f"created={vm.reconcile_created} "
            f"cleared={vm.reconcile_cleared} "
            f"msg={vm.reconcile_last_message or '-'}"
        )
        self.reconcile_policy_label.setText(
            "Reconcile Policy: "
            f"mode={vm.reconcile_policy_mode} "
            f"action={vm.reconcile_policy_action} "
            f"pending_manual={'yes' if vm.reconcile_pending_manual else 'no'}"
        )
        self.recent_list.clear()
        for entry in vm.recent_sessions:
            current_marker = " [current]" if entry.session_ref == vm.session_ref else ""
            touched = self._fmt_epoch(entry.last_touched_epoch)
            label = (
                f"{entry.session_ref}{current_marker}\n"
                f"{entry.last_operation} | {touched}\n"
                f"{entry.storage_path or '-'}"
            )
            item = QListWidgetItem(label)
            item.setData(0x0100, entry.session_ref)
            self.recent_list.addItem(item)
        if self.recent_list.count() > 0 and self.recent_list.currentItem() is None:
            self.recent_list.setCurrentRow(0)
        self.last_action_label.setText(f"Last Action: {vm.last_action}")

    def selected_recent_session_ref(self) -> str:
        item = self.recent_list.currentItem()
        if item is None:
            return ""
        return str(item.data(0x0100) or "")

    @staticmethod
    def _fmt_epoch(value: int) -> str:
        if value <= 0:
            return "-"
        return datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S")
