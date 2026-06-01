# Image-Line / FL Studio Workflow For MIDAS

Source material:

- `/Users/matthewperalta/Documents/Image-Line`

This folder is both an FL Studio project area and a content-library area. Unlike REAPER `.RPP`, FL Studio `.flp` files are binary project files, so MIDAS should treat them as preview-first imports owned by backend parsing/facade code. The frontend should not parse binary `.flp` files directly.

## Observed Library Shape

- FL Studio project files: `35` `.flp` files, including:
  - `FL Studio/Projects/RENT DUE/RENT DUE.flp`
  - `FL Studio/Projects/Project_1/Project_1.flp`
  - `FL Studio/Projects/Untitled/Untitled.flp`
  - multiple autosave/backup `.flp` files
- Project-local audio exists under `FL Studio/Projects/RENT DUE/Audio`.
- FLP headers identify Image-Line project chunks such as `FLhd` and `FLdt`.
- Detected FL Studio version strings include `25.2.3.4889` and `25.2.5.5055`.
- String previews show plugin/content references such as `Arksun Cityscape`, `Punch It`, and FL scratch/gate preset names.
- FLEX content is present under `FLEX/Packs`, with `47` `.preset` pack index files.
- FLEX pack indices are plain text lists of preset names, including `Hard 808s`, `Essential Pianos`, `Chill-Lo-Fi`, `General Midi Library`, `Analog Monsters by UVI`, and other pack names.
- Factory/mobile data includes samples, shader/data resources, languages, templates, and many FL Studio preset/resource formats.

## User Workflow To Create

1. User chooses `Open FL Studio Project` or drags an `.flp` file into MIDAS.
2. MIDAS requests an FL project preview from the backend:
   - source path
   - detected FL Studio version
   - project name
   - project-local audio folder
   - project audio count
   - visible strings/preset/plugin hints, where safe
   - unsupported binary chunks/warnings
3. MIDAS shows an import preview before creating a session.
4. User confirms `Create MIDAS Session`.
5. MIDAS creates a native session from supported project-level settings and provenance metadata.
6. Unsupported binary state remains warnings; the original `.flp` is never modified.

## FLEX / Content Library Workflow

1. User adds `/Users/matthewperalta/Documents/Image-Line` as a library root.
2. MIDAS indexes supported content without copying vendor assets:
   - FLEX pack names
   - preset names from plain-text `.preset` files
   - audio samples under factory/mobile data
   - project-local audio folders
3. Browser presents Image-Line/FLEX as a source group:
   - Packs
   - Presets
   - Samples
   - Projects
   - Backups
4. User can preview/index metadata first; actual sample playback/import is a later scoped workflow.

## Import Preview Contract Needs

The backend/facade should expose a small project preview DTO before any session mutation:

```text
FlStudioProjectPreview
  source_path
  project_name
  detected_format
  fl_studio_version
  project_audio_path
  project_audio_count
  backup_count
  visible_plugin_or_preset_hints[]
  warnings[]
```

For the content library, MIDAS should expose a separate browser/index DTO:

```text
ImageLineLibraryPreview
  root_path
  flp_count
  flex_pack_count
  flex_preset_count
  audio_sample_count
  project_audio_count
  top_level_groups[]
  warnings[]
```

## Tracking Issues

- Frontend Image-Line preview workflow: <https://github.com/midas-daw-project/midas-ui/issues/11>
- Core Image-Line/FL Studio preview facade: <https://github.com/midas-daw-project/midas-core/issues/3>
- Public Image-Line/FL Studio preview DTOs: <https://github.com/midas-daw-project/shared-contracts/issues/3>
- Local production library metadata: <https://github.com/midas-daw-project/workspace-modules/issues/2>

## Guardrails

- Do not parse `.flp` binary project files inside PySide widgets.
- Do not overwrite or mutate `.flp` files, backups, or Image-Line content.
- Do not copy vendor sample/preset assets into the MIDAS repo.
- Do not claim full FL Studio compatibility until patterns, playlist data, mixer routes, plugin state, automation, and audio clips have scoped support.
- Keep FL project provenance separate from MIDAS session truth.
