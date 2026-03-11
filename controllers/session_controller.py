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
        self._vm.status = status.status
        if status.session_ref:
            self._vm.session_ref = status.session_ref

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
