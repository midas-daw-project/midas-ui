from pathlib import Path
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtWidgets import QApplication

from bridge.fallback_bridge import FallbackBridgeClient
from controllers.browser_controller import BrowserController
from panels.browser.browser_panel import BrowserPanel
from viewmodels.browser_viewmodel import BrowserViewModel


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_browser_registry_load_and_selection():
    bridge = FallbackBridgeClient()
    vm = BrowserViewModel()
    controller = BrowserController(bridge, vm)

    controller.load_registry()
    assert len(vm.plugins) >= 1
    assert vm.selected_plugin_id != ""
    assert vm.selected_name != ""

    selected = vm.plugins[-1].plugin_id
    controller.select_plugin(selected)
    assert vm.selected_plugin_id == selected


def test_browser_selection_queues_only_available_insert_effects():
    bridge = FallbackBridgeClient()
    vm = BrowserViewModel()
    controller = BrowserController(bridge, vm)

    controller.load_registry()
    controller.select_plugin("midas.eq.basic", queue_if_insert=True)
    assert vm.queued_plugin_ids == ["midas.eq.basic"]

    controller.select_plugin("midas.eq.basic", queue_if_insert=True)
    assert vm.queued_plugin_ids == ["midas.eq.basic"]

    controller.select_plugin("midas.focusrite.control", queue_if_insert=True)
    assert vm.selected_plugin_id == "midas.focusrite.control"
    assert vm.queued_plugin_ids == ["midas.eq.basic"]

    controller.clear_plugin_queue()
    assert vm.queued_plugin_ids == []


def test_browser_registry_exposes_midas_native_plugin_equivalents():
    bridge = FallbackBridgeClient()
    plugins = {plugin.plugin_id: plugin for plugin in bridge.get_plugin_registry()}

    for plugin_id in (
        "midas.reverb.silenus",
        "midas.drive.inferno",
        "midas.delay.hermes",
        "midas.stereo.aegean",
        "midas.filter.oracle",
        "midas.lofi.daedalus",
        "midas.mod.nereid",
        "midas.utility.hermes",
        "midas.midi.oracle_chords",
    ):
        assert plugins[plugin_id].available
        assert plugins[plugin_id].source == "builtin"

    assert bridge.insert_plugin(1, "midas.drive.inferno", 0).ok
    assert bridge.get_insert_chain(1)[0].plugin_name == "MIDAS Inferno Drive"


def test_browser_registry_refresh():
    bridge = FallbackBridgeClient()
    vm = BrowserViewModel()
    controller = BrowserController(bridge, vm)

    result = controller.refresh_registry()
    assert result.ok
    assert vm.last_refresh_status == "ok"
    assert len(vm.plugins) >= 1


def test_browser_registry_exposes_reaper_sws_host_extension(monkeypatch, tmp_path):
    sws_path = tmp_path / "reaper_sws-arm64.dylib"
    sws_path.write_bytes(b"test dylib placeholder")
    monkeypatch.setenv("MIDAS_REAPER_SWS_PATH", str(sws_path))

    bridge = FallbackBridgeClient()
    plugins = bridge.get_plugin_registry()
    sws = next(plugin for plugin in plugins if plugin.plugin_id == "reaper.sws.extension")

    assert sws.name == "MIDAS Gordian Action Loom"
    assert sws.category == "Host Extension"
    assert sws.vendor == "SWS/S&M"
    assert not sws.available
    assert sws.source == f"detected: {sws_path}"


def test_browser_registry_exposes_detected_local_sources(monkeypatch, tmp_path):
    reaper = tmp_path / "REAPER.app" / "Contents"
    reaper_fx = reaper / "Plugins" / "FX"
    garageband = tmp_path / "GarageBand.app" / "Contents"
    melda = tmp_path / "MeldaProduction"
    maat = tmp_path / "MAAT" / "GON"
    cymatics = tmp_path / "Cymatics" / "Cymatics Diablo Lite"
    waves_central = tmp_path / "Waves Central.app" / "Contents"
    waves_shells = tmp_path / "Waves" / "WaveShells V16"
    waves_headtracker = tmp_path / "Waves" / "Plug-Ins V16" / "WavesHeadTracker" / "WavesHeadTracker.app" / "Contents"
    focusrite = tmp_path / "Focusrite-Control-2.dmg"
    sitala = tmp_path / "Sitala.app" / "Contents"
    splice = tmp_path / "Splice.app" / "Contents"
    splice_instrument = tmp_path / "Splice INSTRUMENT.app" / "Contents"
    automator = tmp_path / "Automator.app" / "Contents"
    virtualdj = tmp_path / "VirtualDJ.app" / "Contents"
    fl_cloud = tmp_path / "FL Cloud Plugins.app" / "Contents"
    ik = tmp_path / "IK Product Manager.app" / "Contents"
    font_book = tmp_path / "Font Book.app" / "Contents"
    freeform = tmp_path / "Freeform.app" / "Contents"
    dictionary = tmp_path / "Dictionary.app" / "Contents"
    for path in (
        reaper_fx,
        garageband,
        melda,
        maat,
        cymatics,
        waves_central,
        waves_shells,
        waves_headtracker,
        sitala,
        splice,
        splice_instrument,
        automator,
        virtualdj,
        fl_cloud,
        ik,
        font_book,
        freeform,
        dictionary,
    ):
        path.mkdir(parents=True)
    focusrite.write_bytes(b"focusrite installer placeholder")
    monkeypatch.setenv("MIDAS_REAPER_APP_PATH", str(reaper))
    monkeypatch.setenv("MIDAS_REAPER_FX_PATH", str(reaper_fx))
    monkeypatch.setenv("MIDAS_GARAGEBAND_APP_PATH", str(garageband))
    monkeypatch.setenv("MIDAS_MELDA_PATH", str(melda))
    monkeypatch.setenv("MIDAS_MAAT_PATH", str(maat))
    monkeypatch.setenv("MIDAS_CYMATICS_PATH", str(cymatics))
    monkeypatch.setenv("MIDAS_WAVES_CENTRAL_PATH", str(waves_central))
    monkeypatch.setenv("MIDAS_WAVES_SHELLS_PATH", str(waves_shells))
    monkeypatch.setenv("MIDAS_WAVES_HEAD_TRACKER_PATH", str(waves_headtracker))
    monkeypatch.setenv("MIDAS_FOCUSRITE_CONTROL_PATH", str(focusrite))
    monkeypatch.setenv("MIDAS_SITALA_PATH", str(sitala))
    monkeypatch.setenv("MIDAS_SPLICE_PATH", str(splice))
    monkeypatch.setenv("MIDAS_SPLICE_INSTRUMENT_PATH", str(splice_instrument))
    monkeypatch.setenv("MIDAS_AUTOMATOR_PATH", str(automator))
    monkeypatch.setenv("MIDAS_VIRTUALDJ_PATH", str(virtualdj))
    monkeypatch.setenv("MIDAS_FL_CLOUD_PATH", str(fl_cloud))
    monkeypatch.setenv("MIDAS_IK_MANAGER_PATH", str(ik))
    monkeypatch.setenv("MIDAS_FONT_BOOK_PATH", str(font_book))
    monkeypatch.setenv("MIDAS_FREEFORM_PATH", str(freeform))
    monkeypatch.setenv("MIDAS_DICTIONARY_PATH", str(dictionary))

    plugins = {plugin.plugin_id: plugin for plugin in FallbackBridgeClient().get_plugin_registry()}

    assert plugins["midas.host.reaper"].name == "MIDAS Phrygian Gate"
    assert plugins["midas.reaper.reafx"].name == "MIDAS Gordian FX Rack"
    assert plugins["midas.host.garageband"].name == "MIDAS Golden Lyre Sketchpad"
    assert plugins["midas.manager.melda"].name == "MIDAS Dionysus Vault"
    assert plugins["midas.reference.maat"].name == "MIDAS Oracle Mirror"
    assert plugins["midas.pack.ember-lite"].name == "MIDAS Inferno Shaper"
    assert plugins["midas.pack.ember-lite"].category == "Sample Pack"
    assert plugins["midas.pack.ember-lite"].source == f"detected: {cymatics}"
    assert plugins["midas.waves.central"].name == "MIDAS Tide Vault"
    assert plugins["midas.waves.shells"].category == "Plugin Shell"
    assert plugins["midas.waves.headtracker"].name == "MIDAS Argus Head Tracker"
    assert plugins["midas.focusrite.control"].name == "MIDAS Scarlett Hearth"
    assert plugins["midas.focusrite.control"].category == "Audio Interface Utility"
    assert plugins["midas.focusrite.control"].source == f"detected: {focusrite}"
    assert plugins["midas.drumforge.sitala"].category == "Drum Instrument"
    assert plugins["midas.splice.library"].name == "MIDAS Thread Library"
    assert plugins["midas.splice.instrument"].category == "Instrument Source"
    assert plugins["midas.automator.daedalus"].category == "Automation Source"
    assert plugins["midas.virtualdj.helios"].name == "MIDAS Helios Decks"
    assert plugins["midas.flcloud.nimbus"].vendor == "Image-Line"
    assert plugins["midas.ik.titan"].source == f"detected: {ik}"
    assert plugins["midas.skin.fontbook"].name == "MIDAS Athena Font Vault"
    assert plugins["midas.skin.fontbook"].category == "Skin Design Tool"
    assert plugins["midas.skin.freeform"].name == "MIDAS Muse Board"
    assert plugins["midas.reference.dictionary"].category == "Reference Source"


def test_browser_panel_renders_library_marketplace_and_registry():
    _app()
    panel = BrowserPanel(
        on_refresh_registry=lambda: None,
        on_select_plugin=lambda _plugin_id: None,
        on_insert_plugin=lambda: None,
    )
    bridge = FallbackBridgeClient()
    vm = BrowserViewModel(plugins=bridge.get_plugin_registry())
    controller = BrowserController(bridge, vm)
    controller.load_registry()

    panel.render(vm)

    assert panel.browser_search_input.placeholderText() == "Search sounds, plugins, presets"
    assert panel.category_list.count() == 16
    assert panel.category_list.currentItem().text() == "All Sources"
    assert panel.plugin_browser_tabs.count() == 2
    assert panel.plugin_browser_tabs.tabText(0) == "List"
    assert panel.plugin_browser_tabs.tabText(1) == "Wheel"
    assert panel.minimumWidth() == 320
    assert panel.plugin_browser_tabs.minimumHeight() == 340
    assert panel.plugin_list.minimumHeight() == 260
    assert panel.plugin_wheel_box.minimumHeight() == 300
    assert panel.details_box.maximumHeight() == 260
    assert panel.pack_list.count() == 3
    assert "Starter Kit" in panel.pack_list.item(0).text()
    assert panel.plugin_list.count() >= 1

    controller.select_plugin("reaper.sws.extension")
    panel.render(vm)
    assert panel.category_label.text() == "Host Extension"
    assert panel.group_label.text() == "Gordium Action Forge"
    assert panel.available_label.text() == "detected source, not a mixer insert"
    assert "setup, discovery, or reference" in panel.works_label.text()

    panel.browser_search_input.setText("head tracker")
    visible_text = "\n".join(panel.plugin_list.item(row).text() for row in range(panel.plugin_list.count()))
    assert "MIDAS Argus Head Tracker" in visible_text
    assert "Poseidon Wave Harbor" in visible_text

    panel.browser_search_input.setText("font")
    visible_text = "\n".join(panel.plugin_list.item(row).text() for row in range(panel.plugin_list.count()))
    assert "MIDAS Athena Font Vault" in visible_text
    assert "Athena Type Foundry" in visible_text

    controller.select_plugin("midas.eq.basic", queue_if_insert=True)
    panel.render(vm)
    assert "MIDAS Apollo Curve" in panel.queue_label.text()
    assert panel.plugin_wheel_buttons
    assert "MIDAS Apollo Curve" in panel.plugin_explanation_bubble.text()
    assert "can be selected and queued" in panel.works_label.text()

    panel.browser_search_input.setText("scarlett")
    visible_text = "\n".join(panel.plugin_list.item(row).text() for row in range(panel.plugin_list.count()))
    assert "MIDAS Scarlett Hearth" in visible_text
    assert "Hephaestus Interface Forge" in visible_text
