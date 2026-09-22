# Security and privacy

Aura Material Cycler is a user-session appearance plugin. It deliberately avoids silent package installation, privilege escalation, and remote-script execution.

## Trust boundaries

- Wallpaper downloads and remote JSON are bounded and validated before publication/use.
- Remote wallpaper identifiers are sanitized and cache destinations are contained under Aura's cache/data directory.
- Fresh v1.4 installs keep weather/location and online wallpaper streaming disabled until explicitly enabled.
- Automatic IP geolocation uses HTTPS; manual location can avoid IP geolocation entirely.
- Config/location, history and favorites state is owner-only (`0600`).
- `doctor` is read-only and performs no network requests.
- Privacy/config output redacts coordinates by default.
- GPU Auto-Protect changes Aura's own cycling state; it does not terminate unrelated GPU workloads.
- The optional systemd guard validates the plugin id, ownership, real path and executable before running it.
- PID-based daemon stop validates process identity before signaling.

## User-owned data

Aura maintenance commands do not recursively delete configured wallpaper folders. Palette-cache pruning is limited to Aura-generated palette JSON. Local wallpaper paths may still reveal private directory names; review diagnostic output before sharing it publicly.

## Network-capable features

Network access can occur only through explicitly enabled weather/location or online wallpaper streaming paths. Local wallpaper rotation, Material You palette extraction, history/favorites, manual scenes, theme scopes and diagnostics are local.

## Reporting

For a security-sensitive bug, avoid posting secrets, exact private location coordinates, API keys, or other sensitive local data in a public issue. Provide a minimal reproduction and redact private paths/location data where possible.

For normal reproducible bugs, use the repository bug-report template and include `bin/aura-cycler doctor` output after reviewing it for local paths you do not want to publish.

## Dependency policy

Python analysis dependencies are pinned with hashes in `requirements.lock`. Aura does not install them automatically during plugin startup.

## Release policy

The `audit-hardening-v1.4` branch is a test branch. Do not treat an automated CI pass as proof of real GPU, keyboard, Quickshell, Hyprland or systemd behavior; those boundaries require the real-system release checklist before merge/tag/marketplace revalidation.
