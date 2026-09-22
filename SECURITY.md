# Security and privacy

Aura Material Cycler is a user-session appearance plugin. It deliberately avoids silent package installation, privilege escalation, remote-script execution, and hidden telemetry.

## Trust boundaries

- `bin/aura-cycler` is the only executable Aura entrypoint; config/control/runtime/core implementation layers are import-only and CI enforces that boundary.
- Wallpaper downloads and remote JSON are bounded and validated before publication/use.
- Remote wallpaper identifiers are sanitized and cache destinations are contained under Aura's cache/data directory.
- Fresh v1.4 installs keep weather/location and online wallpaper streaming disabled until explicitly enabled.
- Automatic IP geolocation uses HTTPS; manual location can avoid IP geolocation entirely.
- Config/location, history, favorites and backup state is owner-only (`0600`).
- Config writes are serialized with an owner-only process lock and stale updates are merged against the latest state.
- Malformed config is preserved as a `.corrupt-<timestamp>.json` recovery artifact rather than silently deleted.
- `doctor` is read-only and performs no network requests.
- Privacy/config output redacts coordinates by default.
- Normal backups redact private location/weather state; `--private` must be explicit to include private config and an optional Wallhaven key.
- Restore creates an automatic pre-restore safety snapshot.
- GPU Auto-Protect changes Aura's own cycling state; it does not terminate unrelated GPU workloads.
- The optional systemd guard validates the plugin id, ownership, real path and executable before running it.
- PID-based daemon stop validates process identity before signaling.

## User-owned data

Aura maintenance commands do not recursively delete configured wallpaper folders. Palette-cache pruning is limited to Aura-generated palette JSON. Local wallpaper paths may still reveal private directory names; review diagnostic or backup output before sharing it publicly.

## Native Omarchy settings

Aura uses the supported Omarchy bar-widget settings contract and `setBarWidget` IPC. Manifest settings are treated as a UI/integration surface; Aura's private transactional config remains the canonical runtime store. Existing user config is not overwritten merely because a manifest default was injected.

## Network-capable features

Network access can occur only through explicitly enabled weather/location or online wallpaper streaming paths. Local wallpaper rotation, Material You palette extraction, history/favorites, manual scenes, theme scopes, config maintenance and diagnostics are local.

## Reporting

For a security-sensitive bug, avoid posting secrets, exact private location coordinates, API keys, private backup files, or other sensitive local data in a public issue. Provide a minimal reproduction and redact private paths/location data where possible.

For normal reproducible bugs, use the repository bug-report template and include `bin/aura-cycler doctor` output after reviewing it for local paths you do not want to publish.

## Dependency policy

Python analysis dependencies are pinned with hashes in `requirements.lock`. Aura does not install them automatically during plugin startup. CI installs the exact locked set on Python 3.12 and 3.14.

## Release policy

The `audit-hardening-v1.4` branch is a test branch. Automated CI is necessary but not sufficient proof of real GPU, keyboard, Quickshell, Hyprland or systemd behavior; those boundaries require the real-system release checklist before merge/tag/marketplace revalidation.
