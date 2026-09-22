# Changelog

All notable Aura Material Cycler changes are documented here.

## [1.4.0] - 2026-09-22

### Privacy and networking
- Fresh installs are local-first: weather, atmospheric auto-effects and online wallpaper streaming no longer initiate network activity until explicitly enabled.
- Replaced the legacy plain-HTTP IP location lookup with HTTPS IP geolocation.
- Added `location off`, `location auto`, and `location manual <lat> <lon> [city]`.
- Weather state now distinguishes live, cached, stale, disabled and unavailable data.
- Removed fake fallback weather values and the `(0, 0)` coordinate fallback.
- Aura config is persisted owner-only (`0600`) because it may contain location data.
- Added privacy status and redacted-by-default config export; manual coordinates are only shown with explicit private/full output.

### Stable configuration foundation
- Added schema-versioned main config (`config_version: 2`) with explicit/idempotent migrations.
- Added an owner-only process lock for config writes.
- Added conflict-aware stale-save merging so unrelated concurrent Aura updates are preserved rather than silently overwritten.
- Malformed config JSON is preserved as `aura-cycler-config.corrupt-<timestamp>.json` before Aura recovers privacy-safe defaults.
- Added native Omarchy `barWidget.defaults` + `barWidget.schema` for interval, blur, weather, streaming, effects, keyboard sync and theme scope.
- Added a bidirectional native-settings bridge through the supported Omarchy `setBarWidget` IPC.
- Existing v1.3 preferences are protected from untouched v1.4 manifest defaults during first migration.
- Added owner-only `backup`, `restore` and `reset`; restore creates a pre-restore safety snapshot and normal backups redact private location/weather state.

### Reliability
- Preserved the v1.3 engine as `bin/aura-cycler-core`, moved hardening into `bin/aura-cycler-runtime`, kept user-facing features in `bin/aura-cycler-control`, and made `bin/aura-cycler` the only executable public entrypoint.
- Added import-only `bin/aura-config.py` so every normal Aura invocation installs the same config/migration/recovery policy before feature code runs.
- Corrected theme staging rollback so a failed `omarchy-theme-set-templates` run restores the previous staging directory.
- Added XDG-aware Aura-owned state/cache/config paths while retaining compatibility with the standard Omarchy layout.
- Added migration for the previous state-file location.
- Added read-only `doctor` diagnostics and repository smoke checks.
- CI enforces that internal core/runtime/control/config layers are not executable.

### Wallpaper workflow
- Added owner-only wallpaper history capped at 100 transitions with consecutive duplicate collapse.
- Added previous/undo restore and numbered history restore.
- Added local wallpaper favorites with numbered restore/removal.
- Added safe palette-cache inspection and pruning that never deletes wallpaper directories.

### Theme control and scenes
- Added `theme-scope shell|terminals|editors|all` to control known post-theme application refresh helpers while always allowing unknown future subprocesses.
- Added manual `focus`, `gaming`, `battery`, and `ambient` scenes.
- Scenes intentionally never enable weather or online wallpaper networking on their own.

### GPU protection
- Auto-Protect no longer depends on systemd to suspend wallpaper/theme work.
- The daemon remains alive during critical GPU pressure and skips expensive cycling until pressure returns to nominal.
- Added DRM/sysfs telemetry fallback for AMD and Intel GPUs where the kernel exposes usable metrics.
- NVIDIA remains supported through `nvidia-smi`.

### Keyboard
- Added persistent `keyboard sync-on` / `keyboard sync-off`.
- Clarified that RGB color sync requires RGB-capable hardware; monochrome keyboard backlights only expose brightness.

### Plugin quality
- Marked the bar widget `allowMultiple: false`.
- Split the bar into `BarWidget.qml` (native-settings bridge) and `BarWidgetImpl.qml` (proven UI/behavior).
- GitHub Actions now validates the locked dependency set on Python 3.12 and Python 3.14.
- CI covers Python syntax, manifest/settings contract, regression tests, repository smoke checks and QML lint where available.
- Added runtime privacy/regression tests plus control-plane tests for history, favorites, scenes, theme scopes, diagnostics and cache boundaries.
- Added dedicated regression tests for config migration, corruption recovery, concurrent stale-save merging, native settings bounds, backup permissions/redaction, restore safety snapshots and migration-default preservation.
- Added `SECURITY.md`, `CONTRIBUTING.md`, release checklist, architecture/privacy/testing docs, issue templates and PR template.
- Added a focused Codex real-system verification packet so hardware/QML fixes are based on reproduction rather than guesses.

## [1.3.0] - 2026-09

- GPU-aware performance guard.
- Hardened wallpaper downloads and daemon process validation.
- Owner-controlled systemd service guard.
- Dependency lockfile and security regression tests.

## [1.2.0] - 2026-09

- Atmospheric rain, thunder, snow, sun, stars and fog effects.
- Hyprland fullscreen auto-pause.
- Interactive atmospheric controls.

## [1.1.x] - 2026-09

- Interactive panel.
- Live weather adaptation.
- Custom wallpaper folders.
- Material You palette and desktop theme synchronization.
