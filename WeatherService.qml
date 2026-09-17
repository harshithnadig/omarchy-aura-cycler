import QtQuick
import Quickshell
import Quickshell.Wayland
import Quickshell.Io

Item {
  id: root

  readonly property string cliPath: Qt.resolvedUrl("bin/aura-cycler").toString().replace("file://", "")

  property var shell: null
  property var manifest: null
  property bool effectsEnabled: false
  property string weatherMode: "auto" // "auto", "rain", "thunder", "snow", "sun", "stars", "fog"
  property string activeEffect: "rain" // resolved active effect
  property string overlayLayer: "bottom" // "bottom" (behind windows, on wallpaper) or "top" (over windows)
  property real effectIntensity: 1.0
  property bool pauseFullscreen: true
  property bool fullscreenActive: false

  function applyConfig(cfg) {
    if (!cfg) return
    if (cfg.screen_effects !== undefined) root.effectsEnabled = !!cfg.screen_effects
    if (cfg.screen_effects_mode !== undefined) root.weatherMode = cfg.screen_effects_mode
    if (cfg.screen_effects_layer !== undefined) root.overlayLayer = cfg.screen_effects_layer
    if (cfg.screen_effects_intensity !== undefined) root.effectIntensity = cfg.screen_effects_intensity
    root.resolveEffect()
  }

  Socket {
    id: hyprEvents
    connected: root.effectsEnabled && root.pauseFullscreen
    path: Quickshell.env("XDG_RUNTIME_DIR") + "/hypr/"
          + Quickshell.env("HYPRLAND_INSTANCE_SIGNATURE") + "/.socket2.sock"
    parser: SplitParser {
      onRead: function (line) {
        if (line.indexOf("fullscreen>>") === 0)
          root.fullscreenActive = line.substring(12).trim() === "1"
      }
    }
  }

  // Live outdoor weather state from status-json
  property int weatherCode: 51
  property bool isDay: false
  property string weatherCondition: "Light Drizzle"
  property int weatherTemp: 22

  function resolveEffect() {
    if (root.weatherMode !== "auto") {
      root.activeEffect = root.weatherMode
      return
    }

    var code = root.weatherCode
    if (code >= 95 && code <= 99) {
      root.activeEffect = "thunder"
    } else if ((code >= 51 && code <= 65) || (code >= 80 && code <= 82)) {
      root.activeEffect = "rain"
    } else if ((code >= 71 && code <= 77) || (code >= 85 && code <= 86)) {
      root.activeEffect = "snow"
    } else if (code === 45 || code === 48) {
      root.activeEffect = "fog"
    } else if (code <= 1) {
      root.activeEffect = root.isDay ? "sun" : "stars"
    } else if (code <= 3) {
      root.activeEffect = root.isDay ? "sun" : "stars"
    } else {
      root.activeEffect = "rain"
    }
  }

  onWeatherCodeChanged: resolveEffect()
  onWeatherModeChanged: resolveEffect()
  onIsDayChanged: resolveEffect()

  Component.onCompleted: {
    startProc.running = true
    statusTimer.running = true
    refreshStatus()
  }

  function refreshStatus() {
    if (!statusProc.running) statusProc.running = true
  }

  Timer {
    id: statusTimer
    interval: 600000
    repeat: true
    running: true
    onTriggered: root.refreshStatus()
  }

  Process {
    id: statusProc
    command: [root.cliPath, "status-json"]
    running: false
    stdout: StdioCollector {
      waitForEnd: true
      onStreamFinished: {
        try {
          var cleanText = text.trim()
          var firstBrace = cleanText.indexOf("{")
          if (firstBrace !== -1) cleanText = cleanText.substring(firstBrace)
          var d = JSON.parse(cleanText)
          if (d.screen_effects !== undefined) root.effectsEnabled = d.screen_effects
          if (d.screen_effects_mode) root.weatherMode = d.screen_effects_mode
          if (d.screen_effects_layer) root.overlayLayer = d.screen_effects_layer
          if (d.screen_effects_intensity !== undefined) root.effectIntensity = d.screen_effects_intensity

          if (d.weather) {
            root.weatherCode = d.weather.code !== undefined ? d.weather.code : 51
            root.isDay = !!d.weather.is_day
            root.weatherCondition = d.weather.condition || "Light Drizzle"
            root.weatherTemp = d.weather.temp || 22
          }
          root.resolveEffect()
        } catch(e) {}
      }
    }
  }

  Process {
    id: startProc
    command: [root.cliPath, "start"]
    running: false
  }

  Variants {
    model: Quickshell.screens

    PanelWindow {
      id: overlayWindow
      required property var modelData

      screen: modelData
      visible: root.effectsEnabled && !(root.pauseFullscreen && root.fullscreenActive)
      anchors { top: true; bottom: true; left: true; right: true }
      color: "transparent"

      // Click-through input mask: no pointer events intercepted
      mask: Region {}

      WlrLayershell.namespace: "aura-weather-atmosphere"
      WlrLayershell.layer: root.overlayLayer === "overlay" ? WlrLayer.Overlay
                         : root.overlayLayer === "top" ? WlrLayer.Top
                         : WlrLayer.Bottom
      WlrLayershell.keyboardFocus: WlrKeyboardFocus.None
      exclusionMode: ExclusionMode.Ignore

      Canvas {
        id: canvas
        anchors.fill: parent
        renderStrategy: Canvas.Immediate
        smooth: true

        Connections {
          target: root
          function onActiveEffectChanged() { canvas.initParticles() }
          function onEffectIntensityChanged() { canvas.initParticles() }
        }

        property real time: 0
        property var rainDrops: []
        property var splashes: []
        property var snowflakes: []
        property var stars: []
        property var shootingStars: []
        property var sunMotes: []
        property var fogPatches: []

        // Lightning state for thunder
        property real lightningAlpha: 0
        property real nextLightningTime: 6.0
        property var lightningBolt: []

        Component.onCompleted: initParticles()

        function initParticles() {
          var w = overlayWindow.width || 1920
          var h = overlayWindow.height || 1080

          // 1. Rain Drops
          rainDrops = []
          var rainCount = Math.floor(110 * root.effectIntensity)
          for (var i = 0; i < rainCount; i++) {
            rainDrops.push({
              x: Math.random() * (w + 200) - 100,
              y: Math.random() * h,
              len: 16 + Math.random() * 24,
              speed: 18 + Math.random() * 14,
              slant: -2.5 - Math.random() * 1.5,
              alpha: 0.25 + Math.random() * 0.45,
              width: 1.0 + Math.random() * 0.8
            })
          }

          // 2. Snowflakes
          snowflakes = []
          var snowCount = Math.floor(80 * root.effectIntensity)
          for (var s = 0; s < snowCount; s++) {
            snowflakes.push({
              x: Math.random() * w,
              y: Math.random() * h,
              r: 1.5 + Math.random() * 3.5,
              speed: 0.8 + Math.random() * 1.6,
              wobbleAngle: Math.random() * 6.28,
              wobbleSpeed: 0.015 + Math.random() * 0.025,
              wobbleRadius: 0.6 + Math.random() * 1.2,
              alpha: 0.35 + Math.random() * 0.55
            })
          }

          // 3. Stars
          stars = []
          var starCount = Math.floor(75 * root.effectIntensity)
          for (var st = 0; st < starCount; st++) {
            stars.push({
              x: Math.random() * w,
              y: Math.random() * (h * 0.7),
              r: 0.8 + Math.random() * 1.6,
              baseAlpha: 0.3 + Math.random() * 0.5,
              pulseSpeed: 0.02 + Math.random() * 0.04,
              phase: Math.random() * 6.28
            })
          }

          // 4. Sun Motes / Warm Particles
          sunMotes = []
          var moteCount = Math.floor(45 * root.effectIntensity)
          for (var m = 0; m < moteCount; m++) {
            sunMotes.push({
              x: Math.random() * w,
              y: Math.random() * h,
              r: 2 + Math.random() * 4,
              speedY: -0.3 - Math.random() * 0.6,
              speedX: -0.2 + Math.random() * 0.4,
              alpha: 0.2 + Math.random() * 0.45,
              pulse: Math.random() * 6.28
            })
          }

          // 5. Fog Patches
          fogPatches = []
          var fogCount = Math.floor(6 * root.effectIntensity)
          for (var f = 0; f < fogCount; f++) {
            fogPatches.push({
              x: Math.random() * w,
              y: (h * 0.2) + Math.random() * (h * 0.7),
              radiusX: 250 + Math.random() * 300,
              radiusY: 80 + Math.random() * 100,
              speedX: 0.2 + Math.random() * 0.4,
              baseAlpha: 0.06 + Math.random() * 0.08,
              phase: Math.random() * 6.28
            })
          }
        }

        onPaint: {
          var ctx = getContext("2d")
          ctx.reset()
          var w = width
          var h = height
          if (!w || !h || !root.effectsEnabled) return

          var effect = root.activeEffect
          time += 0.016

          // ======================== 1. RAIN & DRIZZLE ========================
          if (effect === "rain" || effect === "thunder") {
            ctx.lineCap = "round"

            // Thunder lightning flash
            if (effect === "thunder") {
              if (time > nextLightningTime) {
                lightningAlpha = 0.35 * root.effectIntensity
                nextLightningTime = time + 7.0 + Math.random() * 12.0

                // Generate branching lightning bolt
                lightningBolt = []
                var startX = w * (0.2 + Math.random() * 0.6)
                var currX = startX
                var currY = 0
                lightningBolt.push({ x: currX, y: currY })
                while (currY < h * 0.8) {
                  currY += 25 + Math.random() * 35
                  currX += (Math.random() - 0.5) * 50
                  lightningBolt.push({ x: currX, y: currY })
                }
              }

              if (lightningAlpha > 0.01) {
                ctx.fillStyle = "rgba(230, 240, 255, " + lightningAlpha + ")"
                ctx.fillRect(0, 0, w, h)

                // Draw lightning bolt
                if (lightningBolt.length > 1) {
                  ctx.beginPath()
                  ctx.moveTo(lightningBolt[0].x, lightningBolt[0].y)
                  for (var b = 1; b < lightningBolt.length; b++) {
                    ctx.lineTo(lightningBolt[b].x, lightningBolt[b].y)
                  }
                  ctx.strokeStyle = "rgba(255, 255, 255, " + (lightningAlpha * 2.2) + ")"
                  ctx.lineWidth = 2.5
                  ctx.stroke()
                }

                lightningAlpha *= 0.86
              }
            }

            // Draw rain streaks
            var dropSpeedMultiplier = effect === "thunder" ? 1.35 : 1.0
            for (var i = 0; i < rainDrops.length; i++) {
              var d = rainDrops[i]
              ctx.beginPath()
              ctx.moveTo(d.x, d.y)
              ctx.lineTo(d.x + d.slant, d.y + d.len)
              ctx.strokeStyle = "rgba(180, 220, 255, " + (d.alpha * root.effectIntensity) + ")"
              ctx.lineWidth = d.width
              ctx.stroke()

              d.y += d.speed * dropSpeedMultiplier
              d.x += d.slant

              // Hit bottom -> trigger splash
              if (d.y > h - 10) {
                if (splashes.length < 35 && Math.random() < 0.4) {
                  splashes.push({
                    x: d.x,
                    y: h - 5,
                    r: 2,
                    maxR: 8 + Math.random() * 10,
                    alpha: 0.5 * root.effectIntensity
                  })
                }
                d.y = -d.len - Math.random() * 20
                d.x = Math.random() * (w + 200) - 100
              }
            }

            // Draw splashes
            for (var sp = splashes.length - 1; sp >= 0; sp--) {
              var s = splashes[sp]
              ctx.beginPath()
              ctx.arc(s.x, s.y, s.r, 0, 6.28)
              ctx.strokeStyle = "rgba(200, 230, 255, " + s.alpha + ")"
              ctx.lineWidth = 1
              ctx.stroke()

              s.r += 1.2
              s.alpha -= 0.04
              if (s.alpha <= 0 || s.r >= s.maxR) {
                splashes.splice(sp, 1)
              }
            }
          }

          // ======================== 2. SNOW ========================
          else if (effect === "snow") {
            ctx.fillStyle = "rgba(240, 248, 255, 0.8)"
            for (var sn = 0; sn < snowflakes.length; sn++) {
              var flake = snowflakes[sn]
              flake.wobbleAngle += flake.wobbleSpeed
              var wobble = Math.sin(flake.wobbleAngle) * flake.wobbleRadius

              ctx.beginPath()
              ctx.arc(flake.x + wobble, flake.y, flake.r, 0, 6.28)
              ctx.fillStyle = "rgba(240, 248, 255, " + (flake.alpha * root.effectIntensity) + ")"
              ctx.fill()

              flake.y += flake.speed
              flake.x += wobble * 0.4

              if (flake.y > h + 10) {
                flake.y = -10
                flake.x = Math.random() * w
              }
            }
          }

          // ======================== 3. SUNNY & WARM ========================
          else if (effect === "sun") {
            // Subtle top-corner golden sunlight glow
            var grad = ctx.createRadialGradient(w * 0.85, 0, 20, w * 0.85, 0, h * 0.9)
            grad.addColorStop(0, "rgba(255, 220, 150, " + (0.12 * root.effectIntensity) + ")")
            grad.addColorStop(0.5, "rgba(255, 200, 120, " + (0.05 * root.effectIntensity) + ")")
            grad.addColorStop(1, "transparent")
            ctx.fillStyle = grad
            ctx.fillRect(0, 0, w, h)

            // Floating golden motes
            for (var sm = 0; sm < sunMotes.length; sm++) {
              var mote = sunMotes[sm]
              mote.pulse += 0.03
              var pulseAlpha = mote.alpha * (0.7 + 0.3 * Math.sin(mote.pulse)) * root.effectIntensity

              ctx.beginPath()
              ctx.arc(mote.x, mote.y, mote.r, 0, 6.28)
              ctx.fillStyle = "rgba(255, 225, 160, " + pulseAlpha + ")"
              ctx.fill()

              mote.y += mote.speedY
              mote.x += mote.speedX + Math.sin(mote.pulse) * 0.2

              if (mote.y < -10) {
                mote.y = h + 10
                mote.x = Math.random() * w
              }
            }
          }

          // ======================== 4. STARRY NIGHT ========================
          else if (effect === "stars") {
            for (var stIdx = 0; stIdx < stars.length; stIdx++) {
              var star = stars[stIdx]
              star.phase += star.pulseSpeed
              var starAlpha = star.baseAlpha * (0.6 + 0.4 * Math.sin(star.phase)) * root.effectIntensity

              ctx.beginPath()
              ctx.arc(star.x, star.y, star.r, 0, 6.28)
              ctx.fillStyle = "rgba(220, 235, 255, " + starAlpha + ")"
              ctx.fill()
            }

            // Shooting star chance
            if (Math.random() < 0.003 * root.effectIntensity && shootingStars.length < 2) {
              shootingStars.push({
                x: Math.random() * (w * 0.8),
                y: Math.random() * (h * 0.3),
                len: 60 + Math.random() * 80,
                speed: 16 + Math.random() * 8,
                alpha: 0.9,
                angle: 0.65
              })
            }

            for (var ss = shootingStars.length - 1; ss >= 0; ss--) {
              var sstar = shootingStars[ss]
              var tailX = sstar.x - Math.cos(sstar.angle) * sstar.len
              var tailY = sstar.y - Math.sin(sstar.angle) * sstar.len

              var sgrad = ctx.createLinearGradient(tailX, tailY, sstar.x, sstar.y)
              sgrad.addColorStop(0, "transparent")
              sgrad.addColorStop(1, "rgba(255, 255, 255, " + (sstar.alpha * root.effectIntensity) + ")")

              ctx.beginPath()
              ctx.moveTo(tailX, tailY)
              ctx.lineTo(sstar.x, sstar.y)
              ctx.strokeStyle = sgrad
              ctx.lineWidth = 2.0
              ctx.stroke()

              sstar.x += Math.cos(sstar.angle) * sstar.speed
              sstar.y += Math.sin(sstar.angle) * sstar.speed
              sstar.alpha -= 0.02

              if (sstar.alpha <= 0 || sstar.x > w || sstar.y > h) {
                shootingStars.splice(ss, 1)
              }
            }
          }

          // ======================== 5. FOG & MIST ========================
          else if (effect === "fog") {
            for (var fg = 0; fg < fogPatches.length; fg++) {
              var fog = fogPatches[fg]
              fog.phase += 0.01
              var fogAlpha = fog.baseAlpha * (0.8 + 0.2 * Math.sin(fog.phase)) * root.effectIntensity

              var fgrad = ctx.createRadialGradient(fog.x, fog.y, 20, fog.x, fog.y, fog.radiusX)
              fgrad.addColorStop(0, "rgba(220, 230, 240, " + fogAlpha + ")")
              fgrad.addColorStop(0.7, "rgba(200, 215, 230, " + (fogAlpha * 0.5) + ")")
              fgrad.addColorStop(1, "transparent")

              ctx.fillStyle = fgrad
              ctx.beginPath()
              ctx.ellipse(fog.x, fog.y, fog.radiusX, fog.radiusY, 0, 0, 6.28)
              ctx.fill()

              fog.x += fog.speedX
              if (fog.x - fog.radiusX > w) {
                fog.x = -fog.radiusX
                fog.y = (h * 0.2) + Math.random() * (h * 0.7)
              }
            }
          }
        }

        FrameAnimation {
          running: overlayWindow.visible
          onTriggered: canvas.requestPaint()
        }
      }
    }
  }
}
