# Architecture

## Layering

```text
PySide6 Widgets
  -> Controllers
    -> Typed Bridge API
      -> midas-core facade/contracts
```

Rules:
- Widgets never call bridge methods directly.
- Controllers own command/query/event coordination.
- ViewModels hold UI state only.
- The fallback bridge remains the default frontend development backend.
- Native bridge work must stay additive to the typed bridge boundary.

## Phase 1 Vertical Slice

- Audio lifecycle panel
- Debug/status panel
- Workspace status and session actions
- Mixer channel and insert-chain controls
- Browser, transport, and session panels

Event model:
- Events notify.
- Controllers re-query authoritative state after event receipt.

## Development Boundary

Frontend issues should land in this repository when the work is a panel, controller, viewmodel, fallback bridge, or UI test change.

Create backend issues only for concrete missing seams:

- a missing bridge method or field
- a fallback/native bridge mismatch
- a machine-readable status the UI cannot infer safely
- backend validation needed for a UI-facing contract
