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
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run:

```bash
python -m app.main
```

By default, the app uses the fallback bridge. Set `MIDAS_UI_USE_NATIVE_BRIDGE=1` after native bindings are available.
