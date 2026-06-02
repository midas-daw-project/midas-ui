# Competitive DAW And Plugin Map For MIDAS

Use these products as workflow references, not visual clones. MIDAS should feel like a real DAW while staying distinct: fast beat creation, clear plugin ownership, beginner-friendly setup, and room for AI-assisted music decisions.

## Language Guardrails

- Say "session-style clip workflow," not "Ableton Session View," unless that becomes an official component name.
- Say "channel-rack-inspired beatmaking workflow," not "FL Channel Rack," unless that becomes an official component name.
- Say "inspector-style side panel," not "Logic Inspector," unless that becomes an official component name.
- Say "drag/drop browser workflow," not "Studio One Browser," unless that becomes an official component name.
- Say "advanced routing/customization inspired by pro DAWs," not "REAPER routing," unless the exact routing system exists.
- Say "third-party plugin hosting is planned/future work," not that VST3/AU/AAX hosting is already complete.
- Use status labels in UI and handoffs: Implemented, Implemented Shell, Prototype, Planned, Reference Source, Backend Required, and Working Name.

## Current Frontend Truth

- Implemented: DAW-style shell, top control bar, arrangement panel, mixer panel, session panel, transport controls, audio/debug panels, responsive window sizing, BPM control, key wheel, sample rate control, block size control, workspace mode buttons, command/search bar, plugin browser, plugin search, plugin categories, grouped plugin list, plugin details, plugin queue, tabbed plugin selection wheel, startup/onboarding window, and MIDI-note-based key detection.
- Implemented Shell: MIDAS-native insert shells can be selected, queued, and inserted in the frontend. Their DSP behavior remains backend-owned.
- Prototype/Reference: session-style clips, channel-rack-inspired beatmaking, smart controls, plugin chain presets, and collaboration surfaces.
- Backend Required: real audio DSP, audio sample key detection, tempo detection from imported loops, full recording/playback behavior, true third-party plugin hosting, cloud collaboration, stem/export analysis, and plugin format scanning/hosting.

## Creator Modes

- Producer Mode: fast beatmaking, drums, MIDI, loops, patterns, and piano-roll-style editing.
- Engineer Mode: mixer control, routing, FX chains, sends, automation, and detailed editing.
- Recording Mode: vocals, instruments, voiceovers, punch-ins, takes, monitoring, and comping.
- Performance Mode: session-style triggering, live looping, session playback, and performance control.
- Collab Mode: project members, comments, version history, roles, and shared assets.
- Master Mode: export, references, loudness checks, stems, formats, and release preparation.

## Logic Pro

- Strong pattern: polished control bar, library/inspector organization, high-quality built-in instruments/effects, loop/audio workflow, mixer clarity, and musical assistant features.
- MIDAS takeaway: keep tempo, key, transport, audio config, and project state in a stable top bar. Add a selected-track inspector and smart controls for the current instrument/effect.
- Near-term UI idea: a "Smart Controls" panel that exposes 4-8 useful macro controls for selected MIDAS insert shells.
- Official reference checked: Apple documents core interface surfaces such as tracks area, library, inspector, mixer, smart controls, loop browser, project audio browser, control bar customization, tempo, key signature, sample rate, track header controls, regions, and chord/key analysis.

## REAPER

- Strong pattern: dense arrange view, track control panels, flexible routing, dockable windows, action list, custom shortcuts, deep plugin support, render matrix, and customizable themes.
- MIDAS takeaway: mirror the structural seriousness: track headers, timeline lanes, item editing, mixer strips, FX chains, actions, dockable panels, and detailed render/export controls.
- Near-term UI idea: make each track row expose arm/mute/solo, input, FX, pan, volume, and routing entry points before adding decorative skin work.
- Official reference checked: REAPER emphasizes nested folder routing/bussing, tempo and time-signature management, take lanes, flexible multichannel routing, third-party plugin formats, customizable layouts, dockable windows, screensets, and thousands of actions assignable to keys/controllers.

## Cakewalk Sonar

- Strong pattern: traditional full DAW workflow, console/mixer depth, project-oriented production, and BandLab ecosystem continuity.
- MIDAS takeaway: keep a clear "project studio" surface for recording, editing, mixing, and mastering without forcing users into too many floating windows.
- Near-term UI idea: a console strip design with inserts, sends, ProChannel-style compact modules, and track/bus separation.
- Official/reference material checked: Cakewalk's modern docs describe Control Bar, Track View, Browser, Console View, Piano Roll, Step Sequencer, Matrix View, Tempo, Meter/Key, markers, contextual help, and routing. Legacy SONAR docs also frame the console as vertical track/bus/hardware channel strips.

## FL Studio

- Strong pattern: channel rack, step sequencer, piano roll, playlist, fast pattern creation, plugin picker, browser-first workflow, mixer routing, and beginner-friendly beatmaking.
- MIDAS takeaway: make first-time beat construction fast: browser -> channel/track -> pattern -> arrangement -> mixer.
- Near-term UI idea: improve the drum/channel rack so each lane has mute, pan, volume, mixer destination, color, and pattern steps.
- Official reference checked: FL Studio's Channel Rack holds instruments and generators, routes channel audio to mixer tracks, supports step sequences and piano-roll scores, and exposes per-channel mute, pan, volume, mixer destination, instrument button, activity/selector, and sequencer controls.
- Extra MIDAS idea: when sample metadata is available, support BPM/key-aware loop auditioning and key matching, but label audio sample detection as Backend Required until the analysis engine exists.

## Ableton Live

- Strong pattern: Session View for launching clips/scenes, Arrangement View for linear timelines, fast experimentation, live performance, and clip-level automation/warping.
- MIDAS takeaway: add a future "Ideas/Clips" workspace that can collect loops, one-shots, and scenes before committing them to the arrangement.
- Near-term UI idea: a clip launcher tab beside Arrangement, with columns for scenes and rows for tracks.

## PreSonus Studio One

- Strong pattern: single-window song workflow, Start/Song/Project thinking, drag-and-drop browser, inspector, console, insert/send racks, and clear document flow.
- MIDAS takeaway: the browser should become an action source: drag plugins to mixer slots, sounds to tracks, presets to instruments, and chains to selected channels.
- Near-term UI idea: implement browser-to-mixer-slot and browser-to-arrange-lane drag targets once backend ownership contracts are ready.

## BandLab / Collaboration Direction

- Strong pattern: cloud-accessible project workflow, beginner accessibility, project sharing, invite/collaborator concepts, and cross-device continuity.
- MIDAS takeaway: collaboration should become a first-class project surface, not a hidden sync setting.
- Future UI ideas:
  - Project members panel
  - Invite link / invite by email
  - Presence indicators on tracks and clips
  - Comments pinned to clips, tracks, and timeline positions
  - Version history and compare/restore
  - "Sync status" chip in the top bar
  - Role-based project permissions

## Waves Plugins / StudioRack

- Strong pattern: effect categories, plugin chains, vocal/drum/mastering chain presets, macros, parallel chains, multiband processing, and host-like plugin rack behavior.
- MIDAS takeaway: our plugin browser should support not just single plugins but reusable chains and macro-driven "custom plugins."
- Official reference checked: Waves describes StudioRack/StudioVerse around full plugin combinations, mix-ready chains, AI search, native CPU processing, optional SoundGrid offload, parallel processing, multiband behavior, mid/side workflows, and macro-driven custom plugin concepts.
- Near-term UI ideas:
  - Save queued insert chain as a MIDAS chain preset
  - Chain categories: Vocal, Drum Bus, 808/Bass, Master, LoFi, Guitar, Podcast/Streaming
  - Macro controls for chain-level intensity, tone, width, space, and output
  - Parallel chain lane inside an FX rack
  - Clear distinction between native MIDAS inserts, detected third-party formats, managers, shells, and unavailable plugins

## Overall MIDAS Direction

- Build the DAW shell like REAPER/Studio One: serious, dense, and operational.
- Build the creation flow like FL/Ableton: immediate, loop-friendly, pattern-friendly, and fast.
- Build the polish like Logic: clean control bar, clear library/inspector, and smart musical help.
- Build plugin workflows like Waves StudioRack: chains, macros, presets, parallel paths, and explanations.
- Build future collaboration like BandLab: shared projects, comments, roles, presence, and versions.

## Next Development Priority

Focus on track and clip realism before advanced AI, full cloud systems, or third-party plugin hosting.

1. Real track headers with arm, mute, solo, input, output, FX, pan, volume, track color, track icon, and track type.
2. Real arrangement clips with drag, resize, split, loop, rename, color, duplicate, fade handles, clip gain, and clip BPM/key metadata.
3. Inspector-style side panel that changes based on selected track, clip, or plugin.
4. Better mixer channels and FX chain UI.
5. Save/load project state.
6. Save/load FX chains.
7. Browser drag/drop into arrangement lanes or mixer slots.
8. Plugin chain presets and smart controls.
9. MIDI scale highlighting based on detected or selected project key.
10. Project intelligence panel under a working name like Oracle Panel or MIDAS Brain.

## Source Links

- Apple Logic Pro User Guide: https://support.apple.com/guide/logicpro/welcome/mac
- Cockos REAPER About / feature overview: https://www.reaper.fm/about.php
- Image-Line FL Studio Channel Rack manual: https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/channelrack.htm
- Ableton Live 12 Concepts manual: https://www.ableton.com/en/live-manual/12/live-concepts/
- Bitwig Studio User Guide: https://www.bitwig.com/userguide/latest/welcome_to_bitwig_studio/
- Waves StudioRack product/workflow page: https://www.waves.com/plugins/studiorack
