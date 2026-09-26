# Aura Material Cycler for Omarchy

[![Omarchy Plugin](https://img.shields.io/badge/Omarchy-plugin-blue)](https://omarchy.org)
[![CI](https://github.com/harshithnadig/omarchy-aura-cycler/actions/workflows/ci.yml/badge.svg)](https://github.com/harshithnadig/omarchy-aura-cycler/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Aura is an adaptive appearance runtime for **Omarchy 4 / Quattro**: dynamic wallpapers, local Material You palettes, optional live-weather atmosphere, keyboard lighting integration, GPU-aware protection, wallpaper history/favorites and scriptable desktop scenes.

> **v1.4 hardening branch:** fresh installs are local-first. Weather/location and online wallpaper downloads require explicit opt-in.

![Aura Material Cycler](preview.png)

## Highlights

- Dynamic local wallpaper rotation + optional Wallhaven/Bing streaming.
- On-device Material You palette extraction and Omarchy theme generation.
- Rain, thunder, snow, sun, stars and fog with fullscreen-aware pausing.
- Runtime hardware adaptation for laptops/desktops instead of machine-model checks.
- RGB/keyboard integration that respects manual brightness/off state and supports OpenRGB desktop keyboards without laptop backlight sysfs.
- NVIDIA + AMD + Intel GPU discovery, including hybrid/multi-GPU aggregation where telemetry is exposed.
- GPU Auto-Protect that reacts to the worst detected GPU pressure and pauses expensive Aura work without killing the daemon.
- History, undo, favorites, theme scopes and manual focus/gaming/battery/ambient scenes.
- Native Omarchy widget settings for interval, blur, weather, streaming, effects, keyboard sync and theme scope.
- Versioned, locked, recoverable config with backup/restore/reset tooling.
- Bounded downloads/JSON, path containment, process identity checks and owner-only private state.
- Bounded private logs with automatic rotation so long-running sessions cannot grow the Aura log indefinitely.

## Hardware portability

Aura is built for the **Omarchy hardware envelope**, not one laptop model. Optional hardware features use runtime capability detection and gracefully become unavailable when a driver/device exposes no compatible controls.

Expected shapes include NVIDIA-, AMD- and Intel-based laptops/desktops; hybrid and multi-GPU systems; ordinary monochrome laptop backlights; ASUS RGB; OpenRGB-controlled desktop/external keyboards; machines with no lighting controls; and systems/VMs where no readable GPU telemetry exists.

On a hybrid or multi-GPU system Aura exposes a per-GPU list and feeds Auto-Protect the highest VRAM pressure, utilization and temperature seen across detected GPUs instead of trusting the first enumerated card.

Inspect what Aura sees on any machine with:

```bash
"$PLUGIN_DIR/bin/aura-cycler" hardware
```

Unsupported optional hardware must not stop wallpaper rotation, palettes, scenes, history/favorites or the rest of Aura. See [`docs/HARDWARE.md`](docs/HARDWARE.md) for the portability contract and test matrix.

## Privacy defaults

A fresh v1.4 install starts with weather/location, atmospheric effects and online wallpaper streaming **off**. GPU Auto-Protect is also off until enabled. Keyboard color sync is enabled, but Aura does not force a manually-off backlight on.

Automatic location uses HTTPS. Manual coordinates avoid IP geolocation entirely. Aura does not invent weather values or silently fall back to `(0, 0)`.

```bash
PLUGIN_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/omarchy/plugins/harshith.aura-cycler"

"$PLUGIN_DIR/bin/aura-cycler" location off
"$PLUGIN_DIR/bin/aura-cycler" location auto
"$PLUGIN_DIR/bin/aura-cycler" location manual 12.9716 77.5946 Bengaluru
```

Private Aura state is written with owner-only permissions (`0600`).

## Installation

Published marketplace version:

```bash
omarchy plugin add https://github.com/harshithnadig/omarchy-aura-cycler.git --enable
```

The `v1.4.3` release is served from the repository's published default branch.

To update an existing installation and reload the supervised service unit:

```bash
omarchy plugin update harshith.aura-cycler
systemctl --user daemon-reload
systemctl --user restart material-cycler.service
```

Aura never installs Python packages silently. Install the locked theme-analysis dependencies explicitly:

```bash
python3 -m venv "$HOME/.local/share/omarchy/aura-cycler-venv"
"$HOME/.local/share/omarchy/aura-cycler-venv/bin/pip" install --require-hashes -r "$PLUGIN_DIR/requirements.lock"
```

CI verifies the exact lock on Python **3.12 and 3.14**.

## Controls

| Action | Bar control |
|---|---|
| Open Aura panel | Left-click |
| Pause/resume | Right-click |
| Cycle speed | Middle-click |
| Fine-tune interval | Mouse wheel |

Common CLI commands:

```bash
# Runtime
"$PLUGIN_DIR/bin/aura-cycler" status
"$PLUGIN_DIR/bin/aura-cycler" status-json
"$PLUGIN_DIR/bin/aura-cycler" next
"$PLUGIN_DIR/bin/aura-cycler" toggle
"$PLUGIN_DIR/bin/aura-cycler" interval 300
"$PLUGIN_DIR/bin/aura-cycler" blur 12

# History / favorites
"$PLUGIN_DIR/bin/aura-cycler" previous
"$PLUGIN_DIR/bin/aura-cycler" history list
"$PLUGIN_DIR/bin/aura-cycler" favorite
"$PLUGIN_DIR/bin/aura-cycler" favorites list

# Theme scope / scenes
"$PLUGIN_DIR/bin/aura-cycler" theme-scope shell
"$PLUGIN_DIR/bin/aura-cycler" theme-scope terminals
"$PLUGIN_DIR/bin/aura-cycler" theme-scope editors
"$PLUGIN_DIR/bin/aura-cycler" theme-scope all
"$PLUGIN_DIR/bin/aura-cycler" scene apply focus
"$PLUGIN_DIR/bin/aura-cycler" scene apply gaming
"$PLUGIN_DIR/bin/aura-cycler" scene apply battery
"$PLUGIN_DIR/bin/aura-cycler" scene apply ambient

# GPU / keyboard / hardware
"$PLUGIN_DIR/bin/aura-cycler" hardware
"$PLUGIN_DIR/bin/aura-cycler" gpu-guard status
"$PLUGIN_DIR/bin/aura-cycler" gpu-guard toggle-protect
"$PLUGIN_DIR/bin/aura-cycler" keyboard sync-on
"$PLUGIN_DIR/bin/aura-cycler" keyboard sync-off

# Diagnostics / privacy
"$PLUGIN_DIR/bin/aura-cycler" doctor
"$PLUGIN_DIR/bin/aura-cycler" privacy
"$PLUGIN_DIR/bin/aura-cycler" config export
"$PLUGIN_DIR/bin/aura-cycler" cache status
```

Scenes never enable weather or wallpaper networking implicitly.

## Backup and recovery

```bash
# Standard backup: coordinates/weather-private state are redacted.
# Local wallpaper/folder paths can still be present; review before sharing.
"$PLUGIN_DIR/bin/aura-cycler" backup ~/aura-backup.json

# Private backup: also includes private config and optional Wallhaven key.
"$PLUGIN_DIR/bin/aura-cycler" backup ~/aura-private-backup.json --private

# Restore creates an automatic owner-only pre-restore snapshot first.
"$PLUGIN_DIR/bin/aura-cycler" restore ~/aura-backup.json

# Return to privacy-safe defaults. Reset is deliberately guarded by --yes.
"$PLUGIN_DIR/bin/aura-cycler" reset --yes
"$PLUGIN_DIR/bin/aura-cycler" reset --yes --keep-favorites --keep-folders
```

Backup files are `0600`. A standard backup is **not automatically safe to publish** because local paths may reveal usernames or directory names.

Malformed main config is preserved as `aura-cycler-config.corrupt-<timestamp>.json` before Aura recovers safe defaults.

## Stable configuration model

Aura v1.4 uses `config_version: 2` and one canonical runtime config.

- An owner-only process lock serializes writes.
- Stale read/modify/write operations merge their actual changes into the newest config instead of overwriting unrelated updates.
- Migrations are explicit and idempotent.
- Native Omarchy widget settings and Aura CLI/panel changes converge on the same runtime store.
- Untouched manifest defaults do not overwrite existing v1.3 preferences during first migration.

## Architecture

Only `bin/aura-cycler` is executable:

```text
bin/aura-cycler                 public entrypoint
        |
        +--> bin/aura-config.py          config/migration/recovery/backup
        |
        +--> bin/aura-hardware.py        GPU/keyboard capability adaptation
        |
        v
bin/aura-cycler-control         history/favorites/scenes/diagnostics
        |
        v
bin/aura-cycler-runtime         privacy/XDG/network/rollback hardening
        |
        v
bin/aura-cycler-core            retained v1.3 feature engine
```

The bar follows the same stability pattern:

```text
BarWidget.qml        native Omarchy settings bridge
        |
        v
BarWidgetImpl.qml    proven Aura bar behavior/UI
```

The existing large `Panel.qml` is intentionally not structurally rewritten during v1.4 hardening. Future UI features can build on the verified baseline instead of mixing a panel redesign into security/runtime changes.

See:

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/HARDWARE.md`](docs/HARDWARE.md)
- [`docs/EXTENDING.md`](docs/EXTENDING.md)
- [`docs/TESTING.md`](docs/TESTING.md)
- [`docs/PRIVACY.md`](docs/PRIVACY.md)
- [`SECURITY.md`](SECURITY.md)
- [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md)

## Development

```bash
python -m pip install pytest
python -m pip install --require-hashes -r requirements.lock
pytest -q
scripts/smoke-test.sh
omarchy plugin validate .
```

GitHub Actions validates Python 3.12 + 3.14, Python syntax, manifest/settings contract, regression tests and smoke checks. The workflow also runs `qmllint` when that tool is present on the runner; a full QML/type check still requires the real Omarchy/Quickshell import environment. Real Quickshell/Hyprland and vendor hardware behavior must still be verified on actual Omarchy machines/community reports before claiming a specific device/backend is supported.

## License

MIT. See [LICENSE](LICENSE).
