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
    ManagedInstanceRecord,
    ManagedInstanceTransitionRecord,
    PluginRegistryEntry,
    BridgeResult,
    MixerChannelStatus,
    RuntimeStatus,
    ReconcileStatus,
    DiscoverableSessionEntry,
    RecentSessionEntry,
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
        self._session.storage_path = "fallback://local-session"
        self._session.last_operation = "none"
        self._session.last_error_message = ""
        self._recent_sessions: List[RecentSessionEntry] = []
        self._saved_sessions: Dict[str, Dict[int, List[InsertedPluginSlot]]] = {}
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
        self._next_placeholder_sequence = 1
        self._next_managed_instance_sequence = 1
        self._reconcile_status = ReconcileStatus()
        self._in_reconcile = False

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
        result = BridgeResult()
        self._apply_live_reconcile_policy("insert_plugin", channel_id, result, immediate=True)
        return result

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
        result = BridgeResult()
        self._apply_live_reconcile_policy("remove_plugin", channel_id, result, immediate=True)
        return result

    def save_session(self) -> BridgeResult:
        self._session.status = "saved"
        self._session.phase = "saved"
        self._session.dirty = False
        self._session.last_operation = "save"
        self._session.last_save_epoch = int(time.time())
        self._session.storage_path = self._session_path(self._session.session_ref)
        self._saved_sessions[self._session.session_ref] = self._intent_snapshot(self._insert_chains)
        self._touch_recent_session("save", promote_to_front=True)
        self._session.last_error_message = ""
        self._publish(
            BridgeEvent(
                category="session",
                emitter=2003,
                metadata={"action": "save", "status": self._session.status, "session_ref": self._session.session_ref},
            )
        )
        return BridgeResult()

    def new_session(self, session_ref: str) -> BridgeResult:
        normalized = self._normalize_session_ref(session_ref)
        if not normalized:
            self._session.last_error_message = "session_ref cannot be empty"
            return BridgeResult(code=3, message="session_ref cannot be empty")
        self._session.session_ref = normalized
        self._session.status = "idle"
        self._session.phase = "new"
        self._session.dirty = False
        self._session.storage_source = "fallback-memory"
        self._session.storage_path = self._session_path(normalized)
        self._session.last_operation = "new"
        self._session.last_error_message = ""
        self._insert_chains = {}
        self._reconcile_status = ReconcileStatus()
        self._publish(
            BridgeEvent(
                category="session",
                emitter=2003,
                metadata={"action": "new", "status": self._session.status, "session_ref": self._session.session_ref},
            )
        )
        return BridgeResult()

    def open_session(self, session_ref: str) -> BridgeResult:
        normalized = self._normalize_session_ref(session_ref)
        if not normalized:
            self._session.last_error_message = "session_ref cannot be empty"
            return BridgeResult(code=3, message="session_ref cannot be empty")
        self._session.session_ref = normalized
        self._session.storage_path = self._session_path(normalized)
        load_result = self.load_session()
        if not load_result.ok:
            return load_result
        return self.apply_session()

    def load_session(self) -> BridgeResult:
        if self._session.session_ref not in self._saved_sessions:
            self._session.last_error_message = "session not found"
            return BridgeResult(code=2, message="session not found")
        self._session.status = "loaded"
        self._session.phase = "loaded"
        self._session.dirty = False
        self._session.last_operation = "load"
        self._session.last_load_epoch = int(time.time())
        self._session.storage_path = self._session_path(self._session.session_ref)
        self._insert_chains = deepcopy(self._saved_sessions[self._session.session_ref])
        for chain in self._insert_chains.values():
            self._evaluate_runtime_state(chain)
        self._reconcile_status.policy_mode = "auto_after_load_apply"
        self._reconcile_status.policy_action = "session_load"
        self.reconcile_all_inserts()
        self._touch_recent_session("load", promote_to_front=True)
        self._session.last_error_message = ""
        self._publish(
            BridgeEvent(
                category="session",
                emitter=2003,
                metadata={"action": "load", "status": self._session.status, "session_ref": self._session.session_ref},
            )
        )
        return BridgeResult()

    def apply_session(self) -> BridgeResult:
        if self._session.session_ref not in self._saved_sessions:
            self._session.last_error_message = "session not found"
            return BridgeResult(code=2, message="session not found")
        self._session.status = "applied"
        self._session.phase = "applied"
        self._session.dirty = False
        self._session.last_operation = "apply"
        self._session.last_apply_epoch = int(time.time())
        self._session.storage_path = self._session_path(self._session.session_ref)
        self._insert_chains = deepcopy(self._saved_sessions[self._session.session_ref])
        for chain in self._insert_chains.values():
            self._evaluate_runtime_state(chain)
        self._reconcile_status.policy_mode = "auto_after_load_apply"
        self._reconcile_status.policy_action = "session_apply"
        self.reconcile_all_inserts()
        if not self._recent_sessions or self._recent_sessions[0].session_ref != self._session.session_ref:
            self._touch_recent_session("apply", promote_to_front=True)
        self._session.last_error_message = ""
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
            last_error_message=self._session.last_error_message,
        )

    def get_recent_sessions(self) -> List[RecentSessionEntry]:
        return [deepcopy(entry) for entry in self._recent_sessions]

    def get_session_storage_root(self) -> str:
        return "fallback://sessions"

    def get_discoverable_sessions(self) -> List[DiscoverableSessionEntry]:
        entries: List[DiscoverableSessionEntry] = []
        for session_ref in sorted(self._saved_sessions.keys()):
            entries.append(
                DiscoverableSessionEntry(
                    session_ref=session_ref,
                    storage_path=self._session_path(session_ref),
                    last_modified_epoch=0,
                )
            )
        return entries

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
        selected_slot = None
        for chain in self._insert_chains.values():
            selected_slot = next((slot for slot in chain if slot.plugin_id), None)
            if selected_slot is not None:
                break
        return RuntimeStatus(
            runtime_started=self._runtime_started,
            bridge_version=self.bridge_version(),
            backend_name="fallback_stub",
            supports_create=True,
            supports_destroy=True,
            supports_query=True,
            support_scope_summary="midas.*",
            catalog_source_label="fallback",
            catalog_source_version="1",
            catalog_descriptor_count=len(self._plugin_registry),
            catalog_valid_descriptor_count=sum(1 for entry in self._plugin_registry if entry.available),
            catalog_policy_supported_descriptor_count=sum(
                1
                for entry in self._plugin_registry
                if entry.plugin_id.startswith("midas.")
            ),
            selected_slot_plugin_id=selected_slot.plugin_id if selected_slot is not None else "",
            selected_slot_index=selected_slot.slot_index if selected_slot is not None else 0,
            selected_slot_adapter_reason_code=(
                selected_slot.managed_instance_adapter_reason_code if selected_slot is not None else ""
            ),
            selected_slot_adapter_message=(
                selected_slot.managed_instance_message if selected_slot is not None else ""
            ),
            selected_slot_loader_reason_code=(
                selected_slot.loader_reason_code if selected_slot is not None else ""
            ),
            selected_slot_loader_message=selected_slot.loader_message if selected_slot is not None else "",
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
                runtime_message=slot.runtime_message,
                host_lifecycle_state=slot.host_lifecycle_state,
                host_message=slot.host_message,
                placeholder_instance_id=slot.placeholder_instance_id,
                placeholder_created_sequence=slot.placeholder_created_sequence,
                managed_instance_id=slot.managed_instance_id,
                managed_instance_state=slot.managed_instance_state,
                managed_instance_adapter_state=slot.managed_instance_adapter_state,
                managed_instance_adapter_reason_code=slot.managed_instance_adapter_reason_code,
                managed_instance_message=slot.managed_instance_message,
                managed_instance_created_sequence=slot.managed_instance_created_sequence,
                managed_instance_backend_name=slot.managed_instance_backend_name,
                managed_instance_backend_handle=slot.managed_instance_backend_handle,
                managed_instance_handle_state=slot.managed_instance_handle_state,
                managed_instance_terminal=slot.managed_instance_terminal,
                managed_instance_retryable=slot.managed_instance_retryable,
                managed_instance_reason_source=slot.managed_instance_reason_source,
                managed_instance_loader_strategy=slot.managed_instance_loader_strategy,
                managed_instance_validator_path=slot.managed_instance_validator_path,
                managed_instance_failure_attribution=slot.managed_instance_failure_attribution,
                managed_instance_descriptor_id=slot.managed_instance_descriptor_id,
                managed_instance_descriptor_kind=slot.managed_instance_descriptor_kind,
                managed_instance_descriptor_ref=slot.managed_instance_descriptor_ref,
                loader_outcome=slot.loader_outcome,
                loader_reason_code=slot.loader_reason_code,
                loader_message=slot.loader_message,
            )
            for slot in self._insert_chains.get(int(channel_id), [])
        ]

    def get_managed_instances(self) -> List[ManagedInstanceRecord]:
        instances: List[ManagedInstanceRecord] = []
        for channel_id, slots in self._insert_chains.items():
            for slot in slots:
                if not slot.managed_instance_id:
                    continue
                instances.append(
                    ManagedInstanceRecord(
                        managed_instance_id=slot.managed_instance_id,
                        plugin_id=slot.plugin_id,
                        channel_id=channel_id,
                        slot_index=slot.slot_index,
                        placeholder_instance_id=slot.placeholder_instance_id,
                        managed_instance_state=slot.managed_instance_state,
                        managed_instance_adapter_state=slot.managed_instance_adapter_state,
                        managed_instance_adapter_reason_code=slot.managed_instance_adapter_reason_code,
                        managed_instance_message=slot.managed_instance_message,
                        managed_instance_created_sequence=slot.managed_instance_created_sequence,
                        managed_instance_backend_name=slot.managed_instance_backend_name,
                        managed_instance_backend_handle=slot.managed_instance_backend_handle,
                        managed_instance_handle_state=slot.managed_instance_handle_state,
                        managed_instance_terminal=slot.managed_instance_terminal,
                        managed_instance_retryable=slot.managed_instance_retryable,
                        managed_instance_reason_source=slot.managed_instance_reason_source,
                        managed_instance_loader_strategy=slot.managed_instance_loader_strategy,
                        managed_instance_validator_path=slot.managed_instance_validator_path,
                        managed_instance_failure_attribution=slot.managed_instance_failure_attribution,
                        managed_instance_descriptor_id=slot.managed_instance_descriptor_id,
                        managed_instance_descriptor_kind=slot.managed_instance_descriptor_kind,
                        managed_instance_descriptor_ref=slot.managed_instance_descriptor_ref,
                    )
                )
        instances.sort(key=lambda item: (item.channel_id, item.slot_index))
        return instances

    def get_managed_instance_history(self) -> List[ManagedInstanceTransitionRecord]:
        return []

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
                    load_state="loaded",
                    runtime_message="plugin ready",
                    host_lifecycle_state="not_requested",
                    host_message="",
                    placeholder_instance_id="",
                    placeholder_created_sequence=0,
                    managed_instance_id="",
                    managed_instance_state="unloaded",
                    managed_instance_adapter_state="unavailable",
                    managed_instance_adapter_reason_code="",
                    managed_instance_message="",
                    managed_instance_created_sequence=0,
                    managed_instance_backend_name="",
                    managed_instance_backend_handle="",
                    managed_instance_handle_state="unavailable",
                    managed_instance_terminal=False,
                    managed_instance_retryable=True,
                    managed_instance_reason_source="none",
                    managed_instance_loader_strategy="default_loader",
                    managed_instance_validator_path="default_validator",
                    managed_instance_failure_attribution="none",
                    managed_instance_descriptor_id="",
                    managed_instance_descriptor_kind="",
                    managed_instance_descriptor_ref="",
                    loader_outcome="",
                    loader_reason_code="",
                    loader_message="",
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
                    load_state="loaded",
                    runtime_message="plugin ready",
                    host_lifecycle_state="not_requested",
                    host_message="",
                    placeholder_instance_id="",
                    placeholder_created_sequence=0,
                    managed_instance_id="",
                    managed_instance_state="unloaded",
                    managed_instance_adapter_state="unavailable",
                    managed_instance_adapter_reason_code="",
                    managed_instance_message="",
                    managed_instance_created_sequence=0,
                    managed_instance_backend_name="",
                    managed_instance_backend_handle="",
                    managed_instance_handle_state="unavailable",
                    managed_instance_terminal=False,
                    managed_instance_retryable=True,
                    managed_instance_reason_source="none",
                    managed_instance_loader_strategy="default_loader",
                    managed_instance_validator_path="default_validator",
                    managed_instance_failure_attribution="none",
                    managed_instance_descriptor_id="",
                    managed_instance_descriptor_kind="",
                    managed_instance_descriptor_ref="",
                    loader_outcome="",
                    loader_reason_code="",
                    loader_message="",
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
        result = BridgeResult()
        self._apply_live_reconcile_policy("insert_plugin", channel_id, result, immediate=True)
        return result

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
        result = BridgeResult()
        self._apply_live_reconcile_policy("remove_plugin", channel_id, result, immediate=True)
        return result

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
        result = BridgeResult()
        self._apply_live_reconcile_policy("move_plugin", channel_id, result, immediate=False)
        return result

    def set_plugin_bypass(self, channel_id: int, slot_index: int, bypassed: bool) -> BridgeResult:
        channel_id = int(channel_id)
        slot_index = int(slot_index)
        chain = self._insert_chains.get(channel_id, [])
        slot = next((item for item in chain if item.slot_index == slot_index), None)
        if slot is None:
            return BridgeResult(code=2, message="plugin slot not found")
        slot.bypassed = bool(bypassed)
        self._evaluate_runtime_state([slot])
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
        result = BridgeResult()
        self._apply_live_reconcile_policy("set_plugin_bypass", channel_id, result, immediate=False)
        return result

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
        result = BridgeResult()
        self._apply_live_reconcile_policy("clear_insert_chain", channel_id, result, immediate=False)
        return result

    def set_channel_insert_bypass(self, channel_id: int, bypassed: bool) -> BridgeResult:
        channel_id = int(channel_id)
        chain = self._insert_chains.get(channel_id, [])
        for slot in chain:
            slot.bypassed = bool(bypassed)
        self._evaluate_runtime_state(chain)
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
        result = BridgeResult()
        self._apply_live_reconcile_policy("set_channel_insert_bypass", channel_id, result, immediate=False)
        return result

    def refresh_insert_runtime_state(self, channel_id: int) -> BridgeResult:
        channel_id = int(channel_id)
        chain = self._insert_chains.get(channel_id, [])
        self._evaluate_runtime_state(chain)
        self._publish(
            BridgeEvent(
                category="mixer",
                emitter=2001,
                metadata={"action": "refresh_insert_runtime_state", "channel": str(channel_id)},
            )
        )
        return BridgeResult()

    def request_insert_load(self, channel_id: int, slot_index: int) -> BridgeResult:
        channel_id = int(channel_id)
        slot_index = int(slot_index)
        chain = self._insert_chains.get(channel_id, [])
        slot = next((item for item in chain if item.slot_index == slot_index), None)
        if slot is None:
            return BridgeResult(code=2, message="plugin slot not found")
        slot.host_lifecycle_state = "load_requested"
        slot.host_message = "load requested"
        if slot.load_state == "loaded":
            slot.host_lifecycle_state = "loaded_placeholder"
            slot.host_message = "placeholder loaded"
            if not slot.placeholder_instance_id:
                seq = self._next_placeholder_sequence
                self._next_placeholder_sequence += 1
                slot.placeholder_instance_id = f"ph-{seq}"
                slot.placeholder_created_sequence = seq
            if not slot.managed_instance_id:
                seq = self._next_managed_instance_sequence
                self._next_managed_instance_sequence += 1
                slot.managed_instance_id = f"stub-{seq}"
                slot.managed_instance_created_sequence = seq
            slot.managed_instance_state = "created"
            slot.managed_instance_adapter_state = "created"
            slot.managed_instance_adapter_reason_code = "created"
            slot.managed_instance_message = "adapter stub created"
            slot.managed_instance_backend_name = "fallback_stub"
            slot.managed_instance_backend_handle = f"fallback-handle-{slot.managed_instance_id}"
            slot.managed_instance_handle_state = "active"
            slot.managed_instance_terminal = False
            slot.managed_instance_retryable = True
            slot.managed_instance_reason_source = "adapter"
            slot.managed_instance_loader_strategy = (
                "builtin_graph_loader"
                if slot.plugin_id.startswith("midas.")
                else "partner_bundle_loader" if slot.plugin_id.startswith("partnerlabs.") else "default_loader"
            )
            slot.managed_instance_validator_path = (
                "builtin_graph_validator"
                if slot.plugin_id.startswith("midas.")
                else "partner_bundle_validator" if slot.plugin_id.startswith("partnerlabs.") else "default_validator"
            )
            slot.managed_instance_failure_attribution = "adapter_runtime"
            slot.managed_instance_descriptor_id = f"fallback.{slot.plugin_id}"
            slot.managed_instance_descriptor_kind = "fallback_builtin"
            slot.managed_instance_descriptor_ref = f"fallback://{slot.plugin_id}"
            slot.loader_outcome = "ok"
            slot.loader_reason_code = "resolved"
            slot.loader_message = "plugin resolved and placeholder created"
        else:
            slot.host_lifecycle_state = "load_failed"
            slot.host_message = slot.runtime_message or "runtime not loadable"
            slot.placeholder_instance_id = ""
            slot.placeholder_created_sequence = 0
            slot.managed_instance_id = ""
            slot.managed_instance_state = "create_failed"
            slot.managed_instance_adapter_state = "unavailable"
            slot.managed_instance_adapter_reason_code = "runtime_not_loadable"
            slot.managed_instance_message = slot.host_message
            slot.managed_instance_created_sequence = 0
            slot.managed_instance_backend_name = ""
            slot.managed_instance_backend_handle = ""
            slot.managed_instance_handle_state = "unavailable"
            slot.managed_instance_terminal = False
            slot.managed_instance_retryable = True
            slot.managed_instance_reason_source = "loader"
            slot.managed_instance_loader_strategy = "default_loader"
            slot.managed_instance_validator_path = "default_validator"
            slot.managed_instance_failure_attribution = "loader"
            slot.managed_instance_descriptor_id = ""
            slot.managed_instance_descriptor_kind = ""
            slot.managed_instance_descriptor_ref = ""
            slot.loader_outcome = "unavailable"
            slot.loader_reason_code = "runtime_not_loadable"
            slot.loader_message = slot.host_message
        self._publish(
            BridgeEvent(
                category="mixer",
                emitter=2001,
                metadata={"action": "request_insert_load", "channel": str(channel_id), "slot": str(slot_index)},
            )
        )
        result = BridgeResult()
        if not self._in_reconcile:
            self._apply_live_reconcile_policy("request_insert_load", channel_id, result, immediate=True)
        return result

    def request_insert_unload(self, channel_id: int, slot_index: int) -> BridgeResult:
        channel_id = int(channel_id)
        slot_index = int(slot_index)
        chain = self._insert_chains.get(channel_id, [])
        slot = next((item for item in chain if item.slot_index == slot_index), None)
        if slot is None:
            return BridgeResult(code=2, message="plugin slot not found")
        slot.host_lifecycle_state = "unload_requested"
        slot.host_message = "unload requested"
        slot.host_lifecycle_state = "unloaded"
        slot.host_message = "placeholder unloaded"
        slot.placeholder_instance_id = ""
        slot.placeholder_created_sequence = 0
        slot.managed_instance_id = ""
        slot.managed_instance_state = "unloaded"
        slot.managed_instance_adapter_state = "destroyed"
        slot.managed_instance_adapter_reason_code = "destroyed"
        slot.managed_instance_message = "adapter stub destroyed"
        slot.managed_instance_created_sequence = 0
        slot.managed_instance_backend_name = ""
        slot.managed_instance_backend_handle = ""
        slot.managed_instance_handle_state = "destroyed"
        slot.managed_instance_terminal = True
        slot.managed_instance_retryable = True
        slot.managed_instance_reason_source = "adapter"
        slot.managed_instance_loader_strategy = "default_loader"
        slot.managed_instance_validator_path = "default_validator"
        slot.managed_instance_failure_attribution = "adapter_runtime"
        slot.managed_instance_descriptor_id = ""
        slot.managed_instance_descriptor_kind = ""
        slot.managed_instance_descriptor_ref = ""
        slot.loader_outcome = "ok"
        slot.loader_reason_code = "unloaded"
        slot.loader_message = "placeholder unloaded"
        self._publish(
            BridgeEvent(
                category="mixer",
                emitter=2001,
                metadata={"action": "request_insert_unload", "channel": str(channel_id), "slot": str(slot_index)},
            )
        )
        result = BridgeResult()
        if not self._in_reconcile:
            self._apply_live_reconcile_policy("request_insert_unload", channel_id, result, immediate=True)
        return result

    def reconcile_channel_inserts(self, channel_id: int) -> BridgeResult:
        self._reconcile_status.policy_mode = "manual"
        self._reconcile_status.policy_action = "reconcile_channel_inserts"
        return self._reconcile([int(channel_id)])

    def reconcile_all_inserts(self) -> BridgeResult:
        channels = sorted(self._insert_chains.keys())
        if not channels:
            channels = [1]
        if self._reconcile_status.policy_mode == "none":
            self._reconcile_status.policy_mode = "manual"
            self._reconcile_status.policy_action = "reconcile_all_inserts"
        return self._reconcile(channels)

    def get_reconcile_status(self) -> ReconcileStatus:
        return deepcopy(self._reconcile_status)

    @staticmethod
    def _evaluate_runtime_state(chain: List[InsertedPluginSlot]) -> None:
        for slot in chain:
            if not slot.plugin_id:
                slot.load_state = "unloaded"
                slot.runtime_message = "slot is empty"
            elif not slot.available:
                slot.load_state = "unavailable"
                slot.runtime_message = "plugin unavailable"
            elif "fail" in slot.plugin_id:
                slot.load_state = "failed"
                slot.runtime_message = "plugin runtime evaluation failed"
            else:
                slot.load_state = "loaded"
                slot.runtime_message = "plugin ready"

    @staticmethod
    def _intent_snapshot(chains: Dict[int, List[InsertedPluginSlot]]) -> Dict[int, List[InsertedPluginSlot]]:
        snapshot: Dict[int, List[InsertedPluginSlot]] = {}
        for channel_id, chain in chains.items():
            copied: List[InsertedPluginSlot] = []
            for slot in chain:
                copied.append(
                    InsertedPluginSlot(
                        channel_id=slot.channel_id,
                        slot_index=slot.slot_index,
                        plugin_id=slot.plugin_id,
                        plugin_name=slot.plugin_name,
                        available=slot.available,
                        bypassed=slot.bypassed,
                        load_state="unloaded",
                        runtime_message="",
                        host_lifecycle_state="not_requested",
                        host_message="",
                        placeholder_instance_id="",
                        placeholder_created_sequence=0,
                        managed_instance_id="",
                        managed_instance_state="unloaded",
                        managed_instance_adapter_state="unavailable",
                        managed_instance_adapter_reason_code="",
                        managed_instance_message="",
                        managed_instance_created_sequence=0,
                        managed_instance_backend_name="",
                        managed_instance_backend_handle="",
                        managed_instance_handle_state="unavailable",
                        managed_instance_terminal=False,
                        managed_instance_retryable=True,
                        managed_instance_reason_source="none",
                        managed_instance_loader_strategy="default_loader",
                        managed_instance_validator_path="default_validator",
                        managed_instance_failure_attribution="none",
                        managed_instance_descriptor_id="",
                        managed_instance_descriptor_kind="",
                        managed_instance_descriptor_ref="",
                        loader_outcome="",
                        loader_reason_code="",
                        loader_message="",
                    )
                )
            snapshot[channel_id] = copied
        return snapshot

    def _reconcile(self, channels: List[int]) -> BridgeResult:
        policy_mode = self._reconcile_status.policy_mode
        policy_action = self._reconcile_status.policy_action
        previous = {
            channel_id: {slot.slot_index: slot.placeholder_instance_id for slot in slots if slot.placeholder_instance_id}
            for channel_id, slots in self._insert_chains.items()
        }

        self._reconcile_status = ReconcileStatus()
        self._reconcile_status.policy_mode = policy_mode
        self._reconcile_status.policy_action = policy_action
        self._reconcile_status.channels_scanned = len(channels)
        self._in_reconcile = True
        try:
            for channel_id in channels:
                self.refresh_insert_runtime_state(channel_id)
                chain = self._insert_chains.get(channel_id, [])
                self._reconcile_status.slots_scanned += len(chain)
                for slot in chain:
                    if not slot.plugin_id:
                        continue
                    if slot.host_lifecycle_state == "unloaded":
                        continue
                    self._reconcile_status.attempted += 1
                    self.request_insert_load(channel_id, slot.slot_index)
                    if slot.loader_outcome == "ok":
                        self._reconcile_status.resolved += 1
                    else:
                        self._reconcile_status.failed += 1
                before = previous.get(channel_id, {})
                after = {
                    slot.slot_index: slot.placeholder_instance_id
                    for slot in chain
                    if slot.placeholder_instance_id
                }
                for slot_index, placeholder_id in before.items():
                    if slot_index not in after or after.get(slot_index) != placeholder_id:
                        self._reconcile_status.cleared += 1
                for slot_index, placeholder_id in after.items():
                    if slot_index not in before and placeholder_id:
                        self._reconcile_status.created += 1
        finally:
            self._in_reconcile = False

        self._reconcile_status.last_message = "ok"
        self._reconcile_status.pending_manual_reconcile = False
        self._publish(
            BridgeEvent(
                category="session",
                emitter=2003,
                metadata={
                    "action": "reconcile_inserts",
                    "attempted": str(self._reconcile_status.attempted),
                    "resolved": str(self._reconcile_status.resolved),
                    "failed": str(self._reconcile_status.failed),
                    "created": str(self._reconcile_status.created),
                    "cleared": str(self._reconcile_status.cleared),
                },
            )
        )
        return BridgeResult()

    def _apply_live_reconcile_policy(self, action: str, channel_id: int, result: BridgeResult, immediate: bool) -> None:
        self._reconcile_status.policy_action = action
        if not result.ok:
            self._reconcile_status.policy_mode = "none"
            return
        if immediate:
            self._reconcile_status.policy_mode = "immediate"
            self._reconcile([int(channel_id)])
            return
        self._reconcile_status.policy_mode = "manual_recommended"
        self._reconcile_status.pending_manual_reconcile = True
        self._reconcile_status.last_message = "manual reconcile recommended"

    def _mark_session_modified(self) -> None:
        self._session.status = "modified"
        self._session.phase = "modified"
        self._session.dirty = True
        self._session.last_operation = "modify"
        self._session.storage_path = self._session_path(self._session.session_ref)

    @staticmethod
    def _normalize_session_ref(session_ref: str) -> str:
        cleaned = "".join("_" if ch in "\\/:*?\"<>|" else ch for ch in session_ref.strip())
        return cleaned

    @staticmethod
    def _session_path(session_ref: str) -> str:
        return f"fallback://{session_ref}"

    def _touch_recent_session(self, action: str, promote_to_front: bool) -> None:
        path = self._session_path(self._session.session_ref)
        self._recent_sessions = [
            entry
            for entry in self._recent_sessions
            if entry.session_ref != self._session.session_ref and entry.storage_path != path
        ]
        entry = RecentSessionEntry(
            session_ref=self._session.session_ref,
            storage_path=path,
            storage_source=self._session.storage_source,
            last_operation=action,
            last_touched_epoch=int(time.time()),
        )
        if promote_to_front or not self._recent_sessions:
            self._recent_sessions.insert(0, entry)
        else:
            self._recent_sessions.append(entry)
        self._recent_sessions = self._recent_sessions[:5]

    def _publish(self, event: BridgeEvent) -> None:
        self._events.append(event)
        for callback in list(self._callbacks.values()):
            callback(event)
