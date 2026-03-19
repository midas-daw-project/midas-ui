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
    assert int(native.new_session("smoke-session")["code"]) == 0
    assert native.get_session_status().get("values", {}).get("session_ref", "") == "smoke-session"
    assert isinstance(native.get_session_storage_root(), str)
    assert int(native.insert_plugin(1, "midas.eq.basic", 0)["code"]) == 0
    assert int(native.save_session()["code"]) == 0
    recent = native.get_recent_sessions()
    assert isinstance(recent, list)
    assert str(recent[0].get("values", {}).get("session_ref", "")) == "smoke-session"
    discoverable = native.get_discoverable_sessions()
    assert isinstance(discoverable, list)
    assert str(discoverable[0].get("values", {}).get("session_ref", "")) == "smoke-session"
    assert int(native.open_session("smoke-session")["code"]) == 0
    assert int(native.insert_plugin(1, "midas.eq.basic", 0)["code"]) == 0
    policy = native.get_reconcile_status().get("values", {})
    assert str(policy.get("policy_mode", "")) == "immediate"
    assert str(policy.get("policy_action", "")) == "insert_plugin"
    assert int(native.insert_plugin(1, "midas.comp.basic", 1)["code"]) == 0
    assert int(native.move_plugin_to_top(1, 1)["code"]) == 0
    policy = native.get_reconcile_status().get("values", {})
    assert str(policy.get("policy_mode", "")) == "manual_recommended"
    assert int(native.set_channel_insert_bypass(1, True)["code"]) == 0
    assert int(native.refresh_insert_runtime_state(1)["code"]) == 0
    assert int(native.request_insert_load(1, 0)["code"]) == 0
    chain = native.get_insert_chain(1)
    assert isinstance(chain, list)
    assert len(chain) >= 1
    assert str(chain[0].get("values", {}).get("plugin_id", "")) == "midas.comp.basic"
    assert str(chain[0].get("values", {}).get("bypassed", "")).lower() == "true"
    assert str(chain[0].get("values", {}).get("runtime_status_message", "")) != ""
    host_state = str(chain[0].get("values", {}).get("host_lifecycle_state", ""))
    assert host_state in {"loaded_placeholder", "load_failed"}
    placeholder_id = str(chain[0].get("values", {}).get("placeholder_instance_id", ""))
    placeholder_seq = str(chain[0].get("values", {}).get("placeholder_created_seq", "0"))
    loader_outcome = str(chain[0].get("values", {}).get("loader_outcome", ""))
    loader_reason = str(chain[0].get("values", {}).get("loader_reason_code", ""))
    initial_managed_id = str(chain[0].get("values", {}).get("managed_instance_id", ""))
    if host_state == "loaded_placeholder":
        assert placeholder_id
        assert int(placeholder_seq) > 0
        assert loader_outcome == "ok"
        assert loader_reason == "resolved"
        assert initial_managed_id != ""
        assert str(chain[0].get("values", {}).get("managed_instance_backend_name", "")) != ""
        assert str(chain[0].get("values", {}).get("managed_instance_backend_handle", "")) != ""
        assert str(chain[0].get("values", {}).get("managed_instance_descriptor_id", "")) != ""
        assert str(chain[0].get("values", {}).get("managed_instance_descriptor_kind", "")) != ""
        assert str(chain[0].get("values", {}).get("managed_instance_descriptor_ref", "")) != ""
        assert str(chain[0].get("values", {}).get("managed_instance_handle_state", "")) == "active"
        assert str(chain[0].get("values", {}).get("managed_instance_terminal", "")).lower() == "false"
        assert str(chain[0].get("values", {}).get("managed_instance_retryable", "")).lower() == "true"
        assert str(chain[0].get("values", {}).get("managed_instance_reason_source", "")) == "adapter"
        assert str(chain[0].get("values", {}).get("managed_instance_state", "")) == "created"
        assert str(chain[0].get("values", {}).get("managed_instance_adapter_state", "")) == "created"
        assert str(chain[0].get("values", {}).get("managed_instance_adapter_reason_code", "")) == "created"
        managed_instances = native.get_managed_instances()
        assert any(str(item.get("values", {}).get("managed_instance_id", "")) == initial_managed_id for item in managed_instances)
        history = native.get_managed_instance_history()
        assert any(str(item.get("values", {}).get("to_adapter_state", "")) == "created" for item in history)
    else:
        assert placeholder_id == ""
        assert int(placeholder_seq) == 0
        assert loader_outcome in {"not_found", "unavailable", "incompatible", "load_not_supported_yet", "internal_error"}
        assert initial_managed_id == ""
    assert int(native.request_insert_unload(1, 0)["code"]) == 0
    chain = native.get_insert_chain(1)
    assert str(chain[0].get("values", {}).get("placeholder_instance_id", "")) == ""
    assert str(chain[0].get("values", {}).get("placeholder_created_seq", "0")) == "0"
    assert str(chain[0].get("values", {}).get("managed_instance_id", "")) == ""
    assert str(chain[0].get("values", {}).get("managed_instance_state", "")) == "unloaded"
    assert str(chain[0].get("values", {}).get("managed_instance_adapter_state", "")) == "destroyed"
    assert str(chain[0].get("values", {}).get("managed_instance_adapter_reason_code", "")) == "destroyed"
    assert str(chain[0].get("values", {}).get("managed_instance_handle_state", "")) == "destroyed"
    assert str(chain[0].get("values", {}).get("managed_instance_terminal", "")).lower() == "true"
    assert str(chain[0].get("values", {}).get("managed_instance_retryable", "")).lower() == "true"
    assert str(chain[0].get("values", {}).get("managed_instance_reason_source", "")) == "adapter"
    assert str(chain[0].get("values", {}).get("loader_outcome", "")) == "ok"
    assert str(chain[0].get("values", {}).get("loader_reason_code", "")) == "unloaded"
    history = native.get_managed_instance_history()
    assert any(str(item.get("values", {}).get("to_adapter_state", "")) == "destroyed" for item in history)
    assert int(native.reconcile_channel_inserts(1)["code"]) == 0
    reconcile = native.get_reconcile_status()
    assert int(reconcile.get("code", 4)) == 0
    rv = reconcile.get("values", {})
    assert int(rv.get("channels_scanned", "0")) >= 1
    assert int(rv.get("attempted", "0")) >= 1
    assert int(native.move_plugin_to_bottom(1, 0)["code"]) == 0
    assert int(native.clear_insert_chain(1)["code"]) == 0
    assert len(native.get_insert_chain(1)) == 0
    assert int(native.insert_plugin(1, "midas.eq.basic", 0)["code"]) == 0
    assert int(native.save_session()["code"]) == 0
    assert int(native.remove_plugin(1, 0)["code"]) == 0
    assert int(native.load_session()["code"]) == 0

    assert int(native.apply_session()["code"]) == 0
    chain = native.get_insert_chain(1)
    assert len(chain) >= 1
    first_values = chain[0].get("values", {})
    if str(first_values.get("host_lifecycle_state", "")) == "loaded_placeholder":
        assert str(first_values.get("managed_instance_id", "")) != ""
        assert str(first_values.get("managed_instance_state", "")) == "created"
        assert str(first_values.get("managed_instance_adapter_state", "")) == "created"
        if initial_managed_id:
            assert str(first_values.get("managed_instance_id", "")) != initial_managed_id
    session_status = native.get_session_status()
    assert int(session_status.get("code", 4)) == 0
    assert str(session_status.get("values", {}).get("status", "")) in {"saved", "loaded", "applied"}
    assert "last_error_message" in session_status.get("values", {})

    assert int(native.init_audio("native-dev", 48000, 256)["code"]) == 0
    assert int(native.open_audio()["code"]) == 0
    assert int(native.start_audio(1, 2001)["code"]) == 0
    transport_status = native.get_runtime_status()
    assert int(transport_status.get("code", 4)) == 0
    values = transport_status.get("values", {})
    assert str(values.get("state", "")) in {"started", "opened", "initialized", "idle"}
    assert str(values.get("runtime_started", "")) in {"true", "false"}
    assert str(values.get("render_status", "")) in {"ok", "no_callback", "partial", "failed", "invalid_runtime_state", "stopped"}
    assert str(values.get("backend_name", "")) != ""
    assert str(values.get("supports_create", "")).lower() in {"true", "false"}
    assert str(values.get("supports_destroy", "")).lower() in {"true", "false"}
    assert str(values.get("supports_query", "")).lower() in {"true", "false"}
    assert str(values.get("support_scope_summary", "")) != ""
    assert int(native.stop_audio()["code"]) == 0
    assert int(native.close_audio()["code"]) == 0

    assert int(native.insert_plugin(1, "thirdparty.reverb.demo", 3)["code"]) == 0
    assert int(native.refresh_insert_runtime_state(1)["code"]) == 0
    assert int(native.request_insert_load(1, 3)["code"]) == 0
    unsupported_chain = native.get_insert_chain(1)
    unsupported = next(
        (slot.get("values", {}) for slot in unsupported_chain if str(slot.get("values", {}).get("slot_index", "")) == "3"),
        {},
    )
    assert str(unsupported.get("loader_outcome", "")) == "unavailable"
    assert str(unsupported.get("loader_reason_code", "")) in {"plugin_unavailable", "plugin_not_supported"}
    assert str(unsupported.get("managed_instance_handle_state", "")) == "unavailable"
    assert str(unsupported.get("managed_instance_reason_source", "")) in {"loader", "policy"}
    assert str(unsupported.get("managed_instance_retryable", "")).lower() == "true"

    assert native.get_mixer_channels()
    assert int(native.shutdown_runtime_profile()["code"]) == 0


if __name__ == "__main__":
    main()
