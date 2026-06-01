# Local Production Assets Reference For MIDAS

Source material:

- `/Users/matthewperalta/Documents/Image-Line`
- `/Applications/FL Cloud Plugins.app`
- `/Users/matthewperalta/Documents/iZotope`
- `/Users/matthewperalta/Documents/MDrummer`
- `/Users/matthewperalta/Documents/MPK mini IV - Logic Pro Setup Guide - v1.1.pdf`
- `/Users/matthewperalta/Documents/REAPER Media`
- `/Users/matthewperalta/Documents/Samples`

Use these local folders as workflow and library references. Do not copy third-party audio, presets, or manuals into MIDAS unless licensing and product intent are confirmed.

## Image-Line

- FL Studio project/import reference.
- Contains `.flp` projects, autosaves/backups, project-local audio, FL Studio Mobile factory data, FLEX pack/preset indexes, samples, templates, and resource files.
- MIDAS should support preview-first FL project import and separate browser indexing for FLEX/content libraries.
- See `docs/workflows/image-line-fl-studio-workflow.md`.

## FL Cloud Plugins

- External Image-Line plug-in manager reference.
- The local bundle is a macOS app, not a loadable audio plug-in bundle.
- It exposes bundle identifier `com.image-line.fl-cloud-plugins`, URL scheme `fl-cloud-plugins`, an install helper, a licensing library, and a WebKit-backed manager surface.
- MIDAS should model this as an external manager/catalog source, then scan installed AU/VST3/CLAP locations separately for plug-ins that can actually be loaded.
- See `docs/workflows/fl-cloud-plugins-manager-workflow.md`.

## iZotope

- Effect/mastering preset category reference.
- The folder currently exposes preset category directories rather than visible user preset files at the inspected depth:
  - Neutron dynamic EQ presets
  - Ozone bass control, clarity, EQ, dynamics, exciter, imager, maximizer, stabilizer, vintage modules, global presets, and more
  - Tonal Balance Control target curves
- MIDAS browser can borrow the category model for effects: module family, preset type, mastering/mix context, and target-curve style metadata.
- Backend should treat missing/empty preset folders as valid library roots with zero indexed presets, not errors.

## MDrummer

- Drum instrument, rhythm, loop, layer, and kit library reference.
- Inventory highlights:
  - `12624` `.mdloop`
  - `3476` `.mddrumset`
  - `1781` `.wav`
  - `748` `.mdrhythm`
  - `391` `.mdeffects`
- Useful groups include drumset generators, drumsets, layers, loops, rhythms, multisamples, output mappings, effects, and song structures.
- MIDAS should borrow the hierarchy for future drum browser design: Kits, Layers, Loops, Rhythms, Effects, Mappings, and Generated Patterns.

## MPK mini IV Logic Setup Guide

- Controller integration reference.
- Important workflow concepts:
  - Separate MIDI ports for performance, DAW control, plugin control, generic software control, and DIN output.
  - DAW preset selection before controlling Logic.
  - Pads support Drum Mode, Track Record, Track Solo/Mute, and Live Loops-style launching.
  - Knobs support Smart Controls, Volume/Pan, Sends, EQ, and other mode banks.
  - Transport maps to undo/redo, loop, stop/play, continue, record, quantize, overdub, and automation.
- MIDAS should design future controller mapping around explicit ports, modes, banks, selected-track focus, and visible assignment state.

## REAPER Media

- Existing project/media corpus reference.
- Inventory highlights:
  - `116` `.RPP` files
  - `4345` `.rpp-bak` backups
  - `4499` `.wav`
  - `147` `.mid`
  - `74` `.mp3`
- MIDAS should support project preview, backup awareness, media folder indexing, and read-only source provenance before deeper import.

## Samples

- MeldaProduction/MSoundFactory essentials sample library reference.
- Inventory highlights:
  - `2906` `.wav`
  - `19` `.msamples`
  - categories such as Instruments, Impacts, Morphing, MultiTextures, Noisy glitch, and Percussive
- MIDAS browser should index this as a sample library with category, instrument/family, pitch-name hints from filenames, and preview/import support later.

## Product Translation

- The Browser should become a multi-root production library, not just a plugin registry.
- Each root should expose a preview summary before indexing or importing.
- Imported projects and indexed libraries need provenance: source product, source path, detected format, scan time, counts, and warnings.
- Unsupported vendor formats should appear as warnings, not silent failures.
- The frontend should never directly parse proprietary binary project formats.

## Tracking Issue

- Local production library metadata: <https://github.com/midas-daw-project/workspace-modules/issues/2>
