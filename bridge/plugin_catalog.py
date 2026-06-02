from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LocalSourceDefinition:
    plugin_id: str
    name: str
    category: str
    vendor: str
    env_names: tuple[str, ...]
    candidates: tuple[str, ...]
    group: str
    purpose: str


NON_INSERT_CATEGORIES = {
    "Automation Source",
    "Audio Interface Utility",
    "Drum Instrument",
    "Host App",
    "Host Extension",
    "Instrument Source",
    "Performance Host",
    "Plugin Manager",
    "Plugin Shell",
    "Reference Source",
    "Reference Suite",
    "REAPER FX",
    "Sample Library",
    "Sample Pack",
    "Skin Design Tool",
    "Spatial Utility",
}

PLUGIN_GROUP_ORDER = [
    "Mount Olympus Signal Forge",
    "Elysium Reverb Fields",
    "Tartarus Tone Crucible",
    "Hermes Echo Roads",
    "Aegean Spatial Harbor",
    "Delphi Filter Temple",
    "Daedalus Texture Labyrinth",
    "Nereid Modulation Springs",
    "Hermes Utility Bench",
    "Oracle Harmony Hall",
    "Phrygia Host Gates",
    "Gordium Action Forge",
    "Poseidon Wave Harbor",
    "Hephaestus Interface Forge",
    "Delphi Instrument Temple",
    "Pactolus Sample River",
    "Daedalus Automation Labyrinth",
    "Rhodes Performance Harbor",
    "Tartarus Manager Vault",
    "Athena Type Foundry",
    "Mnemosyne Idea Garden",
    "Oracle Reference Hall",
    "Unmapped Registry",
]

PLUGIN_GROUPS = {
    "midas.eq.basic": "Mount Olympus Signal Forge",
    "midas.comp.basic": "Mount Olympus Signal Forge",
    "midas.reverb.silenus": "Elysium Reverb Fields",
    "midas.drive.inferno": "Tartarus Tone Crucible",
    "midas.delay.hermes": "Hermes Echo Roads",
    "midas.stereo.aegean": "Aegean Spatial Harbor",
    "midas.filter.oracle": "Delphi Filter Temple",
    "midas.lofi.daedalus": "Daedalus Texture Labyrinth",
    "midas.mod.nereid": "Nereid Modulation Springs",
    "midas.utility.hermes": "Hermes Utility Bench",
    "midas.midi.oracle_chords": "Oracle Harmony Hall",
    "thirdparty.reverb.demo": "Elysium Reverb Fields",
}

PLUGIN_PURPOSES = {
    "midas.eq.basic": "MIDAS-native EQ for shaping tone and carving space in a mix.",
    "midas.comp.basic": "MIDAS-native compressor for controlling dynamics and adding punch.",
    "midas.reverb.silenus": "MIDAS-native reverb for rooms, ambience, tails, and depth around vocals, drums, and instruments.",
    "midas.drive.inferno": "MIDAS-native drive inspired by distortion/saturation workflows for adding grit, edge, and harmonic heat.",
    "midas.delay.hermes": "MIDAS-native tempo-aware delay for echoes, throws, rhythmic repeats, and filtered space.",
    "midas.stereo.aegean": "MIDAS-native stereo width tool for balancing mono focus, spread, pan feel, and left/right offset.",
    "midas.filter.oracle": "MIDAS-native filter for low-pass, high-pass, band-pass, peak, notch, and shelf-style movement.",
    "midas.lofi.daedalus": "MIDAS-native lo-fi texture insert for bit-depth feel, sample-rate reduction, and wet/dry degradation.",
    "midas.mod.nereid": "MIDAS-native chorus/modulation insert for thickening parts, widening pads, and adding gentle movement.",
    "midas.utility.hermes": "MIDAS-native gain and trim utility for level staging before, between, or after other inserts.",
    "midas.midi.oracle_chords": "MIDAS-native key, scale, chord, bass, and melody assistant for sketching harmonic ideas.",
    "thirdparty.reverb.demo": "Demo reverb placeholder for space, ambience, and room-style effects.",
}

PLUGIN_FUNCTION_LABELS = {
    "midas.eq.basic": "EQ",
    "midas.comp.basic": "Compressor",
    "midas.reverb.silenus": "Reverb",
    "midas.drive.inferno": "Drive",
    "midas.delay.hermes": "Delay",
    "midas.stereo.aegean": "Width",
    "midas.filter.oracle": "Filter",
    "midas.lofi.daedalus": "LoFi",
    "midas.mod.nereid": "Chorus",
    "midas.utility.hermes": "Gain",
    "midas.midi.oracle_chords": "Chords",
    "thirdparty.reverb.demo": "Reverb",
}

LOCAL_SOURCE_DEFINITIONS = (
    LocalSourceDefinition(
        plugin_id="midas.host.reaper",
        name="MIDAS Phrygian Gate",
        category="Host App",
        vendor="Cockos REAPER",
        env_names=("MIDAS_REAPER_APP_PATH",),
        candidates=("/Applications/REAPER.app/Contents",),
        group="Phrygia Host Gates",
        purpose="REAPER host installation used for DAW reference, actions, routing ideas, and compatibility studies.",
    ),
    LocalSourceDefinition(
        plugin_id="midas.reaper.reafx",
        name="MIDAS Gordian FX Rack",
        category="REAPER FX",
        vendor="Cockos REAPER",
        env_names=("MIDAS_REAPER_FX_PATH",),
        candidates=("/Applications/REAPER.app/Contents/Plugins/FX",),
        group="Gordium Action Forge",
        purpose="REAPER's bundled FX library, useful as a reference rack for stock EQ, dynamics, and utility effects.",
    ),
    LocalSourceDefinition(
        plugin_id="reaper.sws.extension",
        name="MIDAS Gordian Action Loom",
        category="Host Extension",
        vendor="SWS/S&M",
        env_names=("MIDAS_REAPER_SWS_PATH",),
        candidates=(
            "~/Library/Application Support/REAPER/UserPlugins/reaper_sws-arm64.dylib",
            "/Applications/REAPER.app/Contents/Plugins/reaper_sws-arm64.dylib",
            "/Volumes/sws-2.14.0.7-Darwin-arm64-9daba634/reaper_sws-arm64.dylib",
        ),
        group="Gordium Action Forge",
        purpose="REAPER action extension that expands workflow commands, snapshots, regions, and automation helpers.",
    ),
    LocalSourceDefinition(
        plugin_id="midas.host.garageband",
        name="MIDAS Golden Lyre Sketchpad",
        category="Host App",
        vendor="Apple GarageBand",
        env_names=("MIDAS_GARAGEBAND_APP_PATH",),
        candidates=("/Applications/GarageBand.app/Contents",),
        group="Phrygia Host Gates",
        purpose="GarageBand reference host for beginner-friendly recording, instrument browsing, and song sketching patterns.",
    ),
    LocalSourceDefinition(
        plugin_id="midas.manager.melda",
        name="MIDAS Dionysus Vault",
        category="Plugin Manager",
        vendor="MeldaProduction",
        env_names=("MIDAS_MELDA_PATH",),
        candidates=("/Applications/MeldaProduction/MPluginManager.app/Contents", "/Applications/MeldaProduction"),
        group="Tartarus Manager Vault",
        purpose="MeldaProduction manager/source folder for discovering installed Melda effects and instrument families.",
    ),
    LocalSourceDefinition(
        plugin_id="midas.reference.maat",
        name="MIDAS Oracle Mirror",
        category="Reference Suite",
        vendor="MAAT",
        env_names=("MIDAS_MAAT_PATH",),
        candidates=("/Applications/MAAT/GON", "/Applications/MAAT"),
        group="Oracle Reference Hall",
        purpose="MAAT reference and metering suite source for clarity, loudness, balance, and mix-check workflows.",
    ),
    LocalSourceDefinition(
        plugin_id="midas.pack.ember-lite",
        name="MIDAS Inferno Shaper",
        category="Sample Pack",
        vendor="Cymatics",
        env_names=("MIDAS_CYMATICS_PATH",),
        candidates=("/Applications/Cymatics/Cymatics Diablo Lite", "/Applications/Cymatics"),
        group="Pactolus Sample River",
        purpose="Cymatics Diablo Lite source, used as distortion/saturation inspiration for aggressive sound shaping.",
    ),
    LocalSourceDefinition(
        plugin_id="midas.waves.central",
        name="MIDAS Tide Vault",
        category="Plugin Manager",
        vendor="Waves",
        env_names=("MIDAS_WAVES_CENTRAL_PATH",),
        candidates=("/Applications/Waves Central.app/Contents",),
        group="Poseidon Wave Harbor",
        purpose="Waves Central manager for installing, updating, and licensing Waves products.",
    ),
    LocalSourceDefinition(
        plugin_id="midas.waves.shells",
        name="MIDAS Poseidon WaveShell",
        category="Plugin Shell",
        vendor="Waves",
        env_names=("MIDAS_WAVES_SHELLS_PATH",),
        candidates=("/Applications/Waves/WaveShells V16",),
        group="Poseidon Wave Harbor",
        purpose="Waves shell containers that expose Waves AU, VST3, AAX, ARA, OBS, and WPAPI plugin formats to hosts.",
    ),
    LocalSourceDefinition(
        plugin_id="midas.waves.headtracker",
        name="MIDAS Argus Head Tracker",
        category="Spatial Utility",
        vendor="Waves",
        env_names=("MIDAS_WAVES_HEAD_TRACKER_PATH",),
        candidates=("/Applications/Waves/Plug-Ins V16/WavesHeadTracker/WavesHeadTracker.app/Contents",),
        group="Poseidon Wave Harbor",
        purpose="Waves spatial tracking helper that can use camera, Bluetooth, microphone, and motion data for head-tracked audio.",
    ),
    LocalSourceDefinition(
        plugin_id="midas.focusrite.control",
        name="MIDAS Scarlett Hearth",
        category="Audio Interface Utility",
        vendor="Focusrite",
        env_names=("MIDAS_FOCUSRITE_CONTROL_PATH",),
        candidates=(
            "/Applications/Focusrite Control 2.app/Contents",
            "~/Downloads/Focusrite-Control-2.dmg",
            "~/Downloads/Focusrite-Control-2.exe",
        ),
        group="Hephaestus Interface Forge",
        purpose="Focusrite Control 2 source for Scarlett interface routing, gain, monitoring, firmware, and beginner audio setup workflows.",
    ),
    LocalSourceDefinition(
        plugin_id="midas.drumforge.sitala",
        name="MIDAS Anvil Drumforge",
        category="Drum Instrument",
        vendor="Sitala",
        env_names=("MIDAS_SITALA_PATH",),
        candidates=("/Applications/Sitala.app/Contents",),
        group="Delphi Instrument Temple",
        purpose="Sitala drum instrument source for pad kits, one-shots, sample triggering, and beat construction.",
    ),
    LocalSourceDefinition(
        plugin_id="midas.splice.library",
        name="MIDAS Thread Library",
        category="Sample Library",
        vendor="Splice",
        env_names=("MIDAS_SPLICE_PATH",),
        candidates=("/Applications/Splice.app/Contents",),
        group="Pactolus Sample River",
        purpose="Splice desktop library for browsing, syncing, and importing loops, one-shots, MIDI, and sample packs.",
    ),
    LocalSourceDefinition(
        plugin_id="midas.splice.instrument",
        name="MIDAS Muse Instrument",
        category="Instrument Source",
        vendor="Splice",
        env_names=("MIDAS_SPLICE_INSTRUMENT_PATH",),
        candidates=("/Applications/Splice INSTRUMENT.app/Contents",),
        group="Delphi Instrument Temple",
        purpose="Splice Instrument app source for playable sounds and instrument-driven sketching.",
    ),
    LocalSourceDefinition(
        plugin_id="midas.automator.daedalus",
        name="MIDAS Daedalus Automator",
        category="Automation Source",
        vendor="Apple Automator",
        env_names=("MIDAS_AUTOMATOR_PATH",),
        candidates=("/System/Applications/Automator.app/Contents",),
        group="Daedalus Automation Labyrinth",
        purpose="macOS Automator reference for repeatable local actions, batch operations, and workflow automation ideas.",
    ),
    LocalSourceDefinition(
        plugin_id="midas.virtualdj.helios",
        name="MIDAS Helios Decks",
        category="Performance Host",
        vendor="VirtualDJ",
        env_names=("MIDAS_VIRTUALDJ_PATH",),
        candidates=("/Applications/VirtualDJ.app/Contents",),
        group="Rhodes Performance Harbor",
        purpose="VirtualDJ performance host for decks, sampler, stems, automix, broadcast, and live set workflow reference.",
    ),
    LocalSourceDefinition(
        plugin_id="midas.flcloud.nimbus",
        name="MIDAS Nimbus Rack",
        category="Plugin Manager",
        vendor="Image-Line",
        env_names=("MIDAS_FL_CLOUD_PATH",),
        candidates=("/Applications/FL Cloud Plugins.app/Contents",),
        group="Tartarus Manager Vault",
        purpose="FL Cloud Plugins manager/source app for Image-Line cloud plugin discovery and account-managed installs.",
    ),
    LocalSourceDefinition(
        plugin_id="midas.ik.titan",
        name="MIDAS Titan Vault",
        category="Plugin Manager",
        vendor="IK Multimedia",
        env_names=("MIDAS_IK_MANAGER_PATH",),
        candidates=("/Applications/IK Product Manager.app/Contents",),
        group="Tartarus Manager Vault",
        purpose="IK Product Manager source for installing, updating, and managing IK Multimedia instruments and effects.",
    ),
    LocalSourceDefinition(
        plugin_id="midas.skin.fontbook",
        name="MIDAS Athena Font Vault",
        category="Skin Design Tool",
        vendor="Apple Font Book",
        env_names=("MIDAS_FONT_BOOK_PATH",),
        candidates=("/System/Applications/Font Book.app/Contents",),
        group="Athena Type Foundry",
        purpose="Font management source for previewing, validating, and organizing typography used by MIDAS skins.",
    ),
    LocalSourceDefinition(
        plugin_id="midas.skin.freeform",
        name="MIDAS Muse Board",
        category="Skin Design Tool",
        vendor="Apple Freeform",
        env_names=("MIDAS_FREEFORM_PATH",),
        candidates=("/System/Applications/Freeform.app/Contents",),
        group="Mnemosyne Idea Garden",
        purpose="Moodboard and planning source for sketching DAW skins, arrangement maps, and visual direction boards.",
    ),
    LocalSourceDefinition(
        plugin_id="midas.reference.dictionary",
        name="MIDAS Lyric Lexicon",
        category="Reference Source",
        vendor="Apple Dictionary",
        env_names=("MIDAS_DICTIONARY_PATH",),
        candidates=("/System/Applications/Dictionary.app/Contents",),
        group="Oracle Reference Hall",
        purpose="Reference source for lyric writing, naming presets, checking definitions, and language lookup.",
    ),
)

LOCAL_SOURCE_IDS = {source.plugin_id for source in LOCAL_SOURCE_DEFINITIONS}

for source in LOCAL_SOURCE_DEFINITIONS:
    PLUGIN_GROUPS[source.plugin_id] = source.group
    PLUGIN_PURPOSES[source.plugin_id] = source.purpose
    PLUGIN_FUNCTION_LABELS[source.plugin_id] = source.category


def plugin_group(plugin_id: str) -> str:
    return PLUGIN_GROUPS.get(plugin_id, "Unmapped Registry")


def plugin_purpose(plugin_id: str) -> str:
    return PLUGIN_PURPOSES.get(plugin_id, "Registry entry awaiting a MIDAS role description.")


def plugin_function_label(plugin_id: str, category: str) -> str:
    return PLUGIN_FUNCTION_LABELS.get(plugin_id, category or "Other")
