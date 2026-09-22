# Changelog

All notable Aura Material Cycler changes are documented here.

## [1.4.0] - 2026-09-22

### Privacy and networking
- Fresh installs are offline by default: weather, atmospheric auto-effects and online wallpaper streaming no longer initiate network activity until explicitly enabled.
- Replaced the legacy plain-HTTP IP location lookup with HTTPS IP geolocation.
- Added `location off`, `location auto`, and `location manual <lat> <lon> [city]`.
- Weather state now distinguishes live, cached, stale, disabled and unavailable data.
- Removed fake fallback weather values and the `(0, 0)` coordinate fallback.
- Aura config is persisted owner-only (`0600`) because it may contain location data.

### Reliability
- Preserved the v1.3 engine as `bin/aura-cycler-core` and introduced a small hardened runtime front-end.
- Corrected theme staging rollback so a failed `omarchy-theme-set-templates` run restores the previous staging directory.
- Added XDG-aware Aura-owned state/cache/config paths while retaining compatibility with the standard Omarchy layout.
- Added migration for the previous state-file location.

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
- Added GitHub Actions CI.
- Added runtime privacy/regression tests.
- Added `SECURITY.md`.
- Refreshed README and development verification steps.

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
