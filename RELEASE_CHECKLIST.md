# Release checklist

Before tagging a new Aura release:

- [ ] `pytest -q` is green.
- [ ] `scripts/smoke-test.sh` is green.
- [ ] `omarchy plugin validate .` passes on Omarchy.
- [ ] `bin/aura-cycler doctor` has no unexplained failures.
- [ ] QML bar widget and panel tested on a real Quattro session.
- [ ] Bar tooltip correctly reports scene, theme scope, favorite/history and GPU state.
- [ ] Local-only mode verified with networking disabled.
- [ ] Weather auto/manual/off modes tested separately.
- [ ] History/previous and favorites restore tested with multiple wallpapers.
- [ ] All theme scopes tested without disrupting active applications unexpectedly.
- [ ] Focus/gaming/battery/ambient scenes tested and confirmed not to enable networking implicitly.
- [ ] Material You transition verified with at least three wallpapers.
- [ ] NVIDIA telemetry and Auto-Protect verified on the real test machine.
- [ ] Keyboard sync and manually-off behavior verified.
- [ ] Fullscreen atmosphere pause/resume verified.
- [ ] Optional systemd guard start/stop/uninstall verified.
- [ ] `CHANGELOG.md`, manifest version and docs agree.
- [ ] Marketplace security-sensitive capability changes reviewed.
- [ ] Create/tag the release only after the test branch is merged.
