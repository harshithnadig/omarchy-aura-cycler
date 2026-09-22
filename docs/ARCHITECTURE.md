# Aura architecture

Aura v1.4 deliberately uses three executable layers:

1. `bin/aura-cycler` — control plane: CLI UX, history, favorites, scenes, diagnostics, privacy/config export, cache maintenance and theme live-sync scope.
2. `bin/aura-cycler-runtime` — hardened v1.4 compatibility layer: XDG paths, private config, HTTPS/manual location, weather availability semantics, keyboard policy, GPU protection and transactional theme staging.
3. `bin/aura-cycler-core` — retained v1.3 feature engine: wallpaper selection, image validation/downloads, Material You extraction, Omarchy theme generation, hardware keyboard integration and legacy helpers.

The separation is intentional. It keeps the marketplace-approved core easy to diff while v1.4 is tested on real hardware. Once v1.4 is stable, the core can be split into normal Python modules in a later refactor without combining that large mechanical change with behavior changes.

## State ownership

Aura-owned private state uses XDG-aware paths and `0600` files where it may contain location or user history. Omarchy-owned paths are external integration points and are not recursively cleaned or rewritten by maintenance commands.

## Network boundaries

Fresh v1.4 installs keep weather/location and online wallpaper downloads off. Automatic location is HTTPS-only. Manual coordinates avoid IP geolocation. History, favorites, palette extraction, scenes and diagnostics are local.
