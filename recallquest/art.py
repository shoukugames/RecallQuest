"""Hand-coded cartoon pictures for every character, animal, object and place.

Each picture is drawn on a 300x300 canvas with thick outlines, then smooth-scaled
down, which gives clean anti-aliased edges. Results are cached per size and colour.
"""
import math

import pygame

CANVAS = 300
OUT = (52, 44, 66)
W = 7  # outline width on the canvas

COLORS = {
    "red": (234, 72, 82),
    "blue": (64, 140, 255),
    "green": (86, 190, 120),
    "yellow": (255, 210, 80),
    "purple": (160, 100, 230),
    "pink": (255, 140, 196),
    "orange": (255, 150, 70),
}

WHITE = (255, 255, 255)
CREAM = (255, 240, 214)
SKIN = (255, 214, 180)
PINK = (255, 160, 180)
BLACK = (40, 34, 50)
GOLD = (255, 200, 60)


def shade(col, f):
    """f < 1 darkens, f > 1 lightens."""
    if f < 1:
        return tuple(max(0, int(c * f)) for c in col[:3])
    return tuple(min(255, int(c + (255 - c) * (f - 1))) for c in col[:3])


# ---------------------------------------------------------------- primitives
def oval(s, col, cx, cy, rx, ry, w=W):
    if w:
        pygame.draw.ellipse(s, OUT, (cx - rx - w, cy - ry - w, 2 * (rx + w), 2 * (ry + w)))
    pygame.draw.ellipse(s, col, (cx - rx, cy - ry, 2 * rx, 2 * ry))


def circ(s, col, cx, cy, r, w=W):
    if w:
        pygame.draw.circle(s, OUT, (cx, cy), r + w)
    pygame.draw.circle(s, col, (cx, cy), r)


def poly(s, col, pts, w=W):
    pygame.draw.polygon(s, col, pts)
    if w:
        pygame.draw.lines(s, OUT, True, pts, w)
        for p in pts:
            pygame.draw.circle(s, OUT, p, w // 2)


def rrect(s, col, rect, r, w=W):
    rect = pygame.Rect(rect)
    if w:
        pygame.draw.rect(s, OUT, rect.inflate(2 * w, 2 * w), border_radius=r + w)
    pygame.draw.rect(s, col, rect, border_radius=r)


def bez(p0, p1, p2, n=40):
    pts = []
    for i in range(n + 1):
        t = i / n
        a, b, c = (1 - t) ** 2, 2 * (1 - t) * t, t * t
        pts.append((a * p0[0] + b * p1[0] + c * p2[0], a * p0[1] + b * p1[1] + c * p2[1]))
    return pts


def stroke(s, pts, width, col=OUT, outline=True):
    """A thick round-capped line through pts, optionally with an outline."""
    if outline and col != OUT:
        r = width / 2 + W
        for p in pts:
            pygame.draw.circle(s, OUT, p, r)
    r = width / 2
    for p in pts:
        pygame.draw.circle(s, col, p, r)


def line(s, a, b, width=W, col=OUT):
    pygame.draw.line(s, col, a, b, int(width))
    pygame.draw.circle(s, col, a, width / 2)
    pygame.draw.circle(s, col, b, width / 2)


def eye(s, x, y, r=16, look=(0, 2)):
    circ(s, WHITE, x, y, r, 5)
    pygame.draw.circle(s, BLACK, (x + look[0], y + look[1]), int(r * 0.62))
    pygame.draw.circle(s, WHITE, (x + look[0] - r * 0.25, y + look[1] - r * 0.3), max(2, r * 0.22))


def dot_eye(s, x, y, r=9):
    pygame.draw.circle(s, BLACK, (x, y), r)
    pygame.draw.circle(s, WHITE, (x - r * 0.35, y - r * 0.35), max(2, r * 0.32))


def smile(s, cx, cy, wdt=26, h=14, width=6):
    stroke(s, bez((cx - wdt, cy), (cx, cy + h * 2), (cx + wdt, cy)), width, OUT, False)


def cheeks(s, cx, cy, dx, r=12, col=(255, 130, 150)):
    blush = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(blush, (*col, 120), (0, r // 2, r * 2, r))
    s.blit(blush, (cx - dx - r, cy - r))
    s.blit(blush, (cx + dx - r, cy - r))


def shine(s, cx, cy, rx, ry, alpha=110):
    hl = pygame.Surface((rx * 2, ry * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(hl, (255, 255, 255, alpha), hl.get_rect())
    s.blit(hl, (cx - rx, cy - ry))


def star_pts(cx, cy, r1, r2, n=5, rot=-math.pi / 2):
    pts = []
    for i in range(n * 2):
        r = r1 if i % 2 == 0 else r2
        a = rot + i * math.pi / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def tri(s, col, a, b, c, w=W):
    poly(s, col, [a, b, c], w)


# ------------------------------------------------------------------ animals
def cat(s, c=None):
    col = (246, 166, 90)
    stroke(s, bez((205, 245), (285, 230), (255, 160)), 20, col)
    oval(s, col, 150, 230, 62, 50)
    tri(s, col, (82, 112), (92, 30), (140, 70))
    tri(s, col, (218, 112), (208, 30), (160, 70))
    tri(s, PINK, (96, 90), (100, 52), (124, 74), 0)
    tri(s, PINK, (204, 90), (200, 52), (176, 74), 0)
    oval(s, col, 150, 128, 84, 72)
    for dx in (-14, 0, 14):
        line(s, (150 + dx, 60), (150 + dx * 1.2, 80), 6)
    oval(s, CREAM, 150, 152, 38, 26, 0)
    eye(s, 118, 120, 15)
    eye(s, 182, 120, 15)
    tri(s, PINK, (140, 140), (160, 140), (150, 152), 4)
    stroke(s, bez((150, 152), (140, 168), (130, 160)), 5, OUT, False)
    stroke(s, bez((150, 152), (160, 168), (170, 160)), 5, OUT, False)
    for sy in (-6, 8):
        line(s, (92, 148 + sy), (50, 140 + sy * 2), 4)
        line(s, (208, 148 + sy), (250, 140 + sy * 2), 4)
    cheeks(s, 150, 150, 52)
    oval(s, CREAM, 125, 272, 18, 10)
    oval(s, CREAM, 175, 272, 18, 10)


def dog(s, c=None):
    col = (214, 160, 100)
    dark = (140, 90, 56)
    oval(s, col, 150, 232, 60, 48)
    oval(s, col, 150, 125, 80, 74)
    oval(s, dark, 76, 125, 24, 50)
    oval(s, dark, 224, 125, 24, 50)
    oval(s, dark, 182, 100, 22, 20, 0)
    oval(s, CREAM, 150, 160, 44, 32)
    eye(s, 120, 112, 14)
    eye(s, 180, 112, 14)
    oval(s, BLACK, 150, 146, 16, 11, 0)
    shine(s, 145, 142, 6, 3)
    oval(s, (240, 100, 120), 150, 182, 12, 14, 5)
    smile(s, 150, 162, 22, 6, 5)
    cheeks(s, 150, 150, 58)
    oval(s, CREAM, 122, 275, 18, 10)
    oval(s, CREAM, 178, 275, 18, 10)


def frog(s, c=None):
    col = (110, 200, 90)
    oval(s, col, 150, 230, 70, 48)
    oval(s, (200, 240, 160), 150, 238, 42, 30, 0)
    circ(s, col, 100, 82, 34)
    circ(s, col, 200, 82, 34)
    oval(s, col, 150, 140, 98, 64)
    pygame.draw.ellipse(s, col, (70, 90, 160, 60))
    eye(s, 100, 80, 22)
    eye(s, 200, 80, 22)
    stroke(s, bez((92, 150), (150, 205), (208, 150)), 7, OUT, False)
    cheeks(s, 150, 150, 74, 14)
    for x in (95, 205):
        oval(s, col, x, 276, 28, 12)


def penguin(s, c=None):
    navy = (54, 66, 100)
    oval(s, (255, 160, 60), 120, 280, 24, 10)
    oval(s, (255, 160, 60), 180, 280, 24, 10)
    oval(s, navy, 68, 200, 18, 44)
    oval(s, navy, 232, 200, 18, 44)
    oval(s, navy, 150, 160, 92, 118)
    oval(s, WHITE, 150, 190, 64, 82, 0)
    pygame.draw.ellipse(s, WHITE, (88, 82, 64, 70))
    pygame.draw.ellipse(s, WHITE, (148, 82, 64, 70))
    eye(s, 122, 112, 14)
    eye(s, 178, 112, 14)
    tri(s, (255, 170, 60), (130, 136), (170, 136), (150, 160), 5)
    cheeks(s, 150, 145, 50)


def rabbit(s, c=None):
    col = (236, 236, 244)
    oval(s, col, 112, 60, 22, 58)
    oval(s, col, 188, 60, 22, 58)
    oval(s, PINK, 112, 64, 10, 42, 0)
    oval(s, PINK, 188, 64, 10, 42, 0)
    oval(s, col, 150, 236, 60, 46)
    oval(s, col, 150, 150, 80, 68)
    eye(s, 120, 140, 14)
    eye(s, 180, 140, 14)
    tri(s, PINK, (140, 162), (160, 162), (150, 172), 4)
    rrect(s, WHITE, (140, 182, 20, 18), 3, 4)
    line(s, (150, 182), (150, 198), 3)
    stroke(s, bez((150, 172), (138, 186), (128, 178)), 5, OUT, False)
    stroke(s, bez((150, 172), (162, 186), (172, 178)), 5, OUT, False)
    cheeks(s, 150, 168, 52)
    oval(s, col, 124, 278, 18, 10)
    oval(s, col, 176, 278, 18, 10)


def bear(s, c=None):
    col = (150, 100, 66)
    oval(s, col, 150, 234, 66, 50)
    circ(s, col, 88, 74, 28)
    circ(s, col, 212, 74, 28)
    circ(s, (230, 170, 140), 88, 74, 14, 0)
    circ(s, (230, 170, 140), 212, 74, 14, 0)
    oval(s, col, 150, 132, 86, 76)
    oval(s, (230, 196, 150), 150, 162, 40, 30)
    eye(s, 118, 120, 13)
    eye(s, 182, 120, 13)
    oval(s, BLACK, 150, 150, 15, 10, 0)
    shine(s, 145, 147, 5, 3)
    smile(s, 150, 166, 16, 6, 5)
    cheeks(s, 150, 150, 58)
    oval(s, (230, 196, 150), 150, 240, 36, 28, 0)


def pig(s, c=None):
    col = (255, 178, 196)
    dark = (235, 120, 150)
    oval(s, col, 150, 236, 64, 46)
    tri(s, col, (80, 100), (86, 48), (128, 74))
    tri(s, col, (220, 100), (214, 48), (172, 74))
    oval(s, col, 150, 138, 90, 76)
    eye(s, 116, 118, 13)
    eye(s, 184, 118, 13)
    oval(s, dark, 150, 162, 34, 24)
    oval(s, (180, 70, 100), 138, 162, 6, 9, 0)
    oval(s, (180, 70, 100), 162, 162, 6, 9, 0)
    smile(s, 150, 190, 14, 4, 5)
    cheeks(s, 150, 160, 64)
    stroke(s, bez((212, 240), (246, 222), (226, 210)), 6, OUT, False)


def duck(s, c=None):
    col = (255, 214, 72)
    oval(s, col, 150, 230, 74, 52)
    oval(s, col, 150, 126, 76, 72)
    stroke(s, bez((150, 56), (138, 30), (160, 28)), 8, col)
    eye(s, 122, 112, 14)
    eye(s, 178, 112, 14)
    oval(s, (255, 150, 50), 150, 158, 46, 18)
    line(s, (112, 158), (188, 158), 4)
    cheeks(s, 150, 140, 56)
    oval(s, shade(col, 0.85), 92, 228, 20, 34)
    oval(s, (255, 150, 50), 124, 282, 22, 9)
    oval(s, (255, 150, 50), 176, 282, 22, 9)


def owl(s, c=None):
    col = (150, 110, 160)
    belly = (230, 210, 230)
    tri(s, col, (70, 90), (78, 26), (120, 70))
    tri(s, col, (230, 90), (222, 26), (180, 70))
    oval(s, col, 150, 170, 92, 112)
    oval(s, belly, 150, 214, 54, 58, 0)
    for row, y in enumerate((196, 220, 244)):
        for k in range(3 - row % 2):
            x = 150 + (k - (2 - row % 2) / 2) * 26
            stroke(s, bez((x - 9, y), (x, y + 9), (x + 9, y)), 4, shade(col, 0.8), False)
    oval(s, col, 70, 190, 22, 56)
    oval(s, col, 230, 190, 22, 56)
    circ(s, (255, 236, 200), 115, 112, 32)
    circ(s, (255, 236, 200), 185, 112, 32)
    eye(s, 115, 112, 20)
    eye(s, 185, 112, 20)
    tri(s, (255, 170, 50), (138, 140), (162, 140), (150, 166), 5)
    oval(s, (255, 170, 50), 125, 282, 16, 8)
    oval(s, (255, 170, 50), 175, 282, 16, 8)


def fox(s, c=None):
    col = (240, 112, 50)
    stroke(s, bez((200, 250), (290, 240), (270, 160)), 34, col)
    circ(s, WHITE, 270, 160, 17, 0)
    oval(s, col, 150, 236, 56, 46)
    oval(s, WHITE, 150, 246, 30, 30, 0)
    tri(s, col, (70, 120), (72, 34), (128, 82))
    tri(s, col, (230, 120), (228, 34), (172, 82))
    tri(s, BLACK, (78, 72), (74, 40), (100, 66), 0)
    tri(s, BLACK, (222, 72), (226, 40), (200, 66), 0)
    poly(s, col, [(62, 120), (100, 78), (200, 78), (238, 120), (190, 180), (150, 196), (110, 180)])
    poly(s, WHITE, [(70, 126), (128, 140), (150, 194), (112, 178)], 0)
    poly(s, WHITE, [(230, 126), (172, 140), (150, 194), (188, 178)], 0)
    eye(s, 120, 124, 13)
    eye(s, 180, 124, 13)
    oval(s, BLACK, 150, 182, 11, 8, 0)
    cheeks(s, 150, 152, 50)


def elephant(s, c=None):
    col = (160, 176, 206)
    oval(s, col, 64, 132, 52, 64)
    oval(s, col, 236, 132, 52, 64)
    oval(s, PINK, 64, 136, 34, 44, 0)
    oval(s, PINK, 236, 136, 34, 44, 0)
    oval(s, col, 150, 238, 62, 44)
    oval(s, col, 150, 130, 76, 72)
    stroke(s, bez((150, 150), (148, 230), (196, 224)), 32, col)
    for y in (180, 196, 212):
        line(s, (138, y), (160, y + 2), 3)
    tri(s, WHITE, (112, 170), (126, 172), (110, 196), 4)
    tri(s, WHITE, (188, 170), (174, 172), (190, 196), 4)
    eye(s, 120, 118, 13)
    eye(s, 180, 118, 13)
    cheeks(s, 150, 150, 52)


def monkey(s, c=None):
    col = (150, 96, 60)
    face = (246, 210, 170)
    stroke(s, bez((200, 250), (280, 260), (262, 190)), 14, col)
    oval(s, col, 150, 238, 58, 46)
    circ(s, col, 66, 128, 30)
    circ(s, col, 234, 128, 30)
    circ(s, face, 66, 128, 16, 0)
    circ(s, face, 234, 128, 16, 0)
    oval(s, col, 150, 128, 80, 76)
    pygame.draw.circle(s, face, (124, 116), 32)
    pygame.draw.circle(s, face, (176, 116), 32)
    pygame.draw.ellipse(s, face, (96, 120, 108, 76))
    eye(s, 126, 116, 13)
    eye(s, 174, 116, 13)
    oval(s, BLACK, 142, 150, 4, 3, 0)
    oval(s, BLACK, 158, 150, 4, 3, 0)
    smile(s, 150, 166, 26, 10, 5)
    cheeks(s, 150, 160, 50)


def turtle(s, c=None):
    skin = (130, 200, 120)
    shell = (90, 150, 70)
    oval(s, skin, 76, 254, 24, 16)
    oval(s, skin, 224, 254, 24, 16)
    oval(s, skin, 50, 150, 40, 36)
    oval(s, shell, 160, 196, 104, 72)
    pygame.draw.rect(s, OUT, (52, 220, 216, 10))
    pygame.draw.rect(s, (200, 180, 100), (56, 222, 208, 7))
    for cx, cy in ((160, 168), (112, 192), (208, 192), (136, 148), (184, 148)):
        poly(s, shade(shell, 1.25), [(cx + 18 * math.cos(a * math.pi / 3), cy + 15 * math.sin(a * math.pi / 3))
                                     for a in range(6)], 4)
    dot_eye(s, 40, 140, 8)
    stroke(s, bez((24, 160), (36, 172), (52, 162)), 4, OUT, False)
    cheeks(s, 48, 158, 0, 9)


def octopus(s, c=None):
    col = (170, 110, 230)
    for i in range(6):
        x = 70 + i * 32
        side = -1 if i % 2 else 1
        pts = bez((x, 180), (x + side * 30, 236), (x - side * 8, 280))
        stroke(s, pts, 22, col)
    oval(s, col, 150, 136, 98, 92)
    shine(s, 116, 84, 24, 14)
    for i in range(6):
        x = 70 + i * 32
        side = -1 if i % 2 else 1
        for t in (0.55, 0.8):
            p = bez((x, 180), (x + side * 30, 236), (x - side * 8, 280))[int(t * 40)]
            circ(s, (240, 200, 250), int(p[0]), int(p[1]), 4, 0)
    eye(s, 120, 140, 18)
    eye(s, 180, 140, 18)
    smile(s, 150, 176, 16, 6, 5)
    cheeks(s, 150, 168, 60)


def lion(s, c=None):
    mane = (210, 120, 40)
    face = (255, 200, 90)
    pts = []
    for i in range(28):
        a = i * math.pi / 14
        r = 118 if i % 2 == 0 else 96
        pts.append((150 + r * math.cos(a), 140 + r * math.sin(a) * 0.95))
    poly(s, mane, pts)
    circ(s, face, 96, 74, 18)
    circ(s, face, 204, 74, 18)
    oval(s, face, 150, 146, 74, 70)
    oval(s, CREAM, 150, 176, 34, 24, 0)
    eye(s, 122, 130, 13)
    eye(s, 178, 130, 13)
    tri(s, (150, 80, 60), (138, 160), (162, 160), (150, 172), 4)
    stroke(s, bez((150, 172), (140, 188), (130, 182)), 5, OUT, False)
    stroke(s, bez((150, 172), (160, 188), (170, 182)), 5, OUT, False)
    cheeks(s, 150, 166, 54)


def mouse(s, c=None):
    col = (180, 180, 196)
    stroke(s, bez((200, 250), (280, 270), (270, 200)), 8, (255, 170, 190))
    circ(s, col, 78, 80, 52)
    circ(s, col, 222, 80, 52)
    circ(s, PINK, 78, 80, 32, 0)
    circ(s, PINK, 222, 80, 32, 0)
    oval(s, col, 150, 240, 54, 42)
    oval(s, col, 150, 150, 72, 66)
    eye(s, 124, 140, 13)
    eye(s, 176, 140, 13)
    circ(s, (255, 120, 150), 150, 172, 9, 4)
    for sy in (-5, 7):
        line(s, (110, 176 + sy), (66, 170 + sy * 2), 3)
        line(s, (190, 176 + sy), (234, 170 + sy * 2), 3)
    cheeks(s, 150, 168, 46)


# --------------------------------------------------------------- characters
def robot(s, c=None):
    body = (170, 186, 210)
    line(s, (150, 60), (150, 32), 6)
    circ(s, (240, 80, 90), 150, 28, 12)
    line(s, (68, 200), (44, 248), 14)
    line(s, (232, 200), (256, 248), 14)
    circ(s, body, 44, 252, 14)
    circ(s, body, 256, 252, 14)
    rrect(s, body, (90, 186, 120, 94), 16)
    rrect(s, (70, 80, 110), (110, 204, 80, 40), 8, 0)
    for i, colr in enumerate(((255, 90, 90), (255, 210, 80), (90, 220, 140))):
        circ(s, colr, 128 + i * 22, 224, 7, 0)
    rrect(s, body, (66, 60, 168, 124), 26)
    rrect(s, (40, 56, 84), (86, 78, 128, 82), 18, 4)
    for x in (122, 178):
        circ(s, (110, 240, 255), x, 112, 14, 0)
        circ(s, WHITE, x - 4, 108, 4, 0)
    stroke(s, bez((126, 138), (150, 152), (174, 138)), 5, (110, 240, 255), False)
    rrect(s, shade(body, 0.85), (54, 102, 14, 40), 5)
    rrect(s, shade(body, 0.85), (232, 102, 14, 40), 5)


def alien(s, c=None):
    col = (140, 230, 120)
    line(s, (118, 60), (96, 22), 5)
    line(s, (182, 60), (204, 22), 5)
    circ(s, (255, 120, 200), 96, 22, 11)
    circ(s, (255, 120, 200), 204, 22, 11)
    oval(s, (120, 90, 200), 150, 248, 50, 38)
    pygame.draw.circle(s, GOLD, (150, 240), 10)
    oval(s, col, 150, 128, 96, 84)
    for x in (108, 192):
        oval(s, BLACK, x, 124, 26, 32, 0)
        pygame.draw.ellipse(s, WHITE, (x - 14, 104, 12, 16))
    oval(s, BLACK, 150, 96, 12, 14, 0)
    pygame.draw.circle(s, WHITE, (146, 92), 4)
    smile(s, 150, 172, 18, 6, 5)
    cheeks(s, 150, 168, 62, 13)


def ghost(s, c=None):
    col = (240, 244, 255)
    pts = [(62, 150)]
    pts += [(62 + 176 * i / 40, 150) for i in range(1)]
    top = [(150 + 88 * math.cos(math.pi + math.pi * i / 30), 150 + 100 * math.sin(math.pi + math.pi * i / 30))
           for i in range(31)]
    bottom = []
    for i in range(41):
        x = 238 - 176 * i / 40
        bottom.append((x, 262 + 14 * math.sin(i / 40 * math.pi * 4)))
    poly(s, col, top + [(238, 262)] + bottom + [(62, 262)])
    oval(s, col, 50, 170, 18, 24)
    oval(s, col, 250, 160, 18, 24)
    shine(s, 116, 90, 20, 12, 160)
    oval(s, BLACK, 122, 140, 13, 18, 0)
    oval(s, BLACK, 178, 140, 13, 18, 0)
    pygame.draw.circle(s, WHITE, (118, 134), 5)
    pygame.draw.circle(s, WHITE, (174, 134), 5)
    oval(s, BLACK, 150, 188, 12, 16, 0)
    cheeks(s, 150, 170, 52, 14, (160, 180, 255))


def dinosaur(s, c=None):
    col = (90, 196, 170)
    for i in range(5):
        x = 58 + i * 28
        y = 120 - i * 6 + (i * i)
        tri(s, (255, 170, 80), (x - 14, y + 30), (x, y), (x + 14, y + 30))
    poly(s, col, [(20, 250), (80, 200), (100, 120), (200, 120), (214, 280), (100, 286)])
    oval(s, col, 140, 220, 74, 64)
    oval(s, (200, 240, 200), 160, 236, 40, 42, 0)
    oval(s, col, 196, 96, 82, 58)
    oval(s, col, 116, 280, 26, 12)
    oval(s, col, 184, 280, 26, 12)
    line(s, (206, 196), (230, 206), 12)
    pygame.draw.line(s, col, (206, 196), (230, 206), 6)
    eye(s, 210, 80, 15)
    smile(s, 236, 118, 30, 6, 5)
    for x in (230, 250):
        tri(s, WHITE, (x, 122), (x + 10, 122), (x + 5, 132), 3)
    circ(s, BLACK, 262, 88, 3, 0)
    cheeks(s, 220, 104, 0, 12)


def snowman(s, c=None):
    snow = (250, 252, 255)
    line(s, (78, 180), (30, 140), 7)
    line(s, (50, 158), (40, 134), 5)
    line(s, (222, 180), (270, 140), 7)
    line(s, (250, 158), (262, 134), 5)
    circ(s, snow, 150, 222, 70)
    circ(s, snow, 150, 120, 52)
    for y in (196, 226, 256):
        circ(s, BLACK, 150, y, 6, 0)
    rrect(s, (230, 70, 80), (92, 156, 116, 22), 10)
    rrect(s, (230, 70, 80), (170, 166, 24, 56), 8)
    rrect(s, BLACK, (106, 70, 88, 12), 4, 4)
    rrect(s, BLACK, (118, 18, 64, 56), 6, 4)
    pygame.draw.rect(s, (230, 70, 80), (122, 56, 56, 10))
    dot_eye(s, 132, 116, 7)
    dot_eye(s, 168, 116, 7)
    tri(s, (255, 140, 40), (148, 126), (148, 140), (196, 136), 4)
    for i in range(5):
        circ(s, BLACK, 128 + i * 11, 150 - 6 * math.sin(i / 4 * math.pi), 3, 0)


def wizard(s, c=None):
    robe = (90, 80, 200)
    oval(s, robe, 150, 262, 80, 40)
    tri(s, robe, (150, 4), (62, 108), (238, 108))
    for (x, y, r) in ((140, 50, 10), (172, 82, 8), (122, 88, 7)):
        poly(s, GOLD, star_pts(x, y, r, r * 0.45), 0)
    rrect(s, robe, (48, 98, 204, 24), 12)
    oval(s, SKIN, 150, 150, 54, 44)
    poly(s, WHITE, [(98, 160), (202, 160), (196, 210), (150, 262), (104, 210)])
    oval(s, WHITE, 132, 166, 24, 10, 0)
    oval(s, WHITE, 168, 166, 24, 10, 0)
    dot_eye(s, 130, 142, 7)
    dot_eye(s, 170, 142, 7)
    stroke(s, bez((116, 128), (130, 120), (142, 128)), 6, WHITE, False)
    stroke(s, bez((158, 128), (170, 120), (184, 128)), 6, WHITE, False)
    circ(s, (255, 170, 150), 150, 156, 10, 4)
    line(s, (250, 280), (264, 130), 7, (140, 90, 50))
    poly(s, (120, 230, 255), star_pts(264, 124, 18, 8), 4)


def pirate(s, c=None):
    shirt = (240, 240, 250)
    rrect(s, shirt, (76, 206, 148, 90), 30)
    for y in (226, 254, 282):
        pygame.draw.rect(s, (230, 70, 80), (82, y, 136, 12))
    oval(s, SKIN, 150, 140, 68, 66)
    poly(s, (80, 56, 40), [(92, 150), (208, 150), (190, 206), (150, 218), (110, 206)])
    oval(s, SKIN, 150, 176, 30, 14, 0)
    smile(s, 150, 176, 18, 6, 5)
    poly(s, (40, 36, 50), [(52, 104), (150, 30), (248, 104), (210, 96), (150, 86), (90, 96)])
    rrect(s, (40, 36, 50), (78, 82, 144, 22), 10)
    circ(s, WHITE, 150, 64, 10, 0)
    line(s, (140, 74), (160, 54), 3)
    line(s, (140, 54), (160, 74), 3)
    line(s, (88, 112), (208, 152), 5)
    oval(s, BLACK, 178, 138, 18, 15, 0)
    dot_eye(s, 124, 134, 8)
    circ(s, (255, 190, 160), 150, 156, 9, 4)
    circ(s, GOLD, 86, 162, 8, 4)


# -------------------------------------------------------------------- foods
def banana(s, c=None):
    col = (255, 218, 70)
    outer = [(150 + 120 * math.cos(a), 40 + 160 * math.sin(a)) for a in
             [math.pi * (0.1 + 0.8 * i / 30) for i in range(31)]]
    inner = [(150 + 100 * math.cos(a), 30 + 120 * math.sin(a)) for a in
             [math.pi * (0.9 - 0.8 * i / 30) for i in range(31)]]
    pts = [(x, y + 40) for x, y in outer + inner]
    poly(s, col, pts)
    stroke(s, [(x, y + 30) for x, y in outer[6:25]], 6, shade(col, 0.88), False)
    circ(s, (120, 90, 40), int(pts[0][0]), int(pts[0][1]) - 4, 8, 4)
    rrect(s, (140, 110, 50), (int(pts[30][0]) - 14, int(pts[30][1]) - 26, 18, 30), 4, 5)


def pizza(s, c=None):
    tri(s, (255, 200, 90), (60, 70), (240, 70), (150, 270))
    poly(s, (255, 230, 120), [(76, 90), (224, 90), (150, 250)], 0)
    rrect(s, (220, 150, 70), (48, 52, 204, 36), 18)
    for x, y in ((120, 120), (176, 130), (150, 180), (130, 160)):
        circ(s, (220, 70, 70), x, y, 15, 4)
    for x, y in ((160, 106), (106, 108), (184, 162)):
        circ(s, (90, 170, 80), x, y, 5, 0)


def donut(s, c=None):
    circ(s, (230, 170, 100), 150, 160, 110)
    pts = []
    for i in range(40):
        a = i * math.pi * 2 / 40
        r = 96 + 8 * math.sin(i * 1.7)
        pts.append((150 + r * math.cos(a), 154 + r * math.sin(a)))
    poly(s, (255, 140, 190), pts, 5)
    circ(s, (255, 250, 245), 150, 158, 34)
    import random
    rng = random.Random(4)
    for _ in range(26):
        a = rng.uniform(0, 6.28)
        r = rng.uniform(50, 86)
        x, y = 150 + r * math.cos(a), 154 + r * math.sin(a)
        d = rng.uniform(0, 3.14)
        colr = rng.choice([(255, 255, 255), (80, 180, 255), (255, 220, 80), (120, 220, 120)])
        line(s, (x - 7 * math.cos(d), y - 7 * math.sin(d)), (x + 7 * math.cos(d), y + 7 * math.sin(d)), 6, colr)
    shine(s, 104, 104, 22, 12)


def cupcake(s, c=None):
    poly(s, (110, 190, 240), [(70, 170), (230, 170), (206, 280), (94, 280)])
    for i in range(1, 6):
        x = 70 + i * 160 / 6
        line(s, (x, 176), (94 + i * 112 / 6, 276), 4, shade((110, 190, 240), 0.8))
    frost = (255, 200, 225)
    oval(s, frost, 150, 160, 92, 34)
    oval(s, frost, 150, 126, 70, 34)
    oval(s, frost, 150, 94, 44, 28)
    circ(s, (230, 40, 70), 156, 56, 18)
    shine(s, 150, 50, 6, 4, 180)
    stroke(s, bez((160, 40), (170, 20), (186, 18)), 4, OUT, False)


def apple(s, c=None):
    col = (230, 60, 70)
    circ(s, col, 112, 170, 80)
    circ(s, col, 188, 170, 80)
    pygame.draw.circle(s, col, (112, 170), 80)
    pygame.draw.circle(s, col, (188, 170), 80)
    pygame.draw.ellipse(s, col, (60, 120, 180, 150))
    line(s, (150, 94), (160, 40), 9, (120, 80, 40))
    poly(s, (100, 200, 90), [(162, 62), (196, 34), (230, 50), (196, 76)], 5)
    shine(s, 96, 136, 18, 30)


def carrot(s, c=None):
    for dx, ang in ((-24, -0.5), (0, 0), (24, 0.5)):
        poly(s, (100, 200, 90), [(150 + dx * 0.3, 90), (150 + dx + 70 * math.sin(ang) - 14, 20),
                                 (150 + dx + 70 * math.sin(ang) + 14, 24)], 5)
    poly(s, (255, 140, 50), [(96, 92), (204, 92), (156, 284), (144, 284)])
    pygame.draw.circle(s, OUT, (150, 92), 0)
    for y, w in ((130, 30), (170, 22), (210, 14)):
        line(s, (150 - w, y), (150 - w + 22, y + 4), 5, (210, 100, 40))
        line(s, (150 + w - 4, y + 18), (150 + w - 22, y + 22), 5, (210, 100, 40))


def cheese(s, c=None):
    col = (255, 210, 80)
    poly(s, shade(col, 0.85), [(40, 160), (260, 110), (260, 230), (40, 270)])
    poly(s, col, [(40, 160), (200, 70), (260, 110)])
    for x, y, r in ((90, 210, 16), (170, 180, 22), (220, 220, 12), (130, 248, 10)):
        circ(s, (220, 160, 40), x, y, r, 0)
    circ(s, (220, 160, 40), 196, 100, 8, 0)


def icecream(s, c=None):
    poly(s, (230, 170, 90), [(96, 150), (204, 150), (150, 290)])
    for i in range(-3, 4):
        line(s, (130 + i * 18, 156), (150 + i * 4, 260 - abs(i) * 6), 3, (190, 130, 60))
    circ(s, (140, 225, 190), 116, 138, 42)
    circ(s, (255, 170, 200), 184, 138, 42)
    circ(s, (250, 240, 220), 150, 86, 46)
    circ(s, (230, 40, 70), 160, 38, 14)
    for x, y in ((130, 76), (166, 96), (150, 110), (104, 140), (190, 128)):
        line(s, (x - 5, y), (x + 5, y + 3), 5, (110, 70, 200))


def cookie(s, c=None):
    col = (222, 170, 100)
    pts = [(150 + (108 + 6 * math.sin(i * 2.3)) * math.cos(i * math.pi / 15),
            150 + (108 + 6 * math.sin(i * 2.3)) * math.sin(i * math.pi / 15)) for i in range(30)]
    poly(s, col, pts)
    for x, y in ((110, 110), (180, 100), (150, 160), (100, 190), (200, 180), (160, 220), (124, 236), (210, 130)):
        poly(s, (110, 70, 40), [(x - 10, y), (x, y - 10), (x + 11, y - 2), (x + 6, y + 10), (x - 6, y + 9)], 0)
    shine(s, 110, 90, 26, 12, 70)


def strawberry(s, c=None):
    col = (240, 60, 80)
    pts = []
    for i in range(41):
        t = i / 40 * 2 * math.pi
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((150 + x * 6.2, 160 + y * 7.6))
    pts = [(x, 310 - y) for x, y in pts]
    poly(s, col, pts)
    for x, y in ((120, 160), (150, 150), (180, 160), (132, 196), (168, 196), (150, 234), (106, 128), (194, 128),
                 (150, 120)):
        oval(s, (255, 230, 120), x, y, 4, 6, 0)
    for i in range(5):
        a = -math.pi / 2 + (i - 2) * 0.5
        tri(s, (90, 190, 80), (150, 92), (150 + 50 * math.cos(a + 0.2) * 1.3, 92 + 30 * math.sin(a + 0.2) + 20),
            (150 + 50 * math.cos(a - 0.2) * 1.3, 92 + 30 * math.sin(a - 0.2) + 20), 4)
    line(s, (150, 92), (154, 60), 7, (90, 160, 70))


# ---------------------------------------------------------- objects (colour)
def hat(s, c=None):
    c = c or COLORS["blue"]
    oval(s, c, 150, 220, 124, 34)
    rrect(s, c, (82, 70, 136, 156), 20)
    pygame.draw.ellipse(s, c, (30, 192, 240, 56))
    pygame.draw.rect(s, c, (82, 180, 136, 30))
    pygame.draw.rect(s, OUT, (75, 168, 150, 40))
    pygame.draw.rect(s, shade(c, 0.6), (75, 175, 150, 26))
    shine(s, 108, 120, 12, 36, 90)
    poly(s, WHITE, star_pts(196, 188, 14, 6), 0)


def sock(s, c=None):
    c = c or COLORS["red"]
    pts = [(110, 40), (190, 40), (190, 190), (230, 210), (250, 250), (220, 286), (150, 286), (110, 250)]
    poly(s, c, pts)
    pygame.draw.rect(s, WHITE, (112, 44, 76, 44))
    pygame.draw.line(s, OUT, (110, 88), (190, 88), 5)
    for y in (130, 168):
        pygame.draw.rect(s, shade(c, 1.45), (113, y, 74, 16))
    poly(s, shade(c, 0.75), [(220, 286), (250, 250), (236, 230), (200, 284)], 0)
    shine(s, 132, 200, 12, 30, 70)


def umbrella(s, c=None):
    c = c or COLORS["purple"]
    line(s, (150, 120), (150, 248), 9)
    stroke(s, bez((150, 248), (152, 282), (182, 276)), 9, OUT, False)
    stroke(s, bez((182, 276), (196, 270), (194, 252)), 9, OUT, False)
    top = [(150 + 124 * math.cos(math.pi + math.pi * i / 30), 150 + 110 * math.sin(math.pi + math.pi * i / 30))
           for i in range(31)]
    scallop = []
    for k in range(4):
        x0 = 274 - k * 62
        for i in range(11):
            a = math.pi * i / 10
            scallop.append((x0 - 31 + 31 * math.cos(a), 150 - 16 * math.sin(a)))
    poly(s, c, top + scallop)
    for x in (119, 181):
        stroke(s, bez((150, 42), (x - 6, 90), (x, 136)), 4, shade(c, 0.75), False)
    shine(s, 100, 90, 16, 26, 90)
    circ(s, c, 150, 38, 8, 4)


def balloon(s, c=None):
    c = c or COLORS["red"]
    stroke(s, bez((150, 214), (120, 250), (156, 294)), 4, OUT, False)
    tri(s, c, (138, 222), (162, 222), (150, 206), 5)
    oval(s, c, 150, 120, 84, 100)
    shine(s, 118, 76, 18, 30, 150)


def kite(s, c=None):
    c = c or COLORS["green"]
    stroke(s, bez((150, 250), (110, 270), (130, 296)), 4, OUT, False)
    for x, y in ((128, 268), (122, 284)):
        tri(s, COLORS["yellow"], (x - 12, y - 8), (x - 12, y + 8), (x, y), 3)
        tri(s, COLORS["yellow"], (x + 12, y - 8), (x + 12, y + 8), (x, y), 3)
    pts = [(150, 20), (240, 120), (150, 250), (60, 120)]
    poly(s, c, pts)
    poly(s, shade(c, 1.35), [(150, 20), (240, 120), (150, 120)], 0)
    poly(s, shade(c, 0.8), [(150, 120), (150, 250), (60, 120)], 0)
    pygame.draw.lines(s, OUT, True, pts, W)
    line(s, (150, 20), (150, 250), 4)
    line(s, (60, 120), (240, 120), 4)


def book(s, c=None):
    c = c or COLORS["orange"]
    rrect(s, (250, 246, 232), (70, 60, 170, 210), 10)
    for y in range(80, 260, 12):
        pygame.draw.line(s, (220, 214, 196), (226, y), (238, y), 2)
    rrect(s, c, (54, 48, 168, 216), 12)
    pygame.draw.rect(s, shade(c, 0.7), (54, 48, 24, 216), border_top_left_radius=12, border_bottom_left_radius=12)
    rrect(s, shade(c, 1.5), (100, 90, 100, 50), 8, 4)
    line(s, (114, 108), (186, 108), 5)
    line(s, (114, 124), (168, 124), 5)
    poly(s, GOLD, star_pts(150, 200, 26, 11), 4)


def boot(s, c=None):
    c = c or COLORS["yellow"]
    poly(s, c, [(96, 40), (186, 40), (186, 196), (246, 218), (262, 260), (262, 276), (86, 276), (86, 100)])
    pygame.draw.rect(s, OUT, (82, 256, 184, 26), border_radius=6)
    pygame.draw.rect(s, shade(c, 0.6), (88, 260, 172, 16), border_radius=4)
    rrect(s, shade(c, 0.85), (88, 34, 106, 30), 8)
    shine(s, 116, 140, 10, 46, 90)


def ball(s, c=None):
    c = c or COLORS["blue"]
    circ(s, c, 150, 150, 112)
    band = bez((52, 96), (150, 190), (250, 100), 30) + bez((262, 150), (150, 250), (40, 150), 30)
    poly(s, WHITE, band, 0)
    stroke(s, bez((52, 96), (150, 190), (250, 100)), 5, OUT, False)
    stroke(s, bez((40, 150), (150, 250), (262, 150)), 5, OUT, False)
    pygame.draw.circle(s, OUT, (150, 150), 112 + W // 2, W)
    shine(s, 110, 70, 26, 14, 150)


def teapot(s, c=None):
    c = c or COLORS["pink"]
    stroke(s, bez((214, 130), (290, 130), (220, 230)), 14, c)
    stroke(s, bez((90, 190), (40, 150), (36, 104)), 22, c)
    oval(s, c, 150, 190, 96, 80)
    oval(s, shade(c, 0.85), 150, 118, 60, 16)
    circ(s, c, 150, 92, 14)
    oval(s, OUT, 150, 268, 70, 10, 0)
    for x in (110, 150, 190):
        circ(s, WHITE, x, 196, 12, 0)
    shine(s, 104, 160, 14, 26, 110)


def gift(s, c=None):
    c = c or COLORS["purple"]
    rrect(s, c, (60, 126, 180, 150), 10)
    rrect(s, shade(c, 1.2), (48, 96, 204, 44), 10)
    rib = COLORS["yellow"] if c != COLORS["yellow"] else COLORS["red"]
    pygame.draw.rect(s, rib, (136, 100, 28, 172))
    oval(s, rib, 118, 80, 30, 18)
    oval(s, rib, 182, 80, 30, 18)
    circ(s, rib, 150, 88, 14)


# --------------------------------------------------------- objects (fixed)
def crown(s, c=None):
    pts = [(56, 230), (56, 90), (104, 150), (150, 70), (196, 150), (244, 90), (244, 230)]
    poly(s, GOLD, pts)
    rrect(s, shade(GOLD, 0.85), (50, 200, 200, 44), 8)
    for x, colr in ((96, (240, 70, 90)), (150, (70, 140, 255)), (204, (90, 210, 130))):
        circ(s, colr, x, 222, 12, 4)
    for x, y in ((56, 84), (150, 62), (244, 84)):
        circ(s, WHITE, x, y, 12)
    shine(s, 100, 160, 10, 26, 120)


def key(s, c=None):
    col = GOLD
    rrect(s, col, (140, 120, 132, 30), 10)
    rrect(s, col, (230, 140, 18, 44), 4)
    rrect(s, col, (196, 140, 18, 34), 4)
    circ(s, col, 96, 135, 66)
    circ(s, (255, 250, 240), 96, 135, 26)
    shine(s, 76, 100, 14, 10, 140)


def guitar(s, c=None):
    wood = (220, 140, 70)
    rrect(s, (120, 80, 50), (138, 20, 24, 150), 6)
    rrect(s, (90, 60, 40), (128, 6, 44, 34), 10)
    circ(s, wood, 150, 236, 62)
    circ(s, wood, 150, 160, 46)
    pygame.draw.circle(s, wood, (150, 236), 62)
    pygame.draw.circle(s, wood, (150, 160), 46)
    pygame.draw.rect(s, wood, (110, 170, 80, 40))
    circ(s, (60, 40, 30), 150, 196, 20, 0)
    rrect(s, (90, 60, 40), (124, 248, 52, 14), 4, 0)
    for dx in (-6, 0, 6):
        pygame.draw.line(s, (240, 240, 240), (150 + dx, 30), (150 + dx, 250), 2)


def drum(s, c=None):
    red = (230, 70, 80)
    rrect(s, red, (50, 120, 200, 130), 16)
    for i in range(5):
        x = 60 + i * 45
        line(s, (x, 134), (x + 22, 240), 5, GOLD)
        line(s, (x + 22, 134), (x, 240), 5, GOLD) if i < 4 else None
    oval(s, (250, 246, 236), 150, 120, 104, 34)
    rrect(s, WHITE, (46, 236, 208, 20), 8)
    line(s, (70, 30), (130, 112), 10, (200, 150, 90))
    line(s, (230, 30), (170, 112), 10, (200, 150, 90))
    circ(s, (250, 240, 220), 70, 30, 12)
    circ(s, (250, 240, 220), 230, 30, 12)


def trumpet(s, c=None):
    col = GOLD
    poly(s, col, [(196, 150), (270, 84), (270, 216)])
    oval(s, shade(col, 0.85), 270, 150, 18, 66)
    rrect(s, col, (30, 136, 180, 28), 10)
    rrect(s, col, (70, 166, 110, 30), 12)
    for x in (92, 122, 152):
        rrect(s, shade(col, 0.9), (x, 100, 16, 40), 4)
        circ(s, WHITE, x + 8, 96, 10)
    rrect(s, shade(col, 0.7), (16, 132, 22, 36), 6)


def sunglasses(s, c=None):
    frame = (40, 36, 50)
    line(s, (34, 120), (64, 124), 10, frame)
    line(s, (266, 120), (236, 124), 10, frame)
    for x in (98, 202):
        rrect(s, (70, 60, 120), (x - 58, 110, 116, 84), 30, 9)
        shine(s, x - 22, 132, 18, 10, 120)
    stroke(s, bez((140, 132), (150, 116), (160, 132)), 10, frame, False)


def rocket(s, c=None):
    body = (240, 242, 250)
    red = (230, 70, 80)
    poly(s, (255, 180, 50), [(120, 236), (180, 236), (150, 296)])
    poly(s, (255, 240, 120), [(132, 236), (168, 236), (150, 274)], 0)
    poly(s, red, [(100, 170), (60, 250), (110, 236)])
    poly(s, red, [(200, 170), (240, 250), (190, 236)])
    poly(s, body, [(150, 14), (196, 90), (200, 240), (100, 240), (104, 90)])
    poly(s, red, [(150, 14), (190, 80), (110, 80)])
    circ(s, (110, 200, 255), 150, 140, 26)
    shine(s, 142, 132, 8, 6, 170)
    line(s, (150, 186), (150, 240), 5, red)


# --------------------------------------------------------------------- places
def _scene(s, sky_top, sky_bottom):
    for y in range(CANVAS):
        t = y / CANVAS
        colr = tuple(int(sky_top[i] + (sky_bottom[i] - sky_top[i]) * t) for i in range(3))
        pygame.draw.line(s, colr, (0, y), (CANVAS, y))


def beach(s, c=None):
    _scene(s, (120, 200, 255), (200, 240, 255))
    circ(s, (255, 220, 80), 230, 70, 34, 0)
    pygame.draw.rect(s, (60, 150, 230), (0, 150, 300, 80))
    for x in range(-20, 320, 40):
        pygame.draw.arc(s, WHITE, (x, 160, 40, 20), 0, math.pi, 4)
    pygame.draw.ellipse(s, (255, 226, 160), (-60, 190, 420, 200))
    line(s, (100, 130), (90, 260), 7)
    top = [(100 + 70 * math.cos(math.pi + math.pi * i / 20), 140 + 50 * math.sin(math.pi + math.pi * i / 20))
           for i in range(21)]
    poly(s, (240, 80, 90), top, 6)
    poly(s, WHITE, [(100, 90), (77, 140), (123, 140)], 0)
    circ(s, (255, 150, 200), 200, 252, 14, 5)
    poly(s, (255, 170, 80), star_pts(240, 236, 14, 6), 4)


def castle(s, c=None):
    _scene(s, (150, 200, 255), (230, 240, 255))
    stone = (190, 190, 210)
    pygame.draw.ellipse(s, (120, 200, 110), (-40, 250, 380, 100))
    for x in (40, 200):
        rrect(s, stone, (x, 110, 60, 160), 4)
        tri(s, (90, 110, 220), (x - 8, 112), (x + 30, 50), (x + 68, 112))
        line(s, (x + 30, 50), (x + 30, 24), 4)
        tri(s, (240, 80, 90), (x + 30, 24), (x + 30, 40), (x + 56, 32), 3)
    rrect(s, stone, (90, 140, 120, 130), 4)
    for x in range(90, 210, 30):
        rrect(s, stone, (x, 124, 18, 22), 2, 5)
    rrect(s, (120, 80, 60), (130, 200, 40, 70), 20, 5)
    for x in (58, 218):
        rrect(s, (70, 70, 110), (x, 150, 22, 30), 10, 0)


def moon(s, c=None):
    _scene(s, (20, 24, 70), (60, 50, 130))
    import random
    rng = random.Random(9)
    for _ in range(40):
        pygame.draw.circle(s, (255, 255, 230), (rng.randint(0, 300), rng.randint(0, 300)), rng.choice((1, 2, 2, 3)))
    circ(s, (250, 240, 180), 150, 150, 90)
    for x, y, r in ((120, 120, 20), (180, 170, 14), (130, 190, 10), (184, 112, 9)):
        circ(s, (220, 206, 150), x, y, r, 0)
    pygame.draw.circle(s, (230, 220, 160), (150, 150), 90, 6)
    poly(s, (255, 250, 200), star_pts(60, 60, 14, 6), 0)
    poly(s, (255, 250, 200), star_pts(250, 250, 10, 4), 0)


def forest(s, c=None):
    _scene(s, (170, 220, 255), (220, 250, 230))
    pygame.draw.ellipse(s, (110, 190, 100), (-40, 230, 380, 120))
    for x, h, colr in ((60, 160, (70, 160, 90)), (240, 150, (60, 150, 80)), (150, 200, (90, 180, 100))):
        rrect(s, (130, 90, 60), (x - 10, 260 - 40, 20, 50), 4)
        for k in range(3):
            y0 = 260 - 40 - k * h / 4
            tri(s, colr, (x - 60 + k * 10, y0), (x, y0 - h / 2.2), (x + 60 - k * 10, y0))
    circ(s, (240, 80, 90), 110, 270, 10, 4)
    pygame.draw.rect(s, WHITE, (106, 276, 8, 14))


def volcano(s, c=None):
    _scene(s, (255, 190, 140), (255, 230, 200))
    for x, y, r in ((160, 50, 26), (186, 34, 20), (140, 30, 18)):
        circ(s, (200, 200, 210), x, y, r, 0)
    poly(s, (140, 100, 80), [(10, 290), (120, 100), (180, 100), (290, 290)])
    poly(s, (255, 90, 40), [(120, 100), (180, 100), (172, 140), (160, 124), (150, 170), (138, 130), (128, 146)], 5)
    circ(s, (255, 200, 60), 150, 96, 12, 0)
    for x, y in ((110, 64), (190, 70), (150, 50)):
        circ(s, (255, 120, 40), x, y, 8, 4)


def island(s, c=None):
    _scene(s, (130, 210, 255), (200, 240, 255))
    pygame.draw.rect(s, (60, 160, 230), (0, 190, 300, 110))
    for x in range(-20, 320, 50):
        pygame.draw.arc(s, WHITE, (x, 230, 50, 20), 0, math.pi, 4)
    oval(s, (255, 226, 150), 150, 206, 100, 28)
    stroke(s, bez((150, 200), (140, 140), (166, 90)), 16, (160, 110, 60))
    for ang in (-2.6, -1.9, -1.2, -0.5, 0.2):
        tip = (166 + 80 * math.cos(ang), 90 + 50 * math.sin(ang) + 20)
        poly(s, (90, 190, 90), [(166, 90), (166 + 40 * math.cos(ang - 0.3), 90 + 40 * math.sin(ang - 0.3)),
                                tip, (166 + 40 * math.cos(ang + 0.3), 90 + 40 * math.sin(ang + 0.3))], 5)
    circ(s, (140, 90, 50), 160, 100, 10, 4)
    circ(s, (255, 220, 80), 50, 50, 26, 0)


def farm(s, c=None):
    _scene(s, (150, 210, 255), (230, 245, 255))
    pygame.draw.ellipse(s, (130, 210, 100), (-60, 220, 420, 140))
    red = (220, 70, 70)
    poly(s, red, [(60, 140), (150, 70), (240, 140), (240, 270), (60, 270)])
    poly(s, (120, 60, 60), [(46, 146), (150, 60), (254, 146), (240, 150), (150, 80), (60, 150)])
    rrect(s, WHITE, (110, 180, 80, 90), 2, 5)
    line(s, (114, 184), (186, 266), 5)
    line(s, (186, 184), (114, 266), 5)
    rrect(s, WHITE, (132, 110, 36, 30), 4, 5)
    for x in range(10, 300, 40):
        line(s, (x, 250), (x, 288), 5, (240, 220, 180))
    line(s, (0, 262), (300, 262), 5, (240, 220, 180))


def bakery(s, c=None):
    _scene(s, (255, 220, 230), (255, 245, 235))
    rrect(s, (255, 236, 200), (40, 100, 220, 180), 6)
    for i in range(7):
        x = 40 + i * 31.5
        colr = (240, 90, 120) if i % 2 == 0 else WHITE
        pygame.draw.rect(s, colr, (x, 80, 32, 46))
        pygame.draw.circle(s, colr, (x + 16, 126), 16)
    pygame.draw.rect(s, OUT, (40, 76, 220, 6))
    rrect(s, (140, 200, 255), (60, 160, 100, 70), 8, 5)
    rrect(s, (170, 110, 70), (180, 170, 60, 110), 6, 5)
    oval(s, (230, 170, 90), 110, 210, 32, 14, 4)
    for x in (96, 110, 124):
        line(s, (x, 202), (x + 6, 216), 3, (190, 120, 60))
    rrect(s, WHITE, (96, 30, 108, 40), 18)
    oval(s, (230, 170, 90), 150, 50, 30, 12, 4)


def mountain(s, c=None):
    _scene(s, (140, 200, 255), (220, 240, 255))
    poly(s, (130, 150, 190), [(-10, 290), (90, 110), (170, 290)])
    poly(s, (110, 130, 180), [(70, 290), (190, 60), (310, 290)])
    poly(s, WHITE, [(190, 60), (160, 120), (176, 112), (190, 128), (206, 110), (220, 120)], 5)
    poly(s, WHITE, [(90, 110), (70, 150), (90, 140), (106, 150)], 5)
    pygame.draw.ellipse(s, (240, 248, 255), (-40, 260, 380, 80))
    circ(s, (255, 220, 80), 50, 50, 22, 0)


DRAW = {name: fn for name, fn in globals().items()
        if callable(fn) and not name.startswith("_") and fn.__module__ == __name__
        and name not in {"shade", "oval", "circ", "poly", "rrect", "bez", "stroke", "line", "eye", "dot_eye",
                         "smile", "cheeks", "shine", "star_pts", "tri", "picture", "count_picture"}}

PLACES = {"beach", "castle", "moon", "forest", "volcano", "island", "farm", "bakery", "mountain"}

_CACHE = {}


def picture(name, size, color=None):
    """A cached, anti-aliased picture of `name` at `size` pixels (square)."""
    key = (name, size, color)
    if key in _CACHE:
        return _CACHE[key]
    canvas = pygame.Surface((CANVAS, CANVAS), pygame.SRCALPHA)
    if name in PLACES:
        DRAW[name](canvas, None)
        mask = pygame.Surface((CANVAS, CANVAS), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=60)
        canvas.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        pygame.draw.rect(canvas, OUT, canvas.get_rect(), W + 3, border_radius=60)
    else:
        rgb = COLORS.get(color) if isinstance(color, str) else color
        DRAW[name](canvas, rgb)
    surf = pygame.transform.smoothscale(canvas, (size, size))
    _CACHE[key] = surf
    return surf


def count_picture(name, count, size):
    """`count` small copies of a picture arranged neatly in a square."""
    key = ("#count", name, count, size)
    if key in _CACHE:
        return _CACHE[key]
    cols = 1 if count == 1 else 2 if count <= 4 else 3
    rows = math.ceil(count / cols)
    cell = int(size / max(cols, rows))
    icon = picture(name, int(cell * 0.92))
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    oy = (size - rows * cell) // 2
    for i in range(count):
        r, cidx = divmod(i, cols)
        in_row = min(cols, count - r * cols)
        ox = (size - in_row * cell) // 2
        surf.blit(icon, (ox + cidx * cell + (cell - icon.get_width()) // 2, oy + r * cell))
    _CACHE[key] = surf
    return surf
