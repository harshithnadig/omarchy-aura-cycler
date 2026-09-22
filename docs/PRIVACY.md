# Privacy model

Aura's fresh-install policy is local-first.

- Weather and location are off until explicitly enabled.
- Online wallpaper streaming is off until explicitly enabled.
- Manual coordinates can be used without IP geolocation.
- Automatic geolocation is HTTPS-only.
- History and favorites remain local owner-only state.
- Manual scenes never enable weather or online wallpaper networking implicitly.
- `doctor` performs no network requests.
- `config export` and `privacy` redact manual coordinates by default.
- Cache pruning only removes Aura-generated palette cache files, never wallpaper directories.

Existing users migrating from v1.3 retain their prior weather preference rather than having it silently changed.

## Network-capable features

Network access can occur only through explicitly enabled weather/location or online wallpaper streaming paths. Local wallpaper rotation, Material You analysis, history/favorites, theme scopes, manual scenes and diagnostics do not require a network connection.

## Local private state

Configuration that may contain location data, plus history/favorites files, is written owner-only. Paths to local wallpapers can still be sensitive information, so bug reports and diagnostic sharing should be reviewed by the user before posting publicly.
