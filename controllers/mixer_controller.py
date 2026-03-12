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
        self.refresh_insert_chain(self._vm.selected_channel_id)

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

    def refresh_insert_chain(self, channel_id: int) -> None:
        self._vm.insert_chain = self._bridge.get_insert_chain(channel_id)

    def insert_plugin(self, channel_id: int, plugin_id: str, slot_index: int) -> BridgeResult:
        result = self._bridge.insert_plugin(channel_id, plugin_id, slot_index)
        self._vm.last_insert_status = "ok" if result.ok else "error"
        self._vm.last_error = "" if result.ok else result.message
        self.refresh_insert_chain(channel_id)
        return result

    def remove_plugin(self, channel_id: int, slot_index: int) -> BridgeResult:
        result = self._bridge.remove_plugin(channel_id, slot_index)
        self._vm.last_insert_status = "ok" if result.ok else "error"
        self._vm.last_error = "" if result.ok else result.message
        self.refresh_insert_chain(channel_id)
        return result

    def move_plugin(self, channel_id: int, from_slot_index: int, to_slot_index: int) -> BridgeResult:
        result = self._bridge.move_plugin(channel_id, from_slot_index, to_slot_index)
        self._vm.last_insert_status = "ok" if result.ok else "error"
        self._vm.last_error = "" if result.ok else result.message
        self.refresh_insert_chain(channel_id)
        return result

    def set_plugin_bypass(self, channel_id: int, slot_index: int, bypassed: bool) -> BridgeResult:
        result = self._bridge.set_plugin_bypass(channel_id, slot_index, bypassed)
        self._vm.last_insert_status = "ok" if result.ok else "error"
        self._vm.last_error = "" if result.ok else result.message
        self.refresh_insert_chain(channel_id)
        return result

    def move_plugin_to_top(self, channel_id: int, slot_index: int) -> BridgeResult:
        result = self._bridge.move_plugin_to_top(channel_id, slot_index)
        self._vm.last_insert_status = "ok" if result.ok else "error"
        self._vm.last_error = "" if result.ok else result.message
        self.refresh_insert_chain(channel_id)
        return result

    def move_plugin_to_bottom(self, channel_id: int, slot_index: int) -> BridgeResult:
        result = self._bridge.move_plugin_to_bottom(channel_id, slot_index)
        self._vm.last_insert_status = "ok" if result.ok else "error"
        self._vm.last_error = "" if result.ok else result.message
        self.refresh_insert_chain(channel_id)
        return result

    def clear_insert_chain(self, channel_id: int) -> BridgeResult:
        result = self._bridge.clear_insert_chain(channel_id)
        self._vm.last_insert_status = "ok" if result.ok else "error"
        self._vm.last_error = "" if result.ok else result.message
        self.refresh_insert_chain(channel_id)
        return result

    def set_channel_insert_bypass(self, channel_id: int, bypassed: bool) -> BridgeResult:
        result = self._bridge.set_channel_insert_bypass(channel_id, bypassed)
        self._vm.last_insert_status = "ok" if result.ok else "error"
        self._vm.last_error = "" if result.ok else result.message
        self.refresh_insert_chain(channel_id)
        return result

    def refresh_insert_runtime_state(self, channel_id: int) -> BridgeResult:
        result = self._bridge.refresh_insert_runtime_state(channel_id)
        self._vm.last_insert_status = "ok" if result.ok else "error"
        self._vm.last_error = "" if result.ok else result.message
        self.refresh_insert_chain(channel_id)
        return result
