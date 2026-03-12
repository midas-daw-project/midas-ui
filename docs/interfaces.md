# Interfaces

## Bridge API (Phase 1)

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
- `save_session()`
- `load_session()`
- `apply_session()`
- `get_session_status()`
- `play_transport(track_channel, mixer_subsystem)`
- `stop_transport()`
- `get_transport_status()`
- `get_runtime_status()`
- `get_plugin_registry()`
- `refresh_plugin_registry()`

`get_transport_status()` exposes control/runtime alignment fields:
- `play_state` (control intent)
- `runtime_active` (backend runtime truth)
- `audio_lifecycle_state` (audio subsystem lifecycle)
- `render_status` / `render_produced` (render path truth)

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

## Result Mapping

- `code == 0`: success
- `code != 0`: operation failed

Controllers write user-visible failures into ViewModel state for panel rendering.
