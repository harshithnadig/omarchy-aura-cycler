# Maintainer notes for v1.4 testing

The v1.4 branch intentionally preserves the already-reviewed v1.3 feature engine in `bin/aura-cycler-core`, moves the hardened runtime layer to `bin/aura-cycler-runtime`, and keeps `bin/aura-cycler` as the public control plane.

Do not tag or publish v1.4 until real Omarchy testing is complete. GitHub CI can verify syntax, pure-Python behavior and regression boundaries, but it cannot prove Quickshell/Hyprland rendering, real GPU sysfs semantics, keyboard hardware behavior or Omarchy helper compatibility.
