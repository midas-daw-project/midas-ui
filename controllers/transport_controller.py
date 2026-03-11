from __future__ import annotations

from bridge.protocol import BridgeClient, BridgeResult
from viewmodels.transport_viewmodel import TransportViewModel


class TransportController:
    def __init__(self, bridge: BridgeClient, viewmodel: TransportViewModel) -> None:
        self._bridge = bridge
        self._vm = viewmodel

    @property
    def viewmodel(self) -> TransportViewModel:
        return self._vm

    def play(self) -> BridgeResult:
        result = self._bridge.play_transport(self._vm.track_channel, self._vm.mixer_subsystem)
        self._vm.last_error = "" if result.ok else result.message
        self.refresh_status()
        return result

    def stop(self) -> BridgeResult:
        result = self._bridge.stop_transport()
        self._vm.last_error = "" if result.ok else result.message
        self.refresh_status()
        return result

    def refresh_status(self) -> None:
        status = self._bridge.get_transport_status()
        self._vm.play_state = status.play_state
