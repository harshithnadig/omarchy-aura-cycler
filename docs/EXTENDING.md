# Extending Aura after v1.4

v1.4 is the stability baseline. Future features should extend the existing boundaries rather than create parallel state or bypass the public entrypoint.

## 1. Entry point rule

`bin/aura-cycler` is the only executable Aura entrypoint.

New Python behavior belongs behind one of these import-only layers:

- `aura-config.py` — configuration, migrations, recovery, backup/restore and native-settings integration;
- `aura-cycler-control` — user-facing orchestration/CLI/state features;
- `aura-cycler-runtime` — OS/hardware/network integration and hardening;
- `aura-cycler-core` — retained engine; avoid expanding it further unless fixing existing engine behavior.

Do not add another executable that bypasses the public entrypoint.

## 2. Configuration rule

There is one canonical runtime config. Do not create a second JSON settings file for a new feature.

For a new persistent setting:

1. choose a safe default;
2. add it to config normalization/defaults;
3. bump `CONFIG_VERSION` only if migration semantics are required;
4. add an idempotent migration step;
5. use `runtime.load_config()` + `runtime.save_config()` or `runtime.update_config()`;
6. if it belongs in Omarchy widget settings, add matching `manifest.json` defaults/schema and bridge mapping;
7. add stale-save/concurrency coverage when nested state is mutated.

Never write the config directly with `Path.write_text()`.

## 3. Privacy/network rule

A new network-capable feature must be **off by default** and must not be enabled indirectly by scenes or unrelated controls.

Document:

- endpoint(s);
- data sent;
- cache/state retained;
- timeout/size bounds;
- how the user disables it.

Prefer HTTPS, bounded reads and explicit failure states. Never fabricate remote data when a request fails.

## 4. User-data rule

Do not recursively delete user-owned folders. Maintenance operations must be scoped to Aura-owned generated state.

Private state should be `0600` when it may contain:

- coordinates/location cache;
- API keys;
- local paths/history/favorites;
- backup bundles with private state.

Backup format changes require a `backup_version` migration/compatibility decision.

## 5. QML rule

Keep integration wrappers thin:

- `BarWidget.qml` owns native Omarchy integration;
- `BarWidgetImpl.qml` owns the proven bar UI/behavior;
- `Panel.qml` remains the current panel implementation until a separately tested panel refactor is justified.

Do not mix a large visual redesign with runtime/security changes in one release.

## 6. Hardware rule

Every hardware backend must gracefully report unavailable data rather than guess.

A new GPU/RGB/backend path needs:

- detection;
- bounded timeouts;
- graceful fallback;
- no root requirement unless the product explicitly changes policy;
- a real-system verification item.

## 7. Test rule

At minimum, a new persistent feature should add:

- a regression/unit test for state behavior;
- a privacy/security test if it touches files/network/processes;
- smoke coverage if it affects the public CLI;
- manifest validation if it adds native settings;
- QML lint coverage if it adds/changes QML;
- a real-system checklist item for behavior CI cannot emulate.

Keep CI green on both Python 3.12 and 3.14 until the compatibility baseline intentionally changes.

## 8. Release rule

Do not let `main/master` become the experiment branch.

For significant features:

1. branch from the verified release baseline;
2. keep the feature behind safe defaults where appropriate;
3. add tests/docs while implementing it;
4. run portable CI;
5. verify hardware/QML behavior on Omarchy;
6. merge only after the release checklist is green.

This is how Aura can keep growing without repeating the v1.3-to-v1.4 hardening work every release.
