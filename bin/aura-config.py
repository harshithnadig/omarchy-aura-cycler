"""Transactional configuration and maintenance layer for Aura Material Cycler.

Loaded by the public ``bin/aura-cycler`` entrypoint.  The implementation layers
remain import-only so every normal Aura process receives the same migration,
locking, recovery, backup, and Omarchy-settings policy.
"""

from __future__ import annotations

import contextlib
import copy
import fcntl
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

CONFIG_VERSION = 2
BACKUP_VERSION = 1
PLUGIN_ID = "harshith.aura-cycler"
NATIVE_SETTING_KEYS = {
    "interval": "interval",
    "blur": "blur",
    "weatherSync": "weather_sync",
    "streamOnline": "stream_online",
    "screenEffects": "screen_effects",
    "keyboardSync": "keyboard_sync",
    "themeScope": "theme_scope",
}
PRIVATE_CONFIG_KEYS = {"location_cache", "manual_location", "weather_cache"}
_MISSING = object()
_INSTALLED = False
_LAST_SNAPSHOT = None


class ConfigState(dict):
    """dict carrying the exact base snapshot used for conflict-aware saves."""

    def __init__(self, value=None, *, base=None):
        super().__init__(value or {})
        self._aura_base = copy.deepcopy(base if base is not None else dict(self))


def _stamp():
    return time.strftime("%Y%m%d-%H%M%S")


def _json_copy(value):
    return copy.deepcopy(value)


def _safe_json(path):
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except (OSError, ValueError, TypeError):
        return None


def _nested_diff(base, new):
    if isinstance(base, dict) and isinstance(new, dict):
        patch = {}
        for key in base.keys() | new.keys():
            if key not in new:
                patch[key] = _MISSING
            elif key not in base:
                patch[key] = _json_copy(new[key])
            else:
                child = _nested_diff(base[key], new[key])
                if child is not None:
                    patch[key] = child
        return patch or None
    if base != new:
        return _json_copy(new)
    return None


def _apply_patch(target, patch):
    if not isinstance(patch, dict) or not isinstance(target, dict):
        return _json_copy(patch)
    result = _json_copy(target)
    for key, value in patch.items():
        if value is _MISSING:
            result.pop(key, None)
        elif isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _apply_patch(result[key], value)
        else:
            result[key] = _json_copy(value)
    return result


def _normalize(cfg, runtime):
    cfg = _json_copy(dict(cfg) if isinstance(cfg, dict) else {})

    def clamp_int(value, default, low, high):
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            parsed = default
        return max(low, min(high, parsed))

    cfg["config_version"] = CONFIG_VERSION
    cfg["interval"] = clamp_int(cfg.get("interval", 300), 300, 5, 86400)
    cfg["blur"] = clamp_int(cfg.get("blur", 12), 12, 0, 24)
    for key in ("weather_sync", "stream_online", "screen_effects", "keyboard_sync"):
        cfg[key] = bool(cfg.get(key, False if key != "keyboard_sync" else True))
    if cfg.get("location_mode") not in {"off", "auto", "manual"}:
        cfg["location_mode"] = "off"
    if cfg.get("theme_scope") not in {"shell", "terminals", "editors", "all"}:
        cfg["theme_scope"] = "all"
    if not isinstance(cfg.get("gpu_guard"), dict):
        cfg["gpu_guard"] = copy.deepcopy(runtime.core.GPU_GUARD_DEFAULTS)
    else:
        guard = copy.deepcopy(runtime.core.GPU_GUARD_DEFAULTS)
        guard.update(cfg["gpu_guard"])
        cfg["gpu_guard"] = guard
    return cfg


def _shell_explicit_settings(control):
    """Return settings explicitly stored on Aura's bar entry, excluding manifest defaults."""
    shell_path = Path(control.runtime.XDG_CONFIG_HOME) / "omarchy" / "shell.json"
    data = _safe_json(shell_path)
    if not data:
        return {}
    try:
        layout = data.get("bar", {}).get("layout", {})
        for section in ("left", "center", "right"):
            entries = layout.get(section, [])
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if isinstance(entry, dict) and entry.get("id") == PLUGIN_ID:
                    return {key: entry[key] for key in NATIVE_SETTING_KEYS if key in entry}
    except (AttributeError, TypeError):
        return {}
    return {}


def install(control):
    """Install the transactional config API into Aura's runtime and core."""
    global _INSTALLED, _LAST_SNAPSHOT
    if _INSTALLED:
        return
    runtime = control.runtime
    core = control.core
    original_load = runtime.load_config
    original_save = runtime.save_config
    lock_path = Path(runtime.XDG_RUNTIME_DIR) / "aura-cycler-config.lock"
    config_path = Path(core.CONFIG_FILE)

    @contextlib.contextmanager
    def locked(exclusive=True):
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
            yield
        finally:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                os.close(fd)

    def recover_corrupt_locked():
        if not config_path.exists():
            return None
        raw = _safe_json(config_path)
        if raw is not None:
            return raw
        backup = config_path.with_name(f"{config_path.stem}.corrupt-{_stamp()}{config_path.suffix}")
        try:
            os.replace(config_path, backup)
            core.log(f"Recovered malformed Aura config; preserved copy at {backup}")
            return None
        except OSError as error:
            core.log(f"Could not preserve malformed Aura config: {error}")
            return None

    def migrate_locked(cfg):
        before = _json_copy(cfg)
        try:
            version = int(cfg.get("config_version", 0) or 0)
        except (TypeError, ValueError):
            version = 0
        if version < 1:
            cfg.setdefault("theme_scope", "all")
            cfg.setdefault("scene", "custom")
        if version < 2:
            # v2 formalizes privacy-safe defaults and the native settings bridge.
            cfg.setdefault("location_mode", "auto" if cfg.get("weather_sync") else "off")
            cfg.setdefault("keyboard_sync", True)
        cfg = _normalize(cfg, runtime)
        return cfg, cfg != before

    def load_config():
        global _LAST_SNAPSHOT
        with locked(True):
            recover_corrupt_locked()
            cfg = original_load()
            cfg, changed = migrate_locked(cfg)
            if changed:
                original_save(cfg)
            _LAST_SNAPSHOT = _json_copy(cfg)
            return ConfigState(cfg, base=cfg)

    def _native_changed(before, after):
        changed = {}
        reverse = {private: public for public, private in NATIVE_SETTING_KEYS.items()}
        for private, public in reverse.items():
            if before.get(private, _MISSING) != after.get(private, _MISSING):
                changed[public] = after.get(private)
        return changed

    def _sync_omarchy_settings(changed):
        if not changed or os.environ.get("AURA_DISABLE_SHELL_SETTINGS_SYNC") == "1":
            return
        binary = shutil.which("omarchy-shell")
        if not binary:
            return
        for key, value in changed.items():
            try:
                completed = subprocess.run(
                    [binary, "shell", "setBarWidget", PLUGIN_ID, key, json.dumps(value), "{}"],
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=3,
                    check=False,
                )
                if completed.returncode != 0 or completed.stdout.strip() not in {"", "ok"}:
                    core.log(f"Omarchy settings mirror skipped for {key}: {(completed.stderr or completed.stdout).strip()}")
            except (OSError, subprocess.TimeoutExpired) as error:
                core.log(f"Omarchy settings mirror unavailable for {key}: {error}")

    def save_config(cfg, *, sync_shell=True):
        global _LAST_SNAPSHOT
        base = getattr(cfg, "_aura_base", None)
        incoming = _normalize(cfg, runtime)
        with locked(True):
            recover_corrupt_locked()
            current = _normalize(original_load(), runtime)
            if not isinstance(base, dict):
                base = _LAST_SNAPSHOT
            if isinstance(base, dict):
                patch = _nested_diff(base, incoming)
                final = _apply_patch(current, patch) if patch is not None else current
            else:
                final = incoming
            final = _normalize(final, runtime)
            original_save(final)
            changed = _native_changed(current, final)
            _LAST_SNAPSHOT = _json_copy(final)
        if sync_shell:
            _sync_omarchy_settings(changed)
        return ConfigState(final, base=final)

    def update_config(mutator, *, sync_shell=True):
        global _LAST_SNAPSHOT
        with locked(True):
            recover_corrupt_locked()
            current = _normalize(original_load(), runtime)
            before = _json_copy(current)
            candidate = _json_copy(current)
            result = mutator(candidate)
            if isinstance(result, dict):
                candidate = result
            final = _normalize(candidate, runtime)
            original_save(final)
            changed = _native_changed(before, final)
            _LAST_SNAPSHOT = _json_copy(final)
        if sync_shell:
            _sync_omarchy_settings(changed)
        return ConfigState(final, base=final)

    runtime.load_config = load_config
    runtime.save_config = save_config
    runtime.update_config = update_config
    runtime.sync_native_settings = _sync_omarchy_settings
    core.load_config = load_config
    core.save_config = save_config
    control.load_config = load_config
    control.save_config = save_config
    control.update_config = update_config
    control.CONFIG_VERSION = CONFIG_VERSION
    control.CONFIG_LOCK_FILE = str(lock_path)
    _LAST_SNAPSHOT = None
    _INSTALLED = True


def _redact_config(cfg, private=False):
    result = _json_copy(cfg)
    if not private:
        for key in PRIVATE_CONFIG_KEYS:
            if key in result:
                result[key] = {"configured": bool(result[key]), "redacted": True} if result[key] else None
    return result


def _write_bundle(path, payload):
    target = Path(path).expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".aura-backup-", dir=str(target.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp, 0o600)
        os.replace(tmp, target)
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass
    return target


def _backup(control, args):
    private = "--private" in args
    paths = [arg for arg in args if not arg.startswith("--")]
    if len(paths) != 1:
        print("Usage: aura-cycler backup <file> [--private]")
        return 2
    cfg = control.runtime.load_config()
    payload = {
        "format": "aura-backup",
        "backup_version": BACKUP_VERSION,
        "aura_version": control.VERSION,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "private": private,
        "config": _redact_config(cfg, private=private),
        "history": control._read_json(control.HISTORY_FILE, {"version": 1, "items": []}),
        "favorites": control._read_json(control.FAVORITES_FILE, {"version": 1, "items": []}),
    }
    key_file = Path(control.runtime.core.WALLHAVEN_KEY_FILE)
    if private and key_file.is_file():
        try:
            payload["wallhaven_key"] = key_file.read_text(encoding="utf-8").strip()
        except OSError:
            pass
    target = _write_bundle(paths[0], payload)
    print(f"Aura backup written: {target}")
    return 0


def _restore(control, args):
    paths = [arg for arg in args if not arg.startswith("--")]
    if len(paths) != 1:
        print("Usage: aura-cycler restore <file>")
        return 2
    source = Path(paths[0]).expanduser()
    data = _safe_json(source)
    if not data or data.get("format") != "aura-backup" or data.get("backup_version") != BACKUP_VERSION:
        print("Not a supported Aura backup file.")
        return 2
    cfg = data.get("config")
    if not isinstance(cfg, dict):
        print("Backup does not contain a valid config object.")
        return 2
    # Redacted backups are intentionally useful for inspection, not restoration
    # of location caches. Drop redaction placeholders rather than treating them
    # as real coordinates/weather data.
    for key in PRIVATE_CONFIG_KEYS:
        value = cfg.get(key)
        if isinstance(value, dict) and value.get("redacted") is True:
            cfg.pop(key, None)

    emergency = Path(control.runtime.AURA_STATE_DIR) / f"pre-restore-{_stamp()}.json"
    _write_bundle(emergency, {
        "format": "aura-backup",
        "backup_version": BACKUP_VERSION,
        "aura_version": control.VERSION,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "private": True,
        "config": control.runtime.load_config(),
        "history": control._read_json(control.HISTORY_FILE, {"version": 1, "items": []}),
        "favorites": control._read_json(control.FAVORITES_FILE, {"version": 1, "items": []}),
    })

    control.runtime.update_config(lambda current: {**current, **cfg})
    if isinstance(data.get("history"), dict):
        control._write_private_json(control.HISTORY_FILE, data["history"])
    if isinstance(data.get("favorites"), dict):
        control._write_private_json(control.FAVORITES_FILE, data["favorites"])
    if data.get("private") and isinstance(data.get("wallhaven_key"), str):
        key_file = Path(control.runtime.core.WALLHAVEN_KEY_FILE)
        key_file.parent.mkdir(parents=True, exist_ok=True)
        control.runtime.core.atomic_write_text(str(key_file), data["wallhaven_key"].strip() + "\n", 0o600)
    print(f"Aura backup restored. Automatic pre-restore backup: {emergency}")
    return 0


def _reset(control, args):
    keep_favorites = "--keep-favorites" in args
    keep_folders = "--keep-folders" in args
    current = control.runtime.load_config()
    fresh = copy.deepcopy(control.runtime.core.DEFAULT_CONFIG)
    fresh["config_version"] = CONFIG_VERSION
    fresh["theme_scope"] = "all"
    fresh["scene"] = "custom"
    if keep_folders:
        fresh["custom_folders"] = copy.deepcopy(current.get("custom_folders", fresh.get("custom_folders", [])))
    control.runtime.update_config(lambda _cfg: fresh)
    control._save_history([])
    if not keep_favorites:
        control._save_favorites([])
    print("Aura settings reset to privacy-safe defaults" + ("; favorites kept" if keep_favorites else "") + ".")
    return 0


def _settings_import(control, args):
    if len(args) != 1:
        print("Usage: aura-cycler settings-import <json>")
        return 2
    try:
        injected = json.loads(args[0])
    except (ValueError, TypeError):
        print("Invalid settings JSON.")
        return 2
    if not isinstance(injected, dict):
        print("Settings must be a JSON object.")
        return 2

    # Omarchy injects manifest defaults even when the user has never changed a
    # setting. On the first v1.4 load we must not let those defaults overwrite
    # a v1.3 user's existing Aura config. Prefer values explicitly present in
    # shell.json; if there are none yet, mirror Aura's existing values outward.
    explicit = _shell_explicit_settings(control)
    if not explicit:
        cfg = control.runtime.load_config()
        control.runtime.sync_native_settings({
            public: cfg.get(private) for public, private in NATIVE_SETTING_KEYS.items()
        })
        return 0

    raw = explicit
    updates = {}
    for public, private in NATIVE_SETTING_KEYS.items():
        if public not in raw:
            continue
        value = raw[public]
        if private == "interval":
            try:
                value = max(5, min(86400, int(value)))
            except (TypeError, ValueError):
                continue
        elif private == "blur":
            try:
                value = max(0, min(24, int(value)))
            except (TypeError, ValueError):
                continue
        elif private in {"weather_sync", "stream_online", "screen_effects", "keyboard_sync"}:
            value = value is True
        elif private == "theme_scope":
            value = str(value)
            if value not in {"shell", "terminals", "editors", "all"}:
                continue
        updates[private] = value

    if updates:
        def mutate(cfg):
            cfg.update(updates)
            if "weather_sync" in updates and not updates["weather_sync"]:
                # Disabling weather through native settings must not cause a
                # location request. Preserve the selected location mode for a
                # future re-enable, but weather code will not access it.
                cfg["weather_sync"] = False
            return cfg
        control.runtime.update_config(mutate, sync_shell=False)
    return 0


def dispatch(control, argv):
    """Return None when the normal Aura control plane should handle argv."""
    if not argv:
        return None
    action, args = argv[0], argv[1:]
    if action == "backup":
        return _backup(control, args)
    if action == "restore":
        return _restore(control, args)
    if action == "reset":
        return _reset(control, args)
    if action == "settings-import":
        return _settings_import(control, args)
    return None
