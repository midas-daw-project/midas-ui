from pathlib import Path
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shell.theme import DEFAULT_MIDAS_SKIN, available_midas_skins, get_midas_skin


def test_midas_skin_presets_include_design_tool_lanes():
    skins = available_midas_skins()

    assert DEFAULT_MIDAS_SKIN == "Midas Night Forge"
    assert "Midas Night Forge" in skins
    assert "Athena Type Foundry" in skins
    assert "Mnemosyne Idea Garden" in skins

    default_skin = get_midas_skin()
    assert default_skin.name == "Midas Night Forge"
    assert default_skin.font_source == "Hack"

    font_skin = get_midas_skin("Athena Type Foundry")
    assert font_skin.font_source == "Font Book"
    assert font_skin.location == "Athena Type Foundry"
