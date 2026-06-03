from pathlib import Path
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QPushButton

from bridge.protocol import RecentSessionEntry
from panels.debug.debug_panel import DebugPanel
from panels.session.session_panel import SessionPanel
from panels.workspace.workspace_panel import WorkspacePanel
from viewmodels.session_viewmodel import SessionViewModel
from viewmodels.workspace_viewmodel import WorkspaceViewModel


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_workspace_panel_renders_current_project_and_recent_sections():
    _app()
    panel = WorkspacePanel(
        on_refresh_all=lambda: None,
        on_new_session=lambda _ref: None,
        on_open_session=lambda _ref: None,
        on_open_existing_session=lambda: None,
        on_open_recent=lambda _ref: None,
        on_save_session=lambda: None,
        on_load_session=lambda: None,
        on_apply_session=lambda: None,
        on_reconcile_inserts=lambda: None,
    )
    vm = WorkspaceViewModel(
        session_ref="mix-a",
        session_status="applied",
        session_phase="modified",
        session_dirty=True,
        session_storage_path="C:/sessions/mix-a.session",
        session_storage_source="file",
        session_last_operation="save",
        current_project_summary="mix-a | modified | dirty",
        recent_session_count=2,
        recent_session_summary="mix-a (save)",
        discoverable_session_count=3,
        managed_instance_count=1,
        failed_instance_count=0,
        selected_managed_instance_summary="stub-1:created:created:created:adapter stub created",
        selected_runtime_handle_summary="local_runtime:lrh-1:builtin_graph:builtin://midas/eq/basic",
        recent_sessions=[
            RecentSessionEntry(
                session_ref="mix-a",
                storage_path="C:/sessions/mix-a.session",
                storage_source="file",
                last_operation="save",
                last_touched_epoch=100,
            )
        ],
    )

    panel.render(vm)

    assert panel.project_heading_label.text() == "mix-a"
    assert panel.beat_canvas.objectName() == "beatCanvas"
    assert panel.daw_control_strip.objectName() == "dawControlStrip"
    assert panel.view_mode_strip.objectName() == "viewModeStrip"
    assert panel.arrange_ruler.objectName() == "arrangeRuler"
    assert panel.track_panel_header_label.text() == "Track Control Panel"
    assert panel.timeline_header_label.text() == "Timeline"
    assert panel.summary_tabs.maximumHeight() == 188
    assert panel.status_box.maximumHeight() == 74
    assert panel.beat_canvas.minimumWidth() == 1200
    assert panel.beat_canvas.minimumHeight() == 440
    assert panel.channel_rack.objectName() == "channelRack"
    assert panel.editor_stack.objectName() == "editorStack"
    assert panel.current_editor_name() == "Arrangement"
    panel.show_next_editor()
    assert panel.current_editor_name() == "Drum Machine"
    panel.show_next_editor()
    assert panel.current_editor_name() == "Piano Roll"
    panel.show_previous_editor()
    assert panel.current_editor_name() == "Drum Machine"
    panel.show_previous_editor()
    assert panel.current_editor_name() == "Arrangement"
    panel._select_mode("Record")
    assert panel.current_editor_name() == "Drum Machine"
    panel._select_mode("MIDI")
    assert panel.current_editor_name() == "Piano Roll"
    panel._select_mode("Arrange")
    assert panel.current_editor_name() == "Arrangement"
    assert panel.selected_mix_percent() == 100
    assert panel.selected_playrate() == 1.0
    panel.playrate_input.setValue(75)
    assert panel.playrate_label.text() == "Rate 0.75"
    assert panel.selected_playrate() == 0.75
    assert panel.arrangement_track_count() == 11
    assert panel.arrangement_track_names()[0] == "Master"
    assert panel.arrangement_track_names()[1] == "Audio Track"
    assert panel.arrangement_scroll_area.horizontalScrollBarPolicy() == Qt.ScrollBarAsNeeded
    assert panel.arrangement_scroll_area.verticalScrollBarPolicy() == Qt.ScrollBarAsNeeded
    assert panel.empty_arrangement_label.isVisibleTo(panel) is False or panel.empty_arrangement_label.text().startswith("No tracks")
    panel.add_arrangement_track_button.click()
    assert panel.arrangement_track_count() == 12
    assert panel.arrangement_track_names()[-1] == "Audio Track 2"
    panel.arrangement_track_name_inputs[-1].setText("Hook idea")
    panel.arrangement_track_name_inputs[-1].editingFinished.emit()
    assert panel.arrangement_track_names()[-1] == "Hook idea"
    panel.arrangement_track_name_inputs[-1].parent().findChild(QPushButton, "trackRemoveButton").click()
    assert panel.arrangement_track_count() == 11
    assert panel.drum_track_count() == 0
    panel.show_drum_machine()
    panel.add_drum_track_button.click()
    assert panel.drum_track_count() == 1
    assert panel.drum_track_name_inputs[0].text() == "New Track"
    assert not panel.drum_step_active("drum-track-1", 0)
    panel._drum_step_buttons[("drum-track-1", 0)].click()
    assert panel.drum_step_active("drum-track-1", 0)
    panel.drum_track_name_inputs[0].parent().findChild(QPushButton, "trackRemoveButton").click()
    assert panel.drum_track_count() == 0
    assert panel.midi_note_grid.objectName() == "midiNoteGrid"
    selected_midi_track = panel.selected_midi_track()
    assert selected_midi_track == "Audio Track"
    starting_notes = panel.midi_note_count(selected_midi_track)
    panel.midi_pitch_selector.setCurrentText("C4")
    panel.midi_step_input.setValue(2)
    panel.midi_length_input.setValue(2)
    panel.add_midi_note_button.click()
    assert panel.midi_note_count(selected_midi_track) == starting_notes + 1
    assert panel.midi_pitches_for_track(selected_midi_track) == ["C4"]
    assert "C4@2x2" in panel.midi_note_summary_label.text()
    assert panel.selected_midi_note(selected_midi_track) == (2, "C4", 2)
    panel.move_selected_midi_note(4, "E4", selected_midi_track)
    assert panel.midi_notes_for_track(selected_midi_track) == [(4, "E4", 2)]
    assert "E4@4x2" in panel.midi_note_summary_label.text()
    panel.add_arrangement_track_button.click()
    panel.midi_track_selector.setCurrentText("Audio Track 2")
    panel.midi_pitch_selector.setCurrentText("G4")
    panel.midi_step_input.setValue(4)
    panel.midi_length_input.setValue(1)
    panel.add_midi_note_button.click()
    panel.midi_track_selector.setCurrentText(selected_midi_track)
    assert panel.ghost_notes_visible()
    assert (4, "G4") in panel._midi_grid_buttons
    assert "dashed" in panel._midi_grid_buttons[(4, "G4")].styleSheet()
    panel.ghost_notes_toggle.setChecked(False)
    assert not panel.ghost_notes_visible()
    assert "dashed" not in panel._midi_grid_buttons[(4, "G4")].styleSheet()
    assert "drum pattern" in panel.assistant_prompt_label.text()
    assert "sampled MIDI" in panel.assistant_prompt_label.text()
    assert "Next:" in panel.next_action_label.text()
    assert "Bridge: unknown v0" in panel.bridge_runtime_label.text()
    assert "Session: mix-a" in panel.session_flow_label.text()
    assert "phase: modified" in panel.status_box.toolTip()
    assert "Plugins: 0 available / 0 inserted" in panel.reconcile_flow_label.text()
    assert "Dirty: dirty" in panel.session_identity_label.text()
    assert "Recent: 2" in panel.recent_summary_card_label.text()
    assert "Discoverable: 3" in panel.recent_summary_card_label.text()
    assert "active=1 failed=0" in panel.instance_label.text()
    assert "stub-1:created:created" in panel.selected_instance_label.text()
    assert "lrh-1" in panel.selected_runtime_handle_label.text()
    assert panel.selected_recent_session_ref() == "mix-a"


def test_session_panel_renders_consistent_identity_and_error_state():
    _app()
    panel = SessionPanel(
        on_new=lambda _ref: None,
        on_open=lambda _ref: None,
        on_save=lambda: None,
        on_load=lambda: None,
        on_apply=lambda: None,
        on_refresh=lambda: None,
    )
    vm = SessionViewModel(
        status="loaded",
        phase="modified",
        dirty=True,
        restore_phase="intent_restored",
        runtime_hydrated=False,
        restore_guidance="Apply session before rendering runtime fields.",
        session_ref="mix-b",
        storage_path="C:/sessions/mix-b.session",
        storage_source="file",
        last_operation="load",
        last_load_epoch=120,
        last_error="session warning",
        recent_sessions=[
            RecentSessionEntry(
                session_ref="mix-b",
                storage_path="C:/sessions/mix-b.session",
                storage_source="file",
                last_operation="load",
                last_touched_epoch=120,
            )
        ],
        discoverable_sessions=[],
        storage_root="C:/sessions",
    )

    panel.render(vm)

    assert panel.session_heading_label.text() == "mix-b"
    assert panel.status_label.text() == "Status: loaded"
    assert "Dirty: dirty" in panel.identity_label.text()
    assert "intent_restored" in panel.restore_label.text()
    assert "Runtime: pending" in panel.restore_label.text()
    assert "Apply session before rendering runtime fields." in panel.restore_label.text()
    assert "C:/sessions/mix-b.session" in panel.storage_label.text()
    assert panel.error_label.text() == "session warning"


def test_debug_panel_renders_adapter_backend_summary():
    _app()
    panel = DebugPanel(on_manual_refresh=lambda: None)
    panel.set_backend_summary(
        backend_name="local_runtime",
        supports_create=True,
        supports_destroy=True,
        supports_query=True,
        support_scope="midas.*",
        selected_slot_reason="plugin_unavailable",
        selected_slot_message="plugin is not supported by local runtime backend",
        selected_backend_name="local_runtime",
        selected_backend_handle="lrh-42",
        selected_handle_state="active",
        selected_terminal=False,
        selected_retryable=True,
        selected_reason_source="adapter",
        selected_descriptor_id="midas.eq.basic",
        selected_descriptor_kind="builtin_graph",
        selected_descriptor_ref="builtin://midas/eq/basic",
        catalog_source_label="local_manifest",
        catalog_source_version="1",
        catalog_descriptor_count=4,
        catalog_valid_descriptor_count=3,
        catalog_policy_supported_descriptor_count=3,
    )

    assert panel.backend_label.text() == "Backend: local_runtime"
    assert "create=yes" in panel.capabilities_label.text()
    assert panel.scope_label.text() == "Support Scope: midas.*"
    assert "source=local_manifest@1" in panel.catalog_label.text()
    assert "plugin_unavailable" in panel.slot_adapter_label.text()
    assert "lrh-42" in panel.slot_runtime_label.text()
    assert "handle_state=active" in panel.slot_runtime_label.text()
    assert "source=adapter" in panel.slot_runtime_label.text()
