#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLI="$ROOT/bin/aura-cycler"
CONTROL="$ROOT/bin/aura-cycler-control"
CONFIG_LAYER="$ROOT/bin/aura-config.py"
RUNTIME="$ROOT/bin/aura-cycler-runtime"
CORE="$ROOT/bin/aura-cycler-core"

# Only the public controller is an executable CLI. Every implementation layer
# stays import-only so normal users/services cannot bypass v1.4 policy.
test -x "$CLI"
test ! -x "$CONTROL"
test ! -x "$CONFIG_LAYER"
test ! -x "$RUNTIME"
test ! -x "$CORE"

python -m py_compile \
  "$CLI" \
  "$CONTROL" \
  "$CONFIG_LAYER" \
  "$RUNTIME" \
  "$CORE" \
  "$ROOT/bin/aura-cycler-service-guard"
python -m json.tool "$ROOT/manifest.json" >/dev/null
"$CLI" version
"$CLI" privacy >/dev/null
"$CLI" config export >/dev/null
"$CLI" cache status >/dev/null
"$CLI" doctor --json >/dev/null || true

# Maintenance commands must remain available without needing a live shell.
TMP_BACKUP="$(mktemp)"
rm -f "$TMP_BACKUP"
"$CLI" backup "$TMP_BACKUP" >/dev/null
test -s "$TMP_BACKUP"
python - <<'PY' "$TMP_BACKUP"
import json, os, stat, sys
path = sys.argv[1]
data = json.load(open(path, encoding="utf-8"))
assert data["format"] == "aura-backup"
assert data["backup_version"] == 1
assert stat.S_IMODE(os.stat(path).st_mode) == 0o600
PY
rm -f "$TMP_BACKUP"

if command -v omarchy >/dev/null 2>&1; then
  omarchy plugin validate "$ROOT"
else
  echo "omarchy not available; skipped plugin validate"
fi

echo "Aura smoke checks completed"
