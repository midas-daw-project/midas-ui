from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bridge.fallback_bridge import FallbackBridgeClient
from controllers.session_controller import SessionController
from viewmodels.session_viewmodel import SessionViewModel


def test_session_save_load_apply_flow():
    bridge = FallbackBridgeClient()
    vm = SessionViewModel()
    controller = SessionController(bridge, vm)

    controller.refresh_status()
    assert vm.status == "idle"

    assert controller.save_session().ok
    assert vm.status == "saved"
    assert vm.phase == "saved"
    assert vm.dirty is False
    assert vm.storage_source == "fallback-memory"
    assert vm.storage_path == "fallback://local-session"
    assert vm.last_operation == "save"
    assert vm.last_save_epoch > 0
    assert vm.last_save_status == "ok"
    assert vm.recent_sessions
    assert vm.recent_sessions[0].session_ref == "local-session"

    assert controller.load_session().ok
    assert vm.status == "loaded"
    assert vm.phase == "loaded"
    assert vm.dirty is False
    assert vm.last_operation == "load"
    assert vm.last_load_epoch > 0
    assert vm.last_load_status == "ok"
    assert vm.recent_sessions[0].last_operation == "load"

    assert controller.apply_session().ok
    assert vm.status == "applied"
    assert vm.phase == "applied"
    assert vm.dirty is False
    assert vm.last_operation == "apply"
    assert vm.last_apply_epoch > 0
    assert vm.last_apply_status == "ok"


def test_session_new_open_and_recent_flow():
    bridge = FallbackBridgeClient()
    vm = SessionViewModel()
    controller = SessionController(bridge, vm)

    assert controller.new_session("mix-b").ok
    assert vm.session_ref == "mix-b"
    assert vm.phase == "new"
    assert controller.save_session().ok
    assert vm.recent_sessions[0].session_ref == "mix-b"

    assert controller.new_session("mix-c").ok
    assert controller.save_session().ok
    assert vm.recent_sessions[0].session_ref == "mix-c"

    assert controller.open_session("mix-b").ok
    assert vm.session_ref == "mix-b"
    assert vm.status == "applied"
    assert vm.recent_sessions[0].session_ref == "mix-b"
    assert any(entry.session_ref == "mix-c" for entry in vm.recent_sessions)


def test_session_dirty_transition_after_mutation_and_save():
    bridge = FallbackBridgeClient()
    vm = SessionViewModel()
    controller = SessionController(bridge, vm)

    assert controller.save_session().ok
    assert controller.load_session().ok
    assert controller.apply_session().ok
    assert bridge.set_channel_gain(1, 0.7).ok

    controller.refresh_status()
    assert vm.status == "modified"
    assert vm.phase == "modified"
    assert vm.dirty is True
    assert vm.last_operation == "modify"

    assert controller.save_session().ok
    assert vm.status == "saved"
    assert vm.phase == "saved"
    assert vm.dirty is False
