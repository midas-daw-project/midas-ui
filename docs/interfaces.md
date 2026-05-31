# Interfaces

## Bridge API (Phase 1)

`bridge/protocol.py` is the local source of truth for the Python UI bridge surface. The fallback bridge should support every method needed for normal frontend development. The native bridge should expose the same UI-facing behavior when `midas_bridge_native` is available.

- `bridge_version()`
- `start_default_runtime_profile()`
- `shutdown_runtime_profile()`
- `init_audio(device_id, sample_rate, buffer_size)`
- `open_audio()`
- `start_audio(track_channel, mixer_subsystem)`
- `stop_audio()`
- `close_audio()`
- `get_audio_status()`
- `drain_recent_events(max_events)`
- `subscribe_events(callback)`
- `unsubscribe_events(handle)`
- `get_mixer_channels()`
- `set_channel_mute(channel_id, muted)`
- `set_channel_gain(channel_id, gain)`
- `new_session(session_ref)`
- `open_session(session_ref)`
- `save_session()`
- `load_session()`
- `apply_session()`
- `get_session_status()`
- `get_recent_sessions()`
- `get_session_storage_root()`
- `get_discoverable_sessions()`
- `play_transport(track_channel, mixer_subsystem)`
- `stop_transport()`
- `get_transport_status()`
- `get_runtime_status()`
- `get_plugin_registry()`
- `refresh_plugin_registry()`
- `get_insert_chain(channel_id)`
- `insert_plugin(channel_id, plugin_id, slot_index)`
- `remove_plugin(channel_id, slot_index)`
- `move_plugin(channel_id, from_slot_index, to_slot_index)`
- `set_plugin_bypass(channel_id, slot_index, bypassed)`
- `set_channel_insert_bypass(channel_id, bypassed)`
- `clear_insert_chain(channel_id)`
- `request_insert_load(channel_id, slot_index)`
- `request_insert_unload(channel_id, slot_index)`
- `reconcile_channel_inserts(channel_id)`
- `reconcile_all_inserts()`
- `get_reconcile_status()`

`get_transport_status()` exposes control/runtime alignment fields:
- `play_state` (control intent)
- `runtime_active` (backend runtime truth)
- `audio_lifecycle_state` (audio subsystem lifecycle)
- `render_status` / `render_produced` (render path truth)

Session restore rule:
- `load_session()` restores persisted intent.
- `apply_session()` plus a follow-up query hydrates runtime-facing truth.
- Runtime/load state, host lifecycle, placeholder identity, and managed instance identity are not persisted session truth.

## Controller Contract

`AudioController` owns:
- runtime profile lifecycle
- audio lifecycle command dispatch
- status refresh and ViewModel updates

`WorkspaceController` owns:
- central workspace overview aggregation
- bridge identity display state
- session/runtime/transport/mixer summary refresh

`BrowserController` owns:
- plugin registry load/refresh
- selected plugin detail state
- browser-facing error/refresh status

`MixerController` now also owns:
- insert-chain query for selected channel
- plugin insert/remove command dispatch

## Result Mapping

- `code == 0`: success
- `code != 0`: operation failed

Controllers write user-visible failures into ViewModel state for panel rendering.
