# Testing Aura Material Cycler

## Automated tests

```bash
python -m pip install --require-hashes -r requirements.lock
python -m pip install pytest
pytest -q
python -m py_compile bin/aura-cycler bin/aura-cycler-runtime bin/aura-cycler-core bin/aura-cycler-service-guard
scripts/smoke-test.sh
```

GitHub Actions runs the same portable checks on pushes and pull requests.

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
bin/aura-cycler previous
bin/aura-cycler favorite
bin/aura-cycler favorites list
bin/aura-cycler theme-scope shell
bin/aura-cycler next
bin/aura-cycler theme-scope all
bin/aura-cycler scene apply focus
bin/aura-cycler scene apply gaming
bin/aura-cycler scene apply battery
bin/aura-cycler scene apply ambient
```

Then verify the QML panel/widget, bar tooltip control-plane state, fullscreen atmospheric pause, Material You transition, NVIDIA telemetry, keyboard sync, Auto-Protect, optional systemd unit, and uninstall cleanup.

## Network/privacy verification

With `location off` and `stream_online` disabled, verify that normal `status-json`, history/favorites, scenes and `doctor` do not create outbound weather/location/wallpaper traffic. Test `location auto`, `location manual`, and online wallpaper streaming separately so consent boundaries are obvious.

## History/favorites verification

Cycle at least four wallpapers, inspect `history list`, restore an older item, run `previous`, favorite/unfavorite the current wallpaper, and restore a favorite. Confirm missing files fail safely rather than changing to an unexpected wallpaper.

## Theme-scope verification

Test each scope while relevant applications are open. The expected order is increasingly broad: `shell` < `terminals` < `editors` < `all`. Unknown future Omarchy helper processes must never be blocked by the scope filter.

## Failure policy

Do not merge a hardware-specific workaround based only on a guess. Reproduce it on the real system, capture the relevant command/output, add a regression test where practical, and make the smallest compatible fix.

For the exact Codex handoff, see `docs/CODEX_TEST_PROMPT.md`.
