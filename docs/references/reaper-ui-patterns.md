# REAPER UI Pattern Reference For MIDAS

Source material:

- `ReaperUserGuide773.pdf`
- `WhatsNewReaper7Summary_r2.pdf`

Use these references as DAW interaction precedent, not as a visual clone target. MIDAS keeps its own cosmic/purple beat-production identity while borrowing proven workflow structures.

## Patterns To Borrow

- **Main window structure**: left track/control area, central arrange area, transport, mixer, and dockable utility panels.
- **Track control panel**: each track should expose compact operational controls before advanced editing depth: arm/mute/solo, level, pan, routing/FX entry points, and visible state.
- **Arrange view**: horizontal timeline with stacked lanes; clips/items should be directly visible, selectable, and eventually editable in-place.
- **Mixer view**: channel strips should summarize level, mute/solo, FX/insert state, and master output. Use the mixer as a status surface, not just a settings form.
- **Media explorer/browser**: support browsing by folders/categories/databases/favorites and previewing assets before insertion.
- **FX chain/plugin workflow**: adding effects should feel like choosing from a searchable browser and applying to a track/slot/chain with clear insert order.
- **Transport**: play/stop/record, tempo, time/key/project position, and device status belong in a persistent top-level area.
- **Docking/screensets**: users should be able to reveal/hide focused panels and return to known workspace layouts.
- **Actions/commands**: long term, expose a command palette/action list for power-user workflows and keyboard-driven editing.
- **Project/session workflow**: save/load/apply/recent project behavior should be visible and trustworthy.

## MIDAS Adaptation

- Keep the first screen as the actual application, not a marketing welcome page.
- Use the workspace home as the empty-state/start-state surface for new/open/recent sessions.
- Keep arrangement/step-sequencer visuals prominent for beat creation while backend timeline models are still immature.
- Keep fallback bridge workflows operatable; create backend issues only for missing machine-readable truth.
- Label plugin state layers clearly: persisted slot intent, runtime evaluation, host lifecycle, placeholder identity, managed instance identity.

## Current Priority Translation

1. Top header/transport: project title, search/command box, play/stop, BPM/key, device/runtime status.
2. Left browser: categories, marketplace/packs, preview/install actions, plugin registry.
3. Center workspace: arrangement lanes, step sequencer, session/operator status.
4. Right mixer/effects: channel strips, insert stack, selected plugin/runtime state.
5. Later: action list, track editing, routing matrix, media explorer depth, screensets/layout presets.

## Guardrails

- Do not copy REAPER visuals directly.
- Do not widen into full routing, piano roll, DSP graph, binary plugin loading, or realtime audio until backend issues explicitly select that work.
- Prefer dense, operational UI over splash/welcome screens.
