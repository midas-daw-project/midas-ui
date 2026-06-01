# FL Studio Training Transcript Reference For MIDAS

Source material:

- `/Users/matthewperalta/Downloads/Training for you.pdf`

This PDF contains transcripts from FL Studio training videos. Use it as workflow precedent for how a user learns, creates, edits, records, exports, and customizes inside a DAW. Do not copy transcript wording into the product; translate the teaching flow into MIDAS behavior, status text, and backend contracts.

## Training Journey

The transcript set walks a beginner through a complete DAW arc:

1. Open a project from templates or demos.
2. Understand tempo, metronome, playlist, timeline, browser, channel rack, piano roll, mixer, file/export, audio settings, MIDI settings, and themes.
3. Build a drum pattern in the channel rack.
4. Add samples from the browser or cloud library.
5. Replace samples by dropping onto existing channels.
6. Rename/recolor sounds and adjust channel volume, pan, mute, and solo.
7. Create basslines and melodies in the piano roll.
8. Place patterns in the playlist and switch between pattern playback and song playback.
9. Use loops, one-shots, key/BPM matching, hot-swap, time stretching, and fit-to-tempo.
10. Generate loop-starter ideas, lock parts, generate steps, find similar samples, and send results to the playlist.
11. Arrange with copy, duplicate, brush, slice, delete, mute, picker panel, loop selection, make unique, split by channel, merge, track naming, and alternate arrangements.
12. Add generator plug-ins to the channel rack and effect plug-ins to mixer inserts.
13. Route sounds to mixer inserts manually or automatically.
14. Use master/current insert concepts and effect stacks.
15. Create automation clips for volume, filter cutoff, panning, tempo, and plug-in parameters.
16. Record audio with input selection, monitoring, arming, record filters, countdown, loop recording, and metronome support.
17. Record MIDI from a controller or typing keyboard, select/lock target instruments, quantize, and use snap settings.
18. Export a song or selection with format, quality, tail, metadata, split mixer tracks, PDC trimming, and effects inclusion options.
19. Customize themes, grid contrast, note colors, waveform colors, animations, high visibility, toolbar layout, browser layout, and mixer view.

## Frontend Translation

- Open directly into an operatable shell, but keep a Start tab for templates, recent projects, demos, device setup, and learning-oriented next actions.
- Keep a top cockpit with project title, transport, tempo, metronome/cycle-like controls, key, device/runtime state, and a command/search field.
- Make the left Browser a source of actions: drag/add sample, replace sample, add instrument, add effect, find similar, preview, install, favorite, and filter by source.
- Separate the center workspace into clear modes:
  - Playlist/Arrangement for song structure.
  - Channel Rack for step patterns and sampled channels.
  - MIDI Notes/Piano Roll for pitched notes.
  - Loop Starter/idea generator as a future creative surface.
- Make sampled tracks first-class, not only drum rows: each sampled track should expose source, note count, mixer target, mute/solo, volume/pan, and color/name metadata.
- Treat pattern mode vs song mode as a user-visible playback scope, even if Phase 1 uses simple transport state.
- Use compact hints and next-action labels near tools, but keep them operational rather than instructional walls of text.
- Give Browser, Arrangement, Channel Rack, MIDI Notes, Mixer, Automation, Recording, Export, and Theme/Accessibility visible routes from the shell.
- Keep customization practical: grid contrast, note/waveform color, high-visibility UI, and dock/browser/mixer density should become preferences later.

## Backend And Contract Translation

- Project/session state needs distinct concepts for:
  - project metadata
  - tempo/key/time signature
  - playlist arrangement lanes
  - pattern clips
  - audio clips/loops
  - sampled instrument tracks
  - MIDI note intent
  - generator plug-ins
  - mixer inserts/effect chains
  - automation clips
  - recording inputs/takes
  - export settings
  - UI/theme/layout preferences
- Browser indexing should include provenance and safe metadata for samples, loops, plug-ins, presets, cloud/manager sources, project-local files, and user favorites.
- Loop/sample metadata should eventually include BPM, key, bars/length, one-shot vs loop, source, tags, and fit-to-tempo/stretch warnings.
- Mixer routing contracts should support channel-to-insert assignment, automatic next-free insert routing, master/current insert concepts, and effect-chain order.
- MIDI contracts should support selected target instrument, locked MIDI input target, note pitch/start/length/velocity, quantization settings, and snap-grid intent.
- Recording contracts should keep audio input selection, monitoring, record arm, record filter, countdown, loop recording, and take state separate from playback/render truth.
- Export contracts should distinguish full song vs selected range vs selected pattern, and include format, quality, tail handling, split stems, effects inclusion, metadata, and destination.

## Near-Term MIDAS Opportunities

- Extend the current sampled-track MIDI scaffold into a real lane workflow tied to backend note contracts.
- Add a visible playback-scope toggle that makes `pattern` vs `song` intent clear.
- Add Browser item actions for `Add to Channel Rack`, `Replace Selected Sample`, `Add Generator`, and `Add Effect to Mixer Slot`.
- Add a lightweight picker panel for current project assets: patterns, samples, audio clips, plug-ins, automation clips, and recordings.
- Add route-to-mixer controls on sampled tracks and channel rack rows.
- Add export planning issues before implementing render output, because export reaches audio-engine, session, and mixer concerns.

## Tracking Issues

- Pattern/song scope and Browser action UI: <https://github.com/midas-daw-project/midas-ui/issues/14>
- Pattern/song scope and Browser action facade: <https://github.com/midas-daw-project/midas-core/issues/6>
- Pattern/song scope and Browser action contracts: <https://github.com/midas-daw-project/shared-contracts/issues/6>
- Sampled-track MIDI lane workflow: <https://github.com/midas-daw-project/midas-ui/issues/13>
- Sampled-track MIDI backend persistence: <https://github.com/midas-daw-project/midas-core/issues/5>
- Sampled-track MIDI contracts: <https://github.com/midas-daw-project/shared-contracts/issues/5>

## Guardrails

- Do not clone FL Studio visuals, wording, branding, or exact interaction language.
- Do not imply cloud catalog, plug-in installation, sampler playback, recording, automation, or export is implemented until backend contracts exist.
- Keep frontend scaffolds explicit when they are local-only and not persisted.
- Keep proprietary formats and vendor assets read-only.
