# Aura Material Cycler for Omarchy

[![Omarchy Plugin](https://img.shields.io/badge/omarchy-plugin-blue)](https://omarchy.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An all-in-one dynamic wallpaper cycler, Material You on-device theme generator, and ASUS Aura RGB keyboard backlight synchronizer for [Omarchy Linux](https://omarchy.org).

![Aura Material Cycler](preview.png)

## Highlights

- **Dynamic Wallpaper Engine**: Automatically streams and rotates curated 4K photography from Unsplash via authenticated API and native cartoon & scenic collections (Ben 10, Oggy, Disney, Tom & Jerry, Studio Ghibli landscapes).
- **Aether On-Device Material You Theme Engine**: Automatically analyzes the active wallpaper using Omarchy's native Aether CIELAB perceptual engine, generating a full 16-color palette and dynamically restyling the **entire Omarchy desktop** (top bar, widgets, popouts, active window borders, menus).
- **ASUS Aura Keyboard Backlight Sync**: Isolates the wallpaper's primary accent hue and applies a specialized LED chroma saturation boost ($S \ge 0.98$, normalized $L = 0.50$), commanding `asusctl` to illuminate your keyboard in brilliant, rich colors.
- **Keyboard-First & Mouse-Free**: Full control via Hyprland keybindings without needing a mouse.
- **Manual Brightness Friendly**: Leaves keyboard brightness levels strictly under manual user control (via hardware Fn keys) without overriding or forcing brightness.
- **Top Bar Widget**: Sleek status bar widget (`󰸉`) with live status feedback, pause/play control, and multi-speed interval switching.
- **Bulletproof Persistence**: Operates under systemd user supervisor (`material-cycler.service`) with Hyprland autostart and Omarchy `post-boot` / `post-update` hooks to guarantee it never stops after reboots or system updates.

## Keyboard Shortcuts (Mouse-Free)

| Shortcut | Action | Description |
| :--- | :--- | :--- |
| `SUPER + B` | **Next Wallpaper & Recolor** | Immediately rotates wallpaper, recolors desktop theme, and syncs ASUS Aura LED |
| `SUPER + ALT + P` | **Pause / Resume** | Toggles the background wallpaper rotation daemon |
| `SUPER + ALT + I` | **Cycle Rotation Speed** | Cycles interval between 15s → 30s → 60s → 5m → 10m |

## Bar Widget Controls (Optional)

| Action | Control | Description |
| :--- | :--- | :--- |
| **Next Wallpaper** | **Left Click** | Immediately skips to the next wallpaper and syncs theme & keyboard |
| **Pause / Resume** | **Right Click** | Toggles the auto-rotation loop |
| **Cycle Speed** | **Middle Click** | Cycles through interval speeds: 15s → 30s → 1m → 5m → 10m |
| **Fine-Tune Timer** | **Mouse Wheel** | Scroll up or down over the widget to adjust rotation interval |
| **Live Tooltip** | **Hover** | Displays active state, current timer, wallpaper name, and theme accent |

## CLI Commands

The engine ships with the `aura-cycler` binary (also symlinked as `material-cycler`):

```bash
material-cycler next         # Skip to next wallpaper and recolor
material-cycler interval 15  # Set rotation interval to 15 seconds
material-cycler interval 30  # Set rotation interval to 30 seconds
material-cycler status       # View systemd status & wallpaper pool size
material-cycler stop         # Pause rotation
material-cycler start        # Resume rotation
material-cycler fetch        # Download new batch of 4K wallpapers
```

## Installation

Install directly via the Omarchy plugin CLI:

```bash
omarchy plugin add https://github.com/harshithnadig/omarchy-aura-cycler.git --enable
```

## Compatibility

- Omarchy 4.0+ (Quattro)
- ASUS ROG / TUF Gaming laptops with `asusctl`
- Works with any screen resolution (1080p, 1440p, 4K)

## License

MIT License. See [LICENSE](LICENSE) for details.
