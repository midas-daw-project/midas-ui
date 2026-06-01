# REAPER RPP Starter Workflow For MIDAS

Source material:

- `/Users/matthewperalta/Documents/REAPER Media/Untitled.RPP`

This file is a useful baseline because it represents a clean REAPER project before tracks, items, or effects have been added. MIDAS should treat it as an import/open workflow for a new arrangement-first session, not as a finished song.

## Observed Project Shape

- REAPER version: `7.73/macOS-arm64`
- Project state: unsaved/untitled empty project
- Sample rate: `48000`
- Tempo/signature: `100 BPM`, `4/4`
- Play rate: `1.0`
- Selection: none
- Cursor: start of project
- Media path: `Media`
- Recording mode: normal project recording path/config present
- Metronome: enabled config with `ABBB` pattern and 4-beat length
- Master: stereo master output, volume `1.0`, no mute/solo
- Arrangement: ruler/grid/timeline configured, no tracks, no items, no FX chains

## User Workflow To Create

1. User chooses `Open REAPER Project` or drags an `.RPP` file into MIDAS.
2. MIDAS parses the project header and shows an import preview:
   - project name/path
   - sample rate
   - tempo and time signature
   - media folder
   - track count
   - item/media count
   - FX count
   - unsupported features, if any
3. User confirms `Create MIDAS Session`.
4. MIDAS creates a new session using the REAPER project settings:
   - header/cockpit shows project name, `100 BPM`, `4/4`, `48 kHz`
   - arrangement opens at bar `1.1.00`
   - master channel exists
   - no user tracks are created because the source file has none
   - browser remains available for adding sounds/plugins
   - mixer shows master plus starter channel affordances
5. MIDAS marks the session as imported-from-REAPER metadata, while keeping native MIDAS session persistence separate from the original `.RPP`.

## Empty Project UX

- The center arrangement should dominate the screen even when no tracks exist.
- The left inspector/tool strip should show master/selected-track controls and a clear `Add Track` affordance.
- The top cockpit should show transport, position, tempo, signature, sample rate, and runtime/device status.
- The timeline grid should remain visible so the app feels ready for work, not blank.
- Browser and mixer should support the workflow without crowding the arrangement.

## Import Contract Needs

The backend/facade should expose a small import preview DTO before any session mutation:

```text
ReaperProjectPreview
  source_path
  project_name
  reaper_version
  sample_rate
  tempo_bpm
  time_signature_numerator
  time_signature_denominator
  play_rate
  media_path
  track_count
  item_count
  fx_count
  has_tempo_envelope
  warnings[]
```

After confirmation, MIDAS should create a native session from the preview plus any parsed tracks/items that are supported. Unsupported REAPER fields should be warnings, not hard failures, for an empty starter project.

## Tracking Issues

- Frontend preview workflow: <https://github.com/midas-daw-project/midas-ui/issues/10>
- Core preview/import facade: <https://github.com/midas-daw-project/midas-core/issues/2>
- Public preview/warning DTOs: <https://github.com/midas-daw-project/shared-contracts/issues/2>
- Imported-session provenance persistence: <https://github.com/midas-daw-project/session-system/issues/1>

## Guardrails

- Do not overwrite or mutate the source `.RPP`.
- Do not claim full REAPER compatibility until tracks, media items, routing, automation, and FX chunks are explicitly supported.
- Do not import binary plugin state as runtime truth.
- Keep imported REAPER settings separate from MIDAS session truth.
- Preserve the fallback bridge path so frontend development can test this workflow before native parser support lands.
