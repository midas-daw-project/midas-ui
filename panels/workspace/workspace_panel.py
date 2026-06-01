from __future__ import annotations

from datetime import datetime
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidgetItem,
    QLineEdit,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from viewmodels.workspace_viewmodel import WorkspaceViewModel


SAMPLED_TRACKS = [
    {
        "name": "Kick Sampler",
        "short": "Kick",
        "source": "Sample track",
        "color": "#f9733d",
        "clips": {1, 2, 3, 4, 5, 6},
        "steps": {0, 4, 8, 12},
    },
    {
        "name": "Snare Sampler",
        "short": "Snare",
        "source": "Sample track",
        "color": "#d83a9c",
        "clips": {2, 4, 6, 8},
        "steps": {4, 12},
    },
    {
        "name": "Hi Hat Sampler",
        "short": "Hi Hats",
        "source": "Sample track",
        "color": "#804df2",
        "clips": {1, 2, 3, 4, 5, 6, 7, 8},
        "steps": {0, 2, 4, 6, 8, 10, 12, 14},
    },
    {
        "name": "Melody Sampler",
        "short": "Melody",
        "source": "Sample track",
        "color": "#78a6ff",
        "clips": {2, 3, 4, 5, 6, 7},
        "steps": {1, 2, 5, 6, 9, 10, 13},
    },
    {
        "name": "808 Bass Sampler",
        "short": "808 Bass",
        "source": "Sample track",
        "color": "#2bd2c9",
        "clips": {1, 3, 5, 7},
        "steps": {0, 3, 8, 11},
    },
]

MIDI_PITCHES = ["C5", "A4", "G4", "E4", "C4", "G3", "F#3", "C3"]


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
        on_midi_notes_changed: Callable[[str, int], None] | None = None,
    ) -> None:
        super().__init__()
        self._on_midi_notes_changed = on_midi_notes_changed or (lambda _track, _count: None)
        self._midi_notes: dict[str, list[tuple[int, str, int]]] = {
            "Kick Sampler": [(1, "C3", 1), (5, "C3", 1), (9, "C3", 1), (13, "C3", 1)],
            "Snare Sampler": [(5, "D3", 1), (13, "D3", 1)],
            "Hi Hat Sampler": [(1, "F#3", 1), (3, "F#3", 1), (5, "F#3", 1), (7, "F#3", 1)],
            "Melody Sampler": [(2, "C4", 2), (5, "E4", 2), (9, "G4", 2), (13, "A4", 2)],
            "808 Bass Sampler": [(1, "C3", 2), (4, "C3", 2), (9, "G3", 2), (12, "G3", 2)],
        }
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.title_label = QLabel("MIDAS Workspace")
        self.title_label.setObjectName("workspaceTitle")
        self.mode_label = QLabel("Arrangement / Editor / Runtime")
        self.mode_label.setObjectName("workspaceMode")
        title_row = QHBoxLayout()
        title_row.addWidget(self.title_label)
        title_row.addStretch(1)
        title_row.addWidget(self.mode_label)
        layout.addLayout(title_row)

        status_box = QGroupBox("Operator Status")
        status_box.setMaximumHeight(136)
        status_grid = QGridLayout(status_box)
        self.next_action_label = QLabel("Next: Create a new session or open an existing one.")
        self.next_action_label.setObjectName("operatorNext")
        self.next_action_label.setWordWrap(True)
        self.bridge_runtime_label = QLabel("Bridge: unknown v0 | Runtime: offline")
        self.bridge_runtime_label.setObjectName("operatorBridge")
        self.bridge_runtime_label.setWordWrap(True)
        self.session_flow_label = QLabel("Session: none | Phase: none | clean")
        self.session_flow_label.setObjectName("operatorSession")
        self.session_flow_label.setWordWrap(True)
        self.reconcile_flow_label = QLabel("Reconcile: clear | Plugins: 0 available / 0 inserted")
        self.reconcile_flow_label.setObjectName("operatorReconcile")
        self.reconcile_flow_label.setWordWrap(True)
        status_grid.addWidget(self.next_action_label, 0, 0, 1, 2)
        status_grid.addWidget(self.bridge_runtime_label, 1, 0)
        status_grid.addWidget(self.session_flow_label, 1, 1)
        status_grid.addWidget(self.reconcile_flow_label, 2, 0, 1, 2)
        layout.addWidget(status_box)

        canvas_box = QGroupBox("Arrangement / Sample Tracks")
        canvas_layout = QVBoxLayout(canvas_box)
        self.beat_canvas = QFrame()
        self.beat_canvas.setObjectName("beatCanvas")
        self.beat_canvas.setMinimumHeight(170)
        beat_grid = QGridLayout(self.beat_canvas)
        beat_grid.setContentsMargins(8, 8, 8, 8)
        beat_grid.setHorizontalSpacing(4)
        beat_grid.setVerticalSpacing(4)
        for column in range(1, 9):
            marker = QLabel(str(column))
            marker.setAlignment(Qt.AlignCenter)
            marker.setObjectName("arrangeMarker")
            marker.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
            beat_grid.addWidget(marker, 0, column)
            beat_grid.setColumnStretch(column, 1)
        for row, track in enumerate(SAMPLED_TRACKS, start=1):
            lane_label = QLabel(str(track["short"]))
            lane_label.setProperty("beatLane", True)
            lane_label.setFixedWidth(104)
            lane_label.setWordWrap(True)
            beat_grid.addWidget(lane_label, row, 0)
            for column in range(1, 9):
                active = column in track["clips"]
                cell = QLabel(track["short"] if active and column == min(track["clips"]) else "")
                cell.setProperty("beatCell", True)
                cell.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
                cell.setStyleSheet(
                    f"background-color: {track['color']};"
                    if active
                    else "background-color: rgba(37, 24, 57, 165);"
                )
                beat_grid.addWidget(cell, row, column)
        canvas_layout.addWidget(self.beat_canvas)
        layout.addWidget(canvas_box)

        editor_box = QGroupBox("Editor")
        editor_layout = QVBoxLayout(editor_box)
        editor_header = QHBoxLayout()
        self.previous_editor_button = QPushButton("<")
        self.previous_editor_button.setObjectName("editorArrow")
        self.previous_editor_button.setFixedWidth(32)
        self.next_editor_button = QPushButton(">")
        self.next_editor_button.setObjectName("editorArrow")
        self.next_editor_button.setFixedWidth(32)
        self.editor_mode_label = QLabel("Drum Machine")
        self.editor_mode_label.setObjectName("editorModeLabel")
        self.editor_hint_label = QLabel("Left / Right switches editor.")
        self.editor_hint_label.setObjectName("editorHintLabel")
        editor_header.addWidget(self.previous_editor_button)
        editor_header.addWidget(self.editor_mode_label)
        editor_header.addWidget(self.editor_hint_label, 1)
        editor_header.addWidget(self.next_editor_button)
        editor_layout.addLayout(editor_header)

        self.editor_stack = QStackedWidget()
        self.editor_stack.setObjectName("editorStack")

        drum_page = QWidget()
        drum_layout = QVBoxLayout(drum_page)
        drum_layout.setContentsMargins(0, 0, 0, 0)
        self.channel_rack = QFrame()
        self.channel_rack.setObjectName("channelRack")
        rack_grid = QGridLayout(self.channel_rack)
        rack_grid.setHorizontalSpacing(5)
        rack_grid.setVerticalSpacing(5)
        rack_grid.setContentsMargins(8, 8, 8, 8)
        for row, track in enumerate(SAMPLED_TRACKS):
            rack_label = QLabel(track["short"])
            rack_label.setProperty("rackLane", True)
            rack_label.setFixedWidth(96)
            rack_grid.addWidget(rack_label, row, 0)
            for step_index in range(16):
                step = QLabel("")
                step.setProperty("stepCell", True)
                step.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                step.setStyleSheet(
                    f"background-color: {track['color']};"
                    if step_index in track["steps"]
                    else "background-color: rgba(37, 24, 57, 175);"
                )
                rack_grid.addWidget(step, row, step_index + 1)
                rack_grid.setColumnStretch(step_index + 1, 1)
        self.assistant_prompt_label = QLabel("Assistant: Generate drum pattern | Add sampled MIDI notes | Suggest chord progression")
        self.assistant_prompt_label.setWordWrap(True)
        drum_layout.addWidget(self.channel_rack)
        drum_layout.addWidget(self.assistant_prompt_label)
        self.editor_stack.addWidget(drum_page)

        midi_page = QWidget()
        midi_layout = QVBoxLayout(midi_page)
        midi_layout.setContentsMargins(0, 0, 0, 0)
        midi_controls = QHBoxLayout()
        self.midi_track_selector = QComboBox()
        for track in SAMPLED_TRACKS:
            self.midi_track_selector.addItem(track["name"])
        self.midi_pitch_selector = QComboBox()
        self.midi_pitch_selector.addItems(["C3", "D3", "E3", "F#3", "G3", "A3", "C4", "E4", "G4", "A4", "C5"])
        self.midi_pitch_selector.setCurrentText("C4")
        self.midi_step_input = QSpinBox()
        self.midi_step_input.setRange(1, 16)
        self.midi_step_input.setValue(1)
        self.midi_length_input = QSpinBox()
        self.midi_length_input.setRange(1, 8)
        self.midi_length_input.setValue(2)
        self.add_midi_note_button = QPushButton("Add Note")
        self.clear_midi_notes_button = QPushButton("Clear Track")
        midi_controls.addWidget(QLabel("Track"))
        midi_controls.addWidget(self.midi_track_selector, 1)
        midi_controls.addWidget(QLabel("Pitch"))
        midi_controls.addWidget(self.midi_pitch_selector)
        midi_controls.addWidget(QLabel("Step"))
        midi_controls.addWidget(self.midi_step_input)
        midi_controls.addWidget(QLabel("Length"))
        midi_controls.addWidget(self.midi_length_input)
        midi_controls.addWidget(self.add_midi_note_button)
        midi_controls.addWidget(self.clear_midi_notes_button)
        midi_layout.addLayout(midi_controls)
        self.midi_note_grid = QFrame()
        self.midi_note_grid.setObjectName("midiNoteGrid")
        self._midi_grid_layout = QGridLayout(self.midi_note_grid)
        self._midi_grid_layout.setContentsMargins(8, 8, 8, 8)
        self._midi_grid_layout.setHorizontalSpacing(3)
        self._midi_grid_layout.setVerticalSpacing(3)
        midi_layout.addWidget(self.midi_note_grid)
        self.midi_note_summary_label = QLabel("")
        self.midi_note_summary_label.setWordWrap(True)
        midi_layout.addWidget(self.midi_note_summary_label)
        self.midi_track_selector.currentTextChanged.connect(lambda _value: self._render_midi_grid())
        self.add_midi_note_button.clicked.connect(self._add_selected_midi_note)
        self.clear_midi_notes_button.clicked.connect(self._clear_selected_midi_notes)
        self._render_midi_grid()
        self.editor_stack.addWidget(midi_page)
        editor_layout.addWidget(self.editor_stack)
        self.previous_editor_button.clicked.connect(self.show_previous_editor)
        self.next_editor_button.clicked.connect(self.show_next_editor)
        self._left_shortcut = QShortcut(QKeySequence(Qt.Key_Left), self)
        self._left_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self._left_shortcut.activated.connect(self.show_previous_editor)
        self._right_shortcut = QShortcut(QKeySequence(Qt.Key_Right), self)
        self._right_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self._right_shortcut.activated.connect(self.show_next_editor)
        layout.addWidget(editor_box)

        self.summary_tabs = QTabWidget()
        self.summary_tabs.setObjectName("workspaceSummaryTabs")
        layout.addWidget(self.summary_tabs, 1)

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
        self.summary_tabs.addTab(overview_box, "Project")

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
        self.selected_runtime_handle_label = QLabel("Selected Runtime Handle: -")
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
        runtime_form.addRow(self.selected_runtime_handle_label)
        runtime_form.addRow(self.reconcile_label)
        runtime_form.addRow(self.reconcile_policy_label)
        self.summary_tabs.addTab(runtime_box, "Runtime")

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
        self.recent_list.setMaximumHeight(130)
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

        actions_box = QGroupBox("Quick Actions")
        actions_layout = QGridLayout(actions_box)
        self.refresh_button = QPushButton("Refresh All")
        self.save_button = QPushButton("Save Session")
        self.load_button = QPushButton("Load Session")
        self.apply_button = QPushButton("Apply Session")
        self.reconcile_button = QPushButton("Reconcile Inserts")
        self.last_action_label = QLabel("Last Action: Ready")
        self.last_action_label.setWordWrap(True)
        actions_layout.addWidget(self.refresh_button, 0, 0)
        actions_layout.addWidget(self.save_button, 0, 1)
        actions_layout.addWidget(self.load_button, 0, 2)
        actions_layout.addWidget(self.apply_button, 1, 0)
        actions_layout.addWidget(self.reconcile_button, 1, 1)
        actions_layout.addWidget(self.last_action_label, 1, 2)

        start_tab = QWidget()
        start_layout = QVBoxLayout(start_tab)
        start_layout.setContentsMargins(0, 0, 0, 0)
        start_layout.addWidget(home_box)
        start_layout.addWidget(actions_box)
        self.summary_tabs.addTab(start_tab, "Start")

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
        dirty_text = "dirty" if vm.session_dirty else "clean"
        runtime_text = "active" if vm.runtime_active else "offline"
        pending_text = "pending manual" if vm.reconcile_pending_manual else "clear"
        self.next_action_label.setText(f"Next: {vm.startup_hint}")
        self.bridge_runtime_label.setText(
            f"Bridge: {vm.bridge_mode} v{vm.bridge_version} | "
            f"Runtime: {runtime_text} | Audio: {vm.audio_state} | Transport: {vm.transport_state}"
        )
        self.session_flow_label.setText(
            f"Session: {vm.session_ref or '-'} | Status: {vm.session_status} | "
            f"Phase: {vm.session_phase} | {dirty_text}"
        )
        self.reconcile_flow_label.setText(
            f"Reconcile: {pending_text} | "
            f"attempted={vm.reconcile_attempted} resolved={vm.reconcile_resolved} failed={vm.reconcile_failed} | "
            f"Plugins: {vm.available_plugin_count} available / {vm.inserted_plugin_count} inserted"
        )
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
        self.selected_runtime_handle_label.setText(
            f"Selected Runtime Handle: {vm.selected_runtime_handle_summary or '-'}"
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

    def current_editor_name(self) -> str:
        return "Piano Roll" if self.editor_stack.currentIndex() == 1 else "Drum Machine"

    def show_previous_editor(self) -> None:
        self._set_editor_index((self.editor_stack.currentIndex() - 1) % self.editor_stack.count())

    def show_next_editor(self) -> None:
        self._set_editor_index((self.editor_stack.currentIndex() + 1) % self.editor_stack.count())

    def _set_editor_index(self, index: int) -> None:
        self.editor_stack.setCurrentIndex(index)
        self.editor_mode_label.setText(self.current_editor_name())

    def selected_midi_track(self) -> str:
        return self.midi_track_selector.currentText()

    def midi_note_count(self, track_name: str = "") -> int:
        selected = track_name or self.selected_midi_track()
        return len(self._midi_notes.get(selected, []))

    def _add_selected_midi_note(self) -> None:
        track = self.selected_midi_track()
        note = (int(self.midi_step_input.value()), self.midi_pitch_selector.currentText(), int(self.midi_length_input.value()))
        notes = self._midi_notes.setdefault(track, [])
        if note not in notes:
            notes.append(note)
            notes.sort(key=lambda item: (item[0], item[1], item[2]))
        self._render_midi_grid()
        self._on_midi_notes_changed(track, len(notes))

    def _clear_selected_midi_notes(self) -> None:
        track = self.selected_midi_track()
        self._midi_notes[track] = []
        self._render_midi_grid()
        self._on_midi_notes_changed(track, 0)

    def _render_midi_grid(self) -> None:
        while self._midi_grid_layout.count():
            item = self._midi_grid_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        track = self.selected_midi_track() or SAMPLED_TRACKS[0]["name"]
        notes = self._midi_notes.get(track, [])
        note_cells = {(step + offset, pitch) for step, pitch, length in notes for offset in range(length) if step + offset <= 16}
        for column in range(1, 17):
            marker = QLabel(str(column))
            marker.setObjectName("midiStepMarker")
            marker.setAlignment(Qt.AlignCenter)
            self._midi_grid_layout.addWidget(marker, 0, column)
            self._midi_grid_layout.setColumnStretch(column, 1)
        for row, pitch in enumerate(MIDI_PITCHES, start=1):
            pitch_label = QLabel(pitch)
            pitch_label.setObjectName("midiPitchLabel")
            pitch_label.setFixedWidth(42)
            self._midi_grid_layout.addWidget(pitch_label, row, 0)
            for column in range(1, 17):
                cell = QLabel("")
                cell.setProperty("midiCell", True)
                cell.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                active = (column, pitch) in note_cells
                color = self._track_color(track)
                cell.setStyleSheet(
                    f"background-color: {color};"
                    if active
                    else "background-color: rgba(31, 22, 47, 175);"
                )
                self._midi_grid_layout.addWidget(cell, row, column)
        if hasattr(self, "midi_note_summary_label"):
            summary = ", ".join(f"{pitch}@{step}x{length}" for step, pitch, length in notes) or "No MIDI notes on this track yet."
            self.midi_note_summary_label.setText(f"{track}: {summary}")

    @staticmethod
    def _track_color(track_name: str) -> str:
        for track in SAMPLED_TRACKS:
            if track["name"] == track_name:
                return str(track["color"])
        return "#78a6ff"

    @staticmethod
    def _fmt_epoch(value: int) -> str:
        if value <= 0:
            return "-"
        return datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S")
