from __future__ import annotations

import atexit
from typing import Callable, Dict

from bridge.protocol import (
    AudioStatus,
    BridgeClient,
    BridgeEvent,
    InsertedPluginSlot,
    ManagedInstanceRecord,
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


class NativeBridgeClient(BridgeClient):
    """Thin Python wrapper over the compiled native bridge module."""

    def __init__(self) -> None:
        try:
            import midas_bridge_native as native_module  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "Native bridge module 'midas_bridge_native' is unavailable. "
                "Build/install the binding module (MIDAS_BUILD_PYTHON_NATIVE_MODULE=ON) "
                "with matching PYTHON_EXECUTABLE, or unset MIDAS_UI_USE_NATIVE_BRIDGE."
            ) from exc
        self._native = native_module
        self._handles: Dict[int, int] = {}
        self._next_local_handle = 1
        self._plugin_registry_cache: list[PluginRegistryEntry] = [
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
        ]
        self._insert_chain_cache: dict[int, list[InsertedPluginSlot]] = {}
        self._next_placeholder_sequence = 1
        self._reconcile_status = ReconcileStatus()
        self._in_reconcile = False
        atexit.register(self._shutdown_dispatcher)

    def bridge_version(self) -> int:
        return int(self._native.bridge_version())

    def start_default_runtime_profile(self) -> BridgeResult:
        return _to_result(self._native.start_default_runtime_profile())

    def shutdown_runtime_profile(self) -> BridgeResult:
        return _to_result(self._native.shutdown_runtime_profile())

    def init_audio(self, device_id: str, sample_rate: int, buffer_size: int) -> BridgeResult:
        return _to_result(self._native.init_audio(device_id, sample_rate, buffer_size))

    def open_audio(self) -> BridgeResult:
        return _to_result(self._native.open_audio())

    def start_audio(self, track_channel: int, mixer_subsystem: int) -> BridgeResult:
        return _to_result(self._native.start_audio(track_channel, mixer_subsystem))

    def stop_audio(self) -> BridgeResult:
        return _to_result(self._native.stop_audio())

    def close_audio(self) -> BridgeResult:
        return _to_result(self._native.close_audio())

    def get_audio_status(self) -> AudioStatus:
        raw = self._native.get_audio_status()
        return AudioStatus(
            state=str(raw.get("state", "idle")),
            device_id=str(raw.get("device_id", "")),
            sample_rate=int(raw.get("sample_rate", 0)),
            buffer_size=int(raw.get("buffer_size", 0)),
            render_status=str(raw.get("render_status", "stopped")),
            render_produced=bool(raw.get("render_produced", False)),
            render_frames_produced=int(raw.get("render_frames_produced", 0)),
            render_frames_requested=int(raw.get("render_frames_requested", 0)),
            render_channel_count=int(raw.get("render_channel_count", 0)),
            track_channel=int(raw.get("track_channel", 0)),
            tracked_muted=bool(raw.get("tracked_muted", False)),
            tracked_gain=float(raw.get("tracked_gain", 1.0)),
        )

    def drain_recent_events(self, max_events: int) -> list[BridgeEvent]:
        raw_events = self._native.drain_recent_events(max_events)
        events: list[BridgeEvent] = []
        for item in raw_events:
            events.append(
                BridgeEvent(
                    category=str(item.get("category", "unknown")),
                    emitter=int(item.get("emitter", 0)),
                    metadata=dict(item.get("metadata", {})),
                )
            )
        return events

    def subscribe_events(self, callback: Callable[[BridgeEvent], None]) -> int:
        def _wrapped(raw: dict) -> None:
            event = BridgeEvent(
                category=str(raw.get("category", "unknown")),
                emitter=int(raw.get("emitter", 0)),
                metadata=dict(raw.get("metadata", {})),
            )
            callback(event)

        native_handle = int(self._native.subscribe_events(_wrapped))
        local_handle = self._next_local_handle
        self._next_local_handle += 1
        self._handles[local_handle] = native_handle
        return local_handle

    def unsubscribe_events(self, handle: int) -> None:
        native_handle = self._handles.pop(handle, None)
        if native_handle is None:
            return
        self._native.unsubscribe_events(native_handle)

    def get_mixer_channels(self) -> list[MixerChannelStatus]:
        raw_channels = self._native.get_mixer_channels()
        channels: list[MixerChannelStatus] = []
        for item in raw_channels:
            values = dict(item.get("values", {}))
            channels.append(
                MixerChannelStatus(
                    channel_id=int(values.get("channel", "1")),
                    muted=str(values.get("muted", "false")).lower() == "true",
                    gain=float(values.get("gain", "1.0")),
                )
            )
        return channels

    def set_channel_mute(self, channel_id: int, muted: bool) -> BridgeResult:
        return _to_result(self._native.set_channel_mute(channel_id, bool(muted)))

    def set_channel_gain(self, channel_id: int, gain: float) -> BridgeResult:
        return _to_result(self._native.set_channel_gain(channel_id, float(gain)))

    def save_session(self) -> BridgeResult:
        return _to_result(self._native.save_session())

    def new_session(self, session_ref: str) -> BridgeResult:
        return _to_result(self._native.new_session(session_ref))

    def open_session(self, session_ref: str) -> BridgeResult:
        result = _to_result(self._native.open_session(session_ref))
        if result.ok:
            self._reconcile_status = self.get_reconcile_status()
        return result

    def load_session(self) -> BridgeResult:
        result = _to_result(self._native.load_session())
        if result.ok:
            self._reconcile_status = self.get_reconcile_status()
        return result

    def apply_session(self) -> BridgeResult:
        result = _to_result(self._native.apply_session())
        if result.ok:
            self._reconcile_status = self.get_reconcile_status()
        return result

    def get_session_status(self) -> SessionStatus:
        raw = self._native.get_session_status()
        values = dict(raw.get("values", {}))
        def _as_int(key: str, fallback: int = 0) -> int:
            try:
                return int(values.get(key, str(fallback)))
            except (TypeError, ValueError):
                return fallback

        return SessionStatus(
            status=str(values.get("status", "idle")),
            session_ref=str(values.get("session_ref", "default-session")),
            phase=str(values.get("session_phase", "none")),
            dirty=str(values.get("session_dirty", "false")).lower() in {"1", "true", "yes", "on"},
            storage_path=str(values.get("storage_path", "")),
            storage_source=str(values.get("storage_source", "")),
            last_operation=str(values.get("last_operation", "none")),
            last_save_epoch=_as_int("last_save_epoch", 0),
            last_load_epoch=_as_int("last_load_epoch", 0),
            last_apply_epoch=_as_int("last_apply_epoch", 0),
            last_error_message=str(values.get("last_error_message", "")),
        )

    def get_recent_sessions(self) -> list[RecentSessionEntry]:
        raw_entries = self._native.get_recent_sessions()
        entries: list[RecentSessionEntry] = []
        for item in raw_entries:
            values = dict(item.get("values", {}))
            entries.append(
                RecentSessionEntry(
                    session_ref=str(values.get("session_ref", "")),
                    storage_path=str(values.get("storage_path", "")),
                    storage_source=str(values.get("storage_source", "")),
                    last_operation=str(values.get("last_operation", "none")),
                    last_touched_epoch=int(values.get("last_touched_epoch", 0) or 0),
                )
            )
        return entries

    def get_session_storage_root(self) -> str:
        return str(self._native.get_session_storage_root())

    def get_discoverable_sessions(self) -> list[DiscoverableSessionEntry]:
        raw_entries = self._native.get_discoverable_sessions()
        entries: list[DiscoverableSessionEntry] = []
        for item in raw_entries:
            values = dict(item.get("values", {}))
            entries.append(
                DiscoverableSessionEntry(
                    session_ref=str(values.get("session_ref", "")),
                    storage_path=str(values.get("storage_path", "")),
                    last_modified_epoch=int(values.get("last_modified_epoch", 0) or 0),
                )
            )
        return entries

    def play_transport(self, track_channel: int, mixer_subsystem: int) -> BridgeResult:
        return self.start_audio(track_channel, mixer_subsystem)

    def stop_transport(self) -> BridgeResult:
        return self.stop_audio()

    def get_transport_status(self) -> TransportStatus:
        runtime = self.get_runtime_status()
        return TransportStatus(
            play_state="playing" if runtime.audio.state == "started" else "stopped",
            runtime_active=runtime.audio.state == "started",
            audio_lifecycle_state=runtime.audio.state,
            render_status=runtime.audio.render_status,
            render_produced=runtime.audio.render_produced,
        )

    def get_runtime_status(self) -> RuntimeStatus:
        raw = self._native.get_runtime_status()
        values = dict(raw.get("values", {}))

        def _as_int(key: str, fallback: int = 0) -> int:
            try:
                return int(values.get(key, str(fallback)))
            except (TypeError, ValueError):
                return fallback

        def _as_float(key: str, fallback: float = 0.0) -> float:
            try:
                return float(values.get(key, str(fallback)))
            except (TypeError, ValueError):
                return fallback

        def _as_bool(key: str, fallback: bool = False) -> bool:
            raw_value = str(values.get(key, "true" if fallback else "false")).strip().lower()
            return raw_value in {"1", "true", "yes", "on"}

        audio = AudioStatus(
            state=str(values.get("state", "idle")),
            device_id=str(values.get("device_id", "")),
            sample_rate=_as_int("sample_rate", 0),
            buffer_size=_as_int("buffer_size", 0),
            render_status=str(values.get("render_status", "stopped")),
            render_produced=_as_bool("render_produced", False),
            render_frames_produced=_as_int("render_frames_produced", 0),
            render_frames_requested=_as_int("render_frames_requested", 0),
            render_channel_count=_as_int("render_channel_count", 0),
            track_channel=_as_int("track_channel", 0),
            tracked_muted=_as_bool("muted", False),
            tracked_gain=_as_float("gain", 1.0),
        )
        return RuntimeStatus(
            runtime_started=_as_bool("runtime_started", False),
            bridge_version=_as_int("bridge_version", self.bridge_version()),
            audio=audio,
        )

    def get_plugin_registry(self) -> list[PluginRegistryEntry]:
        if hasattr(self._native, "get_plugin_registry"):
            raw_entries = self._native.get_plugin_registry()
            entries: list[PluginRegistryEntry] = []
            for item in raw_entries:
                values = dict(item.get("values", {}))
                entries.append(
                    PluginRegistryEntry(
                        plugin_id=str(values.get("plugin_id", "")),
                        name=str(values.get("name", "")),
                        category=str(values.get("category", "Unknown")),
                        vendor=str(values.get("vendor", "Unknown")),
                        available=str(values.get("available", "false")).lower() == "true",
                        source=str(values.get("source", "registry")),
                    )
                )
            if entries:
                self._plugin_registry_cache = entries
        return list(self._plugin_registry_cache)

    def refresh_plugin_registry(self) -> BridgeResult:
        if hasattr(self._native, "refresh_plugin_registry"):
            return _to_result(self._native.refresh_plugin_registry())
        self.get_plugin_registry()
        return BridgeResult()

    def get_insert_chain(self, channel_id: int) -> list[InsertedPluginSlot]:
        if hasattr(self._native, "get_insert_chain"):
            raw = self._native.get_insert_chain(int(channel_id))
            slots: list[InsertedPluginSlot] = []
            for item in raw:
                values = dict(item.get("values", {}))
                bypassed = (
                    str(values.get("bypassed", "false")).lower() == "true"
                    or str(values.get("enabled", "true")).lower() == "false"
                )
                slots.append(
                    InsertedPluginSlot(
                        channel_id=int(values.get("channel_id", values.get("channel", str(channel_id)))),
                        slot_index=int(values.get("slot_index", "0")),
                        plugin_id=str(values.get("plugin_id", "")),
                        plugin_name=str(values.get("plugin_name", values.get("plugin_id", ""))),
                        available=str(values.get("available", "false")).lower() == "true",
                        bypassed=bypassed,
                        load_state=str(values.get("load_state", "bypassed" if bypassed else "unloaded")),
                        runtime_message=str(values.get("runtime_status_message", "")),
                        host_lifecycle_state=str(values.get("host_lifecycle_state", "not_requested")),
                        host_message=str(values.get("host_status_message", "")),
                        placeholder_instance_id=str(values.get("placeholder_instance_id", "")),
                        placeholder_created_sequence=int(values.get("placeholder_created_seq", 0) or 0),
                        managed_instance_id=str(values.get("managed_instance_id", "")),
                        managed_instance_state=str(values.get("managed_instance_state", "unloaded")),
                        managed_instance_message=str(values.get("managed_instance_message", "")),
                        managed_instance_created_sequence=int(values.get("managed_instance_created_seq", 0) or 0),
                        loader_outcome=str(values.get("loader_outcome", "")),
                        loader_reason_code=str(values.get("loader_reason_code", "")),
                        loader_message=str(values.get("loader_message", "")),
                    )
                )
            self._insert_chain_cache[int(channel_id)] = slots
        return list(self._insert_chain_cache.get(int(channel_id), []))

    def get_managed_instances(self) -> list[ManagedInstanceRecord]:
        if not hasattr(self._native, "get_managed_instances"):
            return []
        records: list[ManagedInstanceRecord] = []
        for item in self._native.get_managed_instances():
            values = dict(item.get("values", {}))
            records.append(
                ManagedInstanceRecord(
                    managed_instance_id=str(values.get("managed_instance_id", "")),
                    plugin_id=str(values.get("plugin_id", "")),
                    channel_id=int(values.get("channel", 0) or 0),
                    slot_index=int(values.get("slot_index", 0) or 0),
                    placeholder_instance_id=str(values.get("placeholder_instance_id", "")),
                    managed_instance_state=str(values.get("managed_instance_state", "unloaded")),
                    managed_instance_message=str(values.get("managed_instance_message", "")),
                    managed_instance_created_sequence=int(values.get("managed_instance_created_seq", 0) or 0),
                )
            )
        return records

    def insert_plugin(self, channel_id: int, plugin_id: str, slot_index: int) -> BridgeResult:
        if hasattr(self._native, "insert_plugin"):
            result = _to_result(self._native.insert_plugin(int(channel_id), plugin_id, int(slot_index)))
            self._capture_policy_status()
            return result
        plugin = next((p for p in self.get_plugin_registry() if p.plugin_id == plugin_id), None)
        if plugin is None:
            return BridgeResult(code=3, message=f"unknown plugin id: {plugin_id}")
        if not plugin.available:
            return BridgeResult(code=3, message=f"plugin unavailable: {plugin_id}")
        chain = self._insert_chain_cache.setdefault(int(channel_id), [])
        inserted = InsertedPluginSlot(
            channel_id=int(channel_id),
            slot_index=int(slot_index),
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
            loader_outcome="",
            loader_reason_code="",
            loader_message="",
        )
        for i, slot in enumerate(chain):
            if slot.slot_index == int(slot_index):
                chain[i] = inserted
                break
        else:
            chain.append(inserted)
            chain.sort(key=lambda s: s.slot_index)
        result = BridgeResult()
        self._apply_live_reconcile_policy("insert_plugin", int(channel_id), result, immediate=True)
        return result

    def remove_plugin(self, channel_id: int, slot_index: int) -> BridgeResult:
        if hasattr(self._native, "remove_plugin"):
            result = _to_result(self._native.remove_plugin(int(channel_id), int(slot_index)))
            self._capture_policy_status()
            return result
        chain = self._insert_chain_cache.get(int(channel_id), [])
        remaining = [slot for slot in chain if slot.slot_index != int(slot_index)]
        if len(remaining) == len(chain):
            return BridgeResult(code=2, message="plugin slot not found")
        self._insert_chain_cache[int(channel_id)] = remaining
        result = BridgeResult()
        self._apply_live_reconcile_policy("remove_plugin", int(channel_id), result, immediate=True)
        return result

    def move_plugin(self, channel_id: int, from_slot_index: int, to_slot_index: int) -> BridgeResult:
        if hasattr(self._native, "move_plugin"):
            result = _to_result(self._native.move_plugin(int(channel_id), int(from_slot_index), int(to_slot_index)))
            self._capture_policy_status()
            return result
        chain = self._insert_chain_cache.get(int(channel_id), [])
        source = next((slot for slot in chain if slot.slot_index == int(from_slot_index)), None)
        if source is None:
            return BridgeResult(code=2, message="plugin slot not found")
        if int(from_slot_index) != int(to_slot_index):
            dest = next((slot for slot in chain if slot.slot_index == int(to_slot_index)), None)
            source.slot_index = int(to_slot_index)
            if dest is not None and dest is not source:
                dest.slot_index = int(from_slot_index)
            chain.sort(key=lambda s: s.slot_index)
        result = BridgeResult()
        self._apply_live_reconcile_policy("move_plugin", int(channel_id), result, immediate=False)
        return result

    def set_plugin_bypass(self, channel_id: int, slot_index: int, bypassed: bool) -> BridgeResult:
        if hasattr(self._native, "set_plugin_bypass"):
            result = _to_result(self._native.set_plugin_bypass(int(channel_id), int(slot_index), bool(bypassed)))
            self._capture_policy_status()
            return result
        chain = self._insert_chain_cache.get(int(channel_id), [])
        slot = next((item for item in chain if item.slot_index == int(slot_index)), None)
        if slot is None:
            return BridgeResult(code=2, message="plugin slot not found")
        slot.bypassed = bool(bypassed)
        slot.load_state = "loaded" if slot.available else "unavailable"
        slot.runtime_message = "plugin ready" if slot.available else "plugin unavailable"
        result = BridgeResult()
        self._apply_live_reconcile_policy("set_plugin_bypass", int(channel_id), result, immediate=False)
        return result

    def move_plugin_to_top(self, channel_id: int, slot_index: int) -> BridgeResult:
        if hasattr(self._native, "move_plugin_to_top"):
            result = _to_result(self._native.move_plugin_to_top(int(channel_id), int(slot_index)))
            self._capture_policy_status()
            return result
        chain = self._insert_chain_cache.get(int(channel_id), [])
        if not chain:
            return BridgeResult(code=2, message="insert chain is empty")
        target = min(slot.slot_index for slot in chain)
        return self.move_plugin(channel_id, slot_index, target)

    def move_plugin_to_bottom(self, channel_id: int, slot_index: int) -> BridgeResult:
        if hasattr(self._native, "move_plugin_to_bottom"):
            result = _to_result(self._native.move_plugin_to_bottom(int(channel_id), int(slot_index)))
            self._capture_policy_status()
            return result
        chain = self._insert_chain_cache.get(int(channel_id), [])
        if not chain:
            return BridgeResult(code=2, message="insert chain is empty")
        target = max(slot.slot_index for slot in chain)
        return self.move_plugin(channel_id, slot_index, target)

    def clear_insert_chain(self, channel_id: int) -> BridgeResult:
        if hasattr(self._native, "clear_insert_chain"):
            result = _to_result(self._native.clear_insert_chain(int(channel_id)))
            self._capture_policy_status()
            return result
        self._insert_chain_cache[int(channel_id)] = []
        result = BridgeResult()
        self._apply_live_reconcile_policy("clear_insert_chain", int(channel_id), result, immediate=False)
        return result

    def set_channel_insert_bypass(self, channel_id: int, bypassed: bool) -> BridgeResult:
        if hasattr(self._native, "set_channel_insert_bypass"):
            result = _to_result(self._native.set_channel_insert_bypass(int(channel_id), bool(bypassed)))
            self._capture_policy_status()
            return result
        chain = self._insert_chain_cache.get(int(channel_id), [])
        for slot in chain:
            slot.bypassed = bool(bypassed)
            slot.load_state = "loaded" if slot.available else "unavailable"
            slot.runtime_message = "plugin ready" if slot.available else "plugin unavailable"
        result = BridgeResult()
        self._apply_live_reconcile_policy("set_channel_insert_bypass", int(channel_id), result, immediate=False)
        return result

    def refresh_insert_runtime_state(self, channel_id: int) -> BridgeResult:
        if hasattr(self._native, "refresh_insert_runtime_state"):
            return _to_result(self._native.refresh_insert_runtime_state(int(channel_id)))
        chain = self._insert_chain_cache.get(int(channel_id), [])
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
        return BridgeResult()

    def request_insert_load(self, channel_id: int, slot_index: int) -> BridgeResult:
        if hasattr(self._native, "request_insert_load"):
            result = _to_result(self._native.request_insert_load(int(channel_id), int(slot_index)))
            self._capture_policy_status()
            return result
        chain = self._insert_chain_cache.get(int(channel_id), [])
        slot = next((item for item in chain if item.slot_index == int(slot_index)), None)
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
            slot.loader_outcome = "ok"
            slot.loader_reason_code = "resolved"
            slot.loader_message = "plugin resolved and placeholder created"
        else:
            slot.host_lifecycle_state = "load_failed"
            slot.host_message = slot.runtime_message or "runtime not loadable"
            slot.placeholder_instance_id = ""
            slot.placeholder_created_sequence = 0
            slot.loader_outcome = "unavailable"
            slot.loader_reason_code = "runtime_not_loadable"
            slot.loader_message = slot.host_message
        result = BridgeResult()
        if not self._in_reconcile:
            self._apply_live_reconcile_policy("request_insert_load", int(channel_id), result, immediate=True)
        return result

    def request_insert_unload(self, channel_id: int, slot_index: int) -> BridgeResult:
        if hasattr(self._native, "request_insert_unload"):
            result = _to_result(self._native.request_insert_unload(int(channel_id), int(slot_index)))
            self._capture_policy_status()
            return result
        chain = self._insert_chain_cache.get(int(channel_id), [])
        slot = next((item for item in chain if item.slot_index == int(slot_index)), None)
        if slot is None:
            return BridgeResult(code=2, message="plugin slot not found")
        slot.host_lifecycle_state = "unload_requested"
        slot.host_message = "unload requested"
        slot.host_lifecycle_state = "unloaded"
        slot.host_message = "placeholder unloaded"
        slot.placeholder_instance_id = ""
        slot.placeholder_created_sequence = 0
        slot.loader_outcome = "ok"
        slot.loader_reason_code = "unloaded"
        slot.loader_message = "placeholder unloaded"
        result = BridgeResult()
        if not self._in_reconcile:
            self._apply_live_reconcile_policy("request_insert_unload", int(channel_id), result, immediate=True)
        return result

    def reconcile_channel_inserts(self, channel_id: int) -> BridgeResult:
        if hasattr(self._native, "reconcile_channel_inserts"):
            result = _to_result(self._native.reconcile_channel_inserts(int(channel_id)))
            self._reconcile_status = self.get_reconcile_status()
            return result
        self._reconcile_status.policy_mode = "manual"
        self._reconcile_status.policy_action = "reconcile_channel_inserts"
        return self.reconcile_all_inserts()

    def reconcile_all_inserts(self) -> BridgeResult:
        if hasattr(self._native, "reconcile_all_inserts"):
            result = _to_result(self._native.reconcile_all_inserts())
            self._reconcile_status = self.get_reconcile_status()
            return result
        channels = sorted(self._insert_chain_cache.keys()) or [1]
        attempted = resolved = failed = created = cleared = slots_scanned = 0
        before = {
            channel: {slot.slot_index: slot.placeholder_instance_id for slot in slots if slot.placeholder_instance_id}
            for channel, slots in self._insert_chain_cache.items()
        }
        self._in_reconcile = True
        try:
            for channel in channels:
                chain = self._insert_chain_cache.get(channel, [])
                slots_scanned += len(chain)
                for slot in chain:
                    if not slot.plugin_id:
                        continue
                    if slot.host_lifecycle_state == "unloaded":
                        continue
                    attempted += 1
                    self.request_insert_load(channel, slot.slot_index)
                    if slot.loader_outcome == "ok":
                        resolved += 1
                    else:
                        failed += 1
                after = {slot.slot_index: slot.placeholder_instance_id for slot in chain if slot.placeholder_instance_id}
                for slot_index, placeholder_id in before.get(channel, {}).items():
                    if slot_index not in after or after.get(slot_index) != placeholder_id:
                        cleared += 1
                for slot_index, placeholder_id in after.items():
                    if slot_index not in before.get(channel, {}) and placeholder_id:
                        created += 1
        finally:
            self._in_reconcile = False
        self._reconcile_status = ReconcileStatus(
            channels_scanned=len(channels),
            slots_scanned=slots_scanned,
            attempted=attempted,
            resolved=resolved,
            failed=failed,
            created=created,
            cleared=cleared,
            last_message="ok",
            policy_mode="manual",
            policy_action="reconcile_all_inserts",
            pending_manual_reconcile=False,
        )
        return BridgeResult()

    def get_reconcile_status(self) -> ReconcileStatus:
        if hasattr(self._native, "get_reconcile_status"):
            raw = self._native.get_reconcile_status()
            values = dict(raw.get("values", {}))
            return ReconcileStatus(
                channels_scanned=int(values.get("channels_scanned", 0)),
                slots_scanned=int(values.get("slots_scanned", 0)),
                attempted=int(values.get("attempted", 0)),
                resolved=int(values.get("resolved", 0)),
                failed=int(values.get("failed", 0)),
                created=int(values.get("created", 0)),
                cleared=int(values.get("cleared", 0)),
                last_message=str(values.get("last_message", "")),
                policy_mode=str(values.get("policy_mode", "none")),
                policy_action=str(values.get("policy_action", "none")),
                pending_manual_reconcile=str(values.get("pending_manual_reconcile", "false")).lower() == "true",
            )
        return self._reconcile_status

    def _capture_policy_status(self) -> None:
        self._reconcile_status = self.get_reconcile_status()

    def _apply_live_reconcile_policy(self, action: str, channel_id: int, result: BridgeResult, immediate: bool) -> None:
        self._reconcile_status.policy_action = action
        if not result.ok:
            self._reconcile_status.policy_mode = "none"
            return
        if immediate:
            self._reconcile_status.policy_mode = "immediate"
            self.reconcile_channel_inserts(channel_id)
            return
        self._reconcile_status.policy_mode = "manual_recommended"
        self._reconcile_status.pending_manual_reconcile = True
        self._reconcile_status.last_message = "manual reconcile recommended"

    def _shutdown_dispatcher(self) -> None:
        if hasattr(self._native, "shutdown_event_dispatcher"):
            self._native.shutdown_event_dispatcher()


def _to_result(raw: dict) -> BridgeResult:
    return BridgeResult(code=int(raw.get("code", 4)), message=str(raw.get("message", "")))
