"""How to Play, Credits and For Parents screens."""
import math
import webbrowser

import pygame

from .. import RELEASE_DATE, __version__, art, i18n, ui
from ..app import Scene
from ..story import LEVELS
from ..ui import INK, INK_SOFT, PAPER, WHITE

WEBSITE = "https://shoukugames.org/"
EMAIL = "info@shoukugames.org"


class InfoScene(Scene):
    theme = "day"

    def __init__(self, app):
        super().__init__(app)
        self.bg = ui.Background(self.theme, seed=21)
        self.back_btn = ui.Button((24, 18, 150, 50), lambda: i18n.t("back"), ui.INK_SOFT, 22)
        self.buttons = [self.back_btn]

    def back(self):
        from .title import TitleScene
        self.app.switch(TitleScene(self.app))

    def handle(self, event):
        if self.back_btn.clicked(event, self.app) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self.back()

    def update(self, dt):
        super().update(dt)
        self.bg.update(dt)
        for b in self.buttons:
            b.update(dt, self.app)

    def header(self, surf, key, color):
        ui.text(surf, i18n.t(key), (640, 22), 44, color, True, "midtop", shadow=ui.darker(color, 0.6), outline=WHITE)


class HowToScene(InfoScene):
    theme = "mint"

    def draw(self, surf):
        self.bg.draw(surf)
        self.header(surf, "howto", ui.BLUE)
        self.back_btn.draw(surf)
        steps = [("howto_1", None), ("howto_2", "timer"), ("howto_3", "cards"), ("howto_4", "crown")]
        cw, gap = 282, 22
        x0 = (ui.W - (4 * cw + 3 * gap)) // 2
        for i, (key, pic) in enumerate(steps):
            r = pygame.Rect(x0 + i * (cw + gap), 104, cw, 440)
            bob = math.sin(self.time * 2 + i) * 4
            ui.panel(surf, r.move(0, bob), PAPER, 24)
            c = (r.centerx, r.y + 34 + bob)
            pygame.draw.circle(surf, ui.ACCENT, c, 24)
            ui.text(surf, str(i + 1), c, 26, WHITE, True, "center")
            pic_rect = pygame.Rect(r.x + 40, r.y + 70 + bob, r.w - 80, 150)
            self.step_picture(surf, i, pic_rect)
            ui.text_block(surf, i18n.t(key), pygame.Rect(r.x + 22, r.y + 240 + bob, r.w - 44, 200), 20, INK, True,
                          "center", 1.5)
        tip = pygame.Rect(140, 566, 1000, 120)
        ui.panel(surf, tip, WHITE, 22)
        ui.owl_guide(surf, (tip.x + 10, tip.y + 10), self.time, 96)
        ui.text_block(surf, i18n.t("howto_tip"), pygame.Rect(tip.x + 130, tip.y + 18, tip.w - 160, 60), 22,
                      ui.darker(ui.GREEN, 0.75), True)
        ui.text(surf, i18n.t("howto_keys"), (tip.x + 130, tip.bottom - 30), 16, INK_SOFT, True, "midleft")

    def step_picture(self, surf, i, rect):
        c = rect.center
        if i == 0:
            for j, d in enumerate(("easy", "medium", "hard")):
                chip_rect = ui.chip(surf, i18n.t(d), (c[0], rect.y + 12 + j * 44), ui.DIFF_COLORS[d], 20, "midtop")
                del chip_rect
        elif i == 1:
            surf.blit(art.picture("book", 120, "blue"), (rect.x - 6, rect.y + 20))
            cc = (rect.right - 50, rect.y + 60)
            pygame.draw.circle(surf, WHITE, cc, 46)
            pygame.draw.circle(surf, ui.GREEN, cc, 40)
            a = -math.pi / 2 + (self.time % 6) / 6 * 2 * math.pi
            pygame.draw.line(surf, WHITE, cc, (cc[0] + 30 * math.cos(a), cc[1] + 30 * math.sin(a)), 5)
            ui.text(surf, "120", (cc[0], cc[1] + 58), 26, INK, True, "midtop")
        elif i == 2:
            for j, n in enumerate(("cat", "frog", "pig")):
                r = pygame.Rect(rect.x - 10 + j * 72, rect.y + 30, 66, 84)
                ui.panel(surf, r, WHITE, 12, border=ui.GREEN if j == 1 else None, border_w=4)
                surf.blit(art.picture(n, 56), (r.x + 5, r.y + 14))
            ui.text(surf, "+500", (c[0], rect.bottom - 14), 26, ui.GREEN, True, "center", outline=WHITE)
        else:
            surf.blit(art.picture("crown", 130), (c[0] - 65, rect.y + 4))
            for j in range(3):
                ui.star(surf, (c[0] + (j - 1) * 50, rect.bottom - 10), 16, ui.GOLD)


class CreditsScene(InfoScene):
    theme = "dusk"

    def __init__(self, app):
        super().__init__(app)
        self.links = {}

    def handle(self, event):
        super().handle(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for target, rect in self.links.items():
                if rect.collidepoint(event.pos):
                    self.app.audio.play("click")
                    try:
                        webbrowser.open(target)
                    except Exception:  # noqa: BLE001 - no browser is fine
                        pass

    def draw(self, surf):
        self.bg.draw(surf)
        self.header(surf, "credits_title", ui.PURPLE)
        self.back_btn.draw(surf)
        rect = pygame.Rect(190, 100, 900, 590)
        ui.panel(surf, rect, PAPER, 28)
        ui.title_logo(surf, (rect.centerx, rect.y + 54), self.time, 56)
        ui.text(surf, f"v{__version__}", (rect.centerx, rect.y + 96), 20, INK_SOFT, True, "midtop")
        rows = [
            ("created_by", "Shawn Rapaz", None),
            ("made_with", "Claude Code (Anthropic)", None),
            ("date", RELEASE_DATE, None),
            ("release", f"v{__version__}", None),
            ("website", WEBSITE, WEBSITE),
            ("email", EMAIL, "mailto:" + EMAIL),
            ("license", i18n.t("license_name"), None),
        ]
        y = rect.y + 140
        self.links = {}
        mouse = pygame.mouse.get_pos()
        for key, value, link in rows:
            ui.text(surf, i18n.t(key), (rect.x + 290, y), 22, INK_SOFT, True, "topright")
            col = ui.BLUE if link else INK
            r = ui.text(surf, value, (rect.x + 320, y), 24, col, True)
            if link:
                if r.collidepoint(mouse):
                    pygame.draw.line(surf, col, (r.x, r.bottom), (r.right, r.bottom), 2)
                self.links[link] = r
            y += 44
        ui.text_block(surf, i18n.t("license_note"), pygame.Rect(rect.x + 60, y + 8, rect.w - 120, 60), 18, INK_SOFT,
                      True, "center")
        ui.text(surf, i18n.t("fonts"), (rect.centerx, rect.bottom - 70), 16, INK_SOFT, True, "midtop")
        ui.text(surf, i18n.t("music_credit"), (rect.centerx, rect.bottom - 44), 16, INK_SOFT, True, "midtop")
        ui.chip(surf, i18n.t("ages"), (rect.right - 24, rect.y + 24), ui.GOLD, 16, "topright", INK)
        for i, n in enumerate(("frog", "penguin", "robot")):
            surf.blit(art.picture(n, 70), (rect.x + 24 + i * 50, rect.y + 16 + math.sin(self.time * 2 + i) * 5))


class ParentsScene(InfoScene):
    theme = "day"

    def __init__(self, app):
        super().__init__(app)
        self.reset_btn = ui.Button((1050, 24, 206, 46), lambda: i18n.t("reset"), ui.RED, 18)
        self.yes_btn = ui.Button((420, 410, 210, 58), lambda: i18n.t("yes"), ui.RED, 20)
        self.no_btn = ui.Button((650, 410, 210, 58), lambda: i18n.t("no"), ui.INK_SOFT, 20)
        self.buttons += [self.reset_btn]
        self.confirm = False

    def handle(self, event):
        if self.confirm:
            if self.yes_btn.clicked(event, self.app):
                self.app.store.reset()
                self.confirm = False
            elif self.no_btn.clicked(event, self.app) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.confirm = False
            return
        if self.reset_btn.clicked(event, self.app):
            self.confirm = True
            return
        super().handle(event)

    def update(self, dt):
        super().update(dt)
        if self.confirm:
            self.yes_btn.update(dt, self.app)
            self.no_btn.update(dt, self.app)

    def draw(self, surf):
        self.bg.draw(surf, hills=False)
        self.header(surf, "parents_title", ui.PURPLE)
        self.back_btn.draw(surf)
        self.reset_btn.draw(surf)
        store = self.app.store
        s = store.summary()
        ui.text(surf, i18n.t("parents_intro"), (640, 80), 18, INK, True, "midtop", outline=WHITE)
        mins = lambda sec: i18n.t("minutes", m=f"{sec / 60:.0f}") if sec >= 60 else i18n.t("seconds", s=f"{sec:.0f}")  # noqa: E731
        tiles = [
            (i18n.t("levels_played"), str(s["levels"]), ui.BLUE),
            (i18n.t("first_try"), f"{s['accuracy']:.0f}%", ui.GREEN),
            (i18n.t("avg_read"), i18n.t("seconds", s=f"{s['avg_read']:.0f}"), ui.TEAL),
            (i18n.t("avg_total"), i18n.t("seconds", s=f"{s['avg_total']:.0f}"), ui.ACCENT),
            (i18n.t("total_errors"), str(s["errors"]), ui.RED),
            (i18n.t("best_score"), f"{s['best_score']:,}", ui.GOLD),
            (i18n.t("play_time"), mins(s["play_time"]), ui.PURPLE),
        ]
        tw, gap = 166, 12
        x0 = (ui.W - (len(tiles) * tw + (len(tiles) - 1) * gap)) // 2
        for i, (label, value, col) in enumerate(tiles):
            r = pygame.Rect(x0 + i * (tw + gap), 116, tw, 96)
            ui.panel(surf, r, WHITE, 18)
            pygame.draw.rect(surf, col, (r.x, r.y, r.w, 8), border_top_left_radius=18, border_top_right_radius=18)
            ui.text(surf, value, (r.centerx, r.y + 18), 30, ui.darker(col, 0.8), True, "midtop")
            size = 15
            while size > 10 and ui.font(size, True).size(label)[0] > r.w - 12:
                size -= 1
            ui.text(surf, label, (r.centerx, r.bottom - 10), size, INK_SOFT, True, "midbottom")
        self.draw_chart(surf, pygame.Rect(24, 230, 760, 250), store.history[-20:])
        self.draw_diff(surf, pygame.Rect(800, 230, 456, 250), s)
        self.draw_table(surf, pygame.Rect(24, 496, 1232, 210), store.history[-6:][::-1])
        if self.confirm:
            veil = pygame.Surface((ui.W, ui.H), pygame.SRCALPHA)
            veil.fill((30, 20, 50, 160))
            surf.blit(veil, (0, 0))
            r = pygame.Rect(360, 230, 560, 270)
            ui.panel(surf, r, PAPER, 26)
            ui.text_block(surf, i18n.t("reset_confirm"), pygame.Rect(r.x + 40, r.y + 50, r.w - 80, 120), 24, INK, True,
                          "center")
            self.yes_btn.draw(surf)
            self.no_btn.draw(surf)

    def draw_chart(self, surf, rect, hist):
        ui.panel(surf, rect, WHITE, 20)
        ui.text(surf, i18n.t("chart_title"), (rect.x + 20, rect.y + 12), 17, INK, True)
        plot = pygame.Rect(rect.x + 56, rect.y + 50, rect.w - 80, rect.h - 86)
        for k in range(5):
            y = plot.bottom - plot.h * k / 4
            pygame.draw.line(surf, (236, 232, 244), (plot.x, y), (plot.right, y), 1)
            ui.text(surf, f"{30 * k}", (plot.x - 8, y), 13, INK_SOFT, True, "midright")
        if not hist:
            ui.text(surf, i18n.t("no_data"), plot.center, 20, INK_SOFT, True, "center")
            return
        n = 20
        bw = plot.w / n
        for i, h in enumerate(hist):
            v = min(120, h.get("read_time", 0))
            bh = plot.h * v / 120
            col = ui.DIFF_COLORS.get(h.get("difficulty"), ui.BLUE)
            bar = pygame.Rect(plot.x + i * bw + 4, plot.bottom - bh, bw - 8, bh)
            pygame.draw.rect(surf, ui.lighter(col, 0.25), bar, border_top_left_radius=6, border_top_right_radius=6)
            ui.text(surf, str(h.get("level", "")), (bar.centerx, plot.bottom + 4), 12, INK_SOFT, True, "midtop")
            err = h.get("errors", 0)
            for e in range(min(err, 6)):
                pygame.draw.circle(surf, ui.RED, (bar.centerx, plot.bottom - bh - 10 - e * 12), 5)

    def draw_diff(self, surf, rect, s):
        ui.panel(surf, rect, WHITE, 20)
        ui.text(surf, i18n.t("per_diff"), (rect.x + 20, rect.y + 12), 17, INK, True)
        best = {}
        for h in self.app.store.history:
            d = h.get("difficulty")
            best.setdefault(d, []).append(h)
        y = rect.y + 54
        for d in ("easy", "medium", "hard"):
            lv = s["progress"][d]
            col = ui.DIFF_COLORS[d]
            ui.chip(surf, i18n.t(d), (rect.x + 20, y), col, 16, pad=(12, 3))
            rows = best.get(d, [])
            acc = (sum(r.get("first_try", 0) for r in rows) / max(1, sum(r.get("questions", 3) for r in rows)) * 100)
            ui.text(surf, f"{i18n.t('first_try')}: {acc:.0f}%" if rows else "-", (rect.right - 20, y + 2), 14, INK_SOFT,
                    True, "topright")
            y += 32
            for k in range(LEVELS):
                c = (rect.x + 34 + k * 40, y + 10)
                filled = k < lv
                pygame.draw.circle(surf, col if filled else (236, 232, 244), c, 15)
                ui.text(surf, str(k + 1), c, 13, WHITE if filled else INK_SOFT, True, "center")
            y += 34

    def draw_table(self, surf, rect, rows):
        ui.panel(surf, rect, WHITE, 20)
        ui.text(surf, i18n.t("recent"), (rect.x + 20, rect.y + 10), 17, INK, True)
        cols = [("col_date", 20), ("col_diff", 220), ("col_level", 380), ("col_read", 490), ("col_total", 620),
                ("col_words", 760), ("col_errors", 870), ("col_score", 1000)]
        y = rect.y + 40
        for key, x in cols:
            ui.text(surf, i18n.t(key), (rect.x + x, y), 15, INK_SOFT, True)
        y += 26
        if not rows:
            ui.text(surf, i18n.t("no_data"), (rect.centerx, rect.y + 130), 18, INK_SOFT, True, "center")
            return
        for i, h in enumerate(rows):
            if i % 2 == 0:
                pygame.draw.rect(surf, (246, 244, 252), (rect.x + 10, y - 2, rect.w - 20, 23), border_radius=8)
            d = h.get("difficulty", "easy")
            vals = [h.get("date", ""), i18n.t(d), str(h.get("level", "")),
                    i18n.t("seconds", s=f"{h.get('read_time', 0):.0f}"),
                    i18n.t("seconds", s=f"{h.get('total_time', 0):.0f}"), str(h.get("words", "")),
                    str(h.get("errors", 0)), f"{h.get('score', 0):,}"]
            for (key, x), v in zip(cols, vals):
                col = ui.DIFF_COLORS.get(d) if key == "col_diff" else (ui.RED if key == "col_errors" and h.get("errors") else INK)
                ui.text(surf, v, (rect.x + x, y), 16, col, True)
            y += 23
