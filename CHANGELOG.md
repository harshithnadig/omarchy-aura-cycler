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

### Reliability
- Preserved the v1.3 engine as `bin/aura-cycler-core`, moved hardening into `bin/aura-cycler-runtime`, and made `bin/aura-cycler` the small public control plane.
- Corrected theme staging rollback so a failed `omarchy-theme-set-templates` run restores the previous staging directory.
- Added XDG-aware Aura-owned state/cache/config paths while retaining compatibility with the standard Omarchy layout.
- Added migration for the previous state-file location.
- Added read-only `doctor` diagnostics and repository smoke checks.

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
- Added GitHub Actions CI covering dependency install, syntax, manifest validation, regression tests, smoke checks and QML lint where available.
- Added runtime privacy/regression tests plus control-plane tests for history, favorites, scenes, theme scopes, diagnostics and cache boundaries.
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
