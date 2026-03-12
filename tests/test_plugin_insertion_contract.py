from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bridge.fallback_bridge import FallbackBridgeClient


def test_plugin_insertion_contract_roundtrip_save_load_apply():
    bridge = FallbackBridgeClient()

    assert bridge.insert_plugin(1, "midas.eq.basic", 0).ok
    assert bridge.insert_plugin(1, "midas.comp.basic", 1).ok
    chain = bridge.get_insert_chain(1)
    assert len(chain) == 2
    assert chain[0].slot_index == 0
    assert chain[1].slot_index == 1

    assert bridge.save_session().ok

    assert bridge.remove_plugin(1, 0).ok
    mutated = bridge.get_insert_chain(1)
    assert len(mutated) == 1

    assert bridge.load_session().ok
    loaded = bridge.get_insert_chain(1)
    assert len(loaded) == 2
    assert loaded[0].plugin_id == "midas.eq.basic"
    assert loaded[1].plugin_id == "midas.comp.basic"

    assert bridge.remove_plugin(1, 1).ok
    assert bridge.apply_session().ok
    applied = bridge.get_insert_chain(1)
    assert len(applied) == 2
