# Codex real-system verification prompt

Use this repository's `audit-hardening-v1.4` branch. Your job is verification and narrowly scoped fixes, not redesign.

Start with:

```bash
git checkout audit-hardening-v1.4
pytest -q
scripts/smoke-test.sh
omarchy plugin validate .
bin/aura-cycler doctor
```

Then test the actual Omarchy session:

1. Test the bar widget and panel; confirm the tooltip shows scene, theme scope, favorite status, history count and GPU state correctly.
2. Test local wallpaper rotation with weather/location and streaming off.
3. Test `location auto` and one manual location separately.
4. Verify Material You recoloring and all `theme-scope` modes (`shell`, `terminals`, `editors`, `all`).
5. Verify history/undo and favorites, including restoring an older wallpaper.
6. Apply each manual scene (`focus`, `gaming`, `battery`, `ambient`) and confirm none silently enables weather or online wallpaper downloads.
7. Verify NVIDIA telemetry and Auto-Protect under a safe reproducible GPU load; confirm the daemon remains alive while expensive cycling pauses.
8. Verify keyboard sync/off behavior without forcing a manually-off backlight on.
9. Verify fullscreen atmospheric effects pause/resume.
10. Verify optional systemd supervision and uninstall cleanup.

For every failure: reproduce it, identify the smallest cause, add/update a regression test where practical, and push the smallest compatible fix to this branch. Do not merge to `master`, remove features, or perform a broad refactor unless a reproducible failure requires it.

Do not spend time inventing new features during this pass. The goal is to make the existing v1.4 branch reliable on the real machine with the minimum required changes.
