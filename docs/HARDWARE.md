# Aura hardware portability

Aura v1.4 is designed for **Omarchy systems**, not for one specific laptop model. Hardware-dependent features are optional capability layers: unsupported hardware must degrade to `unavailable` while wallpaper rotation, local palettes, history/favorites and the rest of Aura continue working.

## Supported shape

Aura should behave sensibly on:

- laptops and desktops;
- NVIDIA, AMD and Intel graphics;
- hybrid and multi-GPU systems;
- systems with no readable GPU telemetry (including many VMs/iGPUs);
- RGB keyboards controlled by `asusctl` or OpenRGB;
- ordinary monochrome laptop keyboard backlights;
- systems with no controllable keyboard lighting;
- user-systemd and detached user-session daemon modes;
- single- and multi-monitor Omarchy/Quickshell setups.

This is a portability contract, not a promise that every vendor exposes every sensor. When the kernel/driver does not expose VRAM, utilization, temperature or lighting controls, Aura reports the capability as unavailable instead of inventing a value.

## GPU discovery

`bin/aura-hardware.py` discovers all telemetry providers it can read:

- NVIDIA: all GPUs returned by `nvidia-smi`;
- AMD: DRM/sysfs cards (`0x1002`) where the driver exports useful metrics;
- Intel: DRM/sysfs cards (`0x8086`) where the driver exports useful metrics.

On multi-GPU systems Aura keeps a per-GPU list and exposes aggregate pressure using the **highest VRAM percentage, utilization and temperature across all detected GPUs**. Auto-Protect therefore cannot accidentally monitor only `card0` while a different dGPU is under pressure.

If no usable telemetry backend exists, GPU monitoring reports unavailable and Auto-Protect does nothing. Core Aura behavior is unaffected.

Use:

```bash
bin/aura-cycler hardware
```

to inspect the detected hardware capability summary without exposing hostnames or private user data.

## Keyboard adaptation

Aura does not require keyboard lighting.

Order of RGB attempts:

1. `asusctl` when available;
2. OpenRGB when available;
3. monochrome backlight awareness when a laptop backlight exists;
4. graceful unavailable state otherwise.

A desktop RGB keyboard can therefore use OpenRGB even when the machine has no laptop-style `/sys/class/leds/*kbd*` brightness device.

If a laptop keyboard backlight is explicitly off, Aura preserves that manual off state rather than forcing it on.

## Displays

Atmospheric QML windows are created from `Quickshell.screens`, so the effect surface is instantiated per detected screen. Aura relies on Omarchy/Quickshell/Hyprland for monitor geometry and scaling rather than hard-coding a specific panel resolution.

## Omarchy state paths

Omarchy itself currently stores generated active theme/background state under:

```text
~/.local/state/omarchy/current/
```

Aura intentionally supports that canonical Omarchy location while using XDG-aware paths for Aura-owned config/cache/state where possible. This is an Omarchy convention, not a path tied to the original developer's machine.

## What is intentionally not guaranteed

Aura does not claim universal Linux support. v1.4 targets Omarchy/Quattro and its supported/community hardware envelope.

Examples that may legitimately expose reduced functionality:

- a GPU driver with no readable telemetry nodes;
- proprietary RGB hardware unsupported by both its native utility and OpenRGB;
- community Omarchy ports on architectures where Aura's Python dependency wheels are unavailable;
- non-Omarchy desktops missing Omarchy shell/theme commands.

Those conditions should disable only the affected optional feature, not crash Aura.

## Release testing matrix

Before a release is advertised as broadly portable, verify at least these classes over time (real hardware where available, community reports otherwise):

| Class | Expected behavior |
|---|---|
| NVIDIA-only laptop/desktop | `nvidia-smi` telemetry; Auto-Protect works |
| AMD-only laptop/desktop | DRM telemetry when exported; otherwise graceful unavailable |
| Intel-only laptop/desktop | DRM telemetry when exported; otherwise graceful unavailable |
| Hybrid Intel + NVIDIA | both discovery paths coexist; worst pressure is protected |
| Hybrid AMD + NVIDIA | both discovery paths coexist; worst pressure is protected |
| Multi-GPU desktop | all detected GPUs appear in `hardware` output |
| No readable GPU/VM | Aura works; GPU telemetry says unavailable |
| ASUS RGB laptop | `asusctl` path when supported |
| OpenRGB desktop keyboard | RGB works without laptop brightness sysfs |
| Monochrome laptop keyboard | manual brightness/off respected |
| No lighting hardware | Aura works; keyboard integration unavailable |
| Multiple monitors | per-screen atmosphere renders and does not intercept input |

A bug on one optional hardware backend should be fixed in the hardware layer rather than by adding machine-specific branches to the preserved wallpaper engine.
