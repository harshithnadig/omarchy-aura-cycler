# Aura Material Cycler for Omarchy

Dynamic wallpaper cycler with Material You adaptive palette extraction, Omarchy shell live recoloring, and ASUS Aura keyboard backlight synchronization.

## Features

- **Dynamic Wallpaper Cycling**: Rotates through local curated themes (Ben 10, Oggy, Disney, Tom & Jerry, Scenic, macOS Glass) and 4K wallpapers.
- **Material You Live Palettes**: Dynamically calculates the Monet-style primary accent, backgrounds, and accents from every active image.
- **Live Omarchy Shell Tinting**: Recolors the top bar, widgets, and menus in real time using Omarchy's `applyTheme` IPC.
- **ASUS Aura Keyboard Sync**: Instantly illuminates the keyboard backlight with matching colors via `asusctl`.
- **Safe & Resilient**: Debounced hardware execution, bounds checking, zero configuration corruption.
- **Interactive Top Bar Widget**:
  - **Left Click**: Immediately skips to the next wallpaper and syncs keyboard/theme.
  - **Right Click**: Toggle auto-cycle (pause / resume).
  - **Middle Click**: Cycle interval speed (10s, 30s, 60s, 5m, 10m).
  - **Scroll Wheel**: Fine-tune speed.
  - **Live Tooltip**: Displays running state, current interval, wallpaper name, and active accent hex.

## CLI Usage

```bash
material-cycler start          # Start background rotation
material-cycler stop           # Pause rotation
material-cycler next           # Skip to next wallpaper immediately
material-cycler interval 10    # Set cycle speed (e.g. 10s, 30s)
material-cycler status         # Check status and wallpaper count
material-cycler fetch          # Download fresh 4K wallpapers
```
