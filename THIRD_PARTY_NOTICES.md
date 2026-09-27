# Third-party notices

The terraDial firmware is MIT-licensed (see [LICENSE](LICENSE)). The firmware
image — including the release binaries and what the web installer flashes —
also contains the third-party software below. Their licences require these
notices to accompany it. Full licence texts are in [`licenses/`](licenses/).

Versions are the ones the current build resolves to (`pio run`); `platformio.ini`
allows compatible newer releases.

## Libraries

| Component | Version | Used for | Licence | Copyright |
|---|---|---|---|---|
| [LVGL](https://github.com/lvgl/lvgl) | 8.4.0 | UI toolkit | MIT — [text](licenses/LVGL-MIT.txt) | © 2021 LVGL Kft |
| [qrcodegen](https://www.nayuki.io/page/qr-code-generator-library) (bundled in LVGL) | — | QR codes on the About screen | MIT — [text](licenses/qrcodegen-MIT.txt) | © Project Nayuki |
| [LovyanGFX](https://github.com/lovyan03/LovyanGFX) | 1.2.30 | Display driver | FreeBSD (BSD-2-Clause), with Adafruit GFX (BSD), Adafruit ILI9341 (MIT) and TFT_eSPI (FreeBSD) portions — [text](licenses/LovyanGFX.txt) | © 2020 lovyan03; © 2012 Adafruit Industries; © 2020 Bodmer |
| [ArduinoJson](https://github.com/bblanchon/ArduinoJson) | 7.4.3 | JSON parsing | MIT — [text](licenses/ArduinoJson-MIT.txt) | © 2014–2026 Benoit Blanchon |
| [arduinoWebSockets](https://github.com/Links2004/arduinoWebSockets) | 2.7.3 | FluidNC connection | LGPL-2.1 — [text](licenses/LGPL-2.1.txt) | © 2015 Markus Sattler |
| [Adafruit NeoPixel](https://github.com/adafruit/Adafruit_NeoPixel) | 1.15.5 | Status LED ring | LGPL-3.0 — [text](licenses/LGPL-3.0.txt), which builds on [GPL-3.0](licenses/GPL-3.0.txt) | Adafruit Industries and contributors (written by Phil Burgess; no explicit copyright line in the source) |
| [Arduino core for ESP32](https://github.com/espressif/arduino-esp32) | 2.0.17 | Framework (Wi-Fi, HTTP, Preferences, mDNS, updates) | LGPL-2.1-or-later — [text](licenses/LGPL-2.1.txt) | © Arduino Team, © Espressif Systems and contributors |
| [ESP-IDF](https://github.com/espressif/esp-idf) (inside the Arduino core) | 4.4.7 | SDK: RTOS, networking, TLS, drivers | Apache-2.0 — [text](licenses/Apache-2.0.txt), plus the licences of its own components, listed in [Espressif's copyright page for this version](https://docs.espressif.com/projects/esp-idf/en/v4.4.7/esp32s3/COPYRIGHT.html) (FreeRTOS, lwIP, mbedTLS and others) | © Espressif Systems and contributors |
| CST816D touch driver (`lib/CST816D`) | — | Touch input | **Unknown** — vendored from Elecrow's CrowPanel 1.28" example code; the vendored copy carries no licence or copyright notice | Elecrow |

## Fonts and icons

| Component | Used for | Licence | Copyright |
|---|---|---|---|
| [Lucide](https://lucide.dev) | UI icons (`src/display/fonts/`) | ISC — [text](src/display/fonts/LICENSE-lucide.txt) | © Lucide Icons and Contributors |
| [Feather](https://feathericons.com), via Lucide | Some of those icons (listed in the Lucide licence file) | MIT — [text](src/display/fonts/LICENSE-lucide.txt) | © 2013–present Cole Bemis |
| [Montserrat](https://github.com/JulietaUla/Montserrat) (LVGL's built-in fonts) | UI text | SIL OFL 1.1 — [text](licenses/Montserrat-OFL-1.1.txt) | © 2011 The Montserrat Project Authors |
| [Font Awesome Free 5](https://fontawesome.com) (symbols in LVGL's built-in fonts) | Compiled into the Montserrat fonts | SIL OFL 1.1 — [text](licenses/FontAwesome-OFL-1.1.txt) | © Fonticons, Inc. |

## LGPL components

arduinoWebSockets, Adafruit NeoPixel and the Arduino core are LGPL-licensed and
are linked statically into a single firmware image. The LGPL lets you use a
modified version of those libraries with this firmware: the complete source is
in this repository, and it builds with PlatformIO (see the README's *Building*
section). To relink against a modified library, point the relevant `lib_deps`
entry in `platformio.ini` (or the platform's framework package) at your version
and rebuild.

## Not included in the firmware

The web installer page loads [ESP Web Tools](https://github.com/esphome/esp-web-tools)
(Apache-2.0) from unpkg.com in the browser; it isn't bundled with or distributed
by this project.
