# FL Studio UI Pattern Reference For MIDAS

Source material:

- <https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/Index_Frame_Left.html>
- <https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/basics_interface.htm>
- `/Users/matthewperalta/Downloads/Training for you.pdf`

Use this as workflow precedent, not a visual clone target. FL Studio is especially useful for MIDAS because it prioritizes beat-making surfaces: browser, channel rack, step sequencer, playlist, pattern workflow, mixer, and a persistent toolbar.

## Patterns To Borrow

- **Toolbar as cockpit**: persistent title/hint/search, transport, pattern/tempo/time controls, output/device status, and shortcut/window controls.
- **Hint/status surface**: show immediate guidance for controls and modes so users discover features without a separate welcome screen; FL's interface notes emphasize hovering controls and reading the hint bar.
- **Browser-first workflow**: searchable library, plugin database, project browser, cloud/sounds/library concepts, preview-before-insert behavior.
- **Channel rack and step sequencer**: rows map to channels/instruments; each row exposes mute/pan/volume/mixer destination and step buttons or piano-roll preview.
- **Playlist**: pattern clips are arranged horizontally; playlist tracks can be linked to instrument/audio tracks when a more traditional track model is desired.
- **Mixer/effects**: mixer tracks carry effects, routing, input/output, levels, and clipping feedback.
- **Modular windows without chaos**: panels should snap/dock into predictable workspace regions, with detach/multi-screen behavior as later power-user scope.
- **Common control gestures**: knobs, sliders, number displays, preset selectors, wave displays, and menu icons should feel consistent across the app.
- **Favorites and presets**: frequently used folders, presets, and reusable content should become first-class browser shortcuts.
- **Power tools later**: piano roll tools, automation tools, controller linking, scripting, and action-like command surfaces can arrive after the shell is stable.
- **Beginner-to-song journey**: training transcripts show a useful order for MIDAS guidance: template/open project, add sounds, make a pattern, draw MIDI, arrange in playlist, route to mixer, add effects, automate, record, export, then customize.

## MIDAS Adaptation

- Keep the top header persistent: project title, search/command box, play/stop, BPM/key, bridge/runtime/device status.
- Add a compact hint/status strip under the cockpit so users always know the next useful action.
- Treat the central beat workspace as an early channel-rack plus playlist hybrid until backend timeline models mature.
- Keep the left browser as category/library/marketplace plus plugin registry.
- Keep the right mixer/effects panel as channel strip plus plugin stack, not a generic settings form.
- Add hint text and next-action guidance near major controls rather than a separate welcome screen.
- Keep windows/panels docked by default; expose detach or multi-screen behavior only after the shell layout is stable.
- See `docs/references/fl-studio-training-transcripts-reference.md` for the expanded frontend/backend workflow translation.

## Guardrails

- Do not copy FL Studio visuals or exact interaction language.
- Do not implement piano roll, automation tools, controller linking, scripting, full routing, or plugin loading until selected by scoped issues.
- Keep fallback bridge workflows operatable while backend/native capabilities catch up.
