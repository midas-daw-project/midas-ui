# PreSonus Studio One UI Pattern Reference For MIDAS

Source material:

- `240735_manual.pdf` from the provided Thomann/PreSonus manual download

Use this manual as workflow precedent, not as a visual clone target. Studio One is useful for MIDAS because it organizes complex DAW work into clear pages, leans heavily on drag-and-drop, and keeps browser, arrange, inspector, console, and plug-in workflows tightly connected.

## Patterns To Borrow

- **Task-oriented pages**: Start, Song, and Project separate document management, multitrack production, and mastering/publishing workflows.
- **Start surface**: recent files, new/open actions, device setup, and learning/news style material live together before the production workspace opens.
- **Single-window song workflow**: arranging, editing, mixing, instruments, effects, and automation are available without scattering core work across unrelated windows.
- **Quick document switching**: users can keep multiple songs/projects open and jump between them quickly.
- **Browser as action source**: files, instruments, effects, presets, and song content can be found in one browser and dragged into the arrangement, track, channel, insert rack, or console.
- **Media pool**: audio assets remain available even when events are removed from the arrangement, with commands for locate, select on track, remove, delete, and convert.
- **Inspector and track column**: selected-track input/output, channel mode, routing, and other operational settings can be adjusted from compact contextual surfaces.
- **Console modes**: the mixer can be compact for routine work, expanded when inserts/sends need more space, or detached for larger displays.
- **Instrument panel**: loaded virtual instruments have a dedicated console panel, with edit, preset save, remove, and multi-output activation behavior.
- **Insert and send racks**: effects have clear ownership, order, bypass/activate behavior, presets, chains, and send destinations.
- **FX chains**: a whole insert rack can be saved and recalled as a reusable sound.
- **Cue mixes and monitoring**: recording workflows need per-performer monitor mixes, zero-latency hardware awareness, and clear channel-level controls.
- **Control Link**: hardware mapping should become context-sensitive and visible, especially for plug-ins, faders, pans, and selected controls.
- **Project/mastering flow**: a separate mastering workspace can reference songs and update when mixes change.

## MIDAS Adaptation

- Keep MIDAS opening directly into the production shell, but let the `Start` workspace tab mature into new/open/recent/device setup rather than a decorative welcome page.
- Treat the left Browser as the primary action source for plugins, sounds, presets, packs, and reusable project content.
- Let drag-and-drop become a future interaction goal: browser item to arrange lane, plugin to mixer slot, preset to selected instrument/effect, and asset to pool.
- Keep the right Mixer as a console-style surface, with compact channel strips first and detailed insert/send racks available for the selected channel.
- Add a future media pool concept once session storage and asset references are stable.
- Use a Studio One-style instrument panel as precedent for showing loaded instruments and activating multi-output instrument channels later.
- Use FX chains as a clear near-term product concept for saving reusable insert stacks, but wait for backend plugin persistence to be firm.
- Keep hardware/control mapping as future scope, but design selected parameter views so they can eventually support Control Link-like assignment.
- Treat mastering/project publishing as long-term scope; it should not distract from the Phase 1 beat-production shell.

## Current Priority Translation

1. Default shell layout should stay clean: center workspace, left browser, right mixer, and secondary panels available through tabs or View.
2. Browser should evolve from a placeholder list into a source of actions: insert plugin, preview sound, install pack, drag/import asset, and recall preset.
3. Mixer should expose inserts as a rack, with order, bypass, load/unload, remove, and future chain save/recall.
4. Workspace should separate Start, Project, Runtime, and future Pool-style asset views with tabs or contextual panels.
5. Later: drag-and-drop, media pool, cue mixes, detached/large console mode, hardware control mapping, and mastering/project page.

## Guardrails

- Do not copy Studio One's visual design or exact page layout.
- Do not build a separate mastering/project workflow until core session, mixer, browser, and plugin workflows are stable.
- Do not implement drag-and-drop before the backend contract can describe target ownership and insertion results.
- Do not imply real hardware monitoring, cue mixes, or control-surface mapping until the backend exposes those capabilities.
- Keep fallback bridge workflows operatable and visible while backend/native development catches up.
