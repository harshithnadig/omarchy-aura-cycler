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

  Component.onCompleted: refreshState()

  Timer {
    interval: 3000
    running: true
    repeat: true
    onTriggered: root.refreshState()
  }

  Process {
    id: stateProc
    command: ["sh", "-c", "python3 -c '\nimport os, re, subprocess\nrunning = subprocess.run([\"systemctl\", \"--user\", \"is-active\", \"--quiet\", \"material-cycler.service\"]).returncode == 0\nint_file = os.path.expanduser(\"~/.local/state/omarchy/material-cycler-interval.txt\")\ninterval = 30\nif os.path.exists(int_file):\n    try: interval = int(open(int_file).read().strip())\n    except: pass\nblur_file = os.path.expanduser(\"~/.local/state/omarchy/glass-blur.txt\")\nblur = 12\nif os.path.exists(blur_file):\n    try: blur = int(open(blur_file).read().strip())\n    except: pass\nlog_file = os.path.expanduser(\"~/.local/state/omarchy/material-cycler.log\")\naccent = \"#00FF66\"\nwp = \"\"\nif os.path.exists(log_file):\n    lines = open(log_file).readlines()[-30:]\n    for l in reversed(lines):\n        m = re.search(r\"Theme Accent: #([0-9A-Fa-f]{6})\", l)\n        if m and accent == \"#00FF66\": accent = \"#\" + m.group(1)\n        m2 = re.search(r\"Applying New Wallpaper: (.+)\", l)\n        if m2 and not wp: wp = m2.group(1).replace(\"===\", \"\").strip()\nprint(f\"{running}|{interval}|{accent}|{wp}|{blur}\")\n'"]
    stdout: SplitParser {
      onRead: function(data) {
        var parts = data.trim().split("|")
        if (parts.length >= 4) {
          root.active = (parts[0] === "True")
          root.intervalSec = parseInt(parts[1]) || 30
          root.currentAccent = parts[2] || "#00FF66"
          root.currentWallpaper = parts[3] || ""
          if (parts.length >= 5) root.blurPx = parseInt(parts[4]) || 12
        }
      }
    }
  }

  Process {
    id: nextProc
    command: ["material-cycler", "next"]
    onExited: root.refreshState()
  }

  Process {
    id: toggleProc
    command: ["sh", "-c", "if systemctl --user is-active --quiet material-cycler.service; then systemctl --user stop material-cycler.service; else systemctl --user start material-cycler.service; fi"]
    onExited: root.refreshState()
  }

  Process {
    id: speedProc
    command: ["sh", "-c", "python3 -c '\nimport os\ncur = 30\nf = os.path.expanduser(\"~/.local/state/omarchy/material-cycler-interval.txt\")\nif os.path.exists(f):\n    try: cur = int(open(f).read().strip())\n    except: pass\nsteps = [15, 30, 60, 300, 600]\nnext_val = steps[(steps.index(cur) + 1) % len(steps)] if cur in steps else 30\nos.system(f\"material-cycler interval {next_val}\")\n'"]
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
    tooltipText: "Apple Liquid Glass & Aura Cycler: " + (root.active ? "Active" : "Paused")
      + "\n• Rotation: " + root.intervalSec + "s"
      + "\n• Liquid Glass Blur: " + root.blurPx + "px"
      + "\n• Wallpaper: " + (root.currentWallpaper ? root.currentWallpaper : "Active")
      + "\n• Monet Accent: " + root.currentAccent
      + "\n\n⌨ Keyboard Shortcuts (Mouse-Free):"
      + "\n  • Super + B: Next Wallpaper & Sync"
      + "\n  • Super + Alt + P: Pause / Resume"
      + "\n  • Super + Alt + I: Cycle Speed (" + root.intervalSec + "s)"
      + "\n  • Super + Shift + [: Blur Slider Down (-3px)"
      + "\n  • Super + Shift + ]: Blur Slider Up (+3px)"
      + "\n  • Super + Alt + B: Toggle Blur On/Off"
      + "\n\nMouse (Optional): Left click=Next | Right click=Toggle"

    onPressed: function(b) {
      if (b === Qt.LeftButton) root.nextWallpaper()
      else if (b === Qt.RightButton) root.toggleCycle()
      else if (b === Qt.MiddleButton) root.cycleSpeed()
    }
    onWheelMoved: function(delta) {
      var steps = [15, 30, 60, 300, 600]
      var cur = root.intervalSec
      var idx = steps.indexOf(cur)
      if (idx === -1) idx = 1
      var nextIdx = delta > 0 ? Math.min(steps.length - 1, idx + 1) : Math.max(0, idx - 1)
      if (nextIdx !== idx) {
        root.bar.run("material-cycler interval " + steps[nextIdx])
        root.refreshState()
      }
    }
  }
}
