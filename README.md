# Aura Material Cycler for Omarchy

[![Omarchy Plugin](https://img.shields.io/badge/omarchy-plugin-blue)](https://omarchy.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An intelligent dynamic wallpaper engine, Material You on-device theme generator, real-time outdoor weather synchronizer, and ASUS Aura RGB keyboard backlight synchronizer for [Omarchy Linux](https://omarchy.org).

![Aura Material Cycler](preview.png)

## Highlights

- **Dynamic 4K Wallpaper Engine**: Automatically cycles authentic 4K/UHD photography and art from local directories and curated online streams (Wallhaven & Bing daily archives).
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
- **Aether On-Device Material You Theme Engine**: Automatically analyzes active wallpapers using an offline Vision Model (Pillow + K-Means + Google Material You Monet HCT), generating a full 16-color palette and dynamically restyling the **entire Omarchy desktop** (top bar, window borders, menus, Chrome browser policies, Alacritty, Kitty, Ghostty, Foot, VS Code, Obsidian, and Helix).
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
- **Bulletproof Persistence**: Operates under systemd user supervisor (`material-cycler.service`) with auto-recovery and Omarchy hooks.

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

The engine ships with the `aura-cycler` binary (also symlinked as `material-cycler`):

```bash
# Playback & Rotation
aura-cycler next                  # Skip to next wallpaper and recolor system
aura-cycler interval 30           # Set rotation interval to 30 seconds
aura-cycler interval 300          # Set rotation interval to 5 minutes
aura-cycler start                 # Resume rotation daemon
aura-cycler stop                  # Pause rotation daemon
aura-cycler toggle                # Toggle pause/resume

# Weather & Atmospheric Effects
aura-cycler weather-toggle        # Toggle real-time weather-adaptive wallpaper selection
aura-cycler stream-toggle         # Toggle online 4K streaming (Wallhaven/Bing)
aura-cycler effects toggle        # Toggle on-screen atmospheric weather particles on/off
aura-cycler effects mode rain     # Force specific weather effect (auto|rain|thunder|snow|sun|stars|fog)
aura-cycler effects layer top     # Toggle layer (bottom = on wallpaper behind windows, top = over windows)
aura-cycler effects intensity 1.5 # Set particle density/intensity (0.5 = subtle, 1.0 = normal, 1.5 = dramatic)

# Custom Wallpaper Folders
aura-cycler folder list           # List configured wallpaper folders & image counts
aura-cycler folder add ~/Pictures/Wallpapers   # Add a custom wallpaper folder
aura-cycler folder remove ~/Pictures/Wallpapers # Remove a folder from rotation

# Appearance & Hardware
aura-cycler blur 12               # Set glass blur intensity (0 to 24px)
aura-cycler keyboard off          # Turn keyboard LEDs off (disables sync writes)
aura-cycler keyboard allow        # Re-enable keyboard sync writes
aura-cycler status                # View current service, weather, and folder status
aura-cycler status-json           # Export complete machine-readable state JSON
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

## Removal

To uninstall the plugin:

```bash
omarchy plugin disable harshith.aura-cycler
omarchy plugin remove harshith.aura-cycler
```

Or manually remove:

```bash
systemctl --user stop material-cycler.service
rm -rf ~/.config/omarchy/plugins/harshith.aura-cycler
```

## External Dependencies

- `asusctl` (optional, for ASUS ROG / TUF keyboard RGB backlight sync)
- `python3`, `pillow`, `materialyoucolor`, `scikit-learn`, `numpy` (automatically bootstrapped in isolated user runtime)
- `curl` / standard networking (for Open-Meteo weather and 4K wallpaper streaming)

## Compatibility

- Omarchy 4.0+ (Quattro)
- Compatible with all displays (1080p, 1440p, 4K UHD, ultrawide)
- ASUS ROG / TUF Gaming laptops with `asusctl` (gracefully degrades on non-ASUS systems)

## License

MIT License. See [LICENSE](LICENSE) for details.
