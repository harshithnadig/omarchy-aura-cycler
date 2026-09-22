## What changed


## Why


## Test evidence

- [ ] `pytest -q`
- [ ] `scripts/smoke-test.sh`
- [ ] `omarchy plugin validate .` (when Omarchy is available)
- [ ] Real-system test if hardware/QML/systemd behavior changed

## Security / privacy

- [ ] No new silent networking
- [ ] No new privilege escalation or package installation
- [ ] User-owned files are not deleted or overwritten unexpectedly
