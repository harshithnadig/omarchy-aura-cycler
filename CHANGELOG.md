# Changelog

All notable Aura Material Cycler changes are documented here.

## [1.4.1] - 2026-09-26

### Fixed
- Apply rotated images through Omarchy's public wallpaper setter so the persistent background and live desktop stay in sync.
- Log wallpaper setter and shell IPC failures instead of silently hiding them.
- Include Omarchy's `bin` directory in the supervised service `PATH` so the setter resolves when Aura runs under systemd.

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
- Added owner-only `backup`, `restore` and guarded `reset --yes`; restore creates a pre-restore safety snapshot and normal backups redact private location/weather state.

### Reliability
- Preserved the v1.3 engine as `bin/aura-cycler-core`, moved hardening into `bin/aura-cycler-runtime`, kept user-facing features in `bin/aura-cycler-control`, and made `bin/aura-cycler` the only executable public entrypoint.
- Added import-only `bin/aura-config.py` so every normal Aura invocation installs the same config/migration/recovery policy before feature code runs.
- Added import-only `bin/aura-hardware.py` so GPU/keyboard vendor support is capability-based and isolated from the preserved engine.
- Corrected theme staging rollback so a failed `omarchy-theme-set-templates` run restores the previous staging directory.
- Added XDG-aware Aura-owned state/cache/config paths while retaining compatibility with the standard Omarchy layout.
- Added migration for the previous state-file location.
- Added bounded private log rotation to prevent unlimited `material-cycler.log` growth.
- Added read-only `doctor` diagnostics, `hardware` capability diagnostics and repository smoke checks.
- CI enforces that internal core/runtime/control/config/hardware layers are not executable.

### Wallpaper workflow
- Added owner-only wallpaper history capped at 100 transitions with consecutive duplicate collapse.
- Added previous/undo restore and numbered history restore.
- Added local wallpaper favorites with numbered restore/removal.
- Added safe palette-cache inspection and pruning that never deletes wallpaper directories.

### Theme control and scenes
- Added `theme-scope shell|terminals|editors|all` to control known post-theme application refresh helpers while always allowing unknown future subprocesses.
- Added manual `focus`, `gaming`, `battery`, and `ambient` scenes.
- Scenes intentionally never enable weather or online wallpaper networking on their own.

### Hardware portability and GPU protection
- Added runtime hardware capability detection instead of model-specific laptop/desktop branches.
- NVIDIA discovery now supports all GPUs reported by `nvidia-smi` rather than assuming a single card.
- AMD and Intel DRM/sysfs cards are discovered independently where the kernel exposes usable telemetry.
- Hybrid and multi-GPU systems expose a per-GPU list plus aggregate pressure using the highest VRAM percentage, utilization and temperature across detected GPUs.
- Auto-Protect therefore reacts to the worst detected GPU pressure instead of whichever GPU enumerates first.
- Systems with no readable GPU telemetry degrade to an unavailable state without disabling Aura's core features.
- Auto-Protect no longer depends on systemd to suspend wallpaper/theme work; the daemon remains alive during critical pressure and resumes after pressure clears.

### Keyboard portability
- Added persistent `keyboard sync-on` / `keyboard sync-off`.
- Desktop/external OpenRGB keyboards can sync even when there is no laptop-style keyboard backlight sysfs device.
- A manually-off laptop keyboard backlight remains off; Aura does not force it on.
- ASUS RGB remains supported through `asusctl` where available.
- Clarified that monochrome keyboard backlights expose brightness only and do not pretend to support RGB colors.

### Plugin quality
- Marked the bar widget `allowMultiple: false`.
- Split the bar into `BarWidget.qml` (native-settings bridge) and `BarWidgetImpl.qml` (proven UI/behavior).
- GitHub Actions validates the locked dependency set on Python 3.12 and Python 3.14.
- Updated CI to current `actions/checkout@v7` and `actions/setup-python@v7`.
- CI covers Python syntax (including the hardware adapter), manifest/settings contract, regression tests, repository smoke checks and QML lint where available.
- Added runtime privacy/regression tests plus control-plane tests for history, favorites, scenes, theme scopes, diagnostics and cache boundaries.
- Added dedicated regression tests for config migration, corruption recovery, concurrent stale-save merging, native settings bounds, backup permissions/redaction, restore safety snapshots and migration-default preservation.
- Added synthetic hardware tests for multi-GPU aggregation, AMD/Intel DRM enumeration, OpenRGB desktop keyboards, manual-off preservation and no-hardware fallback.
- Added `SECURITY.md`, `CONTRIBUTING.md`, release checklist, architecture/privacy/testing/hardware docs, issue templates and PR template.
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
