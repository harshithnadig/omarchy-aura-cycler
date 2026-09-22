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

Then test the actual Omarchy session in this order:

1. **Upgrade/migration safety** — preserve a copy of the current v1.3 Aura state, launch v1.4, and confirm existing interval/blur/weather/custom-folder preferences survive. Confirm `config_version` becomes `2` and private config remains mode `0600`.
2. **Native Omarchy settings bridge** — change interval, blur, weather sync, online streaming, atmospheric effects, keyboard sync and theme scope through Omarchy's widget settings UI. Confirm `bin/aura-cycler status-json` reflects each change. Then change the same settings through Aura CLI/panel controls and confirm Omarchy shell settings reflect the new values after reload.
3. **Bar/panel regression** — test the bar widget and existing panel controls; confirm tooltip scene/theme-scope/favorite/history/GPU state is correct and the new `BarWidget.qml -> BarWidgetImpl.qml` bridge causes no layout or lifecycle regression.
4. **Offline/privacy mode** — test local wallpaper rotation with weather/location and streaming off. Verify no weather/location requests occur while location/weather are disabled.
5. **Location/weather** — test `location auto`, manual coordinates, stale weather fallback and unavailable weather separately. No fake temperatures or `(0,0)` coordinates.
6. **Material You/theme scopes** — verify recoloring and all `theme-scope` modes (`shell`, `terminals`, `editors`, `all`) with representative applications already open.
7. **History/favorites/scenes** — test previous/undo, numbered restore, favorites and every manual scene (`focus`, `gaming`, `battery`, `ambient`). Confirm scenes never silently enable weather or online wallpaper downloads.
8. **Backup/recovery** — create a normal backup and verify location data is redacted; create a private backup; change several settings; restore and confirm state returns correctly and a pre-restore snapshot is created. Test `reset --keep-favorites --keep-folders`. In a disposable copy of the state file, test malformed JSON recovery and confirm the corrupt file is preserved rather than deleted.
9. **GPU** — verify NVIDIA telemetry and Auto-Protect under a safe reproducible GPU load; confirm the public daemon remains alive while expensive cycling pauses.
10. **Keyboard** — verify keyboard sync/off behavior without forcing a manually-off backlight on, and verify `keyboard sync-off` persists.
11. **Fullscreen effects** — verify atmospheric effects pause/resume for fullscreen Hyprland clients.
12. **systemd/uninstall** — verify optional systemd supervision uses the public `bin/aura-cycler` entrypoint and uninstall cleanup is safe.

For every failure: reproduce it, identify the smallest cause, add/update a regression test where practical, and push the smallest compatible fix to this branch. Do **not** merge to `master`, remove features, add new features, or perform a broad refactor unless a reproducible failure requires it.

Do not spend quota exploring architecture alternatives. `docs/ARCHITECTURE.md` is the intended v1.4 baseline. The goal is to validate that baseline on the real machine and fix only evidence-backed failures.
