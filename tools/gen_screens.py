#!/usr/bin/env python3
"""Generate SVG illustrations of each terraDial screen for the README.

These are RENDERS, not screenshots: there's no way to capture the real
panel's framebuffer from a build machine. Everything here is transcribed
from the layout code -- palette hex from include/palette.h, ring radii and
chip sizes from radial_ring.h/ui_dial.cpp, arc angles from the setArcLayout()
calls, hub sizes and font sizes from each ui_*.cpp -- so the proportions and
colours match what the firmware draws. Icons are the real Lucide glyphs the
firmware's lucide_* fonts carry, at the font size each label uses.

Keep in sync by hand if a screen's geometry changes.

Usage: python tools/gen_screens.py   ->  docs/screens/*.svg
"""
import math
import os

# --- palette (include/palette.h, ported from terraForge's dark theme) ---
BG_APP = "#1a1a2e"
BG_PANEL = "#16213e"
BG_SECONDARY = "#0f3460"
BORDER = "#5c7a9e"
TEXT = "#e0e0e0"
TEXT_MUTED = "#9ca3af"
TEXT_FAINT = "#818ea5"
ACCENT = "#e94560"
ACCENT_FG = "#ffffff"
ACCENT_SECONDARY = "#60a0ff"
ALERT = "#d12b3f"
GREEN = "#3ddc84"

W = 240
FONT = "Segoe UI, Roboto, Helvetica, Arial, sans-serif"

# --- ring geometry, from radial_ring.h defaults + per-screen overrides ---
DIAL_RADIUS, DIAL_NEAR, DIAL_FAR = 84, 62, 34  # ui_dial.cpp RING_*
DIAL_HUB = 96                                  # ui_dial.cpp HUB_SIZE
DIAL_SPREAD = 0.3   # RadialRing::setSpread on the home dial
ARC_SPREAD = 0.55   # ...and on the Jobs/Settings arcs


def head(parts):
    parts.append(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240" width="240" height="240">'
    )
    # bezel + face: the panel is round, so anything past r=120 is unreachable
    parts.append('<circle cx="120" cy="120" r="119" fill="#0a0a12"/>')
    parts.append('<circle cx="120" cy="120" r="116" fill="%s"/>' % BG_APP)
    parts.append('<clipPath id="face"><circle cx="120" cy="120" r="116"/></clipPath>')
    parts.append('<g clip-path="url(#face)">')


def tail(parts):
    parts.append("</g></svg>")


def text(parts, x, y, s, size=12, fill=TEXT, weight="400", anchor="middle"):
    parts.append(
        '<text x="%g" y="%g" font-family="%s" font-size="%g" font-weight="%s" '
        'fill="%s" text-anchor="%s" dominant-baseline="central">%s</text>'
        % (x, y, FONT, size, weight, fill, anchor, esc(s))
    )


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def circle(parts, cx, cy, r, fill, stroke=None, sw=1, opacity=None):
    op = ' opacity="%g"' % opacity if opacity is not None else ""
    st = ' stroke="%s" stroke-width="%g"' % (stroke, sw) if stroke else ""
    parts.append('<circle cx="%g" cy="%g" r="%g" fill="%s"%s%s/>' % (cx, cy, r, fill, st, op))


def rect(parts, x, y, w, h, r, fill, opacity=None, stroke=None):
    op = ' opacity="%g"' % opacity if opacity is not None else ""
    st = ' stroke="%s" stroke-width="1"' % stroke if stroke else ""
    parts.append(
        '<rect x="%g" y="%g" width="%g" height="%g" rx="%g" fill="%s"%s%s/>'
        % (x, y, w, h, r, fill, st, op)
    )


def mix(c1, c2, t):
    """Blend hex colours -- mirrors lv_color_mix(c1, c2, t*255)."""
    a = [int(c1[i : i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i : i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(b[i] + (a[i] - b[i]) * t) for i in range(3))


# ---------------------------------------------------------------- icons
# Lucide icons (lucide.dev, ISC; notices in src/display/fonts/LICENSE-lucide.txt),
# copied from lucide-static at the version tools/gen_lucide_font.py pins, so
# these are the same glyphs the firmware's lucide_* fonts draw. 24x24 boxes,
# stroked at 2 -- the font scales both with its pixel size, and so does icon().
LUCIDE = {
    "house": '<path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/>'
             '<path d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
    "move": '<path d="M12 2v20"/><path d="m15 19-3 3-3-3"/><path d="m19 9 3 3-3 3"/>'
            '<path d="M2 12h20"/><path d="m5 9-3 3 3 3"/><path d="m9 5 3-3 3 3"/>',
    "pen": '<path d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z"/>',
    "card-sim": '<path d="M12 14v4"/>'
                '<path d="M14.172 2a2 2 0 0 1 1.414.586l3.828 3.828A2 2 0 0 1 20 7.828V20a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z"/>'
                '<path d="M8 14h8"/><rect x="8" y="10" width="8" height="8" rx="2"/>',
    "folder": '<path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/>',
    "file": '<path d="M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8v12a2 2 0 0 1-2 2z"/>'
            '<path d="M14 2v5a1 1 0 0 0 1 1h5"/>',
    "camera": '<path d="M13.997 4a2 2 0 0 1 1.76 1.05l.486.9A2 2 0 0 0 18.003 7H20a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2h1.997a2 2 0 0 0 1.759-1.048l.489-.904A2 2 0 0 1 10.004 4z"/>'
              '<circle cx="12" cy="13" r="3"/>',
    "lightbulb": '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/>'
                 '<path d="M9 18h6"/><path d="M10 22h4"/>',
    "settings": '<path d="M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915"/>'
                '<circle cx="12" cy="12" r="3"/>',
    "octagon-x": '<path d="m15 9-6 6"/>'
                 '<path d="M2.586 16.726A2 2 0 0 1 2 15.312V8.688a2 2 0 0 1 .586-1.414l4.688-4.688A2 2 0 0 1 8.688 2h6.624a2 2 0 0 1 1.414.586l4.688 4.688A2 2 0 0 1 22 8.688v6.624a2 2 0 0 1-.586 1.414l-4.688 4.688a2 2 0 0 1-1.414.586H8.688a2 2 0 0 1-1.414-.586z"/>'
                 '<path d="m9 9 6 6"/>',
    "square": '<rect width="18" height="18" x="3" y="3" rx="2"/>',
    "pause": '<rect x="14" y="3" width="5" height="18" rx="1"/><rect x="5" y="3" width="5" height="18" rx="1"/>',
    "play": '<path d="M5 5a2 2 0 0 1 3.008-1.728l11.997 6.998a2 2 0 0 1 .003 3.458l-12 7A2 2 0 0 1 5 19z"/>',
    "wifi": '<path d="M12 20h.01"/><path d="M2 8.82a15 15 0 0 1 20 0"/>'
            '<path d="M5 12.859a10 10 0 0 1 14 0"/><path d="M8.5 16.429a5 5 0 0 1 7 0"/>',
    "sliders-horizontal": '<path d="M10 5H3"/><path d="M12 19H3"/><path d="M14 3v4"/><path d="M16 17v4"/>'
                          '<path d="M21 12h-9"/><path d="M21 19h-5"/><path d="M21 5h-7"/><path d="M8 10v4"/><path d="M8 12H3"/>',
    "monitor": '<rect width="20" height="14" x="2" y="3" rx="2"/>'
               '<line x1="8" x2="16" y1="21" y2="21"/><line x1="12" x2="12" y1="17" y2="21"/>',
    "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
    "eye": '<path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/>'
           '<circle cx="12" cy="12" r="3"/>',
    "delete": '<path d="M10 5a2 2 0 0 0-1.344.519l-6.328 5.74a1 1 0 0 0 0 1.481l6.328 5.741A2 2 0 0 0 10 19h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2z"/>'
              '<path d="m12 9 6 6"/><path d="m18 9-6 6"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "x": '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
    "chevron-left": '<path d="m15 18-6-6 6-6"/>',
    "triangle-alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/>'
                      '<path d="M12 9v4"/><path d="M12 17h.01"/>',
}


def icon(parts, cx, cy, name, px, col):
    """A Lucide glyph at a lucide_<px> font's size, centred on (cx, cy)."""
    parts.append(
        '<g transform="translate(%g %g) scale(%g)" fill="none" stroke="%s" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round">%s</g>'
        % (cx - px / 2.0, cy - px / 2.0, px / 24.0, col, LUCIDE[name])
    )


def ring_icon_px(nearness):
    """uiRingIconFont(uiRingIconSize(...)) in ui_widgets.cpp, settled
    (no hysteresis): lucide_32 in the top slot, 24 mid-ring, 14 beyond."""
    if nearness > 0.90:
        return 32
    return 24 if nearness > 0.52 else 14


def back_button(parts):
    """The shared bottom-centre back chip (ui_screen_shell.cpp)."""
    circle(parts, 120, 214, 18, BG_SECONDARY)
    icon(parts, 120, 214, "chevron-left", 16, TEXT_MUTED)


def estop_pip(parts):
    """The stop pip beside it, on screens that can move the machine
    (ui_screen_shell.cpp's addEstopButton)."""
    circle(parts, 82, 208, 13, ALERT)
    icon(parts, 82, 208, "octagon-x", 12, ACCENT_FG)


# ------------------------------------------------------- ring renderers
def spread_angle(ang, amount, limit=180.0):
    """RadialRing::spreadAngle -- opens the spacing up near the top slot and
    squeezes it shut near the bottom, pinning both ends in place."""
    if not amount:
        return ang
    u = ang / limit
    return limit * (u + amount * math.sin(math.pi * u) / math.pi)


def full_ring(parts, items, selected, radius=DIAL_RADIUS, near=DIAL_NEAR, far=DIAL_FAR,
              opa_far=100 / 255.0, spread=DIAL_SPREAD):
    """Home's full circle (RadialRing default mode), with the dial's spread."""
    n = len(items)
    step = 360.0 / n
    # Far items first, so the bunched-up bottom stacks the way the firmware
    # orders it (nearer chips in front).
    order = sorted(range(n), key=lambda i: -abs(((i - selected) * step + 180) % 360 - 180))
    for i in order:
        kind, alert = items[i]
        ang = spread_angle(((i - selected) * step + 180) % 360 - 180, spread)
        nearness = 1 - abs(ang) / 180.0
        size = far + (near - far) * nearness
        rad = math.radians(ang)
        cx, cy = 120 + radius * math.sin(rad), 120 - radius * math.cos(rad)
        if alert:
            circle(parts, cx, cy, size / 2, ALERT)
            icon(parts, cx, cy, kind, ring_icon_px(nearness), ACCENT_FG)
        else:
            circle(parts, cx, cy, size / 2, mix(ACCENT, BG_SECONDARY, nearness),
                   opacity=opa_far + (1 - opa_far) * nearness)
            icon(parts, cx, cy, kind, ring_icon_px(nearness), mix(ACCENT_FG, TEXT_MUTED, nearness))


def arc_ring(parts, kinds, selected, step_deg, half_arc, radius=80, near=60, far=20,
             opa_far=0.0, spread=ARC_SPREAD):
    """Jobs/Settings open arc -- bottom left clear for the back button."""
    # Far chips first, so the bunched-up tail stacks the way the firmware
    # orders it (nearer chips in front).
    for i in sorted(range(len(kinds)), key=lambda i: -abs((i - selected) * step_deg)):
        kind = kinds[i]
        ang = (i - selected) * step_deg
        if abs(ang) >= half_arc:
            continue
        ang = spread_angle(ang, spread, half_arc)
        nearness = max(0.0, 1 - abs(ang) / half_arc)
        size = far + (near - far) * nearness
        rad = math.radians(ang)
        cx, cy = 120 + radius * math.sin(rad), 120 - radius * math.cos(rad)
        circle(parts, cx, cy, size / 2, mix(ACCENT, BG_SECONDARY, nearness),
               opacity=opa_far + (1 - opa_far) * nearness)
        icon(parts, cx, cy, kind, ring_icon_px(nearness), mix(ACCENT_FG, TEXT_MUTED, nearness))


def hub(parts, size, lines):
    """Centre hub: (text, dy, size, colour, weight) tuples."""
    circle(parts, 120, 120, size / 2, BG_SECONDARY, BORDER, 1)
    for s, dy, sz, col, wt in lines:
        text(parts, 120, 120 + dy, s, sz, col, wt)


# ------------------------------------------------------------- screens
def screen_home():
    p = []
    head(p)
    # Must match DIAL_ITEMS in src/display/ui_dial.cpp:
    # Home XY, Jog, Pen, Jobs, Photo, E-Stop, Lights, Settings.
    items = [("house", 0), ("move", 0), ("pen", 0), ("card-sim", 0),
             ("camera", 0), ("octagon-x", 1), ("lightbulb", 0), ("settings", 0)]
    full_ring(p, items, 0)
    hub(p, DIAL_HUB, [("Home XY", -8, 14, TEXT, "600"), ("IDLE", 12, 12, TEXT_MUTED, "400")])
    tail(p)
    return "home-dial", p


def screen_jobs():
    p = []
    head(p)
    # A folder or two ahead of the files, as an SD root usually lists them.
    arc_ring(p, ["folder", "folder", "file", "file", "file", "file", "file"], 2, 30.0, 132.0)
    hub(p, 96, [("flow_red.gcode", -18, 11, TEXT, "600"),
                ("8.2 MB", 4, 12, TEXT_MUTED, "400")])
    icon(p, 104, 144, "play", 12, ACCENT)
    text(p, 126, 144, "Run", 12, ACCENT, "600")
    back_button(p)
    tail(p)
    return "jobs", p


def screen_jog():
    p = []
    head(p)
    for i, (lbl, sel) in enumerate((("X", 0), ("Y", 1), ("Z", 0))):
        x = 103 + i * 40
        rect(p, x - 17, 32, 34, 26, 13, ACCENT if sel else "none")
        text(p, x, 45, lbl, 14, ACCENT_FG if sel else BORDER, "600")
    text(p, 120, 90, "12.40", 32, TEXT, "600")
    rect(p, 74, 118, 92, 24, 12, BG_SECONDARY)
    text(p, 120, 130, "Set Y zero", 12, TEXT_MUTED)
    # Four chips at 36 wide + 6 gaps = 162px, centred on 120 (see ui_jog.cpp).
    for i, (lbl, sel) in enumerate((("0.1", 0), ("1", 1), ("10", 0), ("100", 0))):
        x = 39 + i * 42
        rect(p, x, 160, 36, 28, 14, ACCENT if sel else BG_SECONDARY)
        text(p, x + 18, 174, lbl, 12, ACCENT_FG if sel else TEXT_MUTED, "600")
    back_button(p)
    estop_pip(p)
    tail(p)
    return "jog", p


def screen_pen():
    p = []
    head(p)
    icon(p, 106, 34, "pen", 14, TEXT_MUTED)
    text(p, 126, 34, "PEN", 12, TEXT_MUTED)
    rect(p, 50, 88, 140, 64, 20, BG_PANEL)
    rect(p, 53, 91, 66, 58, 17, ACCENT)
    text(p, 86, 111, "Pen", 16, ACCENT_FG, "600")
    text(p, 86, 130, "up", 16, ACCENT_FG, "600")
    rect(p, 121, 91, 66, 58, 17, BG_SECONDARY)
    text(p, 154, 111, "Pen", 16, TEXT_MUTED, "600")
    text(p, 154, 130, "down", 16, TEXT_MUTED, "600")
    back_button(p)
    tail(p)
    return "pen", p


def screen_home_confirm():
    p = []
    head(p)
    icon(p, 120, 62, "house", 24, ACCENT)
    text(p, 120, 92, "Clear the bed first", 16, TEXT, "600")
    text(p, 120, 112, "Lift the pen and check the", 12, TEXT_MUTED)
    text(p, 120, 126, "carriage can move freely.", 12, TEXT_MUTED)
    rect(p, 40, 138, 160, 38, 19, ACCENT)
    text(p, 120, 157, "Confirm & home", 14, ACCENT_FG, "600")
    back_button(p)
    tail(p)
    return "home-confirm", p


def screen_lights():
    p = []
    head(p)
    text(p, 120, 52, "LIGHTS", 12, ACCENT_SECONDARY, "600")
    circle(p, 96, 72, 5, TEXT_FAINT)
    text(p, 132, 72, "Rail: IDLE", 12, TEXT_MUTED)
    rows = [("Panel ring brightness", .6), ("Rail brightness", .8)]
    y = 92
    for lbl, frac in rows:
        text(p, 120, y, lbl, 12, TEXT_MUTED)
        rect(p, 30, y + 10, 180, 10, 5, BG_PANEL)
        rect(p, 30, y + 10, 180 * frac, 10, 5, ACCENT)
        circle(p, 30 + 180 * frac, y + 15, 8, ACCENT_FG)
        y += 38
    text(p, 120, y, "Film mode", 12, TEXT_MUTED)
    rect(p, 98, y + 10, 44, 24, 12, BG_PANEL)
    circle(p, 110, y + 22, 9, ACCENT_FG)
    rect(p, 30, y + 44, 180, 30, 15, ACCENT)
    text(p, 120, y + 59, "Party: OFF", 12, ACCENT_FG, "600")
    back_button(p)
    tail(p)
    return "lights", p


def screen_settings_ring():
    p = []
    head(p)
    arc_ring(p, ["wifi", "sliders-horizontal", "monitor", "info"], 0, 40.0, 132.0,
             radius=76, near=64, far=26, opa_far=110 / 255.0)
    hub(p, 82, [("Wi-Fi", -8, 14, TEXT, "600"), ("open", 12, 12, ACCENT, "400")])
    back_button(p)
    tail(p)
    return "settings-ring", p


def screen_settings_display():
    p = []
    head(p)
    text(p, 120, 52, "DISPLAY", 12, ACCENT_SECONDARY, "600")
    text(p, 120, 76, "Brightness: 100%", 12, TEXT_MUTED)
    rect(p, 30, 86, 180, 10, 5, BG_PANEL)
    rect(p, 30, 86, 180, 10, 5, ACCENT)
    circle(p, 205, 91, 8, ACCENT_FG)
    text(p, 120, 112, "Invert menu rotation", 12, TEXT_MUTED)
    rect(p, 98, 122, 44, 24, 12, BG_PANEL)
    circle(p, 110, 134, 9, ACCENT_FG)
    text(p, 120, 162, "Sleep after", 12, TEXT_MUTED)
    for i, (lbl, sel) in enumerate((("Never", 0), ("3m", 0), ("5m", 1), ("10m", 0))):
        x = 36 + i * 42
        rect(p, x, 172, 38, 26, 13, ACCENT if sel else BG_PANEL)
        text(p, x + 19, 185, lbl, 11, ACCENT_FG if sel else TEXT_MUTED, "600")
    back_button(p)
    tail(p)
    return "settings-display", p


def screen_job_progress():
    p = []
    head(p)
    circle(p, 120, 120, 106, "none", BG_PANEL, 12)
    pct = 0.42
    a0, a1 = -90, -90 + 360 * pct
    large = 1 if pct > .5 else 0
    x0, y0 = 120 + 106 * math.cos(math.radians(a0)), 120 + 106 * math.sin(math.radians(a0))
    x1, y1 = 120 + 106 * math.cos(math.radians(a1)), 120 + 106 * math.sin(math.radians(a1))
    p.append('<path d="M%g %g A106 106 0 %d 1 %g %g" stroke="%s" stroke-width="12" fill="none"/>'
             % (x0, y0, large, x1, y1, ACCENT))
    text(p, 120, 64, "flow_red.gcode", 12, TEXT_MUTED)
    text(p, 120, 84, "6:18   ~9 min left", 12, TEXT_MUTED)
    text(p, 120, 106, "42%", 32, TEXT, "600")
    circle(p, 86, 164, 29, BG_SECONDARY)
    icon(p, 86, 164, "pause", 24, TEXT)
    circle(p, 154, 164, 29, ALERT)
    icon(p, 154, 164, "square", 24, ACCENT_FG)
    tail(p)
    return "job-progress", p


def screen_estop():
    p = []
    head(p)
    circle(p, 120, 106, 78, ALERT)
    icon(p, 120, 76, "octagon-x", 24, ACCENT_FG)
    text(p, 120, 104, "E-STOP", 18, ACCENT_FG, "700")
    text(p, 120, 128, "Feed hold", 12, ACCENT_FG)
    text(p, 120, 142, "+ soft reset", 12, ACCENT_FG)
    back_button(p)
    tail(p)
    return "estop", p


def screen_alarm():
    p = []
    head(p)
    icon(p, 120, 62, "triangle-alert", 24, ACCENT)
    text(p, 120, 92, "Alarm active", 16, TEXT, "600")
    text(p, 120, 112, "Clear the bed, then clear", 12, TEXT_MUTED)
    text(p, 120, 126, "the alarm to continue.", 12, TEXT_MUTED)
    rect(p, 40, 138, 160, 38, 19, ACCENT)
    text(p, 120, 157, "Clear alarm", 14, ACCENT_FG, "600")
    back_button(p)
    tail(p)
    return "alarm-clear", p


def logo_mark(parts, cx, cy, size, col):
    """A stand-in for the terraPen mark -- the real one is a single
    continuous stroked path (see tools/gen_logo.py); this just suggests its
    isometric line-work at README scale."""
    u = size / 8.0
    st = ('stroke="%s" stroke-width="1.6" fill="none" stroke-linecap="round" '
          'stroke-linejoin="round"' % col)
    for i in range(-2, 3):
        x = cx + i * u
        parts.append('<path d="M%g %g l%g %g l0 %g l%g %g" %s/>'
                     % (x, cy - size / 2 + abs(i) * u * .5, u, u * .55,
                        size * .45, -u, -u * .55, st))


def qr_block(parts, x, y, size, modules=21):
    """Illustrative QR -- deterministic pattern, not a real encoding."""
    rect(parts, x - 4, y - 4, size + 8, size + 8, 2, "#ffffff")
    m = size / float(modules)
    seed = 12345
    for r in range(modules):
        for c in range(modules):
            finder = ((r < 7 and c < 7) or (r < 7 and c >= modules - 7)
                      or (r >= modules - 7 and c < 7))
            if finder:
                edge = (r in (0, 6) or c in (0, 6) or r in (modules - 1, modules - 7)
                        or c in (modules - 1, modules - 7))
                ring = (2 <= r % (modules - 7) <= 4) if False else None
                on = edge or (2 <= (r % 7) <= 4 and 2 <= (c % 7) <= 4)
            else:
                seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
                on = (seed >> 16) & 1
            if on:
                parts.append('<rect x="%g" y="%g" width="%g" height="%g" fill="%s"/>'
                             % (x + c * m, y + r * m, m, m, BG_APP))


def screen_about():
    p = []
    head(p)
    text(p, 120, 46, "ABOUT", 12, ACCENT_SECONDARY, "600")
    logo_mark(p, 120, 86, 44, TEXT)
    text(p, 120, 120, "terraPen", 16, TEXT, "600")
    text(p, 120, 138, "terrapen.xyz", 12, ACCENT)
    qr_block(p, 88, 152, 64)
    tail(p)
    return "about", p


def screen_brand():
    p = []
    head(p)
    logo_mark(p, 120, 104, 96, TEXT)
    text(p, 120, 182, "terraPen", 16, TEXT, "600")
    text(p, 120, 204, "terrapen.xyz", 12, ACCENT)
    tail(p)
    return "idle-brand", p


def screen_keyboard():
    """radial_keyboard.cpp: the ring turns so the selected key sits at the
    top. Keys get a share of the circle by width (keyWeight), the spread
    opens the top, and keys shrink and fade in bands with distance
    (fontForKey) -- all mirrored here."""
    p = []
    head(p)
    radius, spread, opa_far = 100, 0.35, 110 / 255.0
    # Page one of a password field: letters, then the action keys.
    keys = [(c, "char") for c in "abcdefghijklmnopqrstuvwxyz"] + [
        ("ABC", "word"), ("SP", "word"), ("delete", "icon"),
        ("eye", "icon"), ("check", "icon"), ("x", "icon")]
    weight = {"char": 1.0, "icon": 1.3, "word": 1.6}
    sel = 7

    total = sum(weight[k] for _, k in keys)
    centres, acc = [], 0.0
    for _, kind in keys:
        centres.append(360.0 * (acc - weight[keys[0][1]] / 2 + weight[kind] / 2) / total)
        acc += weight[kind]

    def font_px(kind, is_sel, nearness):
        if kind == "word":
            return 24 if is_sel else (14 if nearness > 0.6 else 12)
        if kind == "icon":
            return 24 if is_sel else (16 if nearness > 0.6 else 14 if nearness > 0.3 else 12)
        return 32 if is_sel else (18 if nearness > 0.6 else 14 if nearness > 0.3 else 12)

    for i, (label, kind) in enumerate(keys):
        ang = (centres[i] - centres[sel] + 180) % 360 - 180
        ang = spread_angle(ang, spread)
        nearness = 1 - abs(ang) / 180.0
        rad = math.radians(ang)
        cx, cy = 120 + radius * math.sin(rad), 120 - radius * math.cos(rad)
        is_sel = i == sel
        px = font_px(kind, is_sel, nearness)
        col = ACCENT if is_sel else TEXT_MUTED
        opa = 1.0 if is_sel else opa_far + (1 - opa_far) * nearness
        p.append('<g opacity="%.3f">' % opa)
        if kind == "icon":
            icon(p, cx, cy, label, px, col)
        else:
            text(p, cx, cy, label, px, col, "600" if is_sel else "400")
        p.append("</g>")

    hub(p, 156, [("Password", -42, 14, TEXT_MUTED, "400"),
                 ("******g", -10, 18, TEXT, "600"),
                 ("h", 30, 24, ACCENT, "700")])
    tail(p)
    return "radial-keyboard", p


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(root, "docs", "screens")
    os.makedirs(out, exist_ok=True)
    for fn in (screen_home, screen_jobs, screen_jog, screen_pen, screen_home_confirm,
               screen_lights, screen_settings_ring, screen_settings_display,
               screen_job_progress, screen_estop, screen_alarm, screen_keyboard,
               screen_about, screen_brand):
        name, parts = fn()
        path = os.path.join(out, name + ".svg")
        open(path, "w").write("\n".join(parts))
        print("wrote docs/screens/%s.svg" % name)


if __name__ == "__main__":
    main()
