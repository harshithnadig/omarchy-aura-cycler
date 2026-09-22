# Codex real-system verification prompt

Use this repository's `audit-hardening-v1.4` branch. Your job is verification and narrowly scoped fixes, not redesign.

1. Run `pytest -q`, `scripts/smoke-test.sh`, and `omarchy plugin validate .`.
2. Run `bin/aura-cycler doctor` and save relevant output.
3. Test the bar widget and panel in the real Omarchy/Hyprland session; confirm the tooltip shows scene, theme scope, favorite status, history count and GPU state correctly.
4. Test local wallpaper rotation with weather/location and streaming off.
5. Test `location auto` and one manual location separately.
6. Verify Material You recoloring and all `theme-scope` modes (`shell`, `terminals`, `editors`, `all`).
7. Verify history/undo and favorites, including restoring an older wallpaper.
8. Apply each manual scene (`focus`, `gaming`, `battery`, `ambient`) and confirm none silently enables weather or online wallpaper downloads.
9. Verify NVIDIA telemetry and Auto-Protect under a safe reproducible GPU load; confirm the daemon remains alive while expensive cycling pauses.
10. Verify keyboard sync/off behavior without forcing a manually-off backlight on.
11. Verify fullscreen atmospheric effects pause/resume.
12. Verify optional systemd supervision and uninstall cleanup.

For every failure: reproduce it, identify the smallest cause, add/update a regression test where practical, and push the smallest compatible fix to this branch. Do not merge to `master`, remove features, or perform a broad refactor unless a reproducible failure requires it.
