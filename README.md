# Aura Material Cycler for Omarchy

[![Omarchy Plugin](https://img.shields.io/badge/omarchy-plugin-blue)](https://omarchy.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An intelligent dynamic wallpaper engine, Material You on-device theme generator, real-time outdoor weather synchronizer, and ASUS Aura RGB keyboard backlight synchronizer for [Omarchy Linux](https://omarchy.org).

![Aura Material Cycler](preview.png)

## Highlights

- **Dynamic 4K Wallpaper Engine**: Automatically cycles authentic 4K/UHD photography and art from local directories. Optional Wallhaven/Bing streaming is disabled by default and can be enabled explicitly.
- **On-Screen Atmospheric Weather Effects**: Renders realistic visual particle effects directly on your display across all weather types:
  - 󰖗 **Rain / Drizzle**: Falling raindrop streaks with realistic slanting speed and bottom splash ripples.
  - 󰖓 **Thunderstorm**: Deluge rainfall with branching lightning bolts and full-screen illumination flashes.
  - 󰖘 **Snow**: Drifting floating snowflakes with sinuous wobbles across depth layers.
  - 󰖙 **Sunny Day**: Radiant warm golden radial glow with shimmering floating sun motes.
  - 󰖔 **Clear Night**: Twinkling star field with realistic streaking shooting stars (meteors).
  - 󰖑 **Fog / Mist**: Soft drifting atmospheric mist patches with pulsing opacity.
  - **100% Click-Through**: Zero disruption to workflows (`mask: Region {}` passes all clicks and input directly to underlying apps).
  - **Layer Placement Control**: Toggle rendering right on the wallpaper behind windows (`WlrLayer.Bottom`) or immersive over windows (`WlrLayer.Top`).
  - **Smart Fullscreen Auto-Pause**: Listens to Hyprland socket2 to instantly unmap/pause animation during fullscreen apps, gaming, or video playback (0% CPU/GPU).
- **Live Weather-Adaptive Atmosphere**: Automatically queries real-time outdoor weather conditions (via Open-Meteo) and streams matching wallpapers and screen effects.
- **Aether On-Device Material You Theme Engine**: Automatically analyzes active wallpapers using local Pillow + K-Means + Google Material You Monet HCT, generating a full palette and dynamically restyling the **entire Omarchy desktop** (top bar, window borders, menus, Chrome browser policies, Alacritty, Kitty, Ghostty, Foot, VS Code, Obsidian, and Helix). Palette results are cached by image path and modification time.
- **ASUS Aura Keyboard Backlight Sync**: Synchronizes the wallpaper's primary accent hue directly to your ASUS laptop keyboard using `asusctl` static mode, while strictly respecting manual user brightness levels.
- **Interactive Settings Panel (`Panel.qml`)**:
  - Live outdoor weather card with real-time temperature, condition icon, and weather-adaptive toggle.
  - Dedicated Atmospheric Weather Effects card with toggle, mode selector pills (`Auto`, `Rain`, `Thunder`, `Snow`, `Sun`, `Stars`, `Mist`), layer placement button (`Wallpaper` vs `Over Windows`), and intensity cycle (`Subtle`, `Normal`, `Dramatic`).
  - Active wallpaper card with live image thumbnail and extracted Monet accent color swatch.
  - Quick action playback controls: Next Wallpaper, Pause/Resume, and Sync.
  - Rotation Timeout (Interval) selector with one-click pills: `15s`, `30s`, `1m`, `5m`, `10m`, `30m`, `1h`.
  - Wallpaper Folders manager: add, remove, and list custom directories.
  - Liquid Glass Blur selector: 0px to 24px.
  - Online 4K stream toggle switch.
- **Keyboard-First & Mouse-Free**: Full control via Hyprland keybindings without needing a mouse.
- **Resource-Conscious Persistence**: New installs use a 5-minute rotation interval and keep online 4K downloads disabled until enabled. The user-session daemon uses an owner-only lock, avoids duplicate processes, and can optionally be supervised by systemd.

## Interactive Settings Panel & Bar Controls

| Action | Control | Description |
| :--- | :--- | :--- |
| **Open Settings Panel** | **Left Click** on bar widget (`󰸉`) | Opens interactive GUI to manage folders, timeout, weather, and blur |
| **Pause / Resume** | **Right Click** on bar widget | Toggles the auto-rotation loop |
| **Cycle Speed** | **Middle Click** on bar widget | Cycles through interval speeds: 15s → 30s → 1m → 5m → 10m |
| **Fine-Tune Timer** | **Mouse Wheel** over widget | Scroll up or down over the widget to adjust rotation interval |
| **Live Tooltip** | **Hover** | Displays active state, current timer, live weather, and theme accent |

## Keyboard Shortcuts (Mouse-Free)

| Shortcut | Action | Description |
| :--- | :--- | :--- |
| `SUPER + B` | **Next Wallpaper & Recolor** | Immediately rotates wallpaper, recolors desktop theme, and syncs ASUS Aura LED |
| `SUPER + ALT + P` | **Pause / Resume** | Toggles the background wallpaper rotation daemon |
| `SUPER + ALT + I` | **Cycle Rotation Speed** | Cycles interval between 15s → 30s → 60s → 5m → 10m → 30m → 1h |

## CLI Commands

The engine ships with `bin/aura-cycler`. Use the installed plugin path unless you create your own shell alias:

```bash
PLUGIN_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/omarchy/plugins/harshith.aura-cycler"

# Playback & Rotation
"$PLUGIN_DIR/bin/aura-cycler" next                  # Skip to next wallpaper and recolor system
"$PLUGIN_DIR/bin/aura-cycler" interval 30           # Set rotation interval to 30 seconds
"$PLUGIN_DIR/bin/aura-cycler" interval 300          # Set rotation interval to 5 minutes
"$PLUGIN_DIR/bin/aura-cycler" start                 # Resume rotation daemon
"$PLUGIN_DIR/bin/aura-cycler" stop                  # Pause rotation daemon
"$PLUGIN_DIR/bin/aura-cycler" toggle                # Toggle pause/resume

# Weather & Atmospheric Effects
"$PLUGIN_DIR/bin/aura-cycler" weather-toggle        # Toggle real-time weather-adaptive wallpaper selection
"$PLUGIN_DIR/bin/aura-cycler" stream-toggle         # Toggle online 4K streaming (Wallhaven/Bing)
"$PLUGIN_DIR/bin/aura-cycler" effects toggle        # Toggle on-screen atmospheric weather particles on/off
"$PLUGIN_DIR/bin/aura-cycler" effects mode rain     # Force specific weather effect (auto|rain|thunder|snow|sun|stars|fog)
"$PLUGIN_DIR/bin/aura-cycler" effects layer top     # Toggle layer (bottom = on wallpaper behind windows, top = over windows)
"$PLUGIN_DIR/bin/aura-cycler" effects intensity 1.5 # Set particle density/intensity (0.5 = subtle, 1.0 = normal, 1.5 = dramatic)

# Custom Wallpaper Folders
"$PLUGIN_DIR/bin/aura-cycler" folder list           # List configured wallpaper folders & image counts
"$PLUGIN_DIR/bin/aura-cycler" folder add ~/Pictures/Wallpapers   # Add a custom wallpaper folder
"$PLUGIN_DIR/bin/aura-cycler" folder remove ~/Pictures/Wallpapers # Remove a folder from rotation

# Appearance & Hardware
"$PLUGIN_DIR/bin/aura-cycler" blur 12               # Set glass blur intensity (0 to 24px)
"$PLUGIN_DIR/bin/aura-cycler" keyboard off          # Turn keyboard LEDs off (disables sync writes)
"$PLUGIN_DIR/bin/aura-cycler" keyboard allow        # Re-enable keyboard sync writes
"$PLUGIN_DIR/bin/aura-cycler" status                # View current service, weather, and folder status
"$PLUGIN_DIR/bin/aura-cycler" status-json           # Export complete machine-readable state JSON
```

## Installation

Install directly via the Omarchy plugin CLI:

```bash
omarchy plugin add https://github.com/harshithnadig/omarchy-aura-cycler.git --enable
```

Or install manually:

```bash
git clone https://github.com/harshithnadig/omarchy-aura-cycler.git ~/.config/omarchy/plugins/harshith.aura-cycler
omarchy plugin enable harshith.aura-cycler
```

Enabling the plugin starts a user-session daemon from the plugin directory. For
systemd supervision across shell restarts, link the included unit explicitly:

```bash
PLUGIN_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/omarchy/plugins/harshith.aura-cycler"
mkdir -p "${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
ln -sf "$PLUGIN_DIR/systemd/material-cycler.service" "${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user/material-cycler.service"
systemctl --user daemon-reload
systemctl --user enable --now material-cycler.service
```

The default mode is local/offline: 5-minute rotation and no online wallpaper
downloads. Enable the online stream from the panel or with
`"$PLUGIN_DIR/bin/aura-cycler" stream-toggle` when desired.

## Removal

To uninstall the plugin:

```bash
PLUGIN_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/omarchy/plugins/harshith.aura-cycler"
"$PLUGIN_DIR/bin/aura-cycler" stop
systemctl --user disable --now material-cycler.service 2>/dev/null || true
rm -f "${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user/material-cycler.service"
systemctl --user daemon-reload
omarchy plugin disable harshith.aura-cycler
omarchy plugin remove harshith.aura-cycler
```

## External Dependencies

- `asusctl` (optional, for ASUS ROG / TUF keyboard RGB backlight sync)
- `python3`, `python3-venv`, `pillow`, `materialyoucolor`, `scikit-learn`, `numpy` (required for image validation and palette extraction)
- standard HTTPS networking (only for weather and optional 4K wallpaper streaming)

The plugin does not silently install packages or run a remote installer. If the
Python packages are not already available, create a user-owned environment and
install them before enabling rotation:

```bash
python3 -m venv "$HOME/.local/share/omarchy/aura-cycler-venv"
"$HOME/.local/share/omarchy/aura-cycler-venv/bin/pip" install Pillow numpy scikit-learn materialyoucolor
```

## Compatibility

- Omarchy 4.0+ (Quattro)
- Compatible with all displays (1080p, 1440p, 4K UHD, ultrawide)
- ASUS ROG / TUF Gaming laptops with `asusctl` (gracefully degrades on non-ASUS systems)

## License

MIT License. See [LICENSE](LICENSE) for details.
