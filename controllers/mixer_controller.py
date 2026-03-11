from __future__ import annotations

from bridge.protocol import BridgeClient, BridgeResult, MixerChannelStatus
from viewmodels.mixer_viewmodel import MixerViewModel


class MixerController:
    def __init__(self, bridge: BridgeClient, viewmodel: MixerViewModel) -> None:
        self._bridge = bridge
        self._vm = viewmodel

    @property
    def viewmodel(self) -> MixerViewModel:
        return self._vm

    def refresh_channels(self) -> None:
        self._vm.channels = self._bridge.get_mixer_channels()
        if not self._vm.channels:
            self._vm.channels = [MixerChannelStatus(channel_id=self._vm.selected_channel_id, muted=False, gain=1.0)]

    def set_mute(self, channel_id: int, muted: bool) -> BridgeResult:
        result = self._bridge.set_channel_mute(channel_id, muted)
        self._vm.last_error = "" if result.ok else result.message
        self.refresh_channels()
        return result

    def set_gain(self, channel_id: int, gain: float) -> BridgeResult:
        result = self._bridge.set_channel_gain(channel_id, gain)
        self._vm.last_error = "" if result.ok else result.message
        self.refresh_channels()
        return result

    def channel(self, channel_id: int) -> MixerChannelStatus:
        for channel in self._vm.channels:
            if channel.channel_id == channel_id:
                return channel
        return MixerChannelStatus(channel_id=channel_id, muted=False, gain=1.0)
