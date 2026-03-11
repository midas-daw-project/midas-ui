from __future__ import annotations

from bridge.protocol import BridgeClient, BridgeResult
from viewmodels.audio_viewmodel import AudioViewModel


class AudioController:
    def __init__(self, bridge: BridgeClient, viewmodel: AudioViewModel) -> None:
        self._bridge = bridge
        self._vm = viewmodel

    @property
    def viewmodel(self) -> AudioViewModel:
        return self._vm

    def start_runtime_profile(self) -> BridgeResult:
        result = self._bridge.start_default_runtime_profile()
        self._vm.last_error = "" if result.ok else result.message
        return result

    def shutdown_runtime_profile(self) -> BridgeResult:
        result = self._bridge.shutdown_runtime_profile()
        self._vm.last_error = "" if result.ok else result.message
        self.refresh_status()
        return result

    def init_audio(self) -> BridgeResult:
        result = self._bridge.init_audio(self._vm.device_id, self._vm.sample_rate, self._vm.buffer_size)
        self._vm.last_error = "" if result.ok else result.message
        self.refresh_status()
        return result

    def open_audio(self) -> BridgeResult:
        result = self._bridge.open_audio()
        self._vm.last_error = "" if result.ok else result.message
        self.refresh_status()
        return result

    def start_audio(self) -> BridgeResult:
        result = self._bridge.start_audio(self._vm.track_channel, self._vm.mixer_subsystem)
        self._vm.last_error = "" if result.ok else result.message
        self.refresh_status()
        return result

    def stop_audio(self) -> BridgeResult:
        result = self._bridge.stop_audio()
        self._vm.last_error = "" if result.ok else result.message
        self.refresh_status()
        return result

    def close_audio(self) -> BridgeResult:
        result = self._bridge.close_audio()
        self._vm.last_error = "" if result.ok else result.message
        self.refresh_status()
        return result

    def refresh_status(self) -> None:
        status = self._bridge.get_audio_status()
        self._vm.state = status.state
        self._vm.device_id = status.device_id
        self._vm.sample_rate = status.sample_rate
        self._vm.buffer_size = status.buffer_size
        self._vm.render_status = status.render_status
