# Release checklist

Before tagging a new Aura release:

- [ ] `pytest -q` is green.
- [ ] `scripts/smoke-test.sh` is green.
- [ ] `omarchy plugin validate .` passes on Omarchy.
- [ ] QML panel/widget tested on a real Quattro session.
- [ ] Local-only mode verified with networking disabled.
- [ ] Weather auto/manual/off modes tested separately.
- [ ] Material You transition verified with at least three wallpapers.
- [ ] NVIDIA telemetry and Auto-Protect verified on the real test machine.
- [ ] Keyboard sync and manually-off behavior verified.
- [ ] Optional systemd guard start/stop/uninstall verified.
- [ ] `CHANGELOG.md`, manifest version and docs agree.
- [ ] Marketplace security-sensitive capability changes reviewed.
- [ ] Create/tag the release only after the test branch is merged.
