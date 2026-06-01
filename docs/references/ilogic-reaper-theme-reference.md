# I Logic V2 REAPER Theme Reference For MIDAS

Source material:

- `I Logic V2 Public.ReaperThemeZip`
- `Screenshot 2026-05-31 at 4.48.13 PM.png`

Use this local theme package as visual precedent only. Do not copy or bundle the theme PNG assets into MIDAS unless we later confirm licensing and intentionally add them as third-party assets.

## What The Theme Contains

- REAPER theme definition: `I Logic V 2.0 Public.ReaperTheme`
- WALTER layout file: `I Logic V 2.0/rtconfig.txt`
- Hundreds of PNG resources for transport, track control panel, mixer control panel, meters, FX/send lists, toolbar states, automation states, MIDI editor pieces, and bus/separator layouts.
- Alternate layouts for bus tracks, separators, and a small transport.

## Patterns To Borrow

- **Calm DAW chrome**: dark neutral panel surfaces with restrained highlight edges keep the workspace professional and readable.
- **Arrangement-first default**: the screenshot makes the timeline/arrange grid the dominant surface, with side controls supporting it rather than competing for attention.
- **Top transport/status band**: transport buttons, time/beat display, tempo, signature, rate, global options, selection, and monitor status live in one horizontal cockpit.
- **Left toolbar and track inspector**: common actions sit in a compact icon grid above the selected track/master controls.
- **Master/selected-track control block**: mute, solo, routing, insert, level, pan, and record/monitor controls are visible as compact operational controls.
- **Empty workspace clarity**: an empty project still looks intentional because timeline rulers, grid lines, scrollbars, and add-track affordances remain visible.
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
- Let the center arrangement become visually dominant by default; browser and mixer should support it, collapse, or dock cleanly instead of shrinking it too aggressively.
- Move toward a clearer top cockpit: transport cluster, large position display, tempo/key/signature, device state, and status/hints.
- Add a left inspector/tool strip concept for selected lane/channel controls before exposing deep browser or debug content.
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
