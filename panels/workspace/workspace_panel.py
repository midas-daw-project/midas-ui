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
    QMenu,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from viewmodels.workspace_viewmodel import WorkspaceViewModel


TRACK_KIND_CONFIG = {
    "Master": ("Master", "#f8d84a"),
    "Audio": ("Audio Track", "#4f8fdc"),
    "Instrument": ("Instrument Track", "#8f63df"),
    "MIDI": ("MIDI Track", "#78a6ff"),
    "Drum/Rhythm": ("Rhythm Track", "#f9733d"),
    "Sampler": ("Sample Track", "#2bd2c9"),
    "Vocal/Dialogue": ("Vocal / Dialogue Track", "#d83a9c"),
    "FX/Texture": ("FX / Texture Track", "#62c7ff"),
    "Bus": ("Bus Track", "#4fbf7a"),
    "Send FX": ("Send FX Track", "#ffb84f"),
    "Folder/Group": ("Folder / Group Track", "#9aa0aa"),
    "Video": ("Video Track", "#ec6a5e"),
    "Reference": ("Reference Track", "#b8c0cc"),
}

DEFAULT_ARRANGEMENT_TRACKS = [
    ("Master", "Master"),
    ("Audio", "Audio Track"),
    ("Instrument", "Instrument Track"),
    ("Drum/Rhythm", "Rhythm Track"),
    ("Sampler", "Sample Track"),
    ("Vocal/Dialogue", "Vocal / Dialogue Track"),
    ("FX/Texture", "FX / Texture Track"),
    ("Bus", "Bus A"),
    ("Bus", "Bus B"),
    ("Send FX", "Reverb Send"),
    ("Send FX", "Delay Send"),
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
        self._midi_notes: dict[str, list[tuple[int, str, int]]] = {}
        self._arrangement_tracks: list[dict[str, object]] = []
        self._arrangement_clips: dict[str, set[int]] = {}
        self._arrangement_colors: dict[str, str] = {}
        self._next_arrangement_track_id = 1
        self._drum_tracks: list[dict[str, str]] = []
        self._drum_steps: dict[str, set[int]] = {}
        self._next_drum_track_id = 1
        self._arrangement_buttons: dict[tuple[str, int], QPushButton] = {}
        self._drum_step_buttons: dict[tuple[str, int], QPushButton] = {}
        self.arrangement_track_name_inputs: list[QLineEdit] = []
        self.drum_track_name_inputs: list[QLineEdit] = []
        self._seed_default_arrangement()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        self.title_label = QLabel("MIDAS Arrange")
        self.title_label.setObjectName("workspaceTitle")
        self.mode_label = QLabel("Tracks | Items | Routing")
        self.mode_label.setObjectName("workspaceMode")
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        title_row.addWidget(self.title_label)
        title_row.addStretch(1)
        title_row.addWidget(self.mode_label)
        layout.addLayout(title_row)

        self.daw_control_strip = QFrame()
        self.daw_control_strip.setObjectName("dawControlStrip")
        project_control_row = QHBoxLayout()
        project_control_row.setContentsMargins(8, 5, 8, 5)
        project_control_row.setSpacing(8)
        self.daw_control_strip.setLayout(project_control_row)
        self.project_mix_label = QLabel("Mix 100%")
        self.project_mix_label.setObjectName("dawStripLabel")
        self.project_mix_input = QSlider(Qt.Horizontal)
        self.project_mix_input.setRange(0, 100)
        self.project_mix_input.setValue(100)
        self.project_mix_input.setMaximumWidth(150)
        self.playrate_label = QLabel("Rate 1.00")
        self.playrate_label.setObjectName("dawStripLabel")
        self.playrate_input = QSlider(Qt.Horizontal)
        self.playrate_input.setRange(0, 200)
        self.playrate_input.setValue(100)
        self.playrate_input.setMaximumWidth(170)
        self.project_mix_input.valueChanged.connect(
            lambda value: self.project_mix_label.setText(f"Mix {value}%")
        )
        self.playrate_input.valueChanged.connect(
            lambda value: self.playrate_label.setText(f"Rate {value / 100:.2f}")
        )
        project_control_row.addWidget(self.project_mix_label)
        project_control_row.addWidget(self.project_mix_input)
        project_control_row.addWidget(self.playrate_label)
        project_control_row.addWidget(self.playrate_input)
        project_control_row.addWidget(QLabel("Snap: grid"))
        project_control_row.addWidget(QLabel("Mode: trim/read"))
        project_control_row.addStretch(1)
        layout.addWidget(self.daw_control_strip)

        self.view_mode_strip = QFrame()
        self.view_mode_strip.setObjectName("viewModeStrip")
        mode_row = QHBoxLayout()
        mode_row.setContentsMargins(6, 4, 6, 4)
        mode_row.setSpacing(4)
        self.view_mode_strip.setLayout(mode_row)
        mode_row.addWidget(QLabel("View"))
        self.mode_buttons: list[QPushButton] = []
        for mode_name in ("Arrange", "Record", "MIDI", "Sound Design", "Mix", "Export"):
            mode_button = QPushButton(mode_name)
            mode_button.setObjectName("modeButton")
            mode_button.setCheckable(True)
            mode_button.setChecked(mode_name == "Arrange")
            mode_button.clicked.connect(
                lambda _checked=False, selected_mode=mode_name: self._select_mode(selected_mode)
            )
            self.mode_buttons.append(mode_button)
            mode_row.addWidget(mode_button)
        mode_row.addStretch(1)
        layout.addWidget(self.view_mode_strip)

        self.status_box = QFrame()
        self.status_box.setObjectName("projectStatusStrip")
        self.status_box.setMaximumHeight(108)
        status_grid = QGridLayout(self.status_box)
        status_grid.setContentsMargins(8, 6, 8, 6)
        status_grid.setHorizontalSpacing(8)
        status_grid.setVerticalSpacing(4)
        self.next_action_label = QLabel("Arrange: build clips, then refine in Mixer or Piano Roll.")
        self.next_action_label.setObjectName("operatorNext")
        self.next_action_label.setWordWrap(True)
        self.bridge_runtime_label = QLabel("Bridge: unknown v0 | Runtime: offline")
        self.bridge_runtime_label.setObjectName("operatorBridge")
        self.bridge_runtime_label.setWordWrap(False)
        self.session_flow_label = QLabel("Session: none | Phase: none | clean")
        self.session_flow_label.setObjectName("operatorSession")
        self.session_flow_label.setWordWrap(False)
        self.reconcile_flow_label = QLabel("Reconcile: clear | Plugins: 0 available / 0 inserted")
        self.reconcile_flow_label.setObjectName("operatorReconcile")
        self.reconcile_flow_label.setWordWrap(False)
        status_grid.addWidget(self.next_action_label, 0, 0, 1, 2)
        status_grid.addWidget(self.bridge_runtime_label, 1, 0)
        status_grid.addWidget(self.session_flow_label, 1, 1)
        status_grid.addWidget(self.reconcile_flow_label, 2, 0, 1, 2)
        status_grid.setColumnStretch(0, 1)
        status_grid.setColumnStretch(1, 1)
        layout.addWidget(self.status_box)

        canvas_box = QGroupBox("Arrange View")
        canvas_box.setObjectName("arrangeView")
        canvas_layout = QVBoxLayout(canvas_box)
        canvas_layout.setContentsMargins(8, 8, 8, 8)
        canvas_layout.setSpacing(6)
        arrangement_actions = QHBoxLayout()
        arrangement_actions.setSpacing(8)
        self.track_panel_header_label = QLabel("Track Control Panel")
        self.track_panel_header_label.setObjectName("trackPanelHeaderLabel")
        self.timeline_header_label = QLabel("Timeline")
        self.timeline_header_label.setObjectName("timelineHeaderLabel")
        self.add_arrangement_track_button = QPushButton("Add Track")
        self.add_arrangement_track_button.setObjectName("addArrangementTrackButton")
        self.add_track_menu = QMenu(self)
        for kind in TRACK_KIND_CONFIG:
            if kind == "Master":
                continue
            action = self.add_track_menu.addAction(TRACK_KIND_CONFIG[kind][0])
            action.triggered.connect(lambda _checked=False, selected_kind=kind: self._add_arrangement_track(selected_kind))
        self.add_arrangement_track_button.setMenu(self.add_track_menu)
        self.add_arrangement_track_button.clicked.connect(lambda: self._add_arrangement_track("Audio"))
        self.empty_arrangement_label = QLabel("Tracks, buses, and sends ready.")
        self.empty_arrangement_label.setObjectName("emptyArrangementLabel")
        self.empty_arrangement_label.setWordWrap(True)
        arrangement_actions.addWidget(self.track_panel_header_label)
        arrangement_actions.addWidget(self.add_arrangement_track_button)
        arrangement_actions.addWidget(self.timeline_header_label)
        arrangement_actions.addWidget(self.empty_arrangement_label, 1)
        canvas_layout.addLayout(arrangement_actions)

        self.arrange_ruler = QFrame()
        self.arrange_ruler.setObjectName("arrangeRuler")
        ruler_layout = QGridLayout(self.arrange_ruler)
        ruler_layout.setContentsMargins(8, 5, 8, 5)
        ruler_layout.setHorizontalSpacing(4)
        ruler_track_label = QLabel("Tracks")
        ruler_track_label.setObjectName("rulerTrackLabel")
        ruler_layout.addWidget(ruler_track_label, 0, 0)
        for column in range(1, 17):
            marker = QLabel(f"{column}.1")
            marker.setObjectName("rulerMarkerLabel")
            marker.setAlignment(Qt.AlignCenter)
            ruler_layout.addWidget(marker, 0, column)
            ruler_layout.setColumnStretch(column, 1)
        canvas_layout.addWidget(self.arrange_ruler)

        self.global_tracks_label = QLabel(
            "Global: Tempo | Signature | Key | Markers | Chords"
        )
        self.global_tracks_label.setObjectName("globalTracksLabel")
        self.global_tracks_label.setWordWrap(True)
        canvas_layout.addWidget(self.global_tracks_label)
        self.beat_canvas = QFrame()
        self.beat_canvas.setObjectName("beatCanvas")
        self.beat_canvas.setMinimumHeight(440)
        self.beat_canvas.setMinimumWidth(1200)
        self._beat_grid = QGridLayout(self.beat_canvas)
        self._beat_grid.setContentsMargins(8, 8, 8, 8)
        self._beat_grid.setHorizontalSpacing(4)
        self._beat_grid.setVerticalSpacing(2)
        self._render_arrangement_grid()
        self.arrangement_scroll_area = QScrollArea()
        self.arrangement_scroll_area.setObjectName("arrangementScrollArea")
        self.arrangement_scroll_area.setWidgetResizable(False)
        self.arrangement_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.arrangement_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.arrangement_scroll_area.setWidget(self.beat_canvas)
        canvas_layout.addWidget(self.arrangement_scroll_area)
        editor_box = QGroupBox("Arrange / Editors")
        editor_box.setObjectName("workspaceEditorBox")
        editor_layout = QVBoxLayout(editor_box)
        editor_layout.setContentsMargins(8, 8, 8, 8)
        editor_layout.setSpacing(6)
        editor_header = QHBoxLayout()
        self.previous_editor_button = QPushButton("<")
        self.previous_editor_button.setObjectName("editorArrow")
        self.previous_editor_button.setFixedWidth(32)
        self.next_editor_button = QPushButton(">")
        self.next_editor_button.setObjectName("editorArrow")
        self.next_editor_button.setFixedWidth(32)
        self.editor_mode_label = QLabel("Arrangement")
        self.editor_mode_label.setObjectName("editorModeLabel")
        self.editor_hint_label = QLabel("Arrangement | Drum Machine | Piano Roll")
        self.editor_hint_label.setObjectName("editorHintLabel")
        editor_header.addWidget(self.previous_editor_button)
        editor_header.addWidget(self.editor_mode_label)
        editor_header.addWidget(self.editor_hint_label, 1)
        editor_header.addWidget(self.next_editor_button)
        editor_layout.addLayout(editor_header)

        self.editor_stack = QStackedWidget()
        self.editor_stack.setObjectName("editorStack")
        self.editor_stack.addWidget(canvas_box)

        drum_page = QWidget()
        drum_layout = QVBoxLayout(drum_page)
        drum_layout.setContentsMargins(0, 0, 0, 0)
        drum_actions = QHBoxLayout()
        self.add_drum_track_button = QPushButton("Add Drum Lane")
        self.add_drum_track_button.setObjectName("addDrumTrackButton")
        self.empty_drum_label = QLabel("No drum lanes yet. Add a lane to build a pattern.")
        self.empty_drum_label.setObjectName("emptyDrumLabel")
        self.empty_drum_label.setWordWrap(True)
        drum_actions.addWidget(self.add_drum_track_button)
        drum_actions.addWidget(self.empty_drum_label, 1)
        drum_layout.addLayout(drum_actions)
        self.channel_rack = QFrame()
        self.channel_rack.setObjectName("channelRack")
        self._rack_grid = QGridLayout(self.channel_rack)
        self._rack_grid.setHorizontalSpacing(5)
        self._rack_grid.setVerticalSpacing(5)
        self._rack_grid.setContentsMargins(8, 8, 8, 8)
        self._render_drum_grid()
        self.assistant_prompt_label = QLabel("Assistant: drum pattern | sampled MIDI | chord idea")
        self.assistant_prompt_label.setWordWrap(True)
        drum_layout.addWidget(self.channel_rack)
        drum_layout.addWidget(self.assistant_prompt_label)
        self.editor_stack.addWidget(drum_page)
        self.add_drum_track_button.clicked.connect(self._add_drum_track)

        midi_page = QWidget()
        midi_layout = QVBoxLayout(midi_page)
        midi_layout.setContentsMargins(0, 0, 0, 0)
        midi_controls = QHBoxLayout()
        self.midi_track_selector = QComboBox()
        self._sync_midi_track_selector()
        self.midi_pitch_selector = QComboBox()
        self.midi_pitch_selector.addItems(["C3", "D3", "E3", "F#3", "G3", "A3", "C4", "E4", "G4", "A4", "C5"])
        self.midi_pitch_selector.setCurrentText("C4")
        self.midi_step_input = QSlider(Qt.Horizontal)
        self.midi_step_input.setRange(1, 16)
        self.midi_step_input.setValue(1)
        self.midi_step_value_label = QLabel("1")
        self.midi_length_input = QSlider(Qt.Horizontal)
        self.midi_length_input.setRange(1, 8)
        self.midi_length_input.setValue(2)
        self.midi_length_value_label = QLabel("2")
        self.add_midi_note_button = QPushButton("Add Note")
        self.clear_midi_notes_button = QPushButton("Clear Track")
        self.midi_step_input.valueChanged.connect(lambda value: self.midi_step_value_label.setText(str(value)))
        self.midi_length_input.valueChanged.connect(lambda value: self.midi_length_value_label.setText(str(value)))
        midi_controls.addWidget(QLabel("Track"))
        midi_controls.addWidget(self.midi_track_selector, 1)
        midi_controls.addWidget(QLabel("Pitch"))
        midi_controls.addWidget(self.midi_pitch_selector)
        midi_controls.addWidget(QLabel("Step"))
        midi_controls.addWidget(self.midi_step_input, 1)
        midi_controls.addWidget(self.midi_step_value_label)
        midi_controls.addWidget(QLabel("Length"))
        midi_controls.addWidget(self.midi_length_input, 1)
        midi_controls.addWidget(self.midi_length_value_label)
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
        layout.addWidget(editor_box, 1)

        self.summary_tabs = QTabWidget()
        self.summary_tabs.setObjectName("workspaceSummaryTabs")
        self.summary_tabs.setMaximumHeight(188)
        layout.addWidget(self.summary_tabs)

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

        runtime_box = QGroupBox("Runtime")
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
            f"a={vm.reconcile_attempted} r={vm.reconcile_resolved} f={vm.reconcile_failed} | "
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
        names = ["Arrangement", "Drum Machine", "Piano Roll"]
        return names[self.editor_stack.currentIndex()] if self.editor_stack.currentIndex() < len(names) else "Arrangement"

    def show_previous_editor(self) -> None:
        self._set_editor_index((self.editor_stack.currentIndex() - 1) % self.editor_stack.count())

    def show_next_editor(self) -> None:
        self._set_editor_index((self.editor_stack.currentIndex() + 1) % self.editor_stack.count())

    def show_arrangement(self) -> None:
        self._set_editor_index(0)

    def show_drum_machine(self) -> None:
        self._set_editor_index(1)

    def show_piano_roll(self) -> None:
        self._set_editor_index(2)

    def _set_editor_index(self, index: int) -> None:
        self.editor_stack.setCurrentIndex(index)
        self.editor_mode_label.setText(self.current_editor_name())

    def selected_midi_track(self) -> str:
        return self.midi_track_selector.currentText()

    def midi_note_count(self, track_name: str = "") -> int:
        selected = track_name or self.selected_midi_track()
        return len(self._midi_notes.get(selected, []))

    def midi_pitches_for_track(self, track_name: str = "") -> list[str]:
        selected = track_name or self.selected_midi_track()
        return [pitch for _step, pitch, _length in self._midi_notes.get(selected, [])]

    def arrangement_clip_active(self, track_name: str, beat: int) -> bool:
        return beat in self._arrangement_clips.get(track_name, set())

    def drum_step_active(self, track_name: str, step_index: int) -> bool:
        return step_index in self._drum_steps.get(track_name, set())

    def selected_mix_percent(self) -> int:
        return int(self.project_mix_input.value())

    def selected_playrate(self) -> float:
        return float(self.playrate_input.value()) / 100.0

    def arrangement_track_names(self) -> list[str]:
        return [field.text() for field in self.arrangement_track_name_inputs]

    def arrangement_track_count(self) -> int:
        return len(self._arrangement_tracks)

    def drum_track_count(self) -> int:
        return len(self._drum_tracks)

    def _seed_default_arrangement(self) -> None:
        for kind, name in DEFAULT_ARRANGEMENT_TRACKS:
            self._create_arrangement_track(kind, name)

    def _create_arrangement_track(self, kind: str, name: str | None = None) -> str:
        track_name, color = TRACK_KIND_CONFIG.get(kind, TRACK_KIND_CONFIG["Audio"])
        if kind == "Master" and not any(str(track["kind"]) == "Master" for track in self._arrangement_tracks):
            track_id = "master-track"
        else:
            track_id = f"arrangement-track-{self._next_arrangement_track_id}"
            self._next_arrangement_track_id += 1
        self._arrangement_tracks.append(
            {
                "id": track_id,
                "name": name or track_name,
                "kind": kind,
                "color": color,
                "clips": [],
            }
        )
        self._arrangement_clips[track_id] = set()
        self._arrangement_colors[track_id] = color
        return track_id

    def _add_arrangement_track(self, kind: str = "Audio") -> None:
        self._create_arrangement_track(kind)
        self._sync_midi_track_selector()
        self._render_arrangement_grid()

    def _select_mode(self, mode_name: str) -> None:
        for button in self.mode_buttons:
            button.setChecked(button.text() == mode_name)
        self.mode_label.setText(f"{mode_name} Mode")
        if mode_name == "Arrange":
            self.show_arrangement()
        elif mode_name == "Record":
            self.show_drum_machine()
        elif mode_name == "MIDI":
            self.show_piano_roll()
        elif mode_name == "Sound Design":
            self.show_drum_machine()
        elif mode_name == "Mix":
            self.show_arrangement()
        elif mode_name == "Export":
            self.show_arrangement()

    def _sync_midi_track_selector(self) -> None:
        if not hasattr(self, "midi_track_selector"):
            return
        current = self.midi_track_selector.currentText()
        names = [
            str(track["name"])
            for track in self._arrangement_tracks
            if str(track["kind"]) not in {"Master", "Bus", "Send FX"}
        ]
        if not names:
            names = ["New Track"]
        self.midi_track_selector.blockSignals(True)
        self.midi_track_selector.clear()
        self.midi_track_selector.addItems(names)
        if current in names:
            self.midi_track_selector.setCurrentText(current)
        self.midi_track_selector.blockSignals(False)
        if hasattr(self, "_midi_grid_layout"):
            self._render_midi_grid()

    def _commit_arrangement_track_name(self, track_id: str, name: str) -> None:
        cleaned = name.strip() or "New Track"
        for track in self._arrangement_tracks:
            if str(track["id"]) == track_id:
                track["name"] = cleaned
                break
        self._sync_midi_track_selector()

    def _commit_drum_track_name(self, track_id: str, name: str) -> None:
        cleaned = name.strip() or "New Track"
        for track in self._drum_tracks:
            if str(track["id"]) == track_id:
                track["name"] = cleaned
                break
        self._sync_midi_track_selector()

    def _add_legacy_arrangement_track(self) -> None:
        track_id = f"arrangement-track-{self._next_arrangement_track_id}"
        self._next_arrangement_track_id += 1
        track = {
            "id": track_id,
            "name": "New Track",
            "kind": "Audio",
            "color": "#4f8fdc",
            "clips": [],
        }
        self._arrangement_tracks.append(track)
        self._arrangement_clips[track_id] = set()
        self._arrangement_colors[track_id] = str(track["color"])
        self._render_arrangement_grid()

    def _add_drum_track(self) -> None:
        track_id = f"drum-track-{self._next_drum_track_id}"
        self._next_drum_track_id += 1
        self._drum_tracks.append({"id": track_id, "name": "New Track", "color": "#804df2"})
        self._drum_steps[track_id] = set()
        self._sync_midi_track_selector()
        self._render_drum_grid()

    def _remove_arrangement_track(self, track_id: str) -> None:
        self._arrangement_tracks = [track for track in self._arrangement_tracks if str(track["id"]) != track_id]
        self._arrangement_clips.pop(track_id, None)
        self._arrangement_colors.pop(track_id, None)
        self._sync_midi_track_selector()
        self._render_arrangement_grid()

    def _remove_drum_track(self, track_id: str) -> None:
        self._drum_tracks = [track for track in self._drum_tracks if str(track["id"]) != track_id]
        self._drum_steps.pop(track_id, None)
        self._sync_midi_track_selector()
        self._render_drum_grid()

    def _render_drum_grid(self) -> None:
        while self._rack_grid.count():
            item = self._rack_grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._drum_step_buttons.clear()
        self.drum_track_name_inputs.clear()
        for column in range(1, 17):
            marker = QLabel(str(column))
            marker.setObjectName("midiStepMarker")
            marker.setAlignment(Qt.AlignCenter)
            self._rack_grid.addWidget(marker, 0, column)
            self._rack_grid.setColumnStretch(column, 1)
        if not self._drum_tracks:
            self.empty_drum_label.show()
            empty = QLabel("Add Drum Lane")
            empty.setObjectName("emptyArrangementCanvasLabel")
            empty.setAlignment(Qt.AlignCenter)
            self._rack_grid.addWidget(empty, 1, 0, 1, 17)
            return
        self.empty_drum_label.hide()
        for row, track in enumerate(self._drum_tracks, start=1):
            track_id = str(track["id"])
            rack_header = self._build_drum_track_header(track_id, str(track["name"]))
            self._rack_grid.addWidget(rack_header, row, 0)
            for step_index in range(16):
                active = step_index in self._drum_steps.get(track_id, set())
                step = QPushButton("")
                step.setProperty("stepCell", True)
                step.setCheckable(True)
                step.setChecked(active)
                step.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                step.setToolTip(f"Step {step_index + 1}")
                step.clicked.connect(
                    lambda checked, name=track_id, step_number=step_index: self._set_drum_step(
                        name, step_number, checked
                    )
                )
                self._drum_step_buttons[(track_id, step_index)] = step
                self._style_toggle_cell(step, str(track["color"]), active)
                self._rack_grid.addWidget(step, row, step_index + 1)
                self._rack_grid.setColumnStretch(step_index + 1, 1)

    def _render_arrangement_grid(self) -> None:
        while self._beat_grid.count():
            item = self._beat_grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._arrangement_buttons.clear()
        self.arrangement_track_name_inputs.clear()
        header = QLabel("Track")
        header.setObjectName("arrangeMarker")
        self._beat_grid.addWidget(header, 0, 0, 2, 1)
        for column in range(1, 17):
            bar = ((column - 1) * 4) + 1
            marker = QLabel(f"{bar}.1")
            marker.setAlignment(Qt.AlignCenter)
            marker.setObjectName("arrangeMarker")
            marker.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
            time_marker = QLabel(f"0:{(column - 1) * 12:02d}.000")
            time_marker.setAlignment(Qt.AlignCenter)
            time_marker.setObjectName("arrangeTimeMarker")
            time_marker.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
            self._beat_grid.addWidget(marker, 0, column)
            self._beat_grid.addWidget(time_marker, 1, column)
            self._beat_grid.setColumnStretch(column, 1)
        if not self._arrangement_tracks:
            self.empty_arrangement_label.show()
            empty = QLabel("Add Track")
            empty.setObjectName("emptyArrangementCanvasLabel")
            empty.setAlignment(Qt.AlignCenter)
            self._beat_grid.addWidget(empty, 2, 0, 1, 17)
            return
        self.empty_arrangement_label.hide()
        for row, track in enumerate(self._arrangement_tracks, start=2):
            track_id = str(track["id"])
            track_header = self._build_arrangement_track_header(
                row - 2,
                track_id,
                str(track["name"]),
                str(track["kind"]),
            )
            self._beat_grid.addWidget(track_header, row, 0)
            occupied: set[int] = set()
            for clip in track["clips"]:
                start = int(clip["start"])
                length = max(1, min(int(clip["length"]), 17 - start))
                occupied.update(range(start, start + length))
                active = start in self._arrangement_clips[track_id]
                cell = QPushButton(f"{clip['label']}  ~~~~~")
                cell.setProperty("beatCell", True)
                cell.setCheckable(True)
                cell.setChecked(active)
                cell.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
                cell.setToolTip(f"{track['kind']} region at bar {start}")
                cell.clicked.connect(
                    lambda checked, name=track_id, beat=start: self._set_arrangement_clip(name, beat, checked)
                )
                self._arrangement_buttons[(track_id, start)] = cell
                self._style_arrangement_region(cell, str(track["color"]), active)
                self._beat_grid.addWidget(cell, row, start, 1, length)
            for column in range(1, 17):
                if column in occupied:
                    continue
                empty = QLabel("")
                empty.setProperty("beatCell", True)
                empty.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
                empty.setStyleSheet(
                    "background-color: rgba(31, 34, 40, 160);"
                    "border: 1px solid rgba(75, 82, 96, 95);"
                    "border-radius: 2px;"
                    "min-height: 26px;"
                )
                self._beat_grid.addWidget(empty, row, column)

    def _set_arrangement_clip(self, track_name: str, beat: int, active: bool) -> None:
        clips = self._arrangement_clips.setdefault(track_name, set())
        if active:
            clips.add(beat)
        else:
            clips.discard(beat)
        button = self._arrangement_buttons.get((track_name, beat))
        if button is not None:
            button.setChecked(active)
            self._style_arrangement_region(button, self._arrangement_colors.get(track_name, "#4f8fdc"), active)

    def _set_drum_step(self, track_name: str, step_index: int, active: bool) -> None:
        steps = self._drum_steps.setdefault(track_name, set())
        if active:
            steps.add(step_index)
        else:
            steps.discard(step_index)
        button = self._drum_step_buttons.get((track_name, step_index))
        if button is not None:
            button.setChecked(active)
            self._style_toggle_cell(button, self._drum_track_color(track_name), active)

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
        track = self.selected_midi_track() or "New Track"
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
                color = "#804df2"
                cell.setStyleSheet(
                    f"background-color: {color};"
                    if active
                    else "background-color: rgba(31, 22, 47, 175);"
                )
                self._midi_grid_layout.addWidget(cell, row, column)
        if hasattr(self, "midi_note_summary_label"):
            summary = ", ".join(f"{pitch}@{step}x{length}" for step, pitch, length in notes) or "No MIDI notes on this track yet."
            self.midi_note_summary_label.setText(f"{track}: {summary}")

    def _drum_track_color(self, track_name: str) -> str:
        for track in self._drum_tracks:
            if track["id"] == track_name:
                return str(track["color"])
        return "#804df2"

    @staticmethod
    def _style_toggle_cell(button: QPushButton, color: str, active: bool) -> None:
        if active:
            button.setStyleSheet(
                f"background-color: {color};"
                "border: 1px solid rgba(255, 255, 255, 90);"
                "border-radius: 4px;"
                "min-height: 16px;"
                "padding: 0;"
            )
            return
        button.setStyleSheet(
            "background-color: rgba(35, 38, 45, 190);"
            "border: 1px solid rgba(80, 88, 102, 115);"
            "border-radius: 3px;"
            "min-height: 16px;"
            "padding: 0;"
        )

    def _build_arrangement_track_header(self, index: int, track_id: str, name: str, kind: str) -> QWidget:
        is_master = kind == "Master"
        header = QFrame()
        header.setObjectName("arrangementTrackHeader")
        header.setProperty("arrangementTrackHeader", True)
        header.setProperty("masterTrack", is_master)
        header.setFixedWidth(184)
        layout = QGridLayout(header)
        layout.setContentsMargins(5, 4, 5, 4)
        layout.setHorizontalSpacing(4)
        layout.setVerticalSpacing(3)
        number_label = QLabel("00" if is_master else f"{index:02d}")
        number_label.setObjectName("trackNumberLabel")
        name_input = QLineEdit(name)
        name_input.setObjectName("arrangementTrackName")
        name_input.setPlaceholderText("New Track")
        name_input.editingFinished.connect(
            lambda selected_track=track_id, field=name_input: self._commit_arrangement_track_name(
                selected_track,
                field.text(),
            )
        )
        kind_label = QLabel(kind)
        kind_label.setObjectName("arrangementTrackKind")
        volume_slider = QSlider(Qt.Horizontal)
        volume_slider.setRange(0, 200)
        volume_slider.setValue(100)
        volume_slider.setObjectName("arrangementTrackVolume")
        meter_label = QLabel("LUFS -14 | TP -1.0" if is_master else "meter")
        meter_label.setObjectName("trackMeterLabel")
        mute_button = QPushButton("M")
        solo_button = QPushButton("S")
        record_button = QPushButton("R")
        input_button = QPushButton("I")
        fx_button = QPushButton("FX")
        route_button = QPushButton("Route")
        remove_button = QPushButton("-")
        for button in (mute_button, solo_button, record_button, input_button):
            button.setObjectName("trackControlButton")
            button.setCheckable(True)
            button.setFixedWidth(24)
        for button in (fx_button, route_button):
            button.setObjectName("trackControlButton")
            button.setFixedWidth(42)
        record_button.setToolTip("Record arm")
        input_button.setToolTip("Input / FX monitor on or off")
        remove_button.setObjectName("trackRemoveButton")
        remove_button.setToolTip("Remove track")
        remove_button.setFixedWidth(24)
        remove_button.setEnabled(not is_master)
        if not is_master:
            remove_button.clicked.connect(lambda _checked=False, selected_track=track_id: self._remove_arrangement_track(selected_track))
        layout.addWidget(number_label, 0, 0)
        layout.addWidget(name_input, 0, 1, 1, 3)
        layout.addWidget(remove_button, 0, 4)
        layout.addWidget(kind_label, 1, 1, 1, 4)
        layout.addWidget(meter_label, 2, 1, 1, 4)
        layout.addWidget(volume_slider, 3, 1, 1, 4)
        layout.addWidget(mute_button, 4, 1)
        layout.addWidget(solo_button, 4, 2)
        layout.addWidget(record_button, 4, 3)
        layout.addWidget(input_button, 4, 4)
        layout.addWidget(fx_button, 5, 1, 1, 2)
        layout.addWidget(route_button, 5, 3, 1, 2)
        self.arrangement_track_name_inputs.append(name_input)
        return header

    def _build_drum_track_header(self, track_id: str, name: str) -> QWidget:
        header = QFrame()
        header.setObjectName("arrangementTrackHeader")
        header.setProperty("arrangementTrackHeader", True)
        header.setFixedWidth(132)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(5, 4, 5, 4)
        layout.setSpacing(4)
        name_input = QLineEdit(name)
        name_input.setObjectName("arrangementTrackName")
        name_input.setPlaceholderText("New Track")
        name_input.editingFinished.connect(
            lambda selected_track=track_id, field=name_input: self._commit_drum_track_name(
                selected_track,
                field.text(),
            )
        )
        remove_button = QPushButton("-")
        remove_button.setObjectName("trackRemoveButton")
        remove_button.setToolTip("Remove drum lane")
        remove_button.setFixedWidth(24)
        remove_button.clicked.connect(lambda _checked=False, selected_track=track_id: self._remove_drum_track(selected_track))
        layout.addWidget(name_input, 1)
        layout.addWidget(remove_button)
        self.drum_track_name_inputs.append(name_input)
        return header

    @staticmethod
    def _style_arrangement_region(button: QPushButton, color: str, active: bool) -> None:
        if active:
            button.setStyleSheet(
                f"background-color: {color};"
                "border: 1px solid rgba(190, 220, 255, 165);"
                "border-radius: 4px;"
                "min-height: 26px;"
                "padding: 0 8px;"
                "color: #eef6ff;"
                "font-weight: 600;"
                "text-align: left;"
            )
            return
        button.setStyleSheet(
            "background-color: rgba(35, 38, 45, 190);"
            "border: 1px solid rgba(80, 88, 102, 115);"
            "border-radius: 3px;"
            "min-height: 26px;"
            "padding: 0;"
        )

    @staticmethod
    def _fmt_epoch(value: int) -> str:
        if value <= 0:
            return "-"
        return datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S")
