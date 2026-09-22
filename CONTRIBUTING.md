# Contributing

Thanks for improving Aura Material Cycler.

## Before opening a change

- Keep fresh-install networking opt-in.
- Do not add package installation, privilege escalation or remote-script execution to plugin startup.
- Preserve user-owned wallpaper files and existing Omarchy configuration.
- Prefer bounded reads/downloads and atomic file replacement.
- Add a regression test for bug fixes when practical.
- Run `pytest -q` and `omarchy plugin validate .` when Omarchy is available.

## Architecture

Read `docs/ARCHITECTURE.md` before changing runtime boundaries. During the v1.4 hardening cycle, avoid folding the retained core back into the control plane. That separation makes real-system debugging and rollback straightforward.

## Pull requests

Describe the user-visible behavior, security/privacy impact, test evidence and hardware/driver environment when relevant. Avoid unrelated formatting or mass refactors in a bug-fix PR.
