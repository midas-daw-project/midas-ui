# FL Studio UI Pattern Reference For MIDAS

Source material:

- <https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/Index_Frame_Left.html>

Use this as workflow precedent, not a visual clone target. FL Studio is especially useful for MIDAS because it prioritizes beat-making surfaces: browser, channel rack, step sequencer, playlist, pattern workflow, mixer, and a persistent toolbar.

## Patterns To Borrow

- **Toolbar as cockpit**: persistent title/hint/search, transport, pattern/tempo/time controls, output/device status, and shortcut/window controls.
- **Hint/status surface**: show immediate guidance for controls and modes so users discover features without a separate welcome screen.
- **Browser-first workflow**: searchable library, plugin database, project browser, cloud/sounds/library concepts, preview-before-insert behavior.
- **Channel rack and step sequencer**: rows map to channels/instruments; each row exposes mute/pan/volume/mixer destination and step buttons or piano-roll preview.
- **Playlist**: pattern clips are arranged horizontally; playlist tracks can be linked to instrument/audio tracks when a more traditional track model is desired.
- **Mixer/effects**: mixer tracks carry effects, routing, input/output, levels, and clipping feedback.
- **Power tools later**: piano roll tools, automation tools, controller linking, scripting, and action-like command surfaces can arrive after the shell is stable.

## MIDAS Adaptation

- Keep the top header persistent: project title, search/command box, play/stop, BPM/key, bridge/runtime/device status.
- Treat the central beat workspace as an early channel-rack plus playlist hybrid until backend timeline models mature.
- Keep the left browser as category/library/marketplace plus plugin registry.
- Keep the right mixer/effects panel as channel strip plus plugin stack, not a generic settings form.
- Add hint text and next-action guidance near major controls rather than a separate welcome screen.

## Guardrails

- Do not copy FL Studio visuals or exact interaction language.
- Do not implement piano roll, automation tools, controller linking, scripting, full routing, or plugin loading until selected by scoped issues.
- Keep fallback bridge workflows operatable while backend/native capabilities catch up.
