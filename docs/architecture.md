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

## Phase 1 Vertical Slice

- Audio lifecycle panel
- Debug/status panel
- Workspace placeholder

Event model:
- Events notify.
- Controllers re-query authoritative state after event receipt.
