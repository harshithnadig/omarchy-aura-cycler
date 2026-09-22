# Testing Aura Material Cycler

## Automated tests

```bash
python -m pip install --require-hashes -r requirements.lock
python -m pip install pytest
pytest -q
python -m py_compile bin/aura-cycler bin/aura-cycler-runtime bin/aura-cycler-core bin/aura-cycler-service-guard
scripts/smoke-test.sh
```

GitHub Actions runs the same Python checks on pushes and pull requests.

## Real Omarchy smoke test

Run these on the actual Omarchy machine before merging v1.4:

```bash
omarchy plugin validate .
bin/aura-cycler doctor
bin/aura-cycler status-json | python -m json.tool
bin/aura-cycler privacy
bin/aura-cycler location off
bin/aura-cycler next
bin/aura-cycler history list
bin/aura-cycler favorite
bin/aura-cycler favorites list
bin/aura-cycler theme-scope shell
bin/aura-cycler next
bin/aura-cycler theme-scope all
```

Then verify the QML panel/widget, fullscreen atmospheric pause, Material You transition, NVIDIA telemetry, keyboard sync, Auto-Protect, optional systemd unit, and uninstall cleanup.

## Network/privacy verification

With `location off`, verify that a normal `status-json` call does not create outbound weather/location traffic. Test `location auto` and a manual location separately.

## Failure policy

Do not merge a hardware-specific workaround based only on a guess. Reproduce it on the real system, capture the relevant command/output, add a regression test where practical, and make the smallest compatible fix.
