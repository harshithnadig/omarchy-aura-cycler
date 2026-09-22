# Aura architecture

Aura v1.4 deliberately uses three executable layers:

1. `bin/aura-cycler` — **control plane**: public CLI, history, favorites, scenes, diagnostics, privacy/config export, cache maintenance and theme live-sync scope.
2. `bin/aura-cycler-runtime` — **hardened runtime**: XDG paths, private config, HTTPS/manual location, weather availability semantics, keyboard policy, cross-vendor GPU protection and transactional theme staging.
3. `bin/aura-cycler-core` — **retained v1.3 feature engine**: wallpaper selection, image validation/downloads, Material You extraction, Omarchy theme generation, hardware keyboard integration and legacy helpers.

The separation is intentional. It keeps the marketplace-approved core easy to diff while v1.4 is tested on real hardware. Once v1.4 is stable, the retained core can be split into normal Python modules in a later refactor without combining that large mechanical change with behavior changes.

## Stable process identity

The control plane sets the hardened runtime's wrapper identity to the public `bin/aura-cycler` path. Detached daemon startup and PID identity validation therefore continue to recognize the public entrypoint rather than leaking the internal layer split into service behavior.

## Theme live-sync boundary

Theme scope filtering applies only to Aura's known post-theme application refresh helpers. Unknown subprocesses are always allowed. This prevents a future Omarchy helper from being silently suppressed simply because Aura does not recognize its name yet.

## State ownership

Aura-owned private state uses XDG-aware paths and `0600` files where it may contain location, history or favorites. Omarchy-owned paths are external integration points and are not recursively cleaned or rewritten by maintenance commands.

## Network boundaries

Fresh v1.4 installs keep weather/location and online wallpaper downloads off. Automatic location is HTTPS-only. Manual coordinates avoid IP geolocation. History, favorites, palette extraction, scenes and diagnostics are local. Scenes never turn a network feature on implicitly.

## Future refactor boundary

Do not split `aura-cycler-core` into many modules during v1.4 hardware validation. That refactor is worthwhile later, but mixing it into the hardening release would make regressions much harder to attribute.
