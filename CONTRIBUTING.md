# Contributing

Thanks for improving Aura Material Cycler.

## Before opening a change

- Keep fresh-install networking opt-in.
- Do not add package installation, privilege escalation or remote-script execution to plugin startup.
- Preserve user-owned wallpaper files and existing Omarchy configuration.
- Prefer bounded reads/downloads and atomic file replacement.
- Add a regression test for bug fixes when practical.
- Run `pytest -q`, `scripts/smoke-test.sh`, and `omarchy plugin validate .` when Omarchy is available.

## Architecture

Read `docs/ARCHITECTURE.md` and `docs/EXTENDING.md` before changing runtime boundaries.

The v1.4 baseline has one executable entrypoint: `bin/aura-cycler`. Config/control/runtime/core layers are import-only. Do not add a second executable that bypasses config migrations, recovery, privacy policy or process identity checks.

There is one canonical Aura runtime config. New persistent settings must use the installed `runtime.load_config()` / `runtime.save_config()` / `runtime.update_config()` API rather than writing a parallel settings file.

During the v1.4 hardening cycle, avoid folding the retained core back into the control plane. That separation makes real-system debugging and rollback straightforward.

## Configuration changes

For new persistent config:

- choose a privacy-safe default;
- add normalization/migration semantics where needed;
- bump the config schema only when a real migration is required;
- update manifest defaults/schema if the setting belongs in Omarchy's native widget settings;
- add regression coverage for migration and concurrent/stale updates where relevant.

## Hardware-specific fixes

Do not infer a driver workaround from a single error message. Include the GPU/driver or keyboard hardware, a reproducible command/action, relevant `bin/aura-cycler doctor` output, and the smallest fix that resolves the observed behavior. Preserve graceful degradation on hardware that does not expose the same metrics/features.

## Pull requests

Describe the user-visible behavior, security/privacy impact, test evidence and hardware/driver environment when relevant. Avoid unrelated formatting or mass refactors in a bug-fix PR.
