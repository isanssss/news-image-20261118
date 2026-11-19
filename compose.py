#!/usr/bin/env python3
"""compose.py — draws "The World in One Day" for Wednesday 18 November 2026.

A single-page newspaper front page (1024x1024) summing up one day of world
news: masthead and date check, a UTC timeline of the day, six illustrated
panels, and a sourced list of 50 stories. Rendered at 2048x2048 with Pillow
and downscaled with LANCZOS so the small type stays crisp.

Deterministic: no clocks, no randomness without a fixed seed, no network.
Running it twice produces byte-identical entry.png files.
"""

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- constants

S = 2                      # render scale (2048 -> 1024)
SIZE = 1024
MX = 34                    # side margin (final px)
CW = SIZE - 2 * MX         # content width
RIGHT = SIZE - MX

PAPER = (247, 243, 233)
INK = (26, 22, 16)
ACCENT = (156, 40, 32)     # the one accent colour: deep press red
GRAY = (96, 90, 78)
FAINT = (203, 195, 172)

FD = "/usr/share/fonts/truetype/noto/"
SERIF = FD + "NotoSerif-Regular.ttf"
SERIF_B = FD + "NotoSerif-Bold.ttf"
SERIF_BLACK = FD + "NotoSerif-Black.ttf"
SANS = FD + "NotoSans-Regular.ttf"
SANS_M = FD + "NotoSans-Medium.ttf"
SANS_SB = FD + "NotoSans-SemiBold.ttf"
SANS_B = FD + "NotoSans-Bold.ttf"
SANSC_B = FD + "NotoSans-CondensedBold.ttf"
SERIFC = FD + "NotoSerif-Condensed.ttf"
SERIFC_I = FD + "NotoSerif-CondensedItalic.ttf"

OUT = Path(__file__).resolve().parent / "entry.png"


def F(path, size):
    """Font at `size` final px (scaled to render resolution)."""
    return ImageFont.truetype(path, int(round(size * S)))


def X(v):
    return v * S


# ------------------------------------------------------------------- stories
# (time or None, headline, summary, source) — timed stories first, UTC order.

STORIES = [
    ("00:48", "Quake shakes Romania's Vrancea zone",
     "M5.3 deep quake felt in Bucharest; two hurt by falling furniture", "Orbis Weather"),
    ("01:14", "Xi and Putin open talks in Shenzhen",
     "Ahead of Thursday's trilateral with Trump", "Reuters"),
    ("02:17", "Iran fires drones at US bases in Kuwait, Bahrain",
     "First attack on Kuwait since Sept; Hormuz mine claims", "Reuters"),
    ("06:07", "M5.9 earthquake strikes off Peru",
     "85 km WNW of San Juan; the day's strongest quake", "Orbis Weather"),
    ("07:20", "Two feeding black holes in one early galaxy",
     "Webb + Gemini find pair 18,100 light-years apart", "World of Now"),
    ("08:52", "Trump lands in Shenzhen; APEC opens",
     "Xi calls for unity and openness on technology", "AP"),
    ("10:16", "Voyager 1 reaches one light-day from Earth",
     "25.9bn km out; its signals now take a full day", "Smithsonian"),
    ("12:07", "Prosecutor seeks probe of ex-central bank chief",
     "Turkey's Kavcioglu investigated over fund-crisis links", "Reuters"),
    ("13:29", "Indonesia–China deals worth $71.8B",
     "Four partnerships incl. 10 smart cities; Prabowo attends", "Reuters"),
    ("13:52", "FIFA opens anonymous integrity channel",
     "Reporting line for players and officials", "FIFA"),
    ("14:04", "COP31 launches second Global Stocktake",
     "Antalya talks deadlocked; 21 issues unresolved", "UN News"),
    ("15:22", "UNICEF: 64 children killed in Yemen",
     "64 more injured since 3 September escalation", "UNICEF"),
    ("15:54", "Clues to ancient ice beyond Neptune",
     "NASA finds heavier oxygen isotopes in Kuiper dust", "NASA"),
    ("16:33", "Ugandan activist charged with treachery",
     "Sam Mugumya in military court a year after seizure", "Reuters"),
    ("19:08", "EU approves signing of Indonesia trade deal",
     "CEPA + investment pact; signature still to come", "Wire reports"),
    ("19:50", "Trials approved for two new Ebola vaccines",
     "For the Bundibugyo strain in DR Congo", "Al Jazeera"),
    ("21:07", "Gaza ceasefire 'could collapse' — Board of Peace",
     "Report faults both sides; tanks cross Yellow Line, 3 killed", "Reuters"),
    ("21:17", "UK asks YouTube to remove Russell Brand",
     "Google rejects a related UK request same day", "BBC"),
    ("21:35", "William and Kate end India trip with Modi",
     "Final meeting of the royal visit, in New Delhi", "IANS"),
    ("23:25", "Van Gogh blossoms sell for record $190.4M",
     "'Châtaigniers en fleurs', Sotheby's New York", "Reuters"),
    (None, "Anthropic prices IPO at $83, $1.5T value",
     "Biggest Wall Street debut ever; trades Thu as ANT", "AP"),
    (None, "15 inches of rain floods South Florida",
     "Broward emergency; schools shut; roof collapse, no injuries", "AP"),
    (None, "S&P 500 falls fifth straight day",
     "Hawkish Fed minutes; Dow -1.11%; gold -3.51%", "Motley Fool"),
    (None, "Nvidia falls despite revenue doubling",
     "$115.8B quarter fails to end the sell-off", "Motley Fool"),
    (None, "US: outage week was not a cyberattack",
     "Microsoft 365, FAA stop, bank faults 'unrelated'", "AP"),
    (None, "WHO keeps DR Congo Ebola a global emergency",
     "11,000+ cases, ~5,400 deaths; cases doubled in 3 months", "UN News"),
    (None, "950,000 displaced Palestinians on flood-prone ground",
     "Gaza's fourth winter; 1.4M in acute hunger", "UN via Al Jazeera"),
    (None, "Russian attacks kill at least five in Ukraine",
     "141 drones overnight; 126 downed", "Al Jazeera"),
    (None, "Air defence is Ukraine's top Ramstein priority",
     "Zelenskyy seeks fighters and interceptors", "Ukraine govt"),
    (None, "EU proposes €45B Ukraine loan for 2027",
     "€25B military + €20B budget support", "Reuters"),
    (None, "Ethiopia, Eritrea mass forces on border",
     "Build-up near Badme raises war fears", "Reuters"),
    (None, "All 36 Nigerian states approve state police",
     "Awaits President Tinubu's signature", "OkayAfrica"),
    (None, "US signs military deal with Venezuela",
     "Hegseth in Caracas; ties restored after 2005", "AP"),
    (None, "Democrats nominate Jeffries for Speaker",
     "251–11; would be first Black Speaker", "AP"),
    (None, "Pastor convicted in Haiti president's killing",
     "Sanon guilty of conspiracy in Moïse assassination", "AP"),
    (None, "Quad leaders meet in Manila",
     "US, India, Australia, Japan after two-year gap", "BusinessWorld"),
    (None, "US sanctions Hezbollah in new round",
     "Pressure stepped up on Iran-backed group", "Al Jazeera"),
    (None, "UK–EU drop 'trusted partnership' from draft",
     "Row over cars, tuition before Friday summit", "BBC"),
    (None, "Pakistan: India can't hold 240M hostage on Indus",
     "Cites ruling that water treaty stands", "Global News Watch"),
    (None, "BASIC bloc pushes climate equity at COP31",
     "23 countries back Antalya fire plan", "UN News"),
    (None, "Cat 5 Cyclone Xavier hits Cook Islands wharves",
     "Manihiki damaged; no casualties", "Orbis Weather"),
    (None, "GTA VI begins global rollout",
     "After 13-year wait; Metacritic 99", "Le Monde"),
    (None, "England win ODI series 2–1 in Hobart",
     "Beat Australia by 97 runs; Duckett 133", "Sky Sports"),
    (None, "Arizona upsets UConn 85–79",
     "Kharchenkov 20 pts for No. 12 Arizona", "AP"),
    (None, "Real Madrid extends Güler to 2032",
     "New deal for Turkish midfielder", "IANS"),
    (None, "Atlético's Lookman likely out for 2026",
     "Knee injury on Nigeria duty", "IANS"),
    (None, "Israel coach Ben Shimon steps down",
     "After Nations League campaign", "IANS"),
    (None, "India U17 beat Palestine 4–1",
     "Asian Cup qualifiers, Kuala Lumpur", "IANS"),
    (None, "Star spirals into a supergiant, Webb confirms",
     "First-of-its-kind merger in Andromeda", "Phys.org"),
    (None, "Dead star's radio bursts every 62 minutes",
     "Long-period transient puzzles astronomers", "Phys.org"),
]

PINS = [
    ("00:48", 48, "Romania quake"),
    ("02:17", 137, "Iran drones Gulf"),
    ("06:07", 367, "Peru quake"),
    ("08:52", 532, "Trump lands Shenzhen"),
    ("10:16", 616, "Voyager 1 light-day"),
    ("12:07", 727, "Turkey probe"),
    ("13:29", 809, "Indonesia–China $71.8B"),
    ("14:04", 844, "COP31 stocktake"),
    ("16:33", 993, "Uganda activist charged"),
    ("19:50", 1190, "Ebola vaccine trials"),
    ("21:07", 1267, "Gaza collapse warning"),
    ("23:25", 1405, "Van Gogh record $190.4M"),
]

CAPTIONS = [
    "Xi–Putin talks open in Shenzhen — Reuters",
    "Iran drones at US bases; Hormuz mine claims — Reuters",
    "Ceasefire 'could collapse'; tanks cross Yellow Line — Reuters",
    "Anthropic IPO prices at $83 — $1.5 trillion value — AP",
    "Voyager 1 reaches one light-day, 10:16 UTC — Smithsonian",
    "15 inches of rain floods South Florida — AP",
]


# -------------------------------------------------------------- text helpers

def wrap_runs(d, runs, max_w):
    """Greedy word-wrap of (text, font, fill) runs into lines of words."""
    words = []
    for text, font, fill in runs:
        for w in text.split(" "):
            if w:
                words.append((w, font, fill))
    lines, cur, cur_w = [], [], 0.0
    for wtext, font, fill in words:
        ww = d.textlength(wtext, font=font)
        sp = d.textlength(" ", font=font)
        add = ww if not cur else ww + sp
        if cur and cur_w + add > max_w:
            lines.append(cur)
            cur, cur_w = [(wtext, font, fill)], ww
        else:
            cur.append((wtext, font, fill))
            cur_w += add
    if cur:
        lines.append(cur)
    return lines


def draw_words(d, x, y, line):
    cx = x
    for i, (wtext, font, fill) in enumerate(line):
        if i:
            cx += d.textlength(" ", font=font)
        d.text((cx, y), wtext, font=font, fill=fill)
        cx += d.textlength(wtext, font=font)
    return cx


def fit_size(d, text, path, start, max_w, step=1.0):
    """Largest font size <= start at which text fits max_w (final px)."""
    size = start
    while size > 8:
        if d.textlength(text, font=F(path, size)) <= X(max_w):
            return size
        size -= step
    return size


def centered(d, cx, y, text, font, fill):
    d.text((X(cx), X(y)), text, font=font, fill=fill, anchor="mt")


# ------------------------------------------------------------------ masthead

def masthead(d):
    title = "THE WORLD IN ONE DAY"
    size = fit_size(d, title, SERIF_BLACK, 57, 930)
    centered(d, SIZE / 2, 24, title, F(SERIF_BLACK, size), INK)
    d.line([X(MX), X(88), X(RIGHT), X(88)], fill=INK, width=S)
    date = "Wednesday, 18 November 2026"
    dsize = fit_size(d, date, SERIF_B, 47, 780)
    centered(d, SIZE / 2, 95, date, F(SERIF_B, dsize), INK)
    d.rectangle([X(MX), X(147), X(RIGHT), X(152)], fill=INK)
    d.line([X(MX), X(157), X(RIGHT), X(157)], fill=INK, width=S)


def date_check(d):
    y0, y1 = 165, 197
    d.rectangle([X(MX), X(y0), X(RIGHT), X(y1)], outline=INK, width=S)
    f = F(SANS_SB, 10.5)
    lines = [
        [("DATE CHECK", F(SANS_B, 10.5), ACCENT),
         (" · Wednesday · 18 November 2026 · day 322 of 2026", f, INK)],
        [("every story on this page happened or was first reported on this day"
          " · all times UTC", f, INK)],
    ]
    for i, runs in enumerate(lines):
        words = []
        for text, font, fill in runs:
            for w in text.split(" "):
                if w:
                    words.append((w, font, fill))
        total = sum(d.textlength(w, font=fo) for w, fo, _ in words)
        total += sum(d.textlength(" ", font=words[i + 1][1])
                     for i in range(len(words) - 1))
        draw_words(d, X(SIZE / 2) - total / 2, X(170 + i * 13),
                   [(w, fo, fi) for w, fo, fi in words])


# ------------------------------------------------------------------ timeline

def timeline(d):
    d.text((X(MX), X(205)), "THE DAY IN UTC", font=F(SANS_B, 11), fill=INK)
    line_y = 255
    d.line([X(MX), X(line_y), X(RIGHT), X(line_y)], fill=INK, width=2 * S)
    f_time, f_label = F(SANS_B, 11), F(SANS, 9.5)
    for above in (True, False):
        blocks = []
        for i, (tstr, minutes, label) in enumerate(PINS):
            if (i % 2 == 0) != above:
                continue
            cx = MX + minutes / 1440 * CW
            twf = max(d.textlength(tstr, font=f_time),
                      d.textlength(label, font=f_label)) / S
            bx = min(max(cx - twf / 2, MX), RIGHT - twf)
            blocks.append([cx, bx, twf, tstr, label])
        for k in range(1, len(blocks)):       # keep a clear gap per side
            need = blocks[k - 1][1] + blocks[k - 1][2] + 10
            if blocks[k][1] < need:
                blocks[k][1] = need
        over = blocks[-1][1] + blocks[-1][2] - RIGHT
        if over > 0:
            for b in blocks:
                b[1] -= over
        for cx, bx, twf, tstr, label in blocks:
            ccx = bx + twf / 2
            d.ellipse([X(cx - 3), X(line_y - 3), X(cx + 3), X(line_y + 3)],
                      fill=ACCENT)
            if above:
                d.line([X(cx), X(line_y - 4), X(cx), X(245)], fill=GRAY,
                       width=S)
                centered(d, ccx, 221, tstr, f_time, ACCENT)
                centered(d, ccx, 235, label, f_label, INK)
            else:
                d.line([X(cx), X(line_y + 4), X(cx), X(265)], fill=GRAY,
                       width=S)
                centered(d, ccx, 266, tstr, f_time, ACCENT)
                centered(d, ccx, 280, label, f_label, INK)


# -------------------------------------------------------------------- panels

def panel_frame(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], outline=INK, width=S)


def panel_shenzhen(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(213, 227, 238))
    slate = (52, 62, 74)
    widths = [0.14, 0.10, 0.18, 0.12, 0.16, 0.11, 0.19]
    heights = [0.42, 0.58, 0.36, 0.62, 0.45, 0.55, 0.40]
    bx = x
    for wf, hf in zip(widths, heights):
        bw = w * wf
        by = y + h * (1 - hf)
        d.rectangle([bx, by, bx + bw, y + h], fill=slate)
        for wy in range(int(by) + 8, int(y + h) - 6, 13):
            for wx in range(int(bx) + 5, int(bx + bw) - 5, 11):
                if (wx * 7 + wy * 13) % 5 < 2:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=(246, 222, 132))
        bx += bw
    fw, fh = w * 0.13, h * 0.30
    for i, px in enumerate([0.30, 0.50, 0.70]):
        pole_x = x + w * px
        d.line([pole_x, y + h * 0.10, pole_x, y + h * 0.94], fill=(28, 28, 28),
               width=3)
        fx, fy = pole_x, y + h * 0.10
        if i == 0:      # China: red, yellow stars as dots
            d.rectangle([fx, fy, fx + fw, fy + fh], fill=(222, 41, 16))
            d.ellipse([fx + fw * 0.10, fy + fh * 0.14, fx + fw * 0.30,
                       fy + fh * 0.40], fill=(255, 222, 0))
            for dx, dy in [(0.52, 0.12), (0.60, 0.30), (0.58, 0.48),
                           (0.48, 0.62)]:
                d.ellipse([fx + fw * dx, fy + fh * dy, fx + fw * dx + 4,
                           fy + fh * dy + 4], fill=(255, 222, 0))
        elif i == 1:    # Russia: white / blue / red
            for j, col in enumerate([(255, 255, 255), (0, 57, 166),
                                     (213, 43, 30)]):
                d.rectangle([fx, fy + fh * j / 3, fx + fw, fy + fh * (j + 1) / 3],
                            fill=col)
        else:           # USA: stripes + blue canton
            for j in range(7):
                col = (178, 34, 52) if j % 2 == 0 else (255, 255, 255)
                d.rectangle([fx, fy + fh * j / 7, fx + fw, fy + fh * (j + 1) / 7],
                            fill=col)
            d.rectangle([fx, fy, fx + fw * 0.42, fy + fh * 4 / 7],
                        fill=(60, 59, 110))
            for r in range(3):
                for c in range(4):
                    d.ellipse([fx + 4 + c * 8, fy + 3 + r * 6,
                               fx + 6 + c * 8, fy + 5 + r * 6],
                              fill=(255, 255, 255))
    panel_frame(d, x, y, w, h)


def panel_hormuz(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h * 0.45], fill=(228, 233, 236))
    d.rectangle([x, y + h * 0.45, x + w, y + h], fill=(84, 128, 150))
    land = (74, 82, 70)
    d.polygon([(x, y + h * 0.28), (x + w * 0.40, y + h * 0.45),
               (x + w * 0.40, y + h), (x, y + h)], fill=land)
    d.polygon([(x + w, y + h * 0.24), (x + w * 0.62, y + h * 0.45),
               (x + w * 0.62, y + h), (x + w, y + h)], fill=land)
    hull = (24, 26, 30)
    for tx, tw_ in [(0.46, 0.20), (0.72, 0.15)]:
        bx, by = x + w * tx, y + h * 0.66
        d.polygon([(bx, by), (bx + w * tw_, by), (bx + w * tw_ * 0.88, by + h * 0.12),
                   (bx + w * tw_ * 0.10, by + h * 0.12)], fill=hull)
        d.rectangle([bx + w * tw_ * 0.62, by - h * 0.10, bx + w * tw_ * 0.80, by],
                    fill=hull)
        d.rectangle([bx + w * tw_ * 0.12, by - h * 0.05, bx + w * tw_ * 0.55, by],
                    fill=(120, 60, 40))
    dcx, dcy = x + w * 0.52, y + h * 0.20     # drone
    d.ellipse([dcx - 13, dcy - 6, dcx + 13, dcy + 6], fill=(28, 28, 32))
    for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        ex, ey = dcx + dx * 24, dcy + dy * 13
        d.line([dcx, dcy, ex, ey], fill=(28, 28, 32), width=3)
        d.ellipse([ex - 7, ey - 3, ex + 7, ey + 3], outline=(28, 28, 32),
                  width=2)
    for mx_, my_ in [(0.50, 0.82), (0.58, 0.90), (0.80, 0.84)]:
        cx, cy = x + w * mx_, y + h * my_
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(38, 42, 46))
        for a in range(0, 360, 60):
            import math
            d.line([cx, cy, cx + 8 * math.cos(math.radians(a)),
                    cy + 8 * math.sin(math.radians(a))], fill=(38, 42, 46),
                   width=2)
    panel_frame(d, x, y, w, h)


def panel_gaza(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(233, 221, 190))
    strip = [(0.34, 0.04), (0.52, 0.04), (0.44, 0.46), (0.33, 0.96),
             (0.17, 0.96), (0.26, 0.46)]
    d.polygon([(x + w * a, y + h * b) for a, b in strip], fill=(224, 205, 160),
              outline=INK)
    d.line([x + w * 0.135, y + h * 0.50, x + w * 0.475, y + h * 0.50],
           fill=(242, 194, 48), width=6)
    for r in range(2):                        # tent rows
        for c in range(4):
            tx = x + w * (0.56 + c * 0.105)
            ty = y + h * (0.66 + r * 0.20)
            tw_, th = w * 0.085, h * 0.16
            d.polygon([(tx, ty + th), (tx + tw_ / 2, ty), (tx + tw_, ty + th)],
                      fill=(250, 248, 242), outline=INK)
    tx, ty = x + w * 0.70, y + h * 0.14       # tank silhouette
    d.rectangle([tx, ty + h * 0.12, tx + w * 0.20, ty + h * 0.24], fill=(45, 45, 45))
    d.rectangle([tx + w * 0.05, ty + h * 0.03, tx + w * 0.13, ty + h * 0.12],
                fill=(45, 45, 45))
    d.line([tx + w * 0.13, ty + h * 0.07, tx + w * 0.27, ty + h * 0.05],
           fill=(45, 45, 45), width=5)
    panel_frame(d, x, y, w, h)


def panel_ipo(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 24, 34))
    d.rectangle([x + w * 0.05, y + h * 0.10, x + w * 0.54, y + h * 0.52],
                outline=(96, 128, 158), width=2)
    _tf = F(SANS_B, 13)
    d.text((x + w * 0.085, y + h * 0.17), "ANT $83", font=_tf,
           fill=(84, 224, 148))
    _ax = x + w * 0.085 + d.textlength("ANT $83", font=_tf) + w * 0.035
    d.polygon([(_ax, y + h * 0.44), (_ax + w * 0.028, y + h * 0.20),
               (_ax + w * 0.056, y + h * 0.44)], fill=(84, 224, 148))
    brass = (198, 158, 74)
    bcx, by = x + w * 0.70, y + h * 0.16
    d.arc([bcx - 8, by - 6, bcx + 8, by + 10], 180, 360, fill=brass, width=4)
    d.pieslice([bcx - 34, by + 2, bcx + 34, by + 46], 180, 360, fill=brass)
    d.polygon([(bcx - 34, by + 24), (bcx + 34, by + 24), (bcx + 44, by + 52),
               (bcx - 44, by + 52)], fill=brass)
    d.line([bcx - 46, by + 56, bcx + 46, by + 56], fill=brass, width=4)
    d.ellipse([bcx - 6, by + 54, bcx + 6, by + 66], fill=brass)
    panel_frame(d, x, y, w, h)


def panel_voyager(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(8, 12, 30))
    rng = random.Random(20261118)
    for _ in range(80):
        sx = x + rng.random() * w
        sy = y + rng.random() * h
        r = rng.choice([1, 1, 2])
        d.ellipse([sx, sy, sx + r, sy + r], fill=(235, 238, 250))
    ex, ey = x + w * 0.90, y + h * 0.26       # Earth
    d.ellipse([ex - 8, ey - 8, ex + 8, ey + 8], fill=(70, 120, 220))
    d.ellipse([ex - 3, ey - 4, ex + 2, ey + 1], fill=(90, 190, 110))
    px, py = x + w * 0.30, y + h * 0.52       # probe
    d.ellipse([px - 34, py - 26, px + 34, py + 26], outline=(240, 240, 240),
              width=3)
    d.ellipse([px - 12, py - 9, px + 12, py + 9], outline=(200, 200, 200),
              width=2)
    d.line([px, py, px + 26, py - 20], fill=(240, 240, 240), width=2)
    d.rectangle([px - 8, py + 20, px + 10, py + 32], fill=(200, 200, 205))
    d.line([px - 4, py + 30, px - 30, py + 40], fill=(200, 200, 205), width=3)
    d.rectangle([px - 40, py + 37, px - 26, py + 45], fill=(170, 170, 175))
    d.line([px + 8, py + 26, px + 38, py + 38], fill=(170, 170, 175), width=2)
    import math                               # dotted signal line to Earth
    x1, y1, x2, y2 = px + 30, py - 18, ex - 10, ey + 4
    dist = math.hypot(x2 - x1, y2 - y1)
    steps = int(dist // 11)
    for i in range(steps + 1):
        t = i / max(steps, 1)
        dx, dy = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
        d.ellipse([dx - 1.6, dy - 1.6, dx + 1.6, dy + 1.6], fill=(160, 200, 255))
    d.text((x + w * 0.05, y + h * 0.07), "1 LIGHT-DAY",
           font=F(SANS_B, 11), fill=(235, 238, 250))
    panel_frame(d, x, y, w, h)


def panel_florida(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h * 0.62], fill=(176, 192, 204))
    for gx in range(6, int(w), 17):           # rain streaks
        for gy in range(4, int(h * 0.55), 15):
            d.line([x + gx, y + gy, x + gx - 4, y + gy + 8],
                   fill=(130, 150, 168), width=2)
    for hx, hw in [(0.06, 0.20), (0.72, 0.22)]:   # houses
        bx, by = x + w * hx, y + h * 0.40
        d.rectangle([bx, by, bx + w * hw, by + h * 0.24], fill=(120, 116, 108))
        d.polygon([(bx - 4, by), (bx + w * hw / 2, by - h * 0.13),
                   (bx + w * hw + 4, by)], fill=(90, 86, 80))
    green = (44, 92, 58)
    for px_, ps in [(0.33, 1.15), (0.58, 0.95)]:    # palms
        bx, by = x + w * px_, y + h * 0.63
        pts = [(bx + (i * i) * 0.55 * ps, by - i * 7.6 * ps) for i in range(7)]
        d.line(pts, fill=(96, 76, 52), width=4)
        tx, ty = pts[-1]
        for a in (-70, -35, 0, 35, 70):
            import math
            exx = tx + 34 * ps * math.sin(math.radians(a))
            eyy = ty + 17 * ps * math.cos(math.radians(a)) - 5
            d.line([tx, ty, (tx + exx) / 2, ty - 12 * ps, exx, eyy], fill=green,
                   width=3)
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(86, 130, 166))
    for i in range(9):                        # ripples
        ry = y + h * (0.68 + i * 0.035)
        d.line([x + (i % 3) * 23, ry, x + w * 0.30 + (i % 3) * 23, ry],
               fill=(150, 185, 205), width=2)
    bx, by = x + w * 0.40, y + h * 0.70       # rescue boat
    d.polygon([(bx, by), (bx + w * 0.22, by), (bx + w * 0.19, by + h * 0.11),
               (bx + w * 0.03, by + h * 0.11)], fill=(206, 96, 44))
    d.rectangle([bx + w * 0.07, by - h * 0.10, bx + w * 0.15, by],
                fill=(245, 245, 245))
    gx = x + w * 0.86                          # rain gauge
    d.rectangle([gx, y + h * 0.14, gx + w * 0.045, y + h * 0.60],
                outline=INK, width=2)
    d.rectangle([gx + 2, y + h * 0.22, gx + w * 0.045 - 2, y + h * 0.60 - 2],
                fill=(70, 120, 200))
    d.text((gx - w * 0.115, y + h * 0.30), "15 in", font=F(SANS_B, 13),
           fill=INK)
    panel_frame(d, x, y, w, h)


PANEL_ART = [panel_shenzhen, panel_hormuz, panel_gaza,
             panel_ipo, panel_voyager, panel_florida]


def panels(d):
    d.text((X(MX), X(304)), "SIX STORIES IN PICTURES", font=F(SANS_B, 12),
           fill=INK)
    d.line([X(MX), X(320), X(RIGHT), X(320)], fill=INK, width=S)
    pw, ph = 309, 44
    xs = [MX, 358, 681]
    f_cap = F(SANS_M, 10)
    for i, art in enumerate(PANEL_ART):
        px = xs[i % 3]
        py = 326 if i < 3 else 406
        art(d, X(px), X(py), X(pw), X(ph))
        lines = wrap_runs(d, [(CAPTIONS[i], f_cap, INK)], X(pw - 6))
        for j, line in enumerate(lines[:2]):
            lw = sum(d.textlength(w, font=fo) for w, fo, _ in line)
            lw += sum(d.textlength(" ", font=line[k + 1][1])
                      for k in range(len(line) - 1))
            draw_words(d, X(px) + (X(pw) - lw) / 2, X(py + 48 + j * 12), line)


# ----------------------------------------------------------------- story list

LIST_TOP = 522
LIST_BOT = 1003
LIST_GAP = 1.8


def story_runs(n, story, fb, fs, fi):
    time, headline, summary, source = story
    runs = [(f"{n}.", fb, ACCENT)]
    if time:
        runs.append((time, fb, INK))
    runs.append((headline, fb, INK))
    runs.append(("— " + summary, fs, INK))
    runs.append((f"({source})", fi, GRAY))
    return runs


def layout_list(d, size):
    fb = F(SANSC_B, size)
    fs = F(SERIFC, size)
    fi = F(SERIFC_I, size)
    lead = size * 1.15
    gap = LIST_GAP
    col_w = (CW - 26) / 2
    items = []
    for n, story in enumerate(STORIES, 1):
        lines = wrap_runs(d, story_runs(n, story, fb, fs, fi), X(col_w - 4))
        items.append((lines, len(lines) * lead + gap))
    best = None
    for split in range(1, len(items)):
        h1 = sum(h for _, h in items[:split])
        h2 = sum(h for _, h in items[split:])
        score = max(h1, h2)
        if best is None or score < best[0]:
            best = (score, split, h1, h2)
    _, split, h1, h2 = best
    cols = [items[:split], items[split:]]
    return cols, [h1, h2], lead


def story_list(d):
    d.text((X(MX), X(490)), "50 SOURCED STORIES", font=F(SERIF_B, 20), fill=INK)
    note = "timed stories first (UTC), then the rest of the day"
    nw = d.textlength(note, font=F(SERIFC_I, 11))
    d.text((X(RIGHT) - nw, X(497)), note, font=F(SERIFC_I, 11), fill=GRAY)
    d.rectangle([X(MX), X(516), X(RIGHT), X(519)], fill=INK)
    avail = LIST_BOT - LIST_TOP
    size = 10.6
    while size > 10.1:
        cols, heights, lead = layout_list(d, size)
        if max(heights) <= avail:
            break
        size -= 0.1
    col_x = [MX, 525]
    col_w = (CW - 26) / 2
    d.line([X(512), X(LIST_TOP + 4), X(512), X(LIST_BOT - 2)], fill=FAINT,
           width=S)
    for ci, col in enumerate(cols):
        y = LIST_TOP
        for lines, h in col:
            for line in lines:
                draw_words(d, X(col_x[ci]), X(y), line)
                y += lead
            y += LIST_GAP
    return size


# ----------------------------------------------------------------------- main

def build():
    img = Image.new("RGB", (SIZE * S, SIZE * S), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([X(14), X(14), X(SIZE - 14), X(SIZE - 14)], outline=INK,
                width=2)
    d.rectangle([X(19), X(19), X(SIZE - 19), X(SIZE - 19)], outline=INK,
                width=1)
    masthead(d)
    date_check(d)
    timeline(d)
    panels(d)
    size = story_list(d)
    img = img.resize((SIZE, SIZE), Image.LANCZOS)
    img.save(OUT, optimize=True)
    print(f"list size {size:.1f}px; wrote {OUT} "
          f"({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()
