# Classic Media Player Reference For MIDAS

Source material:

- `/Users/matthewperalta/Downloads/Winamp.png`
- User-provided summary of the classic 1997-era media player workflow

Use this as product and interaction precedent, not as a visual clone or a label inside the MIDAS UI. The important lesson is not the old pixel style; it is the compact, modular control surface for local audio, playlists, EQ, visual feedback, customization, and extensions.

## Patterns To Borrow

- **Compact playback deck**: always-available play, pause, stop, previous, next, shuffle/repeat-style controls, elapsed/remaining time, and current item state.
- **Local library ownership**: users can curate local audio files and playlists manually rather than depending on cloud or algorithmic selection.
- **Playlist as a working surface**: queue order, duration, selected item, playback position, and quick remove/reorder actions should be visible and fast.
- **Graphic EQ mindset**: frequency bands, preamp/level, presets, and bypass should be tactile controls, not typed values.
- **Spectrum/analyzer feedback**: visual energy display helps users feel playback, levels, and frequency balance at a glance.
- **Modular windows/panels**: player, playlist, EQ, visualizer, and library can be separate surfaces while still feeling like one instrument.
- **Theme/skin personalization**: users like making the tool feel theirs; MIDAS should support modern theme presets, density, contrast, and accessibility modes without copying old skins.
- **Plug-in/extensibility culture**: third-party extensions and format support were central to the reference; MIDAS should expose clean extension boundaries rather than hardcoding every capability into one panel.

## MIDAS Adaptation

- Keep MIDAS visually modern: dark neutral shell, purple accents, clear DAW controls, readable spacing, and responsive docks.
- Do not title any MIDAS feature after the source reference.
- Translate the player idea into a `Deck` or compact transport/media strip for previewing samples, loops, playlist items, and arrangement selections.
- Translate the playlist idea into a local media/pool queue for auditioning project assets, references, bounced ideas, and imported audio.
- Translate the EQ into mixer/effects macro controls: sliders for frequency bands, dials for effect parameters, bypass, presets, and selected-channel ownership.
- Translate visualizations into a spectrum/analyzer meter that can live in the mixer, inspector, or preview deck.
- Translate skins into theme/layout presets: color theme, grid contrast, high visibility, dock density, waveform/note color maps, and saved workspace layouts.
- Translate plug-ins into extension points: browser source providers, preview decoders, effect modules, analyzer modules, and future third-party processors.

## Frontend Implications

- Prefer tactile controls for music values:
  - sliders for volume, EQ bands, preview gain, rate, and scrub-like values
  - dials/knobs for pan, mix, tone, rate, feedback, send amount, and macro parameters
  - toggles for bypass, loop, shuffle, snap, and monitoring
  - lists/tables for playlist/library queues
- Add a future `Preview Deck` surface to the Browser or lower workspace:
  - current item name
  - play/stop/previous/next
  - waveform or spectrum strip
  - preview gain
  - loop toggle
  - send/add-to-project action
- Add a future `Project Playlist` or media pool surface:
  - local/project audio items
  - duration
  - source/provenance
  - preview state
  - reorder/remove/favorite
- Add a future `EQ/Analyzer` channel view:
  - 6-10 band graphic EQ scaffold
  - preset selector
  - bypass
  - spectrum response display
  - selected mixer channel binding

## Backend And Contract Implications

- Local media library contracts should describe indexed audio files, duration, format, sample rate, channels, tags, source path, and warnings.
- Preview playback contracts should be separate from arrangement/session playback.
- Playlist contracts should support queue order, selected item, loop/shuffle/repeat intent, duration, and item provenance.
- Analyzer contracts should expose lightweight meter/spectrum frames without requiring full realtime DSP graph maturity.
- EQ/effect contracts should expose parameter identity, normalized value, display value, automation eligibility, presets, bypass, and selected-channel ownership.
- Theme/layout contracts should support named presets, density, contrast, high-visibility settings, and saved dock layouts.

## Near-Term MIDAS Opportunities

- Add a modern preview deck to the Browser for auditioning sounds and loops before inserting them.
- Add a local project media queue/pool so imported and previewed audio is easy to find again.
- Upgrade mixer effects from placeholder dials to parameter-backed EQ/effect macro controls.
- Add a small spectrum/analyzer scaffold tied to selected preview or selected mixer channel.
- Add theme/layout preset planning for a modern personalization flow.

## Tracking Issues

- Frontend scaffold: https://github.com/midas-daw-project/midas-ui/issues/15
- Facade/bridge support: https://github.com/midas-daw-project/midas-core/issues/7
- Shared contracts: https://github.com/midas-daw-project/shared-contracts/issues/7
- Preview/analyzer engine support: https://github.com/midas-daw-project/audio-engine/issues/1

## Guardrails

- Do not copy the source image's exact chrome, title, logo, pixel layout, labels, or wording.
- Do not surface the reference name in the app.
- Do not imply full local playback, real spectrum data, or EQ DSP is implemented until backend contracts exist.
- Keep visualizer/analyzer work lightweight until the audio-engine can provide safe meter/spectrum data.
- Keep extension/plugin support behind explicit contracts and trust boundaries.
