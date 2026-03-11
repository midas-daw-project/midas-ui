from pathlib import Path
import importlib.util
import os
import sys


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

    assert int(native.stop_audio()["code"]) == 0
    assert int(native.close_audio()["code"]) == 0
    assert int(native.shutdown_runtime_profile()["code"]) == 0


if __name__ == "__main__":
    main()
