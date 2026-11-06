"""Drawing helpers shared by every screen: fonts, wrapped text, panels, buttons,
the animated storybook background, confetti and the owl guide."""
import math
import random

import pygame

from . import art, i18n, paths

W, H = 1280, 720

INK = (52, 44, 66)
INK_SOFT = (112, 102, 132)
PAPER = (255, 252, 244)
PAPER_EDGE = (236, 222, 196)
WHITE = (255, 255, 255)
ACCENT = (255, 140, 80)
BLUE = (88, 140, 250)
GREEN = (70, 186, 116)
RED = (236, 86, 98)
GOLD = (255, 194, 56)
PURPLE = (146, 108, 230)
TEAL = (52, 182, 188)
DIFF_COLORS = {"easy": GREEN, "medium": BLUE, "hard": PURPLE}

_FONTS = {}
_TEXT = {}


def font(size, bold=False):
    key = (size, bold)
    if key not in _FONTS:
        name = "MPLUSRounded1c-Bold.ttf" if bold else "MPLUSRounded1c-Medium.ttf"
        try:
            _FONTS[key] = pygame.font.Font(paths.asset("fonts", name), size)
        except (OSError, FileNotFoundError):
            _FONTS[key] = pygame.font.Font(None, int(size * 1.3))
    return _FONTS[key]


def render(text, size, color=INK, bold=False):
    key = (text, size, color, bold)
    img = _TEXT.get(key)
    if img is None:
        if len(_TEXT) > 1500:
            _TEXT.clear()
        img = font(size, bold).render(text, True, color)
        _TEXT[key] = img
    return img


def text(surf, s, pos, size, color=INK, bold=False, anchor="topleft", shadow=None, outline=None, alpha=255):
    img = render(s, size, color, bold)
    rect = img.get_rect(**{anchor: pos})
    if outline:
        ring = render(s, size, outline, bold)
        d = max(2, size // 14)
        for dx, dy in ((-d, 0), (d, 0), (0, -d), (0, d), (-d, -d), (d, d), (-d, d), (d, -d)):
            surf.blit(ring, rect.move(dx, dy))
    if shadow:
        sh = render(s, size, shadow, bold)
        surf.blit(sh, rect.move(0, max(2, size // 12)))
    if alpha < 255:
        img = img.copy()
        img.set_alpha(alpha)
    surf.blit(img, rect)
    return rect


NO_START = set("、。，．・：；？！ー）」』】〕…ぁぃぅぇぉっゃゅょゎァィゥェォッャュョヮ,.!?:;)")
NO_END = set("「『（【〔(")


def wrap(s, size, width, bold=False):
    """Word-wrap English; character-wrap Japanese (with kinsoku rules)."""
    f = font(size, bold)
    if any(ord(ch) > 0x2E80 for ch in s):
        lines, cur = [], ""
        for ch in s:
            if f.size(cur + ch)[0] <= width or not cur:
                cur += ch
                continue
            if ch in NO_START:
                # pull the last character down so this one does not start a line
                cur, carry = cur[:-1], cur[-1]
                lines.append(cur)
                cur = carry + ch
            elif cur[-1] in NO_END:
                lines.append(cur[:-1])
                cur = cur[-1] + ch
            else:
                lines.append(cur)
                cur = ch
        if cur:
            lines.append(cur)
        return lines
    words = s.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w) if cur else w
        if f.size(trial)[0] <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(surf, s, rect, size, color=INK, bold=False, align="left", spacing=1.4):
    rect = pygame.Rect(rect)
    lines = wrap(s, size, rect.w, bold)
    lh = int(size * spacing)
    y = rect.y
    for ln in lines:
        if align == "center":
            text(surf, ln, (rect.centerx, y), size, color, bold, "midtop")
        else:
            text(surf, ln, (rect.x, y), size, color, bold)
        y += lh
    return y


# ------------------------------------------------------------------ panels
_SHADOWS = {}


def shadow(w, h, radius=22, blur=14, alpha=60):
    key = (w, h, radius, blur, alpha)
    if key not in _SHADOWS:
        pad = blur * 2
        base = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
        pygame.draw.rect(base, (30, 20, 50, alpha), (pad, pad, w, h), border_radius=radius)
        small = pygame.transform.smoothscale(base, (max(1, base.get_width() // 6), max(1, base.get_height() // 6)))
        _SHADOWS[key] = (pygame.transform.smoothscale(small, base.get_size()), pad)
    return _SHADOWS[key]


def panel(surf, rect, color=PAPER, radius=22, drop=True, border=None, border_w=3):
    rect = pygame.Rect(rect)
    if drop:
        img, pad = shadow(rect.w, rect.h, radius)
        surf.blit(img, (rect.x - pad, rect.y - pad + 8))
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border:
        pygame.draw.rect(surf, border, rect, border_w, border_radius=radius)
    return rect


def chip(surf, s, pos, color, size=20, anchor="topleft", text_color=WHITE, pad=(16, 6)):
    img = render(s, size, text_color, True)
    rect = pygame.Rect(0, 0, img.get_width() + pad[0] * 2, img.get_height() + pad[1] * 2)
    setattr(rect, anchor, pos)
    pygame.draw.rect(surf, color, rect, border_radius=rect.h // 2)
    surf.blit(img, img.get_rect(center=rect.center))
    return rect


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


def darker(c, f=0.78):
    return tuple(int(v * f) for v in c[:3])


def lighter(c, f=0.35):
    return tuple(int(v + (255 - v) * f) for v in c[:3])


def star(surf, center, r, color, outline=INK):
    pts = art.star_pts(center[0], center[1], r, r * 0.45)
    pygame.draw.polygon(surf, color, pts)
    if outline:
        pygame.draw.polygon(surf, outline, pts, 3)


def speaker_icon(surf, center, on, color=WHITE):
    x, y = center
    pygame.draw.polygon(surf, color, [(x - 12, y - 5), (x - 6, y - 5), (x + 2, y - 12), (x + 2, y + 12),
                                      (x - 6, y + 5), (x - 12, y + 5)])
    if on:
        pygame.draw.arc(surf, color, (x - 4, y - 8, 16, 16), -1.0, 1.0, 3)
        pygame.draw.arc(surf, color, (x - 6, y - 13, 26, 26), -1.0, 1.0, 3)
    else:
        pygame.draw.line(surf, color, (x + 7, y - 6), (x + 17, y + 6), 3)
        pygame.draw.line(surf, color, (x + 17, y - 6), (x + 7, y + 6), 3)


# ------------------------------------------------------------------ buttons
class Button:
    def __init__(self, rect, label, color=ACCENT, size=28, text_color=WHITE, sound="click", icon=None):
        self.rect = pygame.Rect(rect)
        self.label = label            # a string, or a function returning one
        self.color = color
        self.size = size
        self.text_color = text_color
        self.sound = sound
        self.icon = icon              # function(surf, center) drawn left of the label
        self.hover = False
        self.t = 0.0
        self.enabled = True
        self.visible = True
        self.selected = False
        self.progress = None          # 0..1 fill while locked

    def caption(self):
        return self.label() if callable(self.label) else self.label

    def update(self, dt, app=None):
        mouse = pygame.mouse.get_pos()
        was = self.hover
        self.hover = self.visible and self.enabled and self.rect.collidepoint(mouse)
        if self.hover and not was and app:
            app.audio.play("hover")
        target = 1.0 if self.hover else 0.0
        self.t += (target - self.t) * min(1.0, dt * 14)

    def clicked(self, event, app=None):
        if (self.visible and self.enabled and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                and self.rect.collidepoint(event.pos)):
            if app and self.sound:
                app.audio.play(self.sound)
            return True
        return False

    def draw(self, surf):
        if not self.visible:
            return
        r = self.rect.copy()
        lift = int(self.t * 3)
        depth = max(4, r.h // 12)
        base = self.color if self.enabled else (190, 186, 200)
        if self.selected:
            base = darker(base, 0.9)
        img, pad = shadow(r.w, r.h, r.h // 2 if r.h < 70 else 22, 10, 50)
        surf.blit(img, (r.x - pad, r.y - pad + 6))
        radius = min(r.h // 2, 26)
        pygame.draw.rect(surf, darker(base, 0.72), r.move(0, depth), border_radius=radius)
        top = r.move(0, -lift)
        fill = lighter(base, 0.12 * self.t) if self.enabled else base
        pygame.draw.rect(surf, fill, top, border_radius=radius)
        if self.progress is not None and not self.enabled:
            prog = top.copy()
            prog.w = int(top.w * max(0.0, min(1.0, self.progress)))
            if prog.w > 2 * radius:
                pygame.draw.rect(surf, lighter(self.color, 0.2), prog, border_radius=radius)
        gloss = pygame.Rect(top.x + 8, top.y + 4, top.w - 16, top.h // 2 - 4)
        g = pygame.Surface(gloss.size, pygame.SRCALPHA)
        pygame.draw.rect(g, (255, 255, 255, 46), g.get_rect(), border_radius=radius)
        surf.blit(g, gloss)
        if self.selected:
            pygame.draw.rect(surf, WHITE, top, 4, border_radius=radius)
        label = self.caption()
        tc = self.text_color if self.enabled else WHITE
        img = render(label, self.size, tc, True)
        if img.get_width() > top.w - 24:
            size = self.size
            while size > 12 and render(label, size, tc, True).get_width() > top.w - 24:
                size -= 1
            img = render(label, size, tc, True)
        cx = top.centerx
        if self.icon:
            cx += 14
            self.icon(surf, (cx - img.get_width() // 2 - 22, top.centery))
        surf.blit(img, img.get_rect(center=(cx, top.centery)))


class Tabs:
    """A segmented control: one choice from several."""

    def __init__(self, rect, values, label_fn, selected, colors=None, size=22):
        self.rect = pygame.Rect(rect)
        self.values = list(values)
        self.label_fn = label_fn
        self.selected = selected
        self.colors = colors or {}
        self.size = size
        self.hover = None
        self.anim = float(self.values.index(selected))

    def cell(self, i):
        w = self.rect.w / len(self.values)
        return pygame.Rect(int(self.rect.x + i * w), self.rect.y, int(w), self.rect.h)

    def update(self, dt, app=None):
        mouse = pygame.mouse.get_pos()
        hov = None
        for i in range(len(self.values)):
            if self.cell(i).collidepoint(mouse):
                hov = i
        if hov is not None and hov != self.hover and app:
            app.audio.play("hover")
        self.hover = hov
        target = self.values.index(self.selected)
        self.anim += (target - self.anim) * min(1.0, dt * 12)

    def clicked(self, event, app=None):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, v in enumerate(self.values):
                if self.cell(i).collidepoint(event.pos):
                    if v != self.selected:
                        self.selected = v
                        if app:
                            app.audio.play("click")
                        return True
        return False

    def draw(self, surf):
        r = self.rect
        img, pad = shadow(r.w, r.h, r.h // 2, 8, 40)
        surf.blit(img, (r.x - pad, r.y - pad + 4))
        pygame.draw.rect(surf, WHITE, r, border_radius=r.h // 2)
        w = r.w / len(self.values)
        knob = pygame.Rect(int(r.x + self.anim * w) + 4, r.y + 4, int(w) - 8, r.h - 8)
        col = self.colors.get(self.selected, ACCENT)
        pygame.draw.rect(surf, col, knob, border_radius=knob.h // 2)
        for i, v in enumerate(self.values):
            c = self.cell(i)
            sel = v == self.selected
            if self.hover == i and not sel:
                pygame.draw.rect(surf, (240, 236, 248), c.inflate(-8, -8), border_radius=(r.h - 8) // 2)
            text(surf, self.label_fn(v), c.center, self.size, WHITE if sel else INK_SOFT, True, "center")


# --------------------------------------------------------------- background
_GRAD = {}


def gradient(size, top, bottom):
    key = (size, top, bottom)
    if key not in _GRAD:
        surf = pygame.Surface(size)
        h = size[1]
        for y in range(h):
            pygame.draw.line(surf, mix(top, bottom, y / max(1, h - 1)), (0, y), (size[0], y))
        _GRAD[key] = surf
    return _GRAD[key]


def cloud_surface(w, seed):
    rng = random.Random(seed)
    h = int(w * 0.5)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for _ in range(7):
        r = rng.randint(int(h * 0.25), int(h * 0.42))
        x = rng.randint(r, w - r)
        y = rng.randint(int(h * 0.45), h - r)
        pygame.draw.circle(surf, (255, 255, 255, 255), (x, y), r)
    pygame.draw.rect(surf, (255, 255, 255, 255), (w * 0.15, h * 0.6, w * 0.7, h * 0.3), border_radius=int(h * 0.15))
    surf.set_alpha(150)
    return surf


class Background:
    """A soft sky with drifting clouds, floating bubbles and gentle hills."""

    THEMES = {
        "day": ((132, 190, 255), (220, 236, 255), (162, 214, 140), (126, 192, 120)),
        "dusk": ((150, 140, 230), (255, 214, 220), (190, 170, 220), (160, 140, 210)),
        "mint": ((120, 210, 210), (232, 252, 236), (150, 214, 170), (110, 190, 150)),
    }

    def __init__(self, theme="day", icons=False, seed=3):
        self.theme = theme
        rng = random.Random(seed)
        self.clouds = [[rng.uniform(0, W), rng.uniform(30, 300), rng.uniform(8, 22), cloud_surface(rng.randint(160, 300), i)]
                       for i in range(6)]
        self.bubbles = [[rng.uniform(0, W), rng.uniform(0, H), rng.uniform(6, 26), rng.uniform(8, 26),
                         rng.uniform(0, 6.28)] for _ in range(26)]
        self.icons = []
        if icons:
            names = [n for n in art.DRAW if n not in art.PLACES]
            rng.shuffle(names)
            for i, n in enumerate(names[:12]):
                img = art.picture(n, rng.randint(54, 84)).copy()
                img.set_alpha(70)
                self.icons.append([rng.uniform(0, W), rng.uniform(0, H), rng.uniform(10, 24), img,
                                   rng.uniform(0, 6.28), rng.uniform(-20, 20)])
        self.time = 0.0
        self.hills = None

    def update(self, dt):
        self.time += dt
        for c in self.clouds:
            c[0] += c[2] * dt
            if c[0] > W + 40:
                c[0] = -c[3].get_width() - 40
        for b in self.bubbles:
            b[1] -= b[3] * dt
            if b[1] < -40:
                b[1] = H + 40
                b[0] = random.uniform(0, W)
        for ic in self.icons:
            ic[1] -= ic[2] * dt
            if ic[1] < -100:
                ic[1] = H + 100
                ic[0] = random.uniform(0, W)

    def _hills(self):
        if self.hills is None:
            _, _, h1, h2 = self.THEMES[self.theme]
            surf = pygame.Surface((W, 260), pygame.SRCALPHA)
            pts = [(0, 260)] + [(x, 120 + 34 * math.sin(x / 210) + 18 * math.sin(x / 77)) for x in range(0, W + 9, 8)]
            pygame.draw.polygon(surf, (*h1, 255), pts + [(W, 260)])
            pts = [(0, 260)] + [(x, 175 + 30 * math.sin(x / 160 + 2) + 12 * math.sin(x / 53)) for x in range(0, W + 9, 8)]
            pygame.draw.polygon(surf, (*h2, 255), pts + [(W, 260)])
            self.hills = surf
        return self.hills

    def draw(self, surf, hills=True):
        top, bottom, _, _ = self.THEMES[self.theme]
        surf.blit(gradient((W, H), top, bottom), (0, 0))
        sun = (W - 150, 110)
        for r, a in ((120, 30), (90, 50), (64, 255)):
            g = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(g, (255, 236, 160, a), (r, r), r)
            surf.blit(g, (sun[0] - r, sun[1] - r))
        for c in self.clouds:
            surf.blit(c[3], (c[0], c[1]))
        for ic in self.icons:
            img = pygame.transform.rotate(ic[3], ic[5] * math.sin(self.time * 0.6 + ic[4]))
            surf.blit(img, img.get_rect(center=(ic[0] + 14 * math.sin(self.time * 0.5 + ic[4]), ic[1])))
        bub = pygame.Surface((60, 60), pygame.SRCALPHA)
        for b in self.bubbles:
            bub.fill((0, 0, 0, 0))
            r = int(b[2])
            pygame.draw.circle(bub, (255, 255, 255, 50), (30, 30), r)
            pygame.draw.circle(bub, (255, 255, 255, 110), (30, 30), r, 2)
            pygame.draw.circle(bub, (255, 255, 255, 140), (30 - r // 3, 30 - r // 3), max(2, r // 4))
            surf.blit(bub, (b[0] + 10 * math.sin(self.time + b[4]) - 30, b[1] - 30))
        if hills:
            surf.blit(self._hills(), (0, H - 260))


# ------------------------------------------------------------------ effects
class Confetti:
    COLORS = [RED, GOLD, GREEN, BLUE, PURPLE, (255, 140, 196), TEAL]

    def __init__(self):
        self.parts = []

    def burst(self, pos, n=40, spread=1.0):
        for _ in range(n):
            a = random.uniform(-math.pi, 0)
            sp = random.uniform(180, 520) * spread
            self.parts.append([pos[0], pos[1], math.cos(a) * sp, math.sin(a) * sp, random.choice(self.COLORS),
                               random.uniform(0, 360), random.uniform(-400, 400), random.uniform(1.2, 2.2),
                               random.randint(6, 12)])

    def rain(self, n=80):
        for _ in range(n):
            self.parts.append([random.uniform(0, W), random.uniform(-200, -10), random.uniform(-40, 40),
                               random.uniform(60, 200), random.choice(self.COLORS), random.uniform(0, 360),
                               random.uniform(-300, 300), random.uniform(3, 5), random.randint(7, 12)])

    def update(self, dt):
        alive = []
        for p in self.parts:
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            p[3] += 600 * dt
            p[2] *= 1 - dt * 1.5
            p[3] = min(p[3], 260)
            p[5] += p[6] * dt
            p[7] -= dt
            if p[7] > 0 and p[1] < H + 30:
                alive.append(p)
        self.parts = alive

    def draw(self, surf):
        for p in self.parts:
            s = p[8]
            w = max(2, int(abs(math.cos(math.radians(p[5]))) * s))
            pygame.draw.rect(surf, p[4], (p[0] - w / 2, p[1] - s / 3, w, s * 0.66), border_radius=2)


class FloatText:
    def __init__(self):
        self.items = []

    def add(self, s, pos, color, size=40):
        self.items.append([s, list(pos), color, size, 1.4])

    def update(self, dt):
        for it in self.items:
            it[1][1] -= 50 * dt
            it[4] -= dt
        self.items = [it for it in self.items if it[4] > 0]

    def draw(self, surf):
        for s, pos, color, size, life in self.items:
            text(surf, s, pos, size, color, True, "center", outline=WHITE, alpha=int(255 * min(1, life / 0.5)))


def owl_guide(surf, pos, t, size=150, bubble=None, bubble_w=360, bubble_size=22, flip=False):
    """The owl guide, gently bobbing, with an optional speech bubble to its right."""
    img = art.picture("owl", size)
    if flip:
        img = pygame.transform.flip(img, True, False)
    bob = math.sin(t * 2.2) * 5
    surf.blit(img, (pos[0], pos[1] + bob))
    if bubble:
        lines = []
        for part in bubble.split("\n"):
            lines += wrap(part, bubble_size, bubble_w - 40, True)
        lh = int(bubble_size * 1.45)
        bh = lh * len(lines) + 30
        bx = pos[0] + size + 14
        by = pos[1] + size // 2 - bh // 2 + bob * 0.4
        rect = pygame.Rect(bx, by, bubble_w, bh)
        panel(surf, rect, WHITE, 20)
        pygame.draw.polygon(surf, WHITE, [(bx + 2, by + bh / 2 - 12), (bx - 18, by + bh / 2 + 4), (bx + 2, by + bh / 2 + 12)])
        y = by + 15
        for ln in lines:
            text(surf, ln, (bx + 20, y), bubble_size, INK, True)
            y += lh
        return rect
    return None


def title_logo(surf, center, t, size=84):
    """The game name in bouncing, colourful letters."""
    name = i18n.t("title")
    colors = [ACCENT, GOLD, GREEN, BLUE, PURPLE, (255, 120, 180), TEAL]
    f = font(size, True)
    widths = [f.size(ch)[0] for ch in name]
    total = sum(widths)
    x = center[0] - total / 2
    for i, ch in enumerate(name):
        y = center[1] + math.sin(t * 2.5 + i * 0.5) * 6
        col = colors[i % len(colors)]
        text(surf, ch, (x + widths[i] / 2, y), size, col, True, "center", shadow=darker(col, 0.55), outline=WHITE)
        x += widths[i]
    return pygame.Rect(center[0] - total / 2, center[1] - size // 2, total, size)
