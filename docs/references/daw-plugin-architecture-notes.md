# DAW And Plugin Architecture Notes For MIDAS

Source material reviewed:

- `the-architecture-of-daws:slides.pdf`
- `Neo-Manual.pdf`
- `VST_Live_1_1_Operation_Manual_en.pdf`
- `PlugIn.pdf`
- Plugin Boutique plugin-format reference
- Captain Plugins / Logic Pro workflow reference
- Existing REAPER, Logic Pro, FL Studio, Ableton-style, and Studio One pattern notes

Use this as product architecture guidance, not as copied manual behavior.

## Core Model

- MIDAS should keep a small stable core: transport, project/session state, audio lifecycle, arrangement, mixer, browser, and command routing.
- Effects, instruments, sources, assistants, skins, and hardware utilities should attach through a registry rather than becoming hard-coded UI branches.
- Each plugin/module needs a clear identity, category, vendor/source, availability, role description, and runtime/load state.
- A module failing to load should not make the DAW unstable; it should fail in its slot with an understandable reason.

## Audio And UI Separation

- The UI must never imply a source app or plugin shell is processing audio unless the bridge can actually insert/load it.
- Audio-device settings such as sample rate and block size belong in the persistent control bar and the deeper Audio panel.
- Transport, rendering, plugin loading, and UI edits should be represented as separate states so users can tell what is configured, what is loaded, and what is running.

## Plugin Formats

- VST, VST3, and AU are the main Mac-facing formats to plan for MIDAS plugin hosting.
- AAX is primarily a Pro Tools plugin format; treat it as detected/reference unless a future backend explicitly supports it.
- Standalone apps, installers, managers, shells, sample libraries, and hardware utilities are sources or setup tools, not mixer inserts.
- MIDAS-native insert shells can be usable before third-party binary hosting exists, but the UI should label them as MIDAS-native.

## Musical Assistant Layer

- Key, scale, chord, bass, and melody helpers should be treated as MIDI/harmony assistants, not audio effects.
- The key wheel should eventually connect to chord suggestions, scale-safe piano-roll behavior, bass-pattern generation, and melody sketching.
- These helpers should share project key and tempo state with the transport/header so the whole DAW feels musically aware.

## UI Translation

- REAPER: dense arrange/mixer/routing precedent, dockable panels, FX chains, action workflow.
- Logic Pro: polished control bar, library/inspector clarity, smart controls, channel strip discipline.
- FL Studio: beat-first browser, channel rack/step sequencer, hint/status feedback, fast pattern creation.
- Ableton-style workflow: quick mode switching, clip/session thinking, immediate loop experimentation.
- Studio One: browser as action source, clear single-window song workflow, insert/send rack ownership.

## Current Implementation Guidance

- Keep the first screen as the DAW itself, with onboarding as a dismissible helper.
- Keep the plugin browser searchable and grouped by user intent.
- Keep the plugin wheel as a focused tab for discovery, not a modal that blocks work.
- Show whether a registry item is insertable, unavailable, detected-only, or reference/setup.
- Prefer smaller, responsive layouts that fit laptop screens before adding heavier skins.
