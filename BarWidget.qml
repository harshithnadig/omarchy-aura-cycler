import QtQuick
import Quickshell
import Quickshell.Io
import qs.Commons
import qs.Ui

BarWidget {
  id: root
  moduleName: "harshith.aura-cycler"

  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  property bool active: true
  property int intervalSec: 30
  property int blurPx: 12
  property string currentAccent: "#00FF66"
  property string currentWallpaper: ""
  property string weatherIcon: "󰖗"
  property int weatherTemp: 22
  property string weatherCondition: "Light Drizzle"
  property bool weatherSync: true

  function injectPanel() {
    var target = panelLoader.item
    if (!target) return
    if ("bar" in target) target.bar = root.bar
    if ("settings" in target) target.settings = root.settings
    if ("anchorItem" in target) target.anchorItem = button
    if ("hostWidget" in target) target.hostWidget = root
  }

  function open() { if (panelLoader.item) panelLoader.item.open() }
  function close() { if (panelLoader.item) panelLoader.item.close() }
  function togglePanel() { if (panelLoader.item) panelLoader.item.toggle() }

  onBarChanged: injectPanel()
  onSettingsChanged: injectPanel()

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

  Timer {
    interval: 3000
    running: true
    repeat: true
    onTriggered: root.refreshState()
  }

  Process {
    id: stateProc
    command: ["aura-cycler", "status-json"]
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
        } catch(e) {}
      }
    }
  }

  Process {
    id: nextProc
    command: ["aura-cycler", "next"]
    onExited: root.refreshState()
  }

  Process {
    id: toggleProc
    command: ["aura-cycler", "toggle"]
    onExited: root.refreshState()
  }

  Process {
    id: speedProc
    command: ["aura-cycler", "cycle-interval"]
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
        root.bar.run("aura-cycler interval " + steps[nextIdx])
        root.refreshState()
      }
    }
  }
}
