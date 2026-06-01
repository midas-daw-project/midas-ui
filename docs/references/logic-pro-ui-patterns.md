# Logic Pro UI Pattern Reference For MIDAS

Source material:

- `logic-pro-mac-user-guide.pdf`
- `logic-pro-mac-instruments-user-guide.pdf`
- `logic-pro-mac-effects-user-guide.pdf`
- `logic-pro-mac-control-surfaces-support-guide.pdf`

Use these manuals as workflow and product-quality precedent, not as a visual clone target. Logic is useful for MIDAS because it balances a polished production workspace with deep instrument, effect, mixer, and control-surface workflows.

## Patterns To Borrow

- **Polished control bar**: keep transport, project state, tempo/key, cycle/metronome-style controls, and status visible at the top.
- **Inspector/library split**: support a left-side area for contextual track/session details and browsing sounds/presets.
- **Track area organization**: tracks should have compact headers plus a main arrangement area with regions/clips.
- **Smart controls**: expose high-value macro controls for a selected instrument/effect rather than forcing users into every advanced parameter.
- **Channel strip workflow**: plug-ins can be added, replaced, moved, copied, and removed from a channel strip; the UI should make insert order and slot ownership obvious.
- **Preset browsing**: instruments and effects benefit from searchable/explorable preset browsers, especially during composition.
- **Drum production surface**: Drum Machine Designer-style kit controls and pad controls are a useful precedent for MIDAS beat workflows.
- **Multi-output instruments**: long term, a drum kit or instrument may route sounds individually into mixer channels.
- **Effects categories**: dynamics, EQ, metering, delay, reverb, pitch, MIDI effects, and multi-effects are useful browser categories.
- **Control surfaces**: hardware devices commonly expose faders, rotary knobs, buttons, displays, fader banks, automation modes, and plug-in control.

## MIDAS Adaptation

- Keep the current cosmic/purple MIDAS identity and beat-workspace emphasis.
- Use Logic as a guide for clarity and refinement: stable top control bar, clean inspector/browser affordances, readable channel strips, and selected-track smart controls.
- Add smart-control style macro panels only after selected plugin/channel state is stable.
- Keep control-surface support as a future backend issue, but design mixer strips and selected controls so they could map to hardware later.
- Treat multi-output instrument routing as future scope; do not build routing topology until the backend explicitly supports it.

## Current Priority Translation

1. Header/control bar should become the stable cockpit for project, transport, tempo/key, and device/runtime status.
2. Left browser should evolve toward Library plus searchable presets/sounds/plugins.
3. Center workspace should eventually distinguish track headers from arrange/playlist content.
4. Right mixer/effects should expose channel strips, insert order, and selected slot details clearly.
5. Later: smart controls, drum kit/pad surface, control-surface mapping, multi-output instrument routing.

## Guardrails

- Do not copy Logic's visual design or exact layout.
- Do not implement control-surface support, smart controls, multi-output routing, or deep instrument/effect editors until selected by scoped issues.
- Keep the first screen operatable against the fallback bridge.
