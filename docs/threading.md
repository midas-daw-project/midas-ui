# Threading

## UI Thread Rules

- All widget updates run on the Qt UI thread.
- Bridge polling for events happens through a UI-thread timer in phase 1.

## Bridge/Event Rules

- The bridge may aggregate backend calls into UI-friendly operations.
- The bridge must not invent domain truth that diverges from shared contracts.
- Event delivery to Python must be marshaled to a UI-safe boundary.
- No Python callback is allowed on realtime-sensitive backend paths.

## Phase 1 Delivery Model

- Push notifications come from `drain_recent_events`.
- Controllers may re-query backend state after events to refresh authoritative state.
