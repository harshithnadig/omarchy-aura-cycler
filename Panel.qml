import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import qs.Commons
import qs.Ui

Panel {
  id: root
  moduleName: "harshith.aura-cycler"
  ipcTarget: "harshith.aura-cycler.panel"
  manageIpc: false

  property var anchorItem: null
  property var hostWidget: null
  readonly property var barIdentity: hostWidget || root

  property bool active: true
  property int intervalSec: 30
  property int blurPx: 12
  property string currentWallpaper: ""
  property string wallpaperName: ""
  property string currentAccent: "#00FF66"
  property string keyboardBrightness: "low"

  // Weather state
  property int weatherTemp: 22
  property string weatherCondition: "Light Drizzle"
  property string weatherIcon: "󰖗"
  property string weatherCity: "Bengaluru"
  property bool weatherSync: true
  property bool streamOnline: true

  // Folders state
  property var customFolders: []
  property int wallpapersCount: 0

  readonly property color fg: bar ? bar.foreground : Color.popups.text
  readonly property color bg: Color.popups.background
  readonly property color accent: currentAccent ? currentAccent : Color.accent
  readonly property string fontFam: bar ? bar.fontFamily : Style.font.family

  function open() {
    root.controller.show()
    root.refresh()
  }

  function close() {
    root.controller.hide()
  }

  function toggle() {
    if (root.opened) root.close()
    else root.open()
  }

  function switchPanel(direction) {
    if (root.bar && typeof root.bar.switchPanelFrom === "function")
      return root.bar.switchPanelFrom(root.hostWidget || root, direction)
    return false
  }

  function refresh() {
    if (!statusProc.running) {
      statusProc.running = true
    }
  }

  function runCmd(cmd) {
    actionProc.command = cmd
    actionProc.running = true
  }

  Process {
    id: statusProc
    command: ["aura-cycler", "status-json"]
    running: false
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
          root.currentWallpaper = d.wallpaper || ""
          root.wallpaperName = d.wallpaper_name || ""
          root.currentAccent = d.accent || "#00FF66"
          root.keyboardBrightness = d.keyboard_brightness || "unknown"
          if (d.weather) {
            root.weatherTemp = d.weather.temp
            root.weatherCondition = d.weather.condition
            root.weatherIcon = d.weather.icon
            root.weatherCity = d.weather.city
          }
          root.weatherSync = d.weather_sync
          root.streamOnline = d.stream_online
          root.customFolders = d.custom_folders || []
          root.wallpapersCount = d.wallpapers_count || 0
        } catch(e) {}
      }
    }
  }

  Process {
    id: actionProc
    running: false
    onExited: root.refresh()
  }

  KeyboardPanel {
    id: panel
    anchorItem: root.anchorItem
    owner: root.hostWidget || root
    bar: root.bar
    open: root.opened
    focusTarget: keyCatcher
    contentWidth: panel.fittedContentWidth(Style.space(420))
    contentHeight: panel.fittedContentHeight(panelColumn.implicitHeight, Style.space(680))

    PanelKeyCatcher {
      id: keyCatcher
      anchors.fill: parent
      onCloseRequested: root.close()
      onTabRequested: function(direction) { root.switchPanel(direction) }
    }

    ScrollView {
      id: scrollArea
      anchors.left: parent.left
      anchors.right: parent.right
      anchors.top: parent.top
      anchors.bottom: parent.bottom
      anchors.bottomMargin: -panel.padding
      clip: true
      ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
      ScrollBar.vertical.policy: panelColumn.implicitHeight > height ? ScrollBar.AsNeeded : ScrollBar.AlwaysOff

      Column {
        id: panelColumn
        width: scrollArea.availableWidth
        spacing: Style.space(12)

        // 1. Header Row
        Item {
          width: parent.width
          implicitHeight: headerTitleCol.implicitHeight

          Rectangle {
            id: headerIconBox
            width: Style.space(38)
            height: Style.space(38)
            radius: Style.cornerRadius
            color: Qt.rgba(root.accent.r, root.accent.g, root.accent.b, 0.15)
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter

            Text {
              anchors.centerIn: parent
              textFormat: Text.PlainText
              text: "󰸉"
              color: root.accent
              font.family: root.fontFam
              font.pixelSize: Style.font.title
            }
          }

          Column {
            id: headerTitleCol
            anchors.left: headerIconBox.right
            anchors.leftMargin: Style.space(10)
            anchors.right: headerStatusBtn.left
            anchors.rightMargin: Style.space(10)
            anchors.verticalCenter: parent.verticalCenter
            spacing: Style.space(1)

            Text {
              textFormat: Text.PlainText
              text: "Aura Material Cycler"
              color: root.fg
              font.family: root.fontFam
              font.pixelSize: Style.font.title
              font.bold: true
            }

            Text {
              textFormat: Text.PlainText
              text: "Dynamic Material You & ASUS Aura Sync"
              color: Qt.darker(root.fg, 1.4)
              font.family: root.fontFam
              font.pixelSize: Style.font.caption
            }
          }

          // Active / Pause Status Pill
          Rectangle {
            id: headerStatusBtn
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            width: statusRow.implicitWidth + Style.space(16)
            height: Style.space(28)
            radius: Style.space(14)
            color: root.active ? Qt.rgba(0.2, 0.8, 0.4, 0.15) : Qt.rgba(root.fg.r, root.fg.g, root.fg.b, 0.08)
            border.color: root.active ? Qt.rgba(0.2, 0.8, 0.4, 0.4) : Qt.rgba(root.fg.r, root.fg.g, root.fg.b, 0.15)
            border.width: 1

            Row {
              id: statusRow
              anchors.centerIn: parent
              spacing: Style.space(6)
              Text {
                textFormat: Text.PlainText
                text: root.active ? "󰐊 Active" : "󰏤 Paused"
                color: root.active ? "#38ef7d" : Qt.darker(root.fg, 1.3)
                font.family: root.fontFam
                font.pixelSize: Style.font.caption
                font.bold: true
              }
            }

            MouseArea {
              anchors.fill: parent
              cursorShape: Qt.PointingHandCursor
              onClicked: root.runCmd(["aura-cycler", "toggle"])
            }
          }
        }

        // 2. Live Weather Card
        Rectangle {
          width: parent.width
          implicitHeight: weatherCol.implicitHeight + Style.space(18)
          radius: Style.cornerRadius
          color: Qt.rgba(root.accent.r, root.accent.g, root.accent.b, 0.08)
          border.color: Qt.rgba(root.accent.r, root.accent.g, root.accent.b, 0.25)
          border.width: 1

          Column {
            id: weatherCol
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: Style.space(10)
            spacing: Style.space(8)

            Item {
              width: parent.width
              implicitHeight: Math.max(weatherIconText.implicitHeight, weatherDetails.implicitHeight)

              Text {
                id: weatherIconText
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                textFormat: Text.PlainText
                text: root.weatherIcon
                color: root.accent
                font.family: root.fontFam
                font.pixelSize: 32
              }

              Column {
                id: weatherDetails
                anchors.left: weatherIconText.right
                anchors.leftMargin: Style.space(12)
                anchors.verticalCenter: parent.verticalCenter
                spacing: Style.space(2)

                Row {
                  spacing: Style.space(8)
                  Text {
                    textFormat: Text.PlainText
                    text: root.weatherTemp + "°C"
                    color: root.fg
                    font.family: root.fontFam
                    font.pixelSize: Style.font.title
                    font.bold: true
                  }
                  Text {
                    textFormat: Text.PlainText
                    text: "•  " + root.weatherCondition
                    color: root.accent
                    font.family: root.fontFam
                    font.pixelSize: Style.font.body
                    font.bold: true
                    anchors.verticalCenter: parent.verticalCenter
                  }
                }

                Text {
                  textFormat: Text.PlainText
                  text: "📍 " + root.weatherCity + "  •  Real-Time Atmosphere"
                  color: Qt.darker(root.fg, 1.4)
                  font.family: root.fontFam
                  font.pixelSize: Style.font.caption
                }
              }

              // Weather Sync Toggle Pill
              Rectangle {
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                width: weatherToggleRow.implicitWidth + Style.space(14)
                height: Style.space(26)
                radius: Style.space(13)
                color: root.weatherSync ? root.accent : Qt.rgba(root.fg.r, root.fg.g, root.fg.b, 0.1)

                Row {
                  id: weatherToggleRow
                  anchors.centerIn: parent
                  spacing: Style.space(4)
                  Text {
                    textFormat: Text.PlainText
                    text: root.weatherSync ? "󰖐 Weather Sync ON" : "󰖐 Weather Sync OFF"
                    color: root.weatherSync ? "#0A0E0A" : root.fg
                    font.family: root.fontFam
                    font.pixelSize: Style.font.caption
                    font.bold: true
                  }
                }

                MouseArea {
                  anchors.fill: parent
                  cursorShape: Qt.PointingHandCursor
                  onClicked: root.runCmd(["aura-cycler", "weather-toggle"])
                }
              }
            }

            Text {
              width: parent.width
              wrapMode: Text.WordWrap
              textFormat: Text.PlainText
              text: root.weatherSync ? "Wallpaper selection and ASUS Aura RGB dynamically reflect live weather outside." : "Weather sync is disabled. Wallpapers rotate from all standard curated topics."
              color: Qt.darker(root.fg, 1.3)
              font.family: root.fontFam
              font.pixelSize: Style.font.caption
            }
          }
        }

        // 3. Current Wallpaper & Accent Card
        Rectangle {
          width: parent.width
          implicitHeight: wpCardCol.implicitHeight + Style.space(16)
          radius: Style.cornerRadius
          color: Qt.rgba(root.fg.r, root.fg.g, root.fg.b, 0.04)
          border.color: Qt.rgba(root.fg.r, root.fg.g, root.fg.b, 0.1)
          border.width: 1

          Column {
            id: wpCardCol
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: Style.space(10)
            spacing: Style.space(10)

            // Wallpaper image preview
            Rectangle {
              width: parent.width
              height: Style.space(130)
              radius: Style.cornerRadius
              clip: true
              color: "#111"

              Image {
                anchors.fill: parent
                source: root.currentWallpaper ? ("file://" + root.currentWallpaper) : ""
                fillMode: Image.PreserveAspectCrop
                smooth: true
              }

              // Gradient banner at bottom of image
              Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                height: Style.space(36)
                color: Qt.rgba(0, 0, 0, 0.65)

                Row {
                  anchors.left: parent.left
                  anchors.right: parent.right
                  anchors.verticalCenter: parent.verticalCenter
                  anchors.leftMargin: Style.space(8)
                  anchors.rightMargin: Style.space(8)
                  spacing: Style.space(8)

                  Text {
                    textFormat: Text.PlainText
                    text: root.wallpaperName ? root.wallpaperName : "Dynamic Wallpaper"
                    color: "#FFFFFF"
                    font.family: root.fontFam
                    font.pixelSize: Style.font.caption
                    font.bold: true
                    elide: Text.ElideMiddle
                    width: parent.width - swatchRow.implicitWidth - Style.space(16)
                  }

                  Row {
                    id: swatchRow
                    spacing: Style.space(6)
                    anchors.verticalCenter: parent.verticalCenter

                    Rectangle {
                      width: Style.space(14)
                      height: Style.space(14)
                      radius: Style.space(7)
                      color: root.accent
                      border.color: "#FFFFFF"
                      border.width: 1
                    }

                    Text {
                      textFormat: Text.PlainText
                      text: root.currentAccent
                      color: "#FFFFFF"
                      font.family: root.fontFam
                      font.pixelSize: Style.font.caption
                      font.bold: true
                    }
                  }
                }
              }
            }

            // ASUS Aura Hardware Bar
            Item {
              width: parent.width
              implicitHeight: auraHardwareRow.implicitHeight

              Row {
                id: auraHardwareRow
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                spacing: Style.space(8)

                Text {
                  textFormat: Text.PlainText
                  text: "󰌌 ASUS Aura Keyboard:"
                  color: root.fg
                  font.family: root.fontFam
                  font.pixelSize: Style.font.caption
                  font.bold: true
                }

                Rectangle {
                  width: Style.space(12)
                  height: Style.space(12)
                  radius: Style.space(6)
                  color: root.accent
                  anchors.verticalCenter: parent.verticalCenter
                }

                Text {
                  textFormat: Text.PlainText
                  text: "RGB #" + root.currentAccent.replace("#", "") + " (Brightness: " + root.keyboardBrightness + ")"
                  color: root.accent
                  font.family: root.fontFam
                  font.pixelSize: Style.font.caption
                  font.bold: true
                }
              }
            }
          }
        }

        // 4. Quick Action Buttons
        Row {
          width: parent.width
          spacing: Style.space(8)

          Rectangle {
            width: (parent.width - Style.space(16)) * 0.45
            height: Style.space(34)
            radius: Style.cornerRadius
            color: root.accent

            Row {
              anchors.centerIn: parent
              spacing: Style.space(6)
              Text { textFormat: Text.PlainText; text: "󰒭"; color: "#0A0E0A"; font.family: root.fontFam; font.bold: true }
              Text { textFormat: Text.PlainText; text: "Next Wallpaper"; color: "#0A0E0A"; font.family: root.fontFam; font.pixelSize: Style.font.body; font.bold: true }
            }

            MouseArea {
              anchors.fill: parent
              cursorShape: Qt.PointingHandCursor
              onClicked: root.runCmd(["aura-cycler", "next"])
            }
          }

          Rectangle {
            width: (parent.width - Style.space(16)) * 0.35
            height: Style.space(34)
            radius: Style.cornerRadius
            color: Qt.rgba(root.fg.r, root.fg.g, root.fg.b, 0.08)
            border.color: Qt.rgba(root.fg.r, root.fg.g, root.fg.b, 0.15)
            border.width: 1

            Row {
              anchors.centerIn: parent
              spacing: Style.space(6)
              Text { textFormat: Text.PlainText; text: root.active ? "󰏤" : "󰐊"; color: root.fg; font.family: root.fontFam }
              Text { textFormat: Text.PlainText; text: root.active ? "Pause" : "Resume"; color: root.fg; font.family: root.fontFam; font.pixelSize: Style.font.body }
            }

            MouseArea {
              anchors.fill: parent
              cursorShape: Qt.PointingHandCursor
              onClicked: root.runCmd(["aura-cycler", "toggle"])
            }
          }

          Rectangle {
            width: (parent.width - Style.space(16)) * 0.20
            height: Style.space(34)
            radius: Style.cornerRadius
            color: Qt.rgba(root.fg.r, root.fg.g, root.fg.b, 0.08)
            border.color: Qt.rgba(root.fg.r, root.fg.g, root.fg.b, 0.15)
            border.width: 1

            Text {
              anchors.centerIn: parent
              textFormat: Text.PlainText
              text: "󰑓 Sync"
              color: root.fg
              font.family: root.fontFam
              font.pixelSize: Style.font.body
            }

            MouseArea {
              anchors.fill: parent
              cursorShape: Qt.PointingHandCursor
              onClicked: root.refresh()
            }
          }
        }

        // 5. Rotation Interval (Timeout) Selector
        Column {
          width: parent.width
          spacing: Style.space(6)

          Text {
            textFormat: Text.PlainText
            text: "󱎫 Rotation Interval: " + (root.intervalSec < 60 ? (root.intervalSec + "s") : ((root.intervalSec / 60) + "m"))
            color: root.fg
            font.family: root.fontFam
            font.pixelSize: Style.font.body
            font.bold: true
          }

          Flow {
            width: parent.width
            spacing: Style.space(6)

            Repeater {
              model: [
                { label: "15s", sec: 15 },
                { label: "30s", sec: 30 },
                { label: "1m", sec: 60 },
                { label: "5m", sec: 300 },
                { label: "10m", sec: 600 },
                { label: "30m", sec: 1800 },
                { label: "1h", sec: 3600 }
              ]

              Rectangle {
                width: Style.space(48)
                height: Style.space(26)
                radius: Style.space(13)
                color: root.intervalSec === modelData.sec ? root.accent : Qt.rgba(root.fg.r, root.fg.g, root.fg.b, 0.08)
                border.color: root.intervalSec === modelData.sec ? root.accent : Qt.rgba(root.fg.r, root.fg.g, root.fg.b, 0.15)
                border.width: 1

                Text {
                  anchors.centerIn: parent
                  textFormat: Text.PlainText
                  text: modelData.label
                  color: root.intervalSec === modelData.sec ? "#0A0E0A" : root.fg
                  font.family: root.fontFam
                  font.pixelSize: Style.font.caption
                  font.bold: root.intervalSec === modelData.sec
                }

                MouseArea {
                  anchors.fill: parent
                  cursorShape: Qt.PointingHandCursor
                  onClicked: root.runCmd(["aura-cycler", "interval", String(modelData.sec)])
                }
              }
            }
          }
        }

        // 6. Wallpaper Folders
        Column {
          width: parent.width
          spacing: Style.space(6)

          Text {
            textFormat: Text.PlainText
            text: "󰉋 Wallpaper Folders (" + root.wallpapersCount + " total wallpapers)"
            color: root.fg
            font.family: root.fontFam
            font.pixelSize: Style.font.body
            font.bold: true
          }

          // Existing Folders List
          Column {
            width: parent.width
            spacing: Style.space(4)

            Repeater {
              model: root.customFolders

              Rectangle {
                width: parent.width
                height: Style.space(28)
                radius: Style.cornerRadius
                color: Qt.rgba(root.fg.r, root.fg.g, root.fg.b, 0.05)

                Row {
                  anchors.left: parent.left
                  anchors.right: delBtn.left
                  anchors.verticalCenter: parent.verticalCenter
                  anchors.leftMargin: Style.space(8)
                  anchors.rightMargin: Style.space(8)
                  spacing: Style.space(6)

                  Text {
                    textFormat: Text.PlainText
                    text: "󰉋"
                    color: root.accent
                    font.family: root.fontFam
                    font.pixelSize: Style.font.caption
                  }

                  Text {
                    textFormat: Text.PlainText
                    text: modelData
                    color: root.fg
                    font.family: root.fontFam
                    font.pixelSize: Style.font.caption
                    elide: Text.ElideMiddle
                    width: parent.width - Style.space(24)
                  }
                }

                Rectangle {
                  id: delBtn
                  anchors.right: parent.right
                  anchors.verticalCenter: parent.verticalCenter
                  anchors.rightMargin: Style.space(4)
                  width: Style.space(20)
                  height: Style.space(20)
                  radius: Style.space(10)
                  color: "transparent"

                  Text {
                    anchors.centerIn: parent
                    textFormat: Text.PlainText
                    text: "󰅖"
                    color: Qt.darker(root.fg, 1.4)
                    font.family: root.fontFam
                    font.pixelSize: Style.font.caption
                  }

                  MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.runCmd(["aura-cycler", "folder", "remove", modelData])
                  }
                }
              }
            }
          }

          // Add Folder Row
          Row {
            width: parent.width
            spacing: Style.space(6)

            Rectangle {
              width: parent.width - addFolderBtn.width - Style.space(6)
              height: Style.space(30)
              radius: Style.cornerRadius
              color: Qt.rgba(root.fg.r, root.fg.g, root.fg.b, 0.08)
              border.color: folderInput.activeFocus ? root.accent : Qt.rgba(root.fg.r, root.fg.g, root.fg.b, 0.15)
              border.width: 1

              TextInput {
                id: folderInput
                anchors.fill: parent
                anchors.leftMargin: Style.space(8)
                anchors.rightMargin: Style.space(8)
                verticalAlignment: TextInput.AlignVCenter
                color: root.fg
                font.family: root.fontFam
                font.pixelSize: Style.font.caption
                clip: true

                Text {
                  anchors.fill: parent
                  verticalAlignment: Text.AlignVCenter
                  text: "Enter folder path (e.g. ~/Pictures/Wallpapers)"
                  color: Qt.darker(root.fg, 1.6)
                  font.family: root.fontFam
                  font.pixelSize: Style.font.caption
                  visible: !folderInput.text && !folderInput.activeFocus
                }

                onAccepted: {
                  if (folderInput.text.trim()) {
                    root.runCmd(["aura-cycler", "folder", "add", folderInput.text.trim()])
                    folderInput.text = ""
                  }
                }
              }
            }

            Rectangle {
              id: addFolderBtn
              width: Style.space(80)
              height: Style.space(30)
              radius: Style.cornerRadius
              color: root.accent

              Text {
                anchors.centerIn: parent
                textFormat: Text.PlainText
                text: "+ Add"
                color: "#0A0E0A"
                font.family: root.fontFam
                font.pixelSize: Style.font.caption
                font.bold: true
              }

              MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: {
                  if (folderInput.text.trim()) {
                    root.runCmd(["aura-cycler", "folder", "add", folderInput.text.trim()])
                    folderInput.text = ""
                  }
                }
              }
            }
          }
        }

        // 7. Liquid Glass Blur
        Column {
          width: parent.width
          spacing: Style.space(6)

          Text {
            textFormat: Text.PlainText
            text: "󰂵 Liquid Glass Blur: " + root.blurPx + "px"
            color: root.fg
            font.family: root.fontFam
            font.pixelSize: Style.font.body
            font.bold: true
          }

          Row {
            width: parent.width
            spacing: Style.space(6)

            Repeater {
              model: [
                { label: "Off (0px)", px: 0 },
                { label: "6px", px: 6 },
                { label: "12px", px: 12 },
                { label: "18px", px: 18 },
                { label: "24px", px: 24 }
              ]

              Rectangle {
                width: (parent.width - Style.space(24)) / 5
                height: Style.space(26)
                radius: Style.space(13)
                color: root.blurPx === modelData.px ? root.accent : Qt.rgba(root.fg.r, root.fg.g, root.fg.b, 0.08)
                border.color: root.blurPx === modelData.px ? root.accent : Qt.rgba(root.fg.r, root.fg.g, root.fg.b, 0.15)
                border.width: 1

                Text {
                  anchors.centerIn: parent
                  textFormat: Text.PlainText
                  text: modelData.label
                  color: root.blurPx === modelData.px ? "#0A0E0A" : root.fg
                  font.family: root.fontFam
                  font.pixelSize: Style.font.caption
                  font.bold: root.blurPx === modelData.px
                }

                MouseArea {
                  anchors.fill: parent
                  cursorShape: Qt.PointingHandCursor
                  onClicked: root.runCmd(["aura-cycler", "blur", String(modelData.px)])
                }
              }
            }
          }
        }

        // 8. Online 4K UHD Stream Toggle
        Rectangle {
          width: parent.width
          height: Style.space(34)
          radius: Style.cornerRadius
          color: Qt.rgba(root.fg.r, root.fg.g, root.fg.b, 0.05)

          Row {
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            anchors.leftMargin: Style.space(10)
            spacing: Style.space(8)

            Text {
              textFormat: Text.PlainText
              text: "󰖟 Stream Fresh 4K Online (Wallhaven & Bing)"
              color: root.fg
              font.family: root.fontFam
              font.pixelSize: Style.font.caption
            }
          }

          Rectangle {
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            anchors.rightMargin: Style.space(6)
            width: streamToggleText.implicitWidth + Style.space(14)
            height: Style.space(22)
            radius: Style.space(11)
            color: root.streamOnline ? root.accent : Qt.rgba(root.fg.r, root.fg.g, root.fg.b, 0.1)

            Text {
              id: streamToggleText
              anchors.centerIn: parent
              textFormat: Text.PlainText
              text: root.streamOnline ? "Enabled" : "Disabled"
              color: root.streamOnline ? "#0A0E0A" : root.fg
              font.family: root.fontFam
              font.pixelSize: Style.font.caption
              font.bold: true
            }

            MouseArea {
              anchors.fill: parent
              cursorShape: Qt.PointingHandCursor
              onClicked: root.runCmd(["aura-cycler", "stream-toggle"])
            }
          }
        }
      }
    }
  }
}
