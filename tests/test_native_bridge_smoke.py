from pathlib import Path
import importlib.util
import os
import sys
import time


def _resolve_native_module() -> str:
    configured = os.getenv("MIDAS_NATIVE_MODULE_DIR", "").strip()
    if configured:
        base = Path(configured)
    else:
        # Default CMake output path for midas_bridge_native.
        base = Path(__file__).resolve().parents[2] / "build" / "python"
    candidates = [base / "Release", base]
    suffix = f"cp{sys.version_info.major}{sys.version_info.minor}"
    for candidate in candidates:
        if not candidate.exists():
            continue
        for module in candidate.glob(f"midas_bridge_native.{suffix}*.pyd"):
            return str(module)
        for module in candidate.glob("midas_bridge_native*.pyd"):
            return str(module)
    raise FileNotFoundError("midas_bridge_native module binary not found")


def _load_native_module():
    module_path = _resolve_native_module()
    spec = importlib.util.spec_from_file_location("midas_bridge_native", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to create spec for module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    native = _load_native_module()

    assert int(native.bridge_version()) == 1
    assert int(native.start_default_runtime_profile()["code"]) == 0
    assert int(native.init_audio("native-dev", 48000, 256)["code"]) == 0
    assert int(native.open_audio()["code"]) == 0
    assert int(native.start_audio(1, 2001)["code"]) == 0

    status = native.get_audio_status()
    assert status["state"] == "started"
    assert status["render_status"] in {"ok", "no_callback", "partial", "failed", "invalid_runtime_state"}

    deadline = time.time() + 1.0
    events = []
    while not events and time.time() < deadline:
        events = native.drain_recent_events(32)
        if not events:
            time.sleep(0.03)
    assert events

    assert int(native.stop_audio()["code"]) == 0
    assert int(native.close_audio()["code"]) == 0

    plugins = []
    if hasattr(native, "get_plugin_registry"):
        plugins = native.get_plugin_registry()
    assert isinstance(plugins, list)
    assert int(native.insert_plugin(1, "midas.eq.basic", 0)["code"]) == 0
    assert int(native.insert_plugin(1, "midas.comp.basic", 1)["code"]) == 0
    assert int(native.move_plugin(1, 1, 0)["code"]) == 0
    assert int(native.set_plugin_bypass(1, 0, True)["code"]) == 0
    chain = native.get_insert_chain(1)
    assert isinstance(chain, list)
    assert len(chain) >= 1
    assert str(chain[0].get("values", {}).get("plugin_id", "")) == "midas.comp.basic"
    assert str(chain[0].get("values", {}).get("bypassed", "")).lower() == "true"
    assert int(native.save_session()["code"]) == 0
    assert int(native.remove_plugin(1, 0)["code"]) == 0
    assert int(native.load_session()["code"]) == 0

    assert int(native.apply_session()["code"]) == 0
    chain = native.get_insert_chain(1)
    assert len(chain) >= 1
    session_status = native.get_session_status()
    assert int(session_status.get("code", 4)) == 0
    assert str(session_status.get("values", {}).get("status", "")) in {"saved", "loaded", "applied"}

    assert int(native.init_audio("native-dev", 48000, 256)["code"]) == 0
    assert int(native.open_audio()["code"]) == 0
    assert int(native.start_audio(1, 2001)["code"]) == 0
    transport_status = native.get_runtime_status()
    assert int(transport_status.get("code", 4)) == 0
    values = transport_status.get("values", {})
    assert str(values.get("state", "")) in {"started", "opened", "initialized", "idle"}
    assert str(values.get("runtime_started", "")) in {"true", "false"}
    assert str(values.get("render_status", "")) in {"ok", "no_callback", "partial", "failed", "invalid_runtime_state", "stopped"}
    assert int(native.stop_audio()["code"]) == 0
    assert int(native.close_audio()["code"]) == 0

    assert native.get_mixer_channels()
    assert int(native.shutdown_runtime_profile()["code"]) == 0


if __name__ == "__main__":
    main()
