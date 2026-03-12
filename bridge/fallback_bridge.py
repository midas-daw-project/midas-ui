from __future__ import annotations

from typing import Callable, Dict
from typing import List
from copy import deepcopy
import time

from bridge.protocol import (
    AudioStatus,
    BridgeClient,
    BridgeEvent,
    InsertedPluginSlot,
    PluginRegistryEntry,
    BridgeResult,
    MixerChannelStatus,
    RuntimeStatus,
    SessionStatus,
    TransportStatus,
)


class FallbackBridgeClient(BridgeClient):
    """Development fallback until native bridge bindings are available."""

    def __init__(self) -> None:
        self._status = AudioStatus()
        self._events: List[BridgeEvent] = []
        self._runtime_started = False
        self._callbacks: Dict[int, Callable[[BridgeEvent], None]] = {}
        self._next_handle = 1
        self._mixer_channels: Dict[int, MixerChannelStatus] = {
            1: MixerChannelStatus(channel_id=1, muted=False, gain=1.0)
        }
        self._session = SessionStatus(status="idle", session_ref="local-session")
        self._session.phase = "none"
        self._session.storage_source = "fallback-memory"
        self._session.last_operation = "none"
        self._transport = TransportStatus(play_state="stopped")
        self._track_channel = 0
        self._plugin_registry = [
            PluginRegistryEntry(
                plugin_id="midas.eq.basic",
                name="MIDAS Basic EQ",
                category="EQ",
                vendor="MIDAS Labs",
                available=True,
                source="builtin",
            ),
            PluginRegistryEntry(
                plugin_id="midas.comp.basic",
                name="MIDAS Basic Compressor",
                category="Dynamics",
                vendor="MIDAS Labs",
                available=True,
                source="builtin",
            ),
            PluginRegistryEntry(
                plugin_id="thirdparty.reverb.demo",
                name="ThirdParty Demo Reverb",
                category="Reverb",
                vendor="ThirdParty Audio",
                available=False,
                source="registry",
            ),
        ]
        self._insert_chains: Dict[int, List[InsertedPluginSlot]] = {}
        self._saved_insert_chains: Dict[int, List[InsertedPluginSlot]] = {}

    def bridge_version(self) -> int:
        return 1

    def start_default_runtime_profile(self) -> BridgeResult:
        self._runtime_started = True
        self._publish(BridgeEvent(category="session", emitter=0, metadata={"status": "runtime_started"}))
        return BridgeResult()

    def shutdown_runtime_profile(self) -> BridgeResult:
        self._runtime_started = False
        self._status = AudioStatus()
        self._publish(BridgeEvent(category="session", emitter=0, metadata={"status": "runtime_stopped"}))
        return BridgeResult()

    def init_audio(self, device_id: str, sample_rate: int, buffer_size: int) -> BridgeResult:
        if not self._runtime_started:
            return BridgeResult(code=3, message="runtime profile not started")
        self._status.state = "initialized"
        self._status.device_id = device_id
        self._status.sample_rate = sample_rate
        self._status.buffer_size = buffer_size
        self._publish(BridgeEvent(category="device", emitter=2002, metadata={"action": "init"}))
        return BridgeResult()

    def open_audio(self) -> BridgeResult:
        if self._status.state not in {"initialized", "closed"}:
            return BridgeResult(code=3, message="audio not initialized")
        self._status.state = "opened"
        self._publish(BridgeEvent(category="device", emitter=2002, metadata={"action": "open"}))
        return BridgeResult()

    def start_audio(self, track_channel: int, mixer_subsystem: int) -> BridgeResult:
        if self._status.state != "opened":
            return BridgeResult(code=3, message="audio not opened")
        self._status.state = "started"
        self._status.render_status = "no_callback"
        self._status.render_produced = False
        self._status.render_frames_produced = 0
        self._status.render_frames_requested = 0
        self._status.render_channel_count = 2
        self._status.track_channel = int(track_channel)
        self._status.tracked_muted = self._mixer_channels.get(track_channel, MixerChannelStatus()).muted
        self._status.tracked_gain = self._mixer_channels.get(track_channel, MixerChannelStatus()).gain
        self._track_channel = int(track_channel)
        self._transport.play_state = "playing"
        self._publish(
            BridgeEvent(
                category="device",
                emitter=2002,
                metadata={
                    "action": "start",
                    "track_channel": str(track_channel),
                    "mixer_subsystem": str(mixer_subsystem),
                },
            )
        )
        return BridgeResult()

    def stop_audio(self) -> BridgeResult:
        if self._status.state != "started":
            return BridgeResult(code=3, message="audio not started")
        self._status.state = "opened"
        self._status.render_status = "stopped"
        self._status.render_produced = False
        self._status.render_frames_produced = 0
        self._status.render_frames_requested = 0
        self._status.render_channel_count = 0
        self._transport.play_state = "stopped"
        self._publish(BridgeEvent(category="transport", emitter=2002, metadata={"action": "stop"}))
        return BridgeResult()

    def close_audio(self) -> BridgeResult:
        if self._status.state not in {"opened", "initialized"}:
            return BridgeResult(code=3, message="audio not open")
        self._status.state = "idle"
        self._status.device_id = ""
        self._status.sample_rate = 0
        self._status.buffer_size = 0
        self._status.render_status = "stopped"
        self._status.render_produced = False
        self._status.render_frames_produced = 0
        self._status.render_frames_requested = 0
        self._status.render_channel_count = 0
        self._status.track_channel = 0
        self._status.tracked_muted = False
        self._status.tracked_gain = 1.0
        self._track_channel = 0
        self._publish(BridgeEvent(category="device", emitter=2002, metadata={"action": "close"}))
        return BridgeResult()

    def get_audio_status(self) -> AudioStatus:
        return AudioStatus(
            state=self._status.state,
            device_id=self._status.device_id,
            sample_rate=self._status.sample_rate,
            buffer_size=self._status.buffer_size,
            render_status=self._status.render_status,
            render_produced=self._status.render_produced,
            render_frames_produced=self._status.render_frames_produced,
            render_frames_requested=self._status.render_frames_requested,
            render_channel_count=self._status.render_channel_count,
            track_channel=self._status.track_channel,
            tracked_muted=self._status.tracked_muted,
            tracked_gain=self._status.tracked_gain,
        )

    def drain_recent_events(self, max_events: int) -> List[BridgeEvent]:
        if max_events <= 0:
            return []
        chunk = self._events[:max_events]
        self._events = self._events[max_events:]
        return chunk

    def subscribe_events(self, callback: Callable[[BridgeEvent], None]) -> int:
        handle = self._next_handle
        self._next_handle += 1
        self._callbacks[handle] = callback
        return handle

    def unsubscribe_events(self, handle: int) -> None:
        self._callbacks.pop(handle, None)

    def get_mixer_channels(self) -> List[MixerChannelStatus]:
        return [MixerChannelStatus(channel_id=c.channel_id, muted=c.muted, gain=c.gain)
                for c in self._mixer_channels.values()]

    def set_channel_mute(self, channel_id: int, muted: bool) -> BridgeResult:
        channel = self._mixer_channels.setdefault(channel_id, MixerChannelStatus(channel_id=channel_id))
        channel.muted = muted
        if int(channel_id) == self._track_channel:
            self._status.tracked_muted = muted
        self._publish(
            BridgeEvent(
                category="mixer",
                emitter=2001,
                metadata={"channel": str(channel_id), "muted": "true" if muted else "false"},
            )
        )
        self._mark_session_modified()
        return BridgeResult()

    def set_channel_gain(self, channel_id: int, gain: float) -> BridgeResult:
        channel = self._mixer_channels.setdefault(channel_id, MixerChannelStatus(channel_id=channel_id))
        channel.gain = float(gain)
        if int(channel_id) == self._track_channel:
            self._status.tracked_gain = float(gain)
        self._publish(
            BridgeEvent(
                category="mixer",
                emitter=2001,
                metadata={"channel": str(channel_id), "gain": f"{channel.gain:.6f}"},
            )
        )
        self._mark_session_modified()
        return BridgeResult()

    def save_session(self) -> BridgeResult:
        self._session.status = "saved"
        self._session.phase = "saved"
        self._session.dirty = False
        self._session.last_operation = "save"
        self._session.last_save_epoch = int(time.time())
        self._session.storage_path = "fallback://local-session"
        self._saved_insert_chains = deepcopy(self._insert_chains)
        self._publish(
            BridgeEvent(
                category="session",
                emitter=2003,
                metadata={"action": "save", "status": self._session.status, "session_ref": self._session.session_ref},
            )
        )
        return BridgeResult()

    def load_session(self) -> BridgeResult:
        self._session.status = "loaded"
        self._session.phase = "loaded"
        self._session.dirty = False
        self._session.last_operation = "load"
        self._session.last_load_epoch = int(time.time())
        self._session.storage_path = "fallback://local-session"
        self._insert_chains = deepcopy(self._saved_insert_chains)
        self._publish(
            BridgeEvent(
                category="session",
                emitter=2003,
                metadata={"action": "load", "status": self._session.status, "session_ref": self._session.session_ref},
            )
        )
        return BridgeResult()

    def apply_session(self) -> BridgeResult:
        self._session.status = "applied"
        self._session.phase = "applied"
        self._session.dirty = False
        self._session.last_operation = "apply"
        self._session.last_apply_epoch = int(time.time())
        self._session.storage_path = "fallback://local-session"
        self._insert_chains = deepcopy(self._saved_insert_chains)
        self._publish(
            BridgeEvent(
                category="session",
                emitter=2003,
                metadata={"action": "apply", "status": self._session.status, "session_ref": self._session.session_ref},
            )
        )
        return BridgeResult()

    def get_session_status(self) -> SessionStatus:
        return SessionStatus(
            status=self._session.status,
            session_ref=self._session.session_ref,
            phase=self._session.phase,
            dirty=self._session.dirty,
            storage_path=self._session.storage_path,
            storage_source=self._session.storage_source,
            last_operation=self._session.last_operation,
            last_save_epoch=self._session.last_save_epoch,
            last_load_epoch=self._session.last_load_epoch,
            last_apply_epoch=self._session.last_apply_epoch,
        )

    def play_transport(self, track_channel: int, mixer_subsystem: int) -> BridgeResult:
        return self.start_audio(track_channel, mixer_subsystem)

    def stop_transport(self) -> BridgeResult:
        return self.stop_audio()

    def get_transport_status(self) -> TransportStatus:
        return TransportStatus(
            play_state=self._transport.play_state,
            runtime_active=self._status.state == "started",
            audio_lifecycle_state=self._status.state,
            render_status=self._status.render_status,
            render_produced=self._status.render_produced,
        )

    def get_runtime_status(self) -> RuntimeStatus:
        return RuntimeStatus(
            runtime_started=self._runtime_started,
            bridge_version=self.bridge_version(),
            audio=self.get_audio_status(),
        )

    def get_plugin_registry(self) -> List[PluginRegistryEntry]:
        return [
            PluginRegistryEntry(
                plugin_id=entry.plugin_id,
                name=entry.name,
                category=entry.category,
                vendor=entry.vendor,
                available=entry.available,
                source=entry.source,
            )
            for entry in self._plugin_registry
        ]

    def refresh_plugin_registry(self) -> BridgeResult:
        self._publish(
            BridgeEvent(
                category="subsystem",
                emitter=2003,
                metadata={"action": "refresh_plugin_registry", "count": str(len(self._plugin_registry))},
            )
        )
        return BridgeResult()

    def get_insert_chain(self, channel_id: int) -> List[InsertedPluginSlot]:
        return [
            InsertedPluginSlot(
                channel_id=slot.channel_id,
                slot_index=slot.slot_index,
                plugin_id=slot.plugin_id,
                plugin_name=slot.plugin_name,
                available=slot.available,
                bypassed=slot.bypassed,
                load_state=slot.load_state,
            )
            for slot in self._insert_chains.get(int(channel_id), [])
        ]

    def insert_plugin(self, channel_id: int, plugin_id: str, slot_index: int) -> BridgeResult:
        plugin = next((p for p in self._plugin_registry if p.plugin_id == plugin_id), None)
        if plugin is None:
            return BridgeResult(code=3, message=f"unknown plugin id: {plugin_id}")
        if not plugin.available:
            return BridgeResult(code=3, message=f"plugin unavailable: {plugin_id}")
        channel_id = int(channel_id)
        slot_index = int(slot_index)
        if slot_index < 0:
            return BridgeResult(code=3, message="slot_index must be >= 0")
        chain = self._insert_chains.setdefault(channel_id, [])
        for i, slot in enumerate(chain):
            if slot.slot_index == slot_index:
                chain[i] = InsertedPluginSlot(
                    channel_id=channel_id,
                    slot_index=slot_index,
                    plugin_id=plugin.plugin_id,
                    plugin_name=plugin.name,
                    available=True,
                    bypassed=False,
                    load_state="inserted",
                )
                break
        else:
            chain.append(
                InsertedPluginSlot(
                    channel_id=channel_id,
                    slot_index=slot_index,
                    plugin_id=plugin.plugin_id,
                    plugin_name=plugin.name,
                    available=True,
                    bypassed=False,
                    load_state="inserted",
                )
            )
            chain.sort(key=lambda s: s.slot_index)
        self._publish(
            BridgeEvent(
                category="mixer",
                emitter=2001,
                metadata={
                    "action": "insert_plugin",
                    "channel": str(channel_id),
                    "slot": str(slot_index),
                    "plugin_id": plugin.plugin_id,
                },
            )
        )
        self._mark_session_modified()
        return BridgeResult()

    def remove_plugin(self, channel_id: int, slot_index: int) -> BridgeResult:
        channel_id = int(channel_id)
        slot_index = int(slot_index)
        chain = self._insert_chains.get(channel_id, [])
        remaining = [slot for slot in chain if slot.slot_index != slot_index]
        if len(remaining) == len(chain):
            return BridgeResult(code=2, message="plugin slot not found")
        self._insert_chains[channel_id] = remaining
        self._publish(
            BridgeEvent(
                category="mixer",
                emitter=2001,
                metadata={"action": "remove_plugin", "channel": str(channel_id), "slot": str(slot_index)},
            )
        )
        self._mark_session_modified()
        return BridgeResult()

    def move_plugin(self, channel_id: int, from_slot_index: int, to_slot_index: int) -> BridgeResult:
        channel_id = int(channel_id)
        from_slot_index = int(from_slot_index)
        to_slot_index = int(to_slot_index)
        if from_slot_index < 0 or to_slot_index < 0:
            return BridgeResult(code=3, message="slot_index must be >= 0")
        chain = self._insert_chains.get(channel_id, [])
        from_slot = next((slot for slot in chain if slot.slot_index == from_slot_index), None)
        if from_slot is None:
            return BridgeResult(code=2, message="plugin slot not found")
        if from_slot_index != to_slot_index:
            to_slot = next((slot for slot in chain if slot.slot_index == to_slot_index), None)
            from_slot.slot_index = to_slot_index
            if to_slot is not None and to_slot is not from_slot:
                to_slot.slot_index = from_slot_index
            chain.sort(key=lambda s: s.slot_index)
        self._publish(
            BridgeEvent(
                category="mixer",
                emitter=2001,
                metadata={
                    "action": "move_plugin",
                    "channel": str(channel_id),
                    "from_slot": str(from_slot_index),
                    "to_slot": str(to_slot_index),
                },
            )
        )
        self._mark_session_modified()
        return BridgeResult()

    def set_plugin_bypass(self, channel_id: int, slot_index: int, bypassed: bool) -> BridgeResult:
        channel_id = int(channel_id)
        slot_index = int(slot_index)
        chain = self._insert_chains.get(channel_id, [])
        slot = next((item for item in chain if item.slot_index == slot_index), None)
        if slot is None:
            return BridgeResult(code=2, message="plugin slot not found")
        slot.bypassed = bool(bypassed)
        slot.load_state = "bypassed" if slot.bypassed else "inserted"
        self._publish(
            BridgeEvent(
                category="mixer",
                emitter=2001,
                metadata={
                    "action": "set_plugin_bypass",
                    "channel": str(channel_id),
                    "slot": str(slot_index),
                    "bypassed": "true" if slot.bypassed else "false",
                },
            )
        )
        self._mark_session_modified()
        return BridgeResult()

    def move_plugin_to_top(self, channel_id: int, slot_index: int) -> BridgeResult:
        chain = self._insert_chains.get(int(channel_id), [])
        if not chain:
            return BridgeResult(code=2, message="insert chain is empty")
        target = min(slot.slot_index for slot in chain)
        return self.move_plugin(channel_id, slot_index, target)

    def move_plugin_to_bottom(self, channel_id: int, slot_index: int) -> BridgeResult:
        chain = self._insert_chains.get(int(channel_id), [])
        if not chain:
            return BridgeResult(code=2, message="insert chain is empty")
        target = max(slot.slot_index for slot in chain)
        return self.move_plugin(channel_id, slot_index, target)

    def clear_insert_chain(self, channel_id: int) -> BridgeResult:
        channel_id = int(channel_id)
        chain = self._insert_chains.get(channel_id, [])
        if not chain:
            return BridgeResult(code=0, message="")
        self._insert_chains[channel_id] = []
        self._publish(
            BridgeEvent(
                category="mixer",
                emitter=2001,
                metadata={"action": "clear_insert_chain", "channel": str(channel_id)},
            )
        )
        self._mark_session_modified()
        return BridgeResult()

    def set_channel_insert_bypass(self, channel_id: int, bypassed: bool) -> BridgeResult:
        channel_id = int(channel_id)
        chain = self._insert_chains.get(channel_id, [])
        for slot in chain:
            slot.bypassed = bool(bypassed)
            slot.load_state = "bypassed" if slot.bypassed else "inserted"
        self._publish(
            BridgeEvent(
                category="mixer",
                emitter=2001,
                metadata={
                    "action": "set_channel_insert_bypass",
                    "channel": str(channel_id),
                    "bypassed": "true" if bool(bypassed) else "false",
                },
            )
        )
        if chain:
            self._mark_session_modified()
        return BridgeResult()

    def _mark_session_modified(self) -> None:
        self._session.status = "modified"
        self._session.phase = "modified"
        self._session.dirty = True
        self._session.last_operation = "modify"

    def _publish(self, event: BridgeEvent) -> None:
        self._events.append(event)
        for callback in list(self._callbacks.values()):
            callback(event)
