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

## Controller Contract

`AudioController` owns:
- runtime profile lifecycle
- audio lifecycle command dispatch
- status refresh and ViewModel updates

## Result Mapping

- `code == 0`: success
- `code != 0`: operation failed

Controllers write user-visible failures into ViewModel state for panel rendering.
