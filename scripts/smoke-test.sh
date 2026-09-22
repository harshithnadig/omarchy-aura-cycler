#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLI="$ROOT/bin/aura-cycler"

python -m py_compile \
  "$ROOT/bin/aura-cycler" \
  "$ROOT/bin/aura-cycler-runtime" \
  "$ROOT/bin/aura-cycler-core" \
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
