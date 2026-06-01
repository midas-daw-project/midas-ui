# FL Cloud Plugins Manager Workflow For MIDAS

Source material:

- `/Applications/FL Cloud Plugins.app`

This application is a macOS manager for Image-Line/FL Cloud instruments and effects. It is not itself an AU, VST3, or CLAP plug-in bundle, so MIDAS should treat it as an external catalog/provenance source and scan installed plug-in locations separately for loadable plug-ins.

## Observed App Shape

- Bundle name: `FL Cloud Plugins`
- Bundle identifier: `com.image-line.fl-cloud-plugins`
- App bundle type: `APPL`
- Minimum macOS version: `10.15`
- URL scheme: `fl-cloud-plugins`
- Main executable: universal `x86_64` and `arm64` Mach-O executable
- Install helper: universal `x86_64` and `arm64` Mach-O executable
- Licensing library: universal `x86_64` and `arm64` dynamic library
- Linked framework signal: `WebKit.framework`, suggesting a web-backed manager/catalog surface
- Offline page title: `Instruments and Effects`
- Offline page message indicates internet connectivity is required to use the application
- Code signing identifier: `com.image-line.fl-cloud-plugins`
- Code signing team identifier observed locally: `N68WEP5ZZZ`

## User Workflow To Create

1. User adds `/Applications/FL Cloud Plugins.app` as an external plug-in manager source.
2. MIDAS reads safe app-bundle metadata:
   - app path
   - bundle name
   - bundle identifier
   - URL scheme
   - supported architectures
   - helper/licensing component presence
   - code signing team identifier, where available
   - connectivity or external-manager warnings
3. MIDAS shows the source in the Browser as `FL Cloud Plugins`, grouped under external managers.
4. User can open the manager from MIDAS when they need to install, update, or authenticate Image-Line cloud plug-ins.
5. MIDAS scans the normal installed plug-in locations separately for actual AU/VST3/CLAP plug-ins after installation.
6. MIDAS links discovered installed plug-ins back to `FL Cloud Plugins` as provenance when metadata supports it.

## Browser UX

- Show `FL Cloud Plugins` as an external source, not as a loadable plug-in.
- Provide actions such as:
  - `Open Manager`
  - `Refresh Installed Plug-ins`
  - `Show Managed Plug-ins`, once backend provenance exists
- Show a clear status if the manager is offline, unavailable, unsigned, missing helper components, or requires login.
- Avoid implying that MIDAS can load the `.app` bundle into the audio graph.
- Keep cloud/authentication state distinct from local installed plug-in availability.

## Contract Needs

The backend/facade should expose a small preview DTO before any browser index mutation:

```text
ExternalPluginManagerPreview
  source_path
  display_name
  bundle_identifier
  bundle_type
  url_schemes[]
  supported_architectures[]
  has_install_helper
  has_license_engine
  code_signing_identifier
  code_signing_team_identifier
  requires_network_hint
  manager_kind
  warnings[]
```

Installed plug-in scanning should stay separate:

```text
InstalledPluginPreview
  plugin_path
  plugin_format
  plugin_name
  manufacturer
  version
  architectures[]
  provenance_source_id
  scan_status
  warnings[]
```

## Tracking Issues

- Frontend FL Cloud manager source workflow: <https://github.com/midas-daw-project/midas-ui/issues/12>
- Core external plug-in manager preview facade: <https://github.com/midas-daw-project/midas-core/issues/4>
- Public external plug-in manager DTOs: <https://github.com/midas-daw-project/shared-contracts/issues/4>
- Local production library metadata: <https://github.com/midas-daw-project/workspace-modules/issues/2>

## Guardrails

- Do not copy FL Cloud app resources, binaries, icons, fonts, or offline page contents into the MIDAS repo.
- Do not attempt to load `/Applications/FL Cloud Plugins.app` as an audio plug-in.
- Do not bypass Image-Line authentication, licensing, install helpers, or online requirements.
- Do not scrape cloud catalog contents from the app bundle.
- Do not treat cloud-manager availability as installed plug-in availability.
- Keep all plug-in loading behind backend/native host contracts.
