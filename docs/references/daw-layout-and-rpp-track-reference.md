# DAW Layout And RPP Track Reference For MIDAS

Source material:

- User-provided DAW layout summary covering Arrangement, Mixer, Browser, and Piano Roll.
- Multiple user-created `.RPP` project files under `/Users/matthewperalta/Documents/REAPER Media`.

Use this as workflow precedent and track-structure evidence, not as default naming. Track names inside user projects can describe a preset, recording pass, song section, sample source, or personal workflow. MIDAS should let users name tracks freely instead of hardcoding those names into the product.

## Layout Principles

- **Arrangement** is the central timeline where sample clips, MIDI regions, and recorded audio takes live.
- **Mixer** owns track volume, panning, sends, buses, and effect chains.
- **Browser** owns samples, presets, plug-ins, instruments, and media/project discovery.
- **Piano Roll** owns MIDI note editing for selected MIDI-capable tracks.
- **Drum Machine** is an editor surface, not a second arrangement view.

## RPP Track Lessons

- Real projects often combine imported/reference audio, recorded vocal takes, doubles/adlibs, drum/sample rows, auxiliary grouping, and printed/bounced regions.
- Empty or temporary track names should not be treated as product labels.
- Specific names such as instrument names, source filenames, or section labels should remain user-owned metadata.
- MIDAS arrangement presets should provide generic lane types first: sample track, MIDI track, audio track, vocal/audio track, and bus/print track.
- Users should be able to rename every track after creation.

## Unit And Control Guidance

- Mixer volume should display in `dB`.
- Mix/blend controls should display as `%`.
- Playrate should display as a decimal from `0.00` to `2.00`; for example, `0.75` means playback at 75% speed.
- Keep these values tactile through sliders/knobs rather than typed-value-first fields.

## Guardrails

- Do not expose source DAW names or user project names as MIDAS default UI copy.
- Do not duplicate the Drum Machine as an arrangement grid.
- Do not imply that `.RPP` import, playback, or track reconstruction is complete until the backend issue track supports it.
