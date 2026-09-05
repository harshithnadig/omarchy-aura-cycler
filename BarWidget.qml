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

  property bool active: false
  property int intervalSec: 10
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
    command: ["sh", "-c", "python3 -c '\nimport os, re\npid_file = os.path.expanduser(\"~/.local/state/omarchy/material-cycler.pid\")\nint_file = os.path.expanduser(\"~/.local/state/omarchy/material-cycler-interval.txt\")\nrunning = False\nif os.path.exists(pid_file):\n    try:\n        pid = int(open(pid_file).read().strip())\n        os.kill(pid, 0)\n        running = True\n    except:\n        pass\ninterval = 10\nif os.path.exists(int_file):\n    try: interval = int(open(int_file).read().strip())\n    except: pass\n\nlog_file = os.path.expanduser(\"~/.local/state/omarchy/material-cycler.log\")\naccent = \"#00FF66\"\nwp = \"\"\nif os.path.exists(log_file):\n    lines = open(log_file).readlines()[-20:]\n    for l in reversed(lines):\n        m = re.search(r\"Material You Accent: #([0-9A-Fa-f]{6})\", l)\n        if m and accent == \"#00FF66\": accent = \"#\" + m.group(1)\n        m2 = re.search(r\"Applying: (.+)\", l)\n        if m2 and not wp: wp = m2.group(1).strip()\nprint(f\"{running}|{interval}|{accent}|{wp}\")\n'"]
    stdout: StdioCollector {
      waitForEnd: true
      onStreamFinished: {
        var parts = text.trim().split("|")
        if (parts.length >= 4) {
          root.active = parts[0] === "True"
          root.intervalSec = parseInt(parts[1]) || 10
          root.currentAccent = parts[2] || "#00FF66"
          root.currentWallpaper = parts[3] || ""
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
    command: ["sh", "-c", "if [ -f ~/.local/state/omarchy/material-cycler.pid ]; then material-cycler stop; else material-cycler start; fi"]
    onExited: root.refreshState()
  }

  Process {
    id: speedProc
    command: ["sh", "-c", "python3 -c '\nimport os\ncur = 10\nf = os.path.expanduser(\"~/.local/state/omarchy/material-cycler-interval.txt\")\nif os.path.exists(f):\n    try: cur = int(open(f).read().strip())\n    except: pass\nsteps = [10, 30, 60, 300, 600]\nnext_val = steps[(steps.index(cur) + 1) % len(steps)] if cur in steps else 10\nos.system(f\"material-cycler interval {next_val}\")\n'"]
    onExited: root.refreshState()
  }

  WidgetButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: "\uf53f"
    fontFamily: "JetBrainsMono Nerd Font"
    horizontalMargin: 8
    useActiveColor: true
    active: root.active
    activeColor: root.currentAccent
    tooltipText: "Aura Material Cycler (" + (root.active ? "Running" : "Paused") + ")"
      + "\n• Interval: " + root.intervalSec + "s"
      + "\n• Wallpaper: " + (root.currentWallpaper ? root.currentWallpaper : "Active")
      + "\n• Accent: " + root.currentAccent
      + "\n\nLeft click: Next wallpaper & sync"
      + "\nRight click: Toggle start / pause"
      + "\nMiddle click: Cycle interval (" + root.intervalSec + "s)"

    onPressed: function(b) {
      if (b === Qt.LeftButton) root.nextWallpaper()
      else if (b === Qt.RightButton) root.toggleCycle()
      else if (b === Qt.MiddleButton) root.cycleSpeed()
    }
    onWheelMoved: function(delta) {
      var steps = [10, 30, 60, 300, 600]
      var cur = root.intervalSec
      var idx = steps.indexOf(cur)
      if (idx === -1) idx = 0
      var nextIdx = delta > 0 ? Math.min(steps.length - 1, idx + 1) : Math.max(0, idx - 1)
      if (nextIdx !== idx) {
        root.bar.run("material-cycler interval " + steps[nextIdx])
        root.refreshState()
      }
    }
  }
}
