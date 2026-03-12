from __future__ import annotations

from dataclasses import dataclass, field

from bridge.protocol import InsertedPluginSlot, MixerChannelStatus


@dataclass(slots=True)
class MixerViewModel:
    channels: list[MixerChannelStatus] = field(default_factory=list)
    insert_chain: list[InsertedPluginSlot] = field(default_factory=list)
    selected_slot_index: int = 0
    selected_channel_id: int = 1
    last_insert_status: str = ""
    last_error: str = ""
