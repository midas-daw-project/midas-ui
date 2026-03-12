from __future__ import annotations

from bridge.protocol import BridgeClient, BridgeResult
from viewmodels.session_viewmodel import SessionViewModel


class SessionController:
    def __init__(self, bridge: BridgeClient, viewmodel: SessionViewModel) -> None:
        self._bridge = bridge
        self._vm = viewmodel

    @property
    def viewmodel(self) -> SessionViewModel:
        return self._vm

    def refresh_status(self) -> None:
        status = self._bridge.get_session_status()
        recents = self._bridge.get_recent_sessions()
        discoverable = self._bridge.get_discoverable_sessions()
        self._vm.status = status.status
        self._vm.phase = status.phase
        self._vm.dirty = status.dirty
        if status.session_ref:
            self._vm.session_ref = status.session_ref
        self._vm.storage_path = status.storage_path
        self._vm.storage_source = status.storage_source
        self._vm.last_operation = status.last_operation
        self._vm.last_save_epoch = status.last_save_epoch
        self._vm.last_load_epoch = status.last_load_epoch
        self._vm.last_apply_epoch = status.last_apply_epoch
        self._vm.last_error = status.last_error_message
        self._vm.recent_sessions = recents
        self._vm.discoverable_sessions = discoverable
        self._vm.storage_root = self._bridge.get_session_storage_root()

    def new_session(self, session_ref: str) -> BridgeResult:
        result = self._bridge.new_session(session_ref)
        self._vm.last_error = "" if result.ok else result.message
        self.refresh_status()
        return result

    def open_session(self, session_ref: str) -> BridgeResult:
        result = self._bridge.open_session(session_ref)
        self._vm.last_load_status = "ok" if result.ok else "error"
        self._vm.last_apply_status = "ok" if result.ok else "error"
        self._vm.last_error = "" if result.ok else result.message
        self.refresh_status()
        return result

    def save_session(self) -> BridgeResult:
        result = self._bridge.save_session()
        self._vm.last_save_status = "ok" if result.ok else "error"
        self._vm.last_error = "" if result.ok else result.message
        self.refresh_status()
        return result

    def load_session(self) -> BridgeResult:
        result = self._bridge.load_session()
        self._vm.last_load_status = "ok" if result.ok else "error"
        self._vm.last_error = "" if result.ok else result.message
        self.refresh_status()
        return result

    def apply_session(self) -> BridgeResult:
        result = self._bridge.apply_session()
        self._vm.last_apply_status = "ok" if result.ok else "error"
        self._vm.last_error = "" if result.ok else result.message
        self.refresh_status()
        return result

    def mark_dirty(self) -> None:
        self._vm.dirty = True
        self._vm.phase = "modified"
        self._vm.status = "modified"
        self._vm.last_operation = "modify"
