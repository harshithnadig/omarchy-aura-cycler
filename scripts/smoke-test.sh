#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLI="$ROOT/bin/aura-cycler"
RUNTIME="$ROOT/bin/aura-cycler-runtime"
CORE="$ROOT/bin/aura-cycler-core"

# Only the public controller is an executable CLI. The retained implementation
# layers are import-only so users/services do not accidentally bypass v1.4
# privacy and control-plane policy.
test -x "$CLI"
test ! -x "$RUNTIME"
test ! -x "$CORE"

python -m py_compile \
  "$CLI" \
  "$RUNTIME" \
  "$CORE" \
  "$ROOT/bin/aura-cycler-service-guard"
python -m json.tool "$ROOT/manifest.json" >/dev/null
"$CLI" version
"$CLI" privacy >/dev/null
"$CLI" config export >/dev/null
"$CLI" cache status >/dev/null
"$CLI" doctor --json >/dev/null || true

if command -v omarchy >/dev/null 2>&1; then
  omarchy plugin validate "$ROOT"
else
  echo "omarchy not available; skipped plugin validate"
fi

echo "Aura smoke checks completed"
