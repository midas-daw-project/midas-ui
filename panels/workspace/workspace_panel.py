from __future__ import annotations

from typing import Callable

from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from viewmodels.workspace_viewmodel import WorkspaceViewModel


class WorkspacePanel(QWidget):
    def __init__(
        self,
        on_refresh_all: Callable[[], None],
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

        overview_box = QGroupBox("Project Context")
        overview_form = QFormLayout(overview_box)
        self.session_label = QLabel("Session: default-session")
        self.session_status_label = QLabel("Session Status: idle")
        self.session_identity_label = QLabel("Phase: none | Dirty: no")
        self.session_storage_label = QLabel("Storage: -")
        self.bridge_label = QLabel("Bridge: unknown v0")
        overview_form.addRow(self.session_label)
        overview_form.addRow(self.session_status_label)
        overview_form.addRow(self.session_identity_label)
        overview_form.addRow(self.session_storage_label)
        overview_form.addRow(self.bridge_label)
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
        self.reconcile_label = QLabel("Reconcile: attempted=0 resolved=0 failed=0 created=0 cleared=0")
        runtime_form.addRow(self.audio_label)
        runtime_form.addRow(self.transport_label)
        runtime_form.addRow(self.runtime_label)
        runtime_form.addRow(self.render_label)
        runtime_form.addRow(self.mixer_label)
        runtime_form.addRow(self.plugin_label)
        runtime_form.addRow(self.selected_plugin_label)
        runtime_form.addRow(self.inserted_plugin_label)
        runtime_form.addRow(self.selected_insert_label)
        runtime_form.addRow(self.reconcile_label)
        layout.addWidget(runtime_box)

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

        self.refresh_button.clicked.connect(on_refresh_all)
        self.save_button.clicked.connect(on_save_session)
        self.load_button.clicked.connect(on_load_session)
        self.apply_button.clicked.connect(on_apply_session)
        self.reconcile_button.clicked.connect(on_reconcile_inserts)

    def render(self, vm: WorkspaceViewModel) -> None:
        self.title_label.setText(vm.workspace_title)
        self.mode_label.setText(vm.workspace_mode)
        self.session_label.setText(f"Session: {vm.session_ref}")
        self.session_status_label.setText(f"Session Status: {vm.session_status}")
        self.session_identity_label.setText(
            f"Phase: {vm.session_phase} | Dirty: {'yes' if vm.session_dirty else 'no'} | Last: {vm.session_last_operation}"
        )
        self.session_storage_label.setText(
            f"Storage: {(vm.session_storage_path or '-')} | Source: {(vm.session_storage_source or '-')}"
        )
        self.bridge_label.setText(f"Bridge: {vm.bridge_mode} v{vm.bridge_version}")
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
        self.reconcile_label.setText(
            "Reconcile: "
            f"attempted={vm.reconcile_attempted} "
            f"resolved={vm.reconcile_resolved} "
            f"failed={vm.reconcile_failed} "
            f"created={vm.reconcile_created} "
            f"cleared={vm.reconcile_cleared} "
            f"msg={vm.reconcile_last_message or '-'}"
        )
        self.last_action_label.setText(f"Last Action: {vm.last_action}")
