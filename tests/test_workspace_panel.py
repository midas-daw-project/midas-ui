from pathlib import Path
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtWidgets import QApplication

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
