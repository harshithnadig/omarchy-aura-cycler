import QtQuick
import Quickshell.Io

// Thin settings bridge around the proven v1.4 widget implementation. Omarchy
// injects manifest-backed `settings`; Aura mirrors those values transactionally
// into its private runtime config so the panel, daemon and native settings UI
// cannot drift apart after a reload.
BarWidgetImpl {
  id: root

  property string _lastAuraSettingsJson: ""
  readonly property string _settingsCliPath: Qt.resolvedUrl("bin/aura-cycler").toString().replace("file://", "")

  function _syncAuraSettings() {
    var payload = JSON.stringify(root.settings || {})
    if (payload === root._lastAuraSettingsJson || settingsSyncProc.running)
      return
    root._lastAuraSettingsJson = payload
    settingsSyncProc.command = [root._settingsCliPath, "settings-import", payload]
    settingsSyncProc.running = true
  }

  Component.onCompleted: Qt.callLater(root._syncAuraSettings)
  onSettingsChanged: Qt.callLater(root._syncAuraSettings)

  Process {
    id: settingsSyncProc
    running: false
    onExited: {
      // A second settings change may have arrived while this short-lived
      // importer was running. Re-check once before refreshing state so rapid
      // native-settings edits cannot be dropped.
      Qt.callLater(root._syncAuraSettings)
      if (root.refreshState)
        root.refreshState()
    }
  }
}
