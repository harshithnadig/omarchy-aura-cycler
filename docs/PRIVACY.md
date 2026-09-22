# Privacy model

Aura's fresh-install policy is local-first.

- Weather and location are off until explicitly enabled.
- Online wallpaper streaming is off until explicitly enabled.
- Manual coordinates can be used without IP geolocation.
- Automatic geolocation is HTTPS-only.
- History and favorites remain local owner-only state.
- `doctor` performs no network requests.
- `config export` and `privacy` redact manual coordinates by default.
- Cache pruning only removes Aura-generated palette cache files, never wallpaper directories.

Existing users migrating from v1.3 retain their prior weather preference rather than having it silently changed.
