# Aura Material Cycler for Omarchy

[![Omarchy Plugin](https://img.shields.io/badge/Omarchy-plugin-blue)](https://omarchy.org)
[![CI](https://github.com/harshithnadig/omarchy-aura-cycler/actions/workflows/ci.yml/badge.svg)](https://github.com/harshithnadig/omarchy-aura-cycler/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Aura is an adaptive appearance runtime for **Omarchy 4 / Quattro**. It combines wallpaper rotation, on-device Material You palette generation, optional live-weather atmosphere, ambient keyboard integration, and GPU-aware protection.

> **v1.4 hardening branch:** fresh installs are offline by default. Weather/location and online wallpaper downloads require an explicit user action.

![Aura Material Cycler](preview.png)

## What Aura does

- **Dynamic wallpaper engine** — rotates local wallpapers and can optionally fetch 4K/UHD images from Wallhaven and Bing.
- **On-device Material You theming** — extracts a focal accent locally with Pillow, NumPy, scikit-learn and Material You HCT, then regenerates Omarchy theme files.
- **Atmospheric screen effects** — rain, thunder, snow, sun, stars and fog with click-through Wayland rendering.
- **Fullscreen-aware effects** — pauses the effect surface for fullscreen Hyprland clients.
- **Ambient keyboard integration** — RGB color sync where supported; manual brightness is respected.
- **GPU-aware protection** — NVIDIA telemetry via `nvidia-smi`, plus AMD/Intel DRM/sysfs fallback where the kernel exposes usable metrics.
- **Interactive bar panel** — wallpaper, weather, folders, effects, blur, interval and GPU controls.
- **CLI automation** — all important actions are scriptable.
- **Hardened downloads** — bounded remote JSON, bounded wallpaper size, image validation and cache-path containment.
- **Safe daemon control** — owner locks, PID identity checks and a guarded optional systemd user unit.

## Privacy defaults

Aura v1.4 deliberately separates local features from network features.

A **fresh install** starts with:

- local wallpaper rotation available;
- weather sync **off**;
- screen weather effects **off**;
- online 4K downloads **off**;
- GPU Auto-Protect **off**;
- keyboard color sync **on**, but it never turns a manually-off keyboard light back on.

Aura-owned config is written with owner-only permissions because it may contain location data.

### Weather/location modes

```bash
PLUGIN_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/omarchy/plugins/harshith.aura-cycler"

# No weather/location requests
"$PLUGIN_DIR/bin/aura-cycler" location off

# Explicitly opt in to HTTPS IP geolocation + Open-Meteo
"$PLUGIN_DIR/bin/aura-cycler" location auto

# Avoid IP geolocation entirely by supplying coordinates yourself
"$PLUGIN_DIR/bin/aura-cycler" location manual 12.9716 77.5946 Bengaluru

# Inspect current mode
"$PLUGIN_DIR/bin/aura-cycler" location status

# Force a fresh weather read
"$PLUGIN_DIR/bin/aura-cycler" weather-refresh
```

Automatic location uses HTTPS. Aura no longer substitutes `(0, 0)` or a made-up temperature when weather cannot be obtained; status reports whether weather is live, cached, stale, disabled or unavailable.

## Installation

```bash
omarchy plugin add https://github.com/harshithnadig/omarchy-aura-cycler.git --enable
```

For this development branch:

```bash
omarchy plugin add https://github.com/harshithnadig/omarchy-aura-cycler.git --branch audit-hardening-v1.4 --enable
```

If your Omarchy CLI does not expose a branch flag, clone the branch manually into:

```text
~/.config/omarchy/plugins/harshith.aura-cycler
```

then enable `harshith.aura-cycler`.

## Python dependencies

Aura does **not** silently install packages.

```bash
PLUGIN_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/omarchy/plugins/harshith.aura-cycler"
python3 -m venv "$HOME/.local/share/omarchy/aura-cycler-venv"
"$HOME/.local/share/omarchy/aura-cycler-venv/bin/pip" install --require-hashes -r "$PLUGIN_DIR/requirements.lock"
```

Required Python packages:

- Pillow
- NumPy
- scikit-learn
- materialyoucolor

## Controls

| Action | Control |
|---|---|
| Open Aura panel | Left-click bar icon |
| Pause/resume rotation | Right-click |
| Cycle speed | Middle-click |
| Fine-tune speed | Mouse wheel |

Common CLI commands:

```bash
"$PLUGIN_DIR/bin/aura-cycler" status
"$PLUGIN_DIR/bin/aura-cycler" status-json
"$PLUGIN_DIR/bin/aura-cycler" next
"$PLUGIN_DIR/bin/aura-cycler" start
"$PLUGIN_DIR/bin/aura-cycler" stop
"$PLUGIN_DIR/bin/aura-cycler" toggle
"$PLUGIN_DIR/bin/aura-cycler" interval 300
"$PLUGIN_DIR/bin/aura-cycler" blur 12

"$PLUGIN_DIR/bin/aura-cycler" folder list
"$PLUGIN_DIR/bin/aura-cycler" folder add ~/Pictures/Wallpapers
"$PLUGIN_DIR/bin/aura-cycler" folder remove ~/Pictures/Wallpapers

"$PLUGIN_DIR/bin/aura-cycler" effects toggle
"$PLUGIN_DIR/bin/aura-cycler" effects mode rain
"$PLUGIN_DIR/bin/aura-cycler" effects layer top
"$PLUGIN_DIR/bin/aura-cycler" effects intensity 1.0

"$PLUGIN_DIR/bin/aura-cycler" stream-toggle
"$PLUGIN_DIR/bin/aura-cycler" gpu-guard status
"$PLUGIN_DIR/bin/aura-cycler" gpu-guard toggle-protect

"$PLUGIN_DIR/bin/aura-cycler" keyboard status
"$PLUGIN_DIR/bin/aura-cycler" keyboard sync-off
"$PLUGIN_DIR/bin/aura-cycler" keyboard sync-on
"$PLUGIN_DIR/bin/aura-cycler" keyboard off
```

## GPU Auto-Protect in v1.4

Earlier versions depended on a systemd-managed daemon to pause cycling. That meant the default detached user-session daemon could remain active during critical GPU pressure.

v1.4 changes the model:

1. telemetry is read;
2. if Auto-Protect is enabled and pressure becomes critical, the running daemon marks Aura paused;
3. expensive wallpaper/theme work is skipped while the daemon stays alive;
4. the daemon rechecks pressure every few seconds;
5. cycling resumes only after pressure returns to nominal.

This works whether Aura was started directly or by the optional systemd unit.

## GPU providers

Aura first tries NVIDIA `nvidia-smi`. If unavailable, v1.4 checks Linux DRM/sysfs for AMD or Intel metrics such as:

- VRAM total/used where exposed;
- GPU busy percentage where exposed;
- hwmon temperature where exposed.

Kernel/driver support varies, so missing fields are reported as unavailable rather than invented.

## Keyboard behavior

RGB color is applied through supported RGB tools such as `asusctl` or OpenRGB. Standard monochrome laptop backlights cannot change color; Aura only observes/respects their brightness state.

`keyboard sync-off` is a persistent software preference. `keyboard off` is a direct hardware brightness action.

## Optional systemd supervision

The default user-session daemon does not require systemd. If you want systemd supervision:

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

The external guard verifies the plugin id, ownership, path structure and executable entry point before running Aura.

## Development and verification

Before merging changes:

```bash
python -m py_compile bin/aura-cycler bin/aura-cycler-core bin/aura-cycler-service-guard
python -m json.tool manifest.json >/dev/null
pytest -q
omarchy plugin validate .
```

If `qmllint` is available:

```bash
qmllint BarWidget.qml Panel.qml WeatherService.qml
```

CI performs the portable checks automatically on every push and pull request.

## Architecture

v1.4 intentionally keeps the already-hardened v1.3 engine intact:

```text
bin/aura-cycler
    hardened v1.4 runtime/front-end
            |
            v
bin/aura-cycler-core
    preserved v1.3 feature engine
```

This makes the hardening diff reviewable and gives real-system testing a safe rollback path. Once v1.4 is proven on Omarchy hardware, the wrapper and core can be folded into a cleaner package/module layout without changing behavior.

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

## Security

See [SECURITY.md](SECURITY.md) for trust boundaries and reporting guidance.

## License

MIT. See [LICENSE](LICENSE).
