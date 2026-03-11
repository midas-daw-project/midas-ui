from __future__ import annotations

from dataclasses import dataclass, field

from bridge.protocol import MixerChannelStatus


@dataclass(slots=True)
class MixerViewModel:
    channels: list[MixerChannelStatus] = field(default_factory=list)
    selected_channel_id: int = 1
    last_error: str = ""
