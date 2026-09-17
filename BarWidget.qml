import QtQuick
import Quickshell
import Quickshell.Io
import qs.Commons
import qs.Ui

BarWidget {
  id: root
  moduleName: "harshith.aura-cycler"

  // Resolve the CLI from the installed plugin directory so marketplace
  // installs do not depend on a user-managed ~/.local/bin symlink.
  readonly property string cliPath: Qt.resolvedUrl("bin/aura-cycler").toString().replace("file://", "")

  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  property bool active: true
  property int intervalSec: 300
  property int blurPx: 12
  property string currentAccent: "#00FF66"
  property string currentWallpaper: ""
  property string weatherIcon: "󰖗"
  property int weatherTemp: 22
  property string weatherCondition: "Light Drizzle"
  property bool weatherSync: true
  property string gpuGuardLevel: "unavailable"
  property bool gpuGuardAutoProtect: false
  property bool gpuGuardAuraPaused: false
  property string gpuGuardName: "GPU unavailable"
  property string gpuGuardError: ""
  property int gpuVramUsedMib: 0
  property int gpuVramTotalMib: 0
  property real gpuVramPercent: 0
  property int gpuTemperatureC: 0
  property int gpuUtilizationPercent: 0
  property var gpuProcesses: []

  readonly property var service: bar && bar.shell ? bar.shell.serviceFor(moduleName) : null

  function injectPanel() {
    var target = panelLoader.item
    if (!target) return
    if ("anchorItem" in target) target.anchorItem = button
    if ("hostWidget" in target) target.hostWidget = root
    if ("service" in target) target.service = root.service
  }

  Binding {
    target: panelLoader.item
    property: "settings"
    value: root.settings
    when: panelLoader.item !== null
    restoreMode: Binding.RestoreNone
  }

  Binding {
    target: panelLoader.item
    property: "bar"
    value: root.bar
    when: panelLoader.item !== null
    restoreMode: Binding.RestoreNone
  }

  readonly property bool opened: panelLoader.item ? panelLoader.item.opened === true : false
  readonly property bool popoutSwitchClosing: panelLoader.item ? panelLoader.item.popoutSwitchClosing === true : false

  function open() { if (panelLoader.item && panelLoader.item.open) panelLoader.item.open() }
  function close() { if (panelLoader.item && panelLoader.item.close) panelLoader.item.close() }
  function togglePanel() { if (panelLoader.item && panelLoader.item.toggle) panelLoader.item.toggle() }
  function closeForPopoutSwitch() {
    if (panelLoader.item && panelLoader.item.closeForPopoutSwitch) panelLoader.item.closeForPopoutSwitch()
    else close()
  }

  Component.onCompleted: refreshState()

  Loader {
    id: panelLoader
    active: true
    source: Qt.resolvedUrl("Panel.qml")
    visible: false
    onLoaded: {
      root.injectPanel()
      Qt.callLater(root.injectPanel)
    }
  }

  function refreshState() {
    if (!stateProc.running) stateProc.running = true
  }

  function nextWallpaper() {
    if (!nextProc.running) nextProc.running = true
  }

  function toggleCycle() {
    if (!toggleProc.running) toggleProc.running = true
  }

  function cycleSpeed() {
    if (!speedProc.running) speedProc.running = true
  }

  function toggleGpuProtection() {
    if (!guardProc.running) guardProc.running = true
  }

  Timer {
    interval: root.opened ? 3000 : 10000
    running: true
    repeat: true
    onTriggered: root.refreshState()
  }

  Process {
    id: stateProc
    command: [root.cliPath, "status-json"]
    stdout: StdioCollector {
      waitForEnd: true
      onStreamFinished: {
        try {
          var cleanText = text.trim()
          var firstBrace = cleanText.indexOf("{")
          if (firstBrace !== -1) {
            cleanText = cleanText.substring(firstBrace)
          }
          var d = JSON.parse(cleanText)
          root.active = d.active
          root.intervalSec = d.interval
          root.blurPx = d.blur
          root.currentAccent = d.accent || "#00FF66"
          root.currentWallpaper = d.wallpaper_name || ""
          if (d.weather) {
            root.weatherTemp = d.weather.temp
            root.weatherCondition = d.weather.condition
            root.weatherIcon = d.weather.icon
          }
          root.weatherSync = d.weather_sync
          var guard = d.gpu_guard || {}
          root.gpuGuardLevel = guard.level || "unavailable"
          root.gpuGuardAutoProtect = guard.auto_protect || false
          root.gpuGuardAuraPaused = guard.aura_paused || false
          root.gpuProcesses = guard.processes || []
          root.gpuGuardError = guard.metrics && guard.metrics.error ? guard.metrics.error : ""
          if (guard.metrics && guard.metrics.available) {
            root.gpuGuardName = guard.metrics.name || "GPU"
            root.gpuVramUsedMib = guard.metrics.used_mib || 0
            root.gpuVramTotalMib = guard.metrics.total_mib || 0
            root.gpuVramPercent = guard.metrics.vram_percent || 0
            root.gpuTemperatureC = guard.metrics.temperature_c || 0
            root.gpuUtilizationPercent = guard.metrics.utilization_percent || 0
          }
        } catch(e) {}
      }
    }
  }

  Process {
    id: nextProc
    command: [root.cliPath, "next"]
    onExited: root.refreshState()
  }

  Process {
    id: toggleProc
    command: [root.cliPath, "toggle"]
    onExited: root.refreshState()
  }

  Process {
    id: speedProc
    command: [root.cliPath, "cycle-interval"]
    onExited: root.refreshState()
  }

  Process {
    id: guardProc
    command: [root.cliPath, "gpu-guard", "toggle-protect"]
    onExited: root.refreshState()
  }

  WidgetButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: "󰸉"
    fontFamily: "JetBrainsMono Nerd Font"
    fontSize: 16
    horizontalMargin: 8
    useActiveColor: true
    active: root.active
    activeColor: root.currentAccent
    tooltipText: "Aura Material Cycler: " + (root.active ? "Active" : "Paused")
      + "\n• Rotation: " + root.intervalSec + "s"
      + "\n• Outdoor Weather: " + root.weatherIcon + " " + root.weatherTemp + "°C (" + root.weatherCondition + ")"
      + "\n• Weather Sync: " + (root.weatherSync ? "Enabled (Adaptive)" : "Disabled")
      + "\n• Liquid Glass Blur: " + root.blurPx + "px"
      + "\n• Active Wallpaper: " + (root.currentWallpaper ? root.currentWallpaper : "Active")
      + "\n• Monet Accent: " + root.currentAccent
      + "\n• GPU Guard: " + root.gpuGuardLevel.toUpperCase()
      + (root.gpuGuardLevel === "unavailable" ? " (" + root.gpuGuardError + ")" : " • VRAM " + root.gpuVramPercent + "% • Temp " + root.gpuTemperatureC + "°C")
      + "\n• Auto-Protect: " + (root.gpuGuardAutoProtect ? "Enabled" : "Off")
      + (root.gpuGuardAuraPaused ? "\n• Aura Guard paused rotation for protection" : "")
      + "\n\nLeft Click: Open Settings Panel (Folders, Timeout, Weather, Blur)"
      + "\nRight Click: Pause / Resume"
      + "\nMiddle Click: Cycle Speed (" + root.intervalSec + "s)"
      + "\nWheel Scroll: Fine-tune rotation timer"

    onPressed: function(b) {
      if (b === Qt.LeftButton) root.togglePanel()
      else if (b === Qt.RightButton) root.toggleCycle()
      else if (b === Qt.MiddleButton) root.cycleSpeed()
    }
    onWheelMoved: function(delta) {
      var steps = [15, 30, 60, 300, 600, 1800, 3600]
      var cur = root.intervalSec
      var idx = steps.indexOf(cur)
      if (idx === -1) idx = 1
      var nextIdx = delta > 0 ? Math.min(steps.length - 1, idx + 1) : Math.max(0, idx - 1)
      if (nextIdx !== idx) {
        speedProc.command = [root.cliPath, "interval", String(steps[nextIdx])]
        speedProc.running = true
      }
    }
  }
}
