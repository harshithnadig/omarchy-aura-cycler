# Maintainer notes for v1.4 testing

The v1.4 branch intentionally preserves the already-reviewed v1.3 feature engine in `bin/aura-cycler-core`, keeps privacy/GPU/XDG hardening in `bin/aura-cycler-runtime`, and uses `bin/aura-cycler` as the public control plane.

Do not tag, publish, or merge v1.4 until real Omarchy testing is complete. GitHub CI verifies syntax, pure-Python behavior, manifest structure, smoke checks and QML lint where available, but it cannot prove real Quickshell/Hyprland rendering, NVIDIA/DRM sysfs semantics, keyboard hardware behavior or Omarchy helper compatibility.

The intended handoff is `docs/CODEX_TEST_PROMPT.md`. Reproducible hardware failures should be fixed narrowly on `audit-hardening-v1.4` with regression coverage where practical. Keep `master` on the last approved marketplace snapshot until the release checklist is green.

If the branch becomes difficult to bisect, use the three-layer boundary first: control-plane bugs belong in `bin/aura-cycler`, hardening/runtime bugs in `bin/aura-cycler-runtime`, and retained wallpaper/theme-engine bugs in `bin/aura-cycler-core`.
