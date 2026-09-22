# Aura architecture

Aura v1.4 freezes a layered baseline so future features can be added without destabilising the proven wallpaper/theme engine.

## Public process boundary

Only one executable user entrypoint exists:

1. `bin/aura-cycler` — **public executable**. Loads the config and hardware foundations, then delegates to the control plane.
2. `bin/aura-config.py` — **import-only config foundation**. Locking, schema migration, corrupt-file recovery, conflict-aware updates, native Omarchy settings mirroring, backup/restore/reset.
3. `bin/aura-hardware.py` — **import-only hardware adaptation**. Multi-vendor/multi-GPU discovery, aggregate pressure semantics, desktop/laptop RGB adaptation and capability reporting.
4. `bin/aura-cycler-control` — **import-only control plane**. History, favorites, scenes, diagnostics, privacy/config export, cache maintenance and theme live-sync scope.
5. `bin/aura-cycler-runtime` — **import-only hardened runtime**. XDG paths, private config defaults, HTTPS/manual location, weather availability semantics, GPU protection policy and transactional theme staging.
6. `bin/aura-cycler-core` — **import-only retained v1.3 feature engine**. Wallpaper selection, image validation/downloads, Material You extraction, Omarchy theme generation and legacy helpers.

CI enforces that only `bin/aura-cycler` is executable. This prevents normal users/services from accidentally bypassing v1.4 privacy, migration, hardware-adaptation or control-plane policy.

## Stable process identity

The public entrypoint rewrites the hardened runtime's wrapper identity to `bin/aura-cycler`. Detached daemon startup and PID identity validation therefore continue to recognise one stable public process even though implementation is layered internally.

## Configuration model

The canonical config remains Aura's private JSON state, now schema-versioned as `config_version: 2`.

Every normal Aura process installs the same config layer before feature code executes:

- an owner-only `flock` serialises writes;
- `ConfigState` records the exact base snapshot returned by a read;
- stale read/modify/write saves compute a nested patch and merge it into the latest file, preserving unrelated concurrent changes;
- migrations are explicit and idempotent;
- malformed JSON is moved to `aura-cycler-config.corrupt-<timestamp>.json` before safe recovery;
- private state is written `0600`.

This gives future modules one rule: **never invent a second config store; use the installed runtime config API.**

## Hardware adaptation boundary

Hardware-specific behavior is capability-based rather than tied to a laptop/desktop model.

`aura-hardware.py` discovers all readable GPU telemetry providers and presents the existing guard API with a backward-compatible aggregate shape plus a per-GPU list. On hybrid or multi-GPU machines the aggregate pressure takes the highest VRAM percentage, utilization and temperature across all detected cards, so Auto-Protect cannot accidentally watch only the first enumerated GPU.

Keyboard adaptation similarly distinguishes RGB backends from laptop brightness hardware. OpenRGB may work on a desktop keyboard even when no laptop-style keyboard backlight sysfs device exists. If a laptop backlight is manually off, that state is preserved.

Unsupported sensors/backends report unavailable and must not disable Aura's core wallpaper/theme behavior. New vendor support belongs in this layer; see `docs/HARDWARE.md`.

## Native Omarchy settings

`manifest.json` publishes `barWidget.defaults` and `barWidget.schema`. `BarWidget.qml` is a thin settings bridge around `BarWidgetImpl.qml`.

Explicit Omarchy widget settings are imported through `aura-cycler settings-import`. Aura config changes are mirrored back using Omarchy's supported `setBarWidget` IPC. On migration, untouched manifest defaults do not overwrite existing Aura preferences.

## Theme live-sync boundary

Theme scope filtering applies only to Aura's known post-theme application refresh helpers. Unknown subprocesses are always allowed. This prevents a future Omarchy helper from being silently suppressed simply because Aura does not recognise its name yet.

## Backup boundary

`backup`, `restore` and `reset` are control-plane maintenance operations.

- normal backups redact location/weather-private config;
- `--private` includes private config and the optional Wallhaven key;
- backup files are `0600`;
- restore creates an automatic pre-restore snapshot before changing state;
- maintenance never recursively deletes configured wallpaper folders.

## State ownership

Aura-owned private state uses XDG-aware paths and `0600` files where it may contain location, history or favorites. Omarchy-owned paths are external integration points and are not recursively cleaned or rewritten by maintenance commands.

## Network boundaries

Fresh v1.4 installs keep weather/location and online wallpaper downloads off. Automatic location is HTTPS-only. Manual coordinates avoid IP geolocation. History, favorites, palette extraction, scenes and diagnostics are local. Scenes never turn a network feature on implicitly.

## QML boundary

The bar is split deliberately:

- `BarWidget.qml` — stable Omarchy-settings bridge;
- `BarWidgetImpl.qml` — proven Aura bar behavior and UI.

Atmospheric windows are created from `Quickshell.screens`, so monitor count/geometry are delegated to Quickshell rather than hard-coded for one display.

The large existing `Panel.qml` is intentionally not structurally rewritten during the hardening release. New panel UX can be layered later after v1.4 has a verified real-system baseline.

## Future refactor boundary

Do not split `aura-cycler-core` into many modules during v1.4 hardware validation. That refactor is worthwhile later, but mixing it into the hardening release would make regressions much harder to attribute. Future work should build outward from the stable public/config/hardware/control/runtime boundaries rather than bypassing them.
