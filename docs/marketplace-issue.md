# Marketplace notes for Aura Material Cycler

The currently published marketplace snapshot remains v1.3 at the approved `master` commit. The `audit-hardening-v1.4` branch is intentionally **not** a marketplace submission yet.

Before proposing v1.4 for marketplace revalidation:

1. complete `RELEASE_CHECKLIST.md` on a real Omarchy system;
2. merge the tested branch to `master`;
3. tag/release the exact tested commit;
4. update the marketplace submission to the exact new `master` SHA;
5. explicitly call out the network/service/package capabilities for security review.

v1.4 adds no silent package installation or privilege escalation. Fresh installs keep weather/location and online wallpaper streaming off until explicitly enabled. Automatic IP geolocation is HTTPS-only; manual location avoids IP geolocation. GPU Auto-Protect pauses Aura's own expensive cycling work rather than stopping unrelated workloads. History/favorites and diagnostics are local-only.
