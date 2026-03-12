from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bridge.fallback_bridge import FallbackBridgeClient


def test_plugin_insertion_contract_roundtrip_save_load_apply():
    bridge = FallbackBridgeClient()

    assert bridge.insert_plugin(1, "midas.eq.basic", 0).ok
    assert bridge.insert_plugin(1, "midas.comp.basic", 1).ok
    assert bridge.move_plugin_to_top(1, 1).ok
    assert bridge.set_channel_insert_bypass(1, True).ok
    assert bridge.request_insert_load(1, 0).ok
    chain = bridge.get_insert_chain(1)
    assert len(chain) == 2
    assert chain[0].slot_index == 0
    assert chain[0].plugin_id == "midas.comp.basic"
    assert chain[0].bypassed is True
    assert chain[1].slot_index == 1
    assert chain[1].plugin_id == "midas.eq.basic"
    assert chain[1].bypassed is True
    assert chain[0].host_lifecycle_state in {"loaded_placeholder", "load_failed"}

    assert bridge.save_session().ok

    assert bridge.remove_plugin(1, 0).ok
    mutated = bridge.get_insert_chain(1)
    assert len(mutated) == 1
    assert bridge.move_plugin_to_bottom(1, 1).ok

    assert bridge.load_session().ok
    assert bridge.refresh_insert_runtime_state(1).ok
    loaded = bridge.get_insert_chain(1)
    assert len(loaded) == 2
    assert loaded[0].plugin_id == "midas.comp.basic"
    assert loaded[0].bypassed is True
    assert loaded[1].plugin_id == "midas.eq.basic"
    assert loaded[1].bypassed is True
    # host lifecycle is ephemeral; it is re-derived and starts from non-requested state after load/apply.
    assert loaded[0].host_lifecycle_state == "not_requested"

    assert bridge.remove_plugin(1, 1).ok
    assert bridge.apply_session().ok
    assert bridge.refresh_insert_runtime_state(1).ok
    assert bridge.request_insert_unload(1, 0).ok
    applied = bridge.get_insert_chain(1)
    assert len(applied) == 2
    assert all(slot.load_state in {"loaded", "unavailable", "failed"} for slot in applied)
    assert applied[0].host_lifecycle_state == "unloaded"
    assert bridge.clear_insert_chain(1).ok
    assert bridge.get_insert_chain(1) == []
