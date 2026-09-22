# Release checklist

Before tagging a new Aura release:

## Portable / CI gates
- [ ] GitHub Actions is green on Python 3.12 and 3.14.
- [ ] `pytest -q` is green.
- [ ] `scripts/smoke-test.sh` is green.
- [ ] Manifest defaults/schema match the runtime config keys and privacy defaults.
- [ ] Only `bin/aura-cycler` is executable; config/hardware/control/runtime/core layers remain import-only.
- [ ] Config migration, corruption recovery, stale-save merge, backup/restore and native-settings tests are green.
- [ ] Synthetic hardware tests cover multi-GPU aggregation, AMD/Intel DRM discovery, desktop OpenRGB without laptop brightness sysfs, manually-off backlight preservation and no-hardware fallback.

## Real Omarchy gates
- [ ] `omarchy plugin validate .` passes on the target Omarchy release.
- [ ] `bin/aura-cycler doctor` has no unexplained failures.
- [ ] `bin/aura-cycler hardware` matches the actual machine and does not omit a readable GPU/backend.
- [ ] Existing v1.3 config is migrated without losing interval/blur/weather/custom-folder preferences.
- [ ] Native Omarchy settings change Aura runtime state and Aura CLI changes mirror back to shell settings.
- [ ] QML bar widget and panel tested on a real Quattro session.
- [ ] Bar tooltip correctly reports scene, theme scope, favorite/history and GPU state.
- [ ] Local-only mode verified with networking disabled.
- [ ] Weather auto/manual/off modes tested separately.
- [ ] History/previous and favorites restore tested with multiple wallpapers.
- [ ] All theme scopes tested without disrupting active applications unexpectedly.
- [ ] Focus/gaming/battery/ambient scenes tested and confirmed not to enable networking implicitly.
- [ ] Material You transition verified with at least three wallpapers.
- [ ] GPU telemetry and Auto-Protect verified on the available real test hardware; vendor-specific claims are made only for backends actually tested or supported by reproducible community reports.
- [ ] Keyboard sync and manually-off behavior verified.
- [ ] If OpenRGB hardware is available, desktop/external RGB works without requiring a laptop backlight sysfs device.
- [ ] If multiple displays are available, per-screen atmosphere renders/scales correctly and remains click-through.
- [ ] Fullscreen atmosphere pause/resume verified.
- [ ] Optional systemd guard start/stop/uninstall verified.

## Recovery gates
- [ ] Normal backup is `0600` and redacts location/weather-private data.
- [ ] Private backup restores optional private state only when explicitly requested.
- [ ] Restore creates a pre-restore snapshot before changing state.
- [ ] `reset --yes --keep-favorites --keep-folders` preserves exactly those requested items.
- [ ] A deliberately malformed config is preserved as `.corrupt-<timestamp>.json` and Aura recovers safely.

## Portability claim gates
- [ ] README hardware claims match `docs/HARDWARE.md`; do not claim universal Linux support.
- [ ] Unsupported GPU/keyboard telemetry leaves core Aura behavior working.
- [ ] Hybrid/multi-GPU protection is based on worst detected pressure, not enumeration order.
- [ ] New vendor/model fixes use capability detection in `aura-hardware.py`, never hostname/model-specific branches in the core.
- [ ] Bug reports/community validation are tracked for hardware classes not physically available to the maintainer.

## Release gates
- [ ] `CHANGELOG.md`, manifest version and docs agree.
- [ ] Marketplace security-sensitive capability changes reviewed.
- [ ] Draft PR checklist is fully green and the PR is marked ready only after real-system verification.
- [ ] Merge to `master` only after all required gates above pass.
- [ ] Create/tag `v1.4.0` from the verified merge commit.
- [ ] Create GitHub Release from the v1.4.0 changelog.
- [ ] Re-submit/revalidate the exact release commit in the Omarchy marketplace if required.
