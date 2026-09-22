# Security and privacy

Aura is an unsandboxed Omarchy plugin and therefore runs with the permissions of the logged-in user. Review plugin updates before enabling them.

## Network behavior

A fresh v1.4 install is designed to work without network access.

Network requests occur only after the corresponding feature is explicitly enabled:

- **Automatic weather location:** `https://ipapi.co/json/`
- **Weather:** `https://api.open-meteo.com/`
- **Optional online wallpapers:** Wallhaven and Bing HTTPS endpoints

Manual coordinates can be used instead of IP geolocation.

Remote JSON responses and wallpaper downloads are size-bounded. Download destinations are restricted to Aura's wallpaper cache and downloaded images are validated before publication.

## Local state

Aura may store:
- selected wallpaper paths;
- generated palette data;
- weather cache;
- optional location coordinates/city;
- GPU guard state.

The main config and palette state are owner-only. Logs may contain operational details such as wallpaper file names and weather lookup failures; do not put secrets in wallpaper paths or API error messages.

## Hardware access

Aura may invoke user-installed tools such as:
- `nvidia-smi`
- `asusctl`
- `openrgb`
- `brightnessctl`

It may also read Linux DRM/sysfs telemetry and keyboard backlight state. Aura does not require root privileges and should not be run as root.

## systemd

Systemd supervision is optional. The service unit launches an external guard stored outside the mutable plugin checkout. The guard verifies the expected plugin id, user ownership, non-symlink path components and executable entry point before launching Aura.

## Reporting a vulnerability

Please open a GitHub issue for non-sensitive security defects. For a vulnerability that would expose credentials, execute unintended commands, escape cache/state boundaries, or overwrite unrelated user data, avoid publishing exploit details until a private reporting route is available; open a minimal issue asking the maintainer for a private contact channel.
