# Aura Material Cycler for Omarchy

[![Omarchy Plugin](https://img.shields.io/badge/Omarchy-plugin-blue)](https://omarchy.org)
[![CI](https://github.com/harshithnadig/omarchy-aura-cycler/actions/workflows/ci.yml/badge.svg)](https://github.com/harshithnadig/omarchy-aura-cycler/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Aura is an adaptive appearance runtime for **Omarchy 4 / Quattro**: dynamic wallpapers, local Material You palettes, optional weather atmosphere, keyboard lighting integration, GPU-aware protection, wallpaper history/favorites, and scriptable desktop scenes.

> **v1.4 hardening branch:** fresh installs are local-first. Weather/location and online wallpaper downloads require an explicit user action.

![Aura Material Cycler](preview.png)

## Highlights

- **Dynamic wallpaper engine** — local rotation plus optional Wallhaven/Bing 4K streaming.
- **On-device Material You** — Pillow + NumPy + scikit-learn + Material You HCT; palette results are cached locally.
- **Atmospheric effects** — rain, thunder, snow, sun, stars and fog on a click-through Wayland surface.
- **Fullscreen-aware rendering** — pauses atmospheric animation for fullscreen Hyprland clients.
- **Keyboard integration** — RGB color sync on capable hardware while respecting manual brightness/off state.
- **GPU Auto-Protect** — NVIDIA plus AMD/Intel DRM/sysfs telemetry where available; critical pressure pauses expensive Aura cycling without killing the daemon.
- **History, undo and favorites** — local owner-only state with one-command restore.
- **Theme scopes** — choose whether wallpaper changes refresh only the shell, terminals, editors, or the whole desktop.
- **Scenes** — conservative focus, gaming, battery and ambient presets that never silently enable networking.
- **Native Omarchy settings** — interval, blur, weather, streaming, effects, keyboard sync and live-theme scope are published through the plugin manifest and mirrored transactionally into Aura runtime config.
- **Resilient config** — process locking, conflict-aware updates, schema versioning, migrations and preservation of malformed config before safe recovery.
- **Maintenance tooling** — backup, restore, reset, diagnostics, privacy status, redacted config export and safe palette-cache maintenance.
- **Security boundaries** — bounded downloads/JSON, image validation, path containment, process identity checks, owner-only private state and a guarded optional systemd unit.

## Privacy defaults

A fresh v1.4 install starts with:

- weather sync **off**;
- location mode **off**;
- screen weather effects **off**;
- online 4K downloads **off**;
- GPU Auto-Protect **off**;
- keyboard color sync **on**, but a manually-off keyboard backlight is not forced on.

Aura-owned private state is written with owner-only permissions (`0600`). History and favorites never leave the machine.

### Location and weather

```bash
PLUGIN_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/omarchy/plugins/harshith.aura-cycler"

"$PLUGIN_DIR/bin/aura-cycler" location off
"$PLUGIN_DIR/bin/aura-cycler" location auto
"$PLUGIN_DIR/bin/aura-cycler" location manual 12.9716 77.5946 Bengaluru
"$PLUGIN_DIR/bin/aura-cycler" location status
"$PLUGIN_DIR/bin/aura-cycler" weather-refresh
```

Automatic location uses HTTPS. Aura reports live/cached/stale/unavailable weather; it does not substitute `(0, 0)` or invented temperatures.

## Installation

Install the published marketplace version from `master`:

```bash
omarchy plugin add https://github.com/harshithnadig/omarchy-aura-cycler.git --enable
```

The `audit-hardening-v1.4` branch is intentionally a test branch. Do not publish/tag it until the real-system checklist is green.

Aura does **not** silently install Python packages:

```bash
PLUGIN_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/omarchy/plugins/harshith.aura-cycler"
python3 -m venv "$HOME/.local/share/omarchy/aura-cycler-venv"
"$HOME/.local/share/omarchy/aura-cycler-venv/bin/pip" install --require-hashes -r "$PLUGIN_DIR/requirements.lock"
```

CI verifies the locked dependency set on Python 3.12 and 3.14. Required packages are Pillow, NumPy, scikit-learn and materialyoucolor.

## Native Omarchy settings

Aura v1.4 publishes a `barWidget.defaults` + `barWidget.schema` contract for:

- wallpaper interval;
- blur;
- weather sync;
- online wallpaper streaming;
- atmospheric effects;
- keyboard color sync;
- theme scope.

`BarWidget.qml` is a thin bridge around the proven widget implementation. Explicit Omarchy settings are imported into Aura through the public CLI and all config writes use the same transactional store. Existing v1.3 users are protected during migration: untouched manifest defaults do **not** overwrite their prior Aura preferences.

## Bar controls

| Action | Control |
|---|---|
| Open Aura panel | Left-click bar icon |
| Pause/resume rotation | Right-click |
| Cycle speed | Middle-click |
| Fine-tune speed | Mouse wheel |

## CLI

### Core controls

```bash
"$PLUGIN_DIR/bin/aura-cycler" status
"$PLUGIN_DIR/bin/aura-cycler" status-json
"$PLUGIN_DIR/bin/aura-cycler" next
"$PLUGIN_DIR/bin/aura-cycler" start
"$PLUGIN_DIR/bin/aura-cycler" stop
"$PLUGIN_DIR/bin/aura-cycler" toggle
"$PLUGIN_DIR/bin/aura-cycler" interval 300
"$PLUGIN_DIR/bin/aura-cycler" blur 12
```

### History and favorites

```bash
"$PLUGIN_DIR/bin/aura-cycler" history list
"$PLUGIN_DIR/bin/aura-cycler" previous
"$PLUGIN_DIR/bin/aura-cycler" history apply 3
"$PLUGIN_DIR/bin/aura-cycler" favorite
"$PLUGIN_DIR/bin/aura-cycler" favorites list
"$PLUGIN_DIR/bin/aura-cycler" favorites apply 2
```

History is capped at 100 transitions and consecutive duplicates are collapsed.

### Theme scopes

```bash
"$PLUGIN_DIR/bin/aura-cycler" theme-scope shell
"$PLUGIN_DIR/bin/aura-cycler" theme-scope terminals
"$PLUGIN_DIR/bin/aura-cycler" theme-scope editors
"$PLUGIN_DIR/bin/aura-cycler" theme-scope all
```

The scope only filters known post-theme refresh helpers. Unknown subprocesses are never suppressed.

### Scenes

```bash
"$PLUGIN_DIR/bin/aura-cycler" scene list
"$PLUGIN_DIR/bin/aura-cycler" scene apply focus
"$PLUGIN_DIR/bin/aura-cycler" scene apply gaming
"$PLUGIN_DIR/bin/aura-cycler" scene apply battery
"$PLUGIN_DIR/bin/aura-cycler" scene apply ambient
```

Scenes never enable weather or wallpaper networking automatically.

### Backup, restore and reset

```bash
# Safe shareable backup: location/weather cache is redacted
"$PLUGIN_DIR/bin/aura-cycler" backup ~/aura-backup.json

# Private backup: includes private config and the optional Wallhaven key
"$PLUGIN_DIR/bin/aura-cycler" backup ~/aura-private-backup.json --private

# Restore; Aura creates an automatic owner-only pre-restore snapshot first
"$PLUGIN_DIR/bin/aura-cycler" restore ~/aura-backup.json

# Return to privacy-safe defaults
"$PLUGIN_DIR/bin/aura-cycler" reset
"$PLUGIN_DIR/bin/aura-cycler" reset --keep-favorites
"$PLUGIN_DIR/bin/aura-cycler" reset --keep-favorites --keep-folders
```

Backup files are owner-only (`0600`). A normal backup deliberately redacts location/weather-private fields. Use `--private` only for a backup you will protect appropriately.

### Folders, effects and streaming

```bash
"$PLUGIN_DIR/bin/aura-cycler" folder list
"$PLUGIN_DIR/bin/aura-cycler" folder add ~/Pictures/Wallpapers
"$PLUGIN_DIR/bin/aura-cycler" folder remove ~/Pictures/Wallpapers
"$PLUGIN_DIR/bin/aura-cycler" effects toggle
"$PLUGIN_DIR/bin/aura-cycler" effects mode rain
"$PLUGIN_DIR/bin/aura-cycler" effects layer top
"$PLUGIN_DIR/bin/aura-cycler" effects intensity 1.0
"$PLUGIN_DIR/bin/aura-cycler" stream-toggle
```

### GPU and keyboard

```bash
"$PLUGIN_DIR/bin/aura-cycler" gpu-guard status
"$PLUGIN_DIR/bin/aura-cycler" gpu-guard toggle-protect
"$PLUGIN_DIR/bin/aura-cycler" keyboard status
"$PLUGIN_DIR/bin/aura-cycler" keyboard sync-off
"$PLUGIN_DIR/bin/aura-cycler" keyboard sync-on
"$PLUGIN_DIR/bin/aura-cycler" keyboard off
```

### Diagnostics and privacy

```bash
"$PLUGIN_DIR/bin/aura-cycler" doctor
"$PLUGIN_DIR/bin/aura-cycler" doctor --json
"$PLUGIN_DIR/bin/aura-cycler" privacy
"$PLUGIN_DIR/bin/aura-cycler" config export
"$PLUGIN_DIR/bin/aura-cycler" cache status
"$PLUGIN_DIR/bin/aura-cycler" cache prune-palettes 30
```

`doctor` is read-only and does not perform network requests. Location coordinates are redacted unless explicitly requested with private/full output.

## Config durability

The main Aura config is schema-versioned (`config_version: 2`). Every normal Aura process enters through `bin/aura-cycler`, which installs the same configuration policy before loading feature commands.

- an owner-only process lock serializes writes;
- stale read/modify/write operations are merged against the latest file to avoid losing unrelated concurrent changes;
- migration runs are explicit and idempotent;
- malformed JSON is moved aside as `aura-cycler-config.corrupt-<timestamp>.json` before Aura recovers safe defaults;
- private config/history/favorites/backup files are written `0600`;
- native Omarchy settings and Aura runtime settings share one canonical store.

## GPU Auto-Protect

v1.4 keeps the daemon alive during critical GPU pressure and pauses expensive wallpaper/theme work internally. This works for both the normal detached daemon and optional systemd supervision.

Aura tries NVIDIA `nvidia-smi` first, then Linux DRM/sysfs for AMD/Intel metrics when the kernel/driver exposes them. Missing telemetry is reported as unavailable, not invented.

## Keyboard behavior

RGB color is applied through supported RGB tools such as `asusctl` or OpenRGB. Standard monochrome laptop backlights cannot change color; Aura only observes/respects their brightness state. `keyboard sync-off` is persistent software policy; `keyboard off` is a direct hardware brightness action.

## Optional systemd supervision

```bash
PLUGIN_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/omarchy/plugins/harshith.aura-cycler"
GUARD_PATH="$HOME/.local/libexec/omarchy/harshith.aura-cycler-service-guard"
UNIT_PATH="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user/material-cycler.service"

install -Dm755 "$PLUGIN_DIR/bin/aura-cycler-service-guard" "$GUARD_PATH"
mkdir -p "$(dirname "$UNIT_PATH")"
install -Dm644 "$PLUGIN_DIR/systemd/material-cycler.service" "$UNIT_PATH"
systemctl --user daemon-reload
systemctl --user enable --now material-cycler.service
```

## Architecture

v1.4 freezes a layered baseline so future features can be added without destabilizing the proven engine:

```text
bin/aura-cycler                 executable public entrypoint
        |
        +--> bin/aura-config.py          config/migration/backup policy
        |
        v
bin/aura-cycler-control         history/favorites/scenes/doctor/theme scope
        |
        v
bin/aura-cycler-runtime         privacy/XDG/GPU/rollback hardening
        |
        v
bin/aura-cycler-core            retained v1.3 feature engine
```

Only `bin/aura-cycler` is executable. The internal layers are import-only and CI enforces that boundary.

The QML bar follows the same pattern:

```text
BarWidget.qml        native Omarchy settings bridge
        |
        v
BarWidgetImpl.qml    proven Aura bar implementation
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/TESTING.md`](docs/TESTING.md), [`docs/PRIVACY.md`](docs/PRIVACY.md), and [`docs/v1.4-control-plane.md`](docs/v1.4-control-plane.md).

## Development

```bash
python -m pip install pytest
python -m pip install --require-hashes -r requirements.lock
pytest -q
scripts/smoke-test.sh
omarchy plugin validate .
```

CI currently validates both Python **3.12 and 3.14**, Python syntax, the manifest/settings contract, regression tests, smoke tests and QML lint where available. Real Quickshell/Hyprland, GPU, keyboard and systemd behavior must still be verified on an actual Omarchy installation before v1.4 is merged.

## Removal

```bash
PLUGIN_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/omarchy/plugins/harshith.aura-cycler"
GUARD_PATH="$HOME/.local/libexec/omarchy/harshith.aura-cycler-service-guard"
UNIT_PATH="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user/material-cycler.service"

"$PLUGIN_DIR/bin/aura-cycler" stop || true
systemctl --user disable --now material-cycler.service 2>/dev/null || true
rm -f "$UNIT_PATH" "$GUARD_PATH"
systemctl --user daemon-reload
omarchy plugin disable harshith.aura-cycler
omarchy plugin remove harshith.aura-cycler
```

## Security and contributing

See [SECURITY.md](SECURITY.md), [CONTRIBUTING.md](CONTRIBUTING.md), and [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md).

## License

MIT. See [LICENSE](LICENSE).
