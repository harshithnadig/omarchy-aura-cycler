import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
from types import SimpleNamespace

MODULE = Path(__file__).parents[1] / "bin" / "aura-hardware.py"


def load_hardware(name="aura_hardware_test"):
    loader = SourceFileLoader(name, str(MODULE))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(value), encoding="utf-8")


def test_aggregate_multi_gpu_uses_worst_pressure():
    hw = load_hardware()
    aggregate = hw._aggregate_gpus([
        {
            "available": True,
            "provider": "intel",
            "name": "Intel iGPU",
            "used_mib": 0,
            "total_mib": 0,
            "vram_percent": 0.0,
            "utilization_percent": 94,
            "temperature_c": 61,
            "power_draw_w": 0.0,
            "power_limit_w": 0.0,
        },
        {
            "available": True,
            "provider": "amd",
            "name": "AMD dGPU",
            "used_mib": 7200,
            "total_mib": 8000,
            "vram_percent": 90.0,
            "utilization_percent": 72,
            "temperature_c": 89,
            "power_draw_w": 0.0,
            "power_limit_w": 0.0,
        },
    ])
    assert aggregate["provider"] == "multi"
    assert aggregate["gpu_count"] == 2
    assert aggregate["vram_percent"] == 90.0
    assert aggregate["utilization_percent"] == 94
    assert aggregate["temperature_c"] == 89
    assert len(aggregate["gpus"]) == 2


def test_drm_scan_does_not_stop_at_first_gpu(tmp_path):
    hw = load_hardware("aura_hardware_drm_test")
    drm = tmp_path / "drm"

    intel = drm / "card0" / "device"
    write(intel / "vendor", "0x8086")
    write(intel / "device", "0x1234")
    write(intel / "gpu_busy_percent", "25")
    write(intel / "hwmon" / "hwmon0" / "temp1_input", "52000")

    amd = drm / "card1" / "device"
    write(amd / "vendor", "0x1002")
    write(amd / "device", "0xabcd")
    write(amd / "mem_info_vram_total", str(8 * 1024 * 1024 * 1024))
    write(amd / "mem_info_vram_used", str(7 * 1024 * 1024 * 1024))
    write(amd / "gpu_busy_percent", "77")
    write(amd / "hwmon" / "hwmon1" / "temp1_input", "81000")

    gpus = hw._drm_gpus(drm)
    assert len(gpus) == 2
    assert {gpu["provider"] for gpu in gpus} == {"intel", "amd"}
    aggregate = hw._aggregate_gpus(gpus)
    assert aggregate["gpu_count"] == 2
    assert aggregate["temperature_c"] == 81
    assert aggregate["vram_percent"] == 87.5


def test_desktop_openrgb_works_without_laptop_backlight(monkeypatch):
    hw = load_hardware("aura_hardware_keyboard_test")
    calls = []

    core = SimpleNamespace(
        get_keyboard_brightness=lambda: None,
        find_keyboard_backlight_device=lambda: None,
        last_keyboard_level=None,
        last_keyboard_color=None,
        log=lambda _message: None,
    )
    runtime = SimpleNamespace(load_config=lambda: {"keyboard_sync": True})
    control = SimpleNamespace(core=core, runtime=runtime)

    monkeypatch.setattr(hw.shutil, "which", lambda name: "/usr/bin/openrgb" if name == "openrgb" else None)

    def fake_run(command, **_kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(hw.subprocess, "run", fake_run)
    assert hw._set_keyboard_color_portable(control, "#12ab34") is True
    assert calls == [["/usr/bin/openrgb", "--color", "12AB34", "--mode", "static"]]
    assert core.last_keyboard_color == "12AB34"


def test_manual_backlight_off_is_respected(monkeypatch):
    hw = load_hardware("aura_hardware_keyboard_off_test")
    core = SimpleNamespace(
        get_keyboard_brightness=lambda: "off",
        find_keyboard_backlight_device=lambda: "/sys/class/leds/kbd_backlight",
        last_keyboard_level=None,
        last_keyboard_color=None,
        log=lambda _message: None,
    )
    runtime = SimpleNamespace(load_config=lambda: {"keyboard_sync": True})
    control = SimpleNamespace(core=core, runtime=runtime)
    monkeypatch.setattr(hw.shutil, "which", lambda name: "/usr/bin/openrgb" if name == "openrgb" else None)

    def forbidden_run(*_args, **_kwargs):
        raise AssertionError("RGB backend must not run when laptop backlight is manually off")

    monkeypatch.setattr(hw.subprocess, "run", forbidden_run)
    assert hw._set_keyboard_color_portable(control, "334455") is False
    assert core.last_keyboard_level == "off"


def test_no_hardware_degrades_cleanly(monkeypatch):
    hw = load_hardware("aura_hardware_none_test")
    monkeypatch.setattr(hw.shutil, "which", lambda _name: None)
    monkeypatch.setattr(hw, "_drm_gpus", lambda: [])
    monkeypatch.setattr(hw, "_nvidia_gpus", lambda: ([], []))

    core = SimpleNamespace(
        _LAST_GPU_METRICS=None,
        _LAST_GPU_METRICS_TIME=0,
        find_keyboard_backlight_device=lambda: None,
    )
    runtime = SimpleNamespace(
        _original_collect_gpu_guard_metrics=lambda max_age=5.0: ({"available": False, "error": "no gpu"}, []),
    )
    control = SimpleNamespace(core=core, runtime=runtime)
    metrics, processes = hw._collect_portable_gpu_metrics(control, max_age=0)
    assert metrics["available"] is False
    assert processes == []
    assert hw._keyboard_capabilities(control)["mode"] == "unavailable"
