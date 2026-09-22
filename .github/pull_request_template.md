## What changed


## Why


## Test evidence

- [ ] `pytest -q`
- [ ] `scripts/smoke-test.sh`
- [ ] `omarchy plugin validate .` (when Omarchy is available)
- [ ] `bin/aura-cycler doctor` reviewed
- [ ] Real-system test if QML/GPU/keyboard/systemd behavior changed

## Security / privacy

- [ ] No new silent networking
- [ ] No new privilege escalation or package installation
- [ ] User-owned files are not deleted or overwritten unexpectedly
- [ ] Location/private state remains redacted or owner-only as appropriate

## Compatibility

- [ ] Existing public CLI behavior preserved or migration documented
- [ ] Unknown future Omarchy helpers are not accidentally blocked
- [ ] Graceful degradation checked when optional hardware/commands are unavailable
