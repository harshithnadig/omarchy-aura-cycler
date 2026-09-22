"""Portable hardware adaptation for Aura Material Cycler.

This layer deliberately sits above the preserved runtime/core. It discovers
available GPU and keyboard capabilities at runtime and degrades gracefully when
a backend is absent. No vendor is required for Aura's core wallpaper features.
"""

from __future__ import annotations

import csv
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

GPU_VENDOR_IDS = {
    "0x1002": "amd",
    "0x8086": "intel",
}

_CACHE = None
_CACHE_TIME = 0.0


def _read_int(path, default=None):
    try:
        return int(Path(path).read_text(encoding="utf-8").strip())
    except (OSError, ValueError, TypeError):
        return default


def _read_text(path, default=""):
    try:
        return Path(path).read_text(encoding="utf-8").strip()
    except OSError:
        return default


def _safe_float(value, default=0.0):
    try:
        text = str(value).strip()
        if not text or text.lower() in {"n/a", "[n/a]", "not supported"}:
            return default
        return float(text)
    except (TypeError, ValueError):
        return default


def _safe_int(value, default=0):
    return int(_safe_float(value, default))


def _nvidia_gpus(binary=None):
    binary = binary or shutil.which("nvidia-smi")
    if not binary:
        return [], []
    try:
        result = subprocess.run(
            [
                binary,
                "--query-gpu=index,name,memory.used,memory.total,utilization.gpu,temperature.gpu,power.draw,power.limit",
                "--format=csv,noheader,nounits",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=3,
            env={**os.environ, "LC_ALL": "C"},
        )
    except (OSError, subprocess.TimeoutExpired):
        return [], []
    if result.returncode != 0:
        return [], []

    gpus = []
    for line in result.stdout.splitlines():
        fields = next(csv.reader([line], skipinitialspace=True), [])
        if len(fields) < 8:
            continue
        total = max(0, _safe_int(fields[3]))
        used = max(0, _safe_int(fields[2]))
        gpus.append({
            "available": True,
            "provider": "nvidia",
            "index": _safe_int(fields[0], len(gpus)),
            "name": fields[1].strip() or "NVIDIA GPU",
            "used_mib": used,
            "total_mib": total,
            "vram_percent": round((used / total) * 100, 1) if total else 0.0,
            "utilization_percent": max(0, min(100, _safe_int(fields[4]))),
            "temperature_c": max(0, _safe_int(fields[5])),
            "power_draw_w": max(0.0, round(_safe_float(fields[6]), 1)),
            "power_limit_w": max(0.0, round(_safe_float(fields[7]), 1)),
        })

    processes = []
    try:
        proc = subprocess.run(
            [binary, "--query-compute-apps=pid,name,used_memory", "--format=csv,noheader,nounits"],
            check=False,
            capture_output=True,
            text=True,
            timeout=3,
            env={**os.environ, "LC_ALL": "C"},
        )
        if proc.returncode == 0:
            for line in proc.stdout.splitlines():
                fields = next(csv.reader([line], skipinitialspace=True), [])
                if len(fields) < 3:
                    continue
                pid = _safe_int(fields[0], -1)
                if pid < 0:
                    continue
                processes.append({
                    "pid": pid,
                    "name": fields[1].strip(),
                    "used_mib": max(0, _safe_int(fields[2])),
                })
            processes.sort(key=lambda item: item["used_mib"], reverse=True)
            processes = processes[:8]
    except (OSError, subprocess.TimeoutExpired):
        pass
    return gpus, processes


def _drm_gpus(drm_root=Path("/sys/class/drm")):
    drm_root = Path(drm_root)
    if not drm_root.is_dir():
        return []

    gpus = []
    for card in sorted(drm_root.glob("card[0-9]*")):
        device = card / "device"
        vendor_id = _read_text(device / "vendor").lower()
        provider = GPU_VENDOR_IDS.get(vendor_id)
        if not provider:
            continue

        total_bytes = _read_int(device / "mem_info_vram_total", 0) or 0
        used_bytes = _read_int(device / "mem_info_vram_used", 0) or 0
        total_mib = int(total_bytes / (1024 * 1024)) if total_bytes else 0
        used_mib = int(used_bytes / (1024 * 1024)) if used_bytes else 0
        busy = _read_int(device / "gpu_busy_percent", 0) or 0

        temperature = 0
        hwmon_root = device / "hwmon"
        if hwmon_root.is_dir():
            for hwmon in sorted(hwmon_root.glob("hwmon*")):
                raw = _read_int(hwmon / "temp1_input")
                if raw is not None:
                    temperature = int(raw / 1000) if raw > 1000 else int(raw)
                    break

        # Some integrated Intel GPUs expose neither dedicated VRAM nor a busy
        # counter. If the kernel exports no useful telemetry, skip the card
        # rather than inventing numbers; Aura's core features still work.
        if not (total_mib or used_mib or busy or temperature):
            continue

        device_id = _read_text(device / "device")
        suffix = f" {device_id}" if device_id else ""
        gpus.append({
            "available": True,
            "provider": provider,
            "index": card.name,
            "name": f"{provider.upper()} GPU{suffix} ({card.name})",
            "used_mib": max(0, used_mib),
            "total_mib": max(0, total_mib),
            "vram_percent": round((used_mib / total_mib) * 100, 1) if total_mib else 0.0,
            "utilization_percent": max(0, min(100, busy)),
            "temperature_c": max(0, temperature),
            "power_draw_w": 0.0,
            "power_limit_w": 0.0,
        })
    return gpus


def _aggregate_gpus(gpus):
    available = [dict(gpu) for gpu in gpus if gpu.get("available")]
    if not available:
        return None

    memory_gpu = max(available, key=lambda gpu: float(gpu.get("vram_percent", 0) or 0))
    providers = sorted({str(gpu.get("provider") or "unknown") for gpu in available})
    aggregate = {
        "available": True,
        "provider": providers[0] if len(providers) == 1 else "multi",
        "name": available[0].get("name", "GPU") if len(available) == 1 else f"Multi-GPU system ({len(available)})",
        "used_mib": int(memory_gpu.get("used_mib", 0) or 0),
        "total_mib": int(memory_gpu.get("total_mib", 0) or 0),
        # Auto-Protect sees the worst pressure on any GPU instead of whichever
        # card happens to enumerate first.
        "vram_percent": max(float(gpu.get("vram_percent", 0) or 0) for gpu in available),
        "utilization_percent": max(int(gpu.get("utilization_percent", 0) or 0) for gpu in available),
        "temperature_c": max(int(gpu.get("temperature_c", 0) or 0) for gpu in available),
        "power_draw_w": round(sum(float(gpu.get("power_draw_w", 0) or 0) for gpu in available), 1),
        "power_limit_w": round(sum(float(gpu.get("power_limit_w", 0) or 0) for gpu in available), 1),
        "gpu_count": len(available),
        "gpus": available,
    }
    return aggregate


def _collect_portable_gpu_metrics(control, max_age=5.0):
    global _CACHE, _CACHE_TIME
    now = time.time()
    if _CACHE is not None and now - _CACHE_TIME < max_age:
        return _CACHE

    nvidia, processes = _nvidia_gpus()
    drm = _drm_gpus()
    aggregate = _aggregate_gpus(nvidia + drm)
    if aggregate is None:
        # Preserve the runtime's useful unavailable/error shape when no backend
        # exposes telemetry (VMs, unsupported iGPUs, headless systems, etc.).
        try:
            original = control.runtime._original_collect_gpu_guard_metrics
            metrics, old_processes = original(max_age=max_age)
            if metrics.get("available"):
                metrics = dict(metrics)
                metrics.setdefault("gpu_count", 1)
                metrics.setdefault("gpus", [dict(metrics)])
                _CACHE = (metrics, old_processes)
            else:
                _CACHE = (metrics, [])
        except Exception:
            _CACHE = ({"available": False, "error": "No supported GPU telemetry backend detected"}, [])
    else:
        _CACHE = (aggregate, processes)

    _CACHE_TIME = now
    control.core._LAST_GPU_METRICS = _CACHE
    control.core._LAST_GPU_METRICS_TIME = now
    return _CACHE


def _keyboard_capabilities(control):
    core = control.core
    device = None
    try:
        device = core.find_keyboard_backlight_device()
    except Exception:
        device = None
    return {
        "backlight_device": bool(device),
        "asusctl": bool(shutil.which("asusctl")),
        "openrgb": bool(shutil.which("openrgb")),
        "brightnessctl": bool(shutil.which("brightnessctl")),
        "mode": "rgb" if (shutil.which("asusctl") or shutil.which("openrgb")) else ("monochrome" if device else "unavailable"),
    }


def _set_keyboard_color_portable(control, hex_code):
    core = control.core
    cfg = control.runtime.load_config()
    if not cfg.get("keyboard_sync", True):
        return False

    clean_hex = str(hex_code).lstrip("#").upper()
    if not re.fullmatch(r"[0-9A-F]{6}", clean_hex):
        core.log(f"Skipped invalid keyboard color: {hex_code}")
        return False

    try:
        level = core.get_keyboard_brightness()
    except Exception:
        level = None

    # If a laptop backlight is explicitly off, preserve that manual state.
    # A desktop with no brightness device reports None and may still use
    # OpenRGB, which is the portability gap the old implementation missed.
    if level == "off":
        core.last_keyboard_level = "off"
        core.last_keyboard_color = clean_hex
        core.log("Keyboard backlight is OFF; preserving manual Off state.")
        return False

    if level == getattr(core, "last_keyboard_level", None) and clean_hex == str(getattr(core, "last_keyboard_color", "") or "").upper():
        return True

    asusctl = shutil.which("asusctl")
    if asusctl:
        try:
            result = subprocess.run(
                [asusctl, "aura", "effect", "static", "--colour", clean_hex],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
            )
            if result.returncode == 0:
                core.last_keyboard_level = level
                core.last_keyboard_color = clean_hex
                core.log(f"ASUS RGB synced to #{clean_hex}.")
                return True
        except (OSError, subprocess.TimeoutExpired):
            pass

    openrgb = shutil.which("openrgb")
    if openrgb:
        try:
            result = subprocess.run(
                [openrgb, "--color", clean_hex, "--mode", "static"],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
            )
            if result.returncode == 0:
                core.last_keyboard_level = level
                core.last_keyboard_color = clean_hex
                core.log(f"OpenRGB color synced to #{clean_hex}.")
                return True
        except (OSError, subprocess.TimeoutExpired):
            pass

    if level is not None:
        # Monochrome laptop keyboards cannot display the palette color, but
        # reporting success here preserves the existing brightness-aware model
        # without pretending RGB support exists.
        core.last_keyboard_level = level
        core.last_keyboard_color = clean_hex
        core.log(f"Monochrome keyboard backlight active at '{level}'; RGB color is unsupported by this device.")
        return True

    return False


def install(control):
    """Install portable hardware discovery without changing core feature APIs."""
    control.core.collect_gpu_guard_metrics = lambda max_age=5.0: _collect_portable_gpu_metrics(control, max_age=max_age)
    control.core.set_keyboard_color = lambda color: _set_keyboard_color_portable(control, color)


def hardware_summary(control):
    metrics, _processes = control.core.collect_gpu_guard_metrics(max_age=0)
    return {
        "gpu": metrics,
        "keyboard": _keyboard_capabilities(control),
        "systemd_user_available": bool(shutil.which("systemctl")),
        "session_type": os.environ.get("XDG_SESSION_TYPE", "unknown"),
        "desktop": os.environ.get("XDG_CURRENT_DESKTOP", "unknown"),
        "architecture": os.uname().machine if hasattr(os, "uname") else "unknown",
    }


def dispatch(control, args):
    if not args or args[0] not in {"hardware", "capabilities"}:
        return None
    print(json.dumps(hardware_summary(control), indent=2, sort_keys=True))
    return 0
