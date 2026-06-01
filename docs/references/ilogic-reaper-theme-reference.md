# I Logic V2 REAPER Theme Reference For MIDAS

Source material:

- `I Logic V2 Public.ReaperThemeZip`

Use this local theme package as visual precedent only. Do not copy or bundle the theme PNG assets into MIDAS unless we later confirm licensing and intentionally add them as third-party assets.

## What The Theme Contains

- REAPER theme definition: `I Logic V 2.0 Public.ReaperTheme`
- WALTER layout file: `I Logic V 2.0/rtconfig.txt`
- Hundreds of PNG resources for transport, track control panel, mixer control panel, meters, FX/send lists, toolbar states, automation states, MIDI editor pieces, and bus/separator layouts.
- Alternate layouts for bus tracks, separators, and a small transport.

## Patterns To Borrow

- **Calm DAW chrome**: dark neutral panel surfaces with restrained highlight edges keep the workspace professional and readable.
- **Thin active-state accents**: selected track and panel states use small bright edge treatments rather than large filled blocks.
- **Compact transport buttons**: play, stop, record, pause, repeat, and navigation controls are icon-first and grouped tightly.
- **Track control hierarchy**: track index/name, mute, solo, record arm, monitor, FX, IO, volume, pan, and meter all have stable positions.
- **Responsive track layouts**: controls appear or collapse based on available track height/width rather than forcing every control to remain visible.
- **Narrow mixer strips**: mixer channels are dense vertical strips with meter, fader, name, FX/send areas, mute/solo, and pan arranged predictably.
- **Visible meter grammar**: green/yellow/orange/red meter bands make level and clipping state scannable.
- **Dedicated bus/separator layouts**: non-audio organizational tracks need slimmer visual treatments.
- **FX/send list zones**: insert and send slots are visually distinct areas in the mixer strip rather than generic form rows.
- **Small colored state badges**: mute, solo, record, and active states are clear but not oversized.

## MIDAS Adaptation

- Keep MIDAS purple/cosmic identity, but borrow the theme's restraint: dark neutral foundations, thin bright accents, and fewer large filled panels.
- Make transport controls more icon-like over time while retaining text labels until the user flow is obvious.
- Refine the mixer toward channel-strip grammar: compact strip, meter, fader/gain, mute/solo/bypass, insert rack, and selected-channel detail.
- Add selected-track/selected-channel edge accents instead of heavy background changes.
- Treat bus/separator tracks as future workspace metadata once lane/module contracts exist.
- Use responsive reveal/collapse behavior for track controls and mixer details as the PySide shell matures.

## Guardrails

- Do not import the theme PNGs into the repo or app.
- Do not clone the exact Logic-inspired visual skin.
- Do not spend Phase 1 effort on full WALTER-style layout configurability.
- Keep the UI operatable through existing fallback/native bridge contracts.
