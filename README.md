# MIDAS UI (Phase 1 Shell)

`midas-ui` is the first real-but-plain MIDAS application shell.

Phase 1 goals:
- Keep architecture durable (`widgets -> controllers -> typed bridge`).
- Keep visuals plain and operational.
- Prove one working vertical slice (audio lifecycle + debug telemetry).

Out of scope in phase 1:
- piano roll
- deep automation editing
- plugin host UI depth
- final visual polish

## Quick Start

1. Create a Python 3.11+ virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the test suite:

```bash
python -m pytest tests -q
```

4. Launch the app:

```bash
python -m app.main
```

By default, the app uses the fallback bridge. Set `MIDAS_UI_USE_NATIVE_BRIDGE=1` only after native bindings are available.

## Bridge Modes

### Fallback bridge

Fallback mode is the default development path. It keeps the frontend operatable while backend/native bridge work continues. Use it for panel work, controller/viewmodel tests, local UI flows, and issue-driven frontend development.

```bash
python -m app.main
```

### Native bridge

Native mode loads the compiled `midas_bridge_native` module. Use it only when the backend binding has been built for the same Python environment.

```bash
MIDAS_UI_USE_NATIVE_BRIDGE=1 python -m app.main
```

If native mode cannot import `midas_bridge_native`, unset `MIDAS_UI_USE_NATIVE_BRIDGE` and continue frontend work in fallback mode.

## Development Loop

1. Pick one bounded GitHub issue with a visible user outcome.
2. Read the relevant panel, controller, viewmodel, bridge method, and tests.
3. Keep widgets routed through controllers; widgets should not call the bridge directly.
4. Update fallback bridge behavior when the UI needs local operatable truth.
5. Add focused tests, then run the full suite.
6. Launch fallback mode and manually try the workflow.
7. Open a backend issue only when the UI proves a missing bridge field, method, or machine-readable status.

## Current Frontend Scope

The Phase 1 shell should stay practical and plain:

- workspace status and next actions
- session new/open/save/load/apply
- mixer channel state and insert-chain intent/runtime labels
- plugin browser selection and insertion
- audio lifecycle and transport controls
- debug/event visibility

Do not widen routine frontend issues into piano roll, routing topology, DSP graph execution, binary plugin loading, plugin editor windows, or final visual branding.
