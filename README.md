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
- **Diagnostics** — read-only `doctor`, privacy status, redacted config export and safe palette-cache maintenance.
- **Interactive QML panel** — wallpaper, weather, folders, effects, blur, interval and GPU controls.
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

# No weather/location requests
"$PLUGIN_DIR/bin/aura-cycler" location off

# Opt in to HTTPS IP geolocation + Open-Meteo
"$PLUGIN_DIR/bin/aura-cycler" location auto

# Avoid IP geolocation entirely
"$PLUGIN_DIR/bin/aura-cycler" location manual 12.9716 77.5946 Bengaluru

"$PLUGIN_DIR/bin/aura-cycler" location status
"$PLUGIN_DIR/bin/aura-cycler" weather-refresh
```

Aura reports live/cached/stale/unavailable weather; it does not substitute `(0, 0)` or invented temperatures.

## Installation

Install the published marketplace version from `master`:

```bash
omarchy plugin add https://github.com/harshithnadig/omarchy-aura-cycler.git --enable
```

The `audit-hardening-v1.4` branch is intentionally a test branch. Do not publish/tag it until the real-system checklist is green.

Aura does **not** silently install Python packages. For the local analysis/theme dependencies:

```bash
PLUGIN_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/omarchy/plugins/harshith.aura-cycler"
python3 -m venv "$HOME/.local/share/omarchy/aura-cycler-venv"
"$HOME/.local/share/omarchy/aura-cycler-venv/bin/pip" install --require-hashes -r "$PLUGIN_DIR/requirements.lock"
```

Required packages: Pillow, NumPy, scikit-learn and materialyoucolor.

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

The external guard verifies plugin id, ownership, path structure and executable entrypoint before running Aura.

## Architecture

v1.4 intentionally separates behavior changes from the retained engine:

```text
bin/aura-cycler
    control plane: history/favorites/scenes/doctor/theme scope
            |
            v
bin/aura-cycler-runtime
    privacy/XDG/GPU/rollback hardening
            |
            v
bin/aura-cycler-core
    retained v1.3 feature engine
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

CI performs portable checks automatically. Real Quickshell/Hyprland, GPU, keyboard and systemd behavior must still be verified on an actual Omarchy installation before v1.4 is merged.

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
