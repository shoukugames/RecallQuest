"""Title screen: language, music, difficulty, top 10 and the parents' progress card."""
import math

import pygame

from .. import __version__, art, i18n, ui
from ..app import Scene
from ..story import LEVELS
from ..ui import INK, INK_SOFT, WHITE


class TitleScene(Scene):
    music = "title"

    def __init__(self, app):
        super().__init__(app)
        self.bg = ui.Background("day", icons=True, seed=11)
        s = app.store.settings
        self.lang_tabs = ui.Tabs((24, 18, 250, 46), ["en", "ja"], lambda v: "English" if v == "en" else "日本語",
                                 s["lang"], {"en": ui.BLUE, "ja": ui.RED}, 20)
        self.bgm_btn = ui.Button((288, 18, 150, 46), lambda: f"{i18n.t('bgm')} {i18n.t('on' if self.app.audio.bgm_on else 'off')}",
                                 ui.TEAL, 20, icon=lambda surf, c: ui.speaker_icon(surf, c, self.app.audio.bgm_on))
        self.diff_tabs = ui.Tabs((80, 372, 540, 54), ["easy", "medium", "hard"], i18n.t, s["difficulty"],
                                 ui.DIFF_COLORS, 22)
        self.play_btn = ui.Button((80, 472, 540, 78), lambda: i18n.t("play"), ui.ACCENT, 36, sound="start")
        self.howto_btn = ui.Button((80, 574, 264, 54), lambda: i18n.t("howto"), ui.BLUE, 22)
        self.parents_btn = ui.Button((356, 574, 264, 54), lambda: i18n.t("parents"), ui.PURPLE, 22)
        self.credits_btn = ui.Button((80, 642, 264, 50), lambda: i18n.t("credits"), ui.INK_SOFT, 20)
        self.quit_btn = ui.Button((356, 642, 264, 50), lambda: i18n.t("quit"), ui.RED, 20)
        self.buttons = [self.bgm_btn, self.play_btn, self.howto_btn, self.parents_btn, self.credits_btn, self.quit_btn]

    def handle(self, event):
        app = self.app
        if self.lang_tabs.clicked(event, app):
            app.set_language(self.lang_tabs.selected)
        elif self.diff_tabs.clicked(event, app):
            app.store.set("difficulty", self.diff_tabs.selected)
        elif self.bgm_btn.clicked(event, app):
            app.audio.set_bgm(not app.audio.bgm_on)
            app.store.set("bgm", app.audio.bgm_on)
        elif self.play_btn.clicked(event, app) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
            from .game import GameScene
            app.switch(GameScene(app, self.diff_tabs.selected))
        elif self.howto_btn.clicked(event, app):
            from .info import HowToScene
            app.switch(HowToScene(app))
        elif self.parents_btn.clicked(event, app):
            from .info import ParentsScene
            app.switch(ParentsScene(app))
        elif self.credits_btn.clicked(event, app):
            from .info import CreditsScene
            app.switch(CreditsScene(app))
        elif self.quit_btn.clicked(event, app) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            app.running = False

    def update(self, dt):
        super().update(dt)
        self.bg.update(dt)
        self.lang_tabs.update(dt, self.app)
        self.diff_tabs.update(dt, self.app)
        for b in self.buttons:
            b.update(dt, self.app)

    def draw(self, surf):
        self.bg.draw(surf)
        # logo and the owl reading a book
        ui.title_logo(surf, (350, 150), self.time, 78)
        owl = art.picture("owl", 110)
        book = art.picture("book", 64, "orange")
        bob = math.sin(self.time * 2) * 5
        surf.blit(owl, (556, 30 + bob))
        surf.blit(book, (604, 100 + bob * 0.6))
        sub = i18n.t("subtitle")
        ui.text(surf, sub, (350, 214), 24, INK, True, "midtop", outline=WHITE)
        ui.chip(surf, i18n.t("ages"), (350, 262), ui.GOLD, 20, "midtop", INK)
        ui.text(surf, i18n.t("difficulty"), (84, 340), 20, INK, True, outline=WHITE)
        desc = i18n.t(f"diff_{self.diff_tabs.selected}_desc")
        ui.text(surf, desc, (84, 434), 18, INK_SOFT, True, outline=WHITE)
        self.lang_tabs.draw(surf)
        self.diff_tabs.draw(surf)
        for b in self.buttons:
            b.draw(surf)
        self.draw_top10(surf)
        self.draw_progress(surf)
        ui.text(surf, f"v{__version__}", (1268, 708), 14, INK_SOFT, True, "bottomright")

    def draw_top10(self, surf):
        rect = pygame.Rect(690, 20, 566, 398)
        ui.panel(surf, rect, (255, 255, 255), 24)
        ui.star(surf, (rect.x + 34, rect.y + 32), 15, ui.GOLD)
        ui.text(surf, i18n.t("top10"), (rect.x + 58, rect.y + 16), 26, INK, True)
        scores = self.app.store.scores
        if not scores:
            ui.text(surf, i18n.t("no_scores"), (rect.centerx, rect.centery), 20, INK_SOFT, True, "center")
            return
        y = rect.y + 62
        medal = [ui.GOLD, (200, 206, 220), (220, 150, 90)]
        for i, s in enumerate(scores[:10]):
            row = pygame.Rect(rect.x + 14, y, rect.w - 28, 31)
            if i % 2 == 0:
                pygame.draw.rect(surf, (246, 244, 252), row, border_radius=10)
            c = (row.x + 20, row.centery)
            pygame.draw.circle(surf, medal[i] if i < 3 else (232, 228, 240), c, 13)
            ui.text(surf, str(i + 1), c, 15, INK, True, "center")
            ui.text(surf, s.get("name", "???"), (row.x + 44, row.centery), 18, INK, True, "midleft")
            d = s.get("difficulty", "easy")
            ui.chip(surf, i18n.t(d), (row.x + 312, row.centery), ui.DIFF_COLORS.get(d, ui.BLUE), 13, "center",
                    pad=(8, 1))
            ui.text(surf, f"Lv{s.get('level', 1)}", (row.x + 380, row.centery), 15, INK_SOFT, True, "midleft")
            ui.text(surf, f"{s['score']:,}", (row.right - 12, row.centery), 19, ui.darker(ui.ACCENT, 0.8), True, "midright")
            y += 33

    def draw_progress(self, surf):
        rect = pygame.Rect(690, 436, 566, 256)
        ui.panel(surf, rect, (255, 255, 255), 24)
        ui.text(surf, i18n.t("progress"), (rect.x + 24, rect.y + 14), 22, ui.PURPLE, True)
        s = self.app.store.summary()
        tiles = [(i18n.t("stories_read"), str(s["levels"])),
                 (i18n.t("accuracy"), f"{s['accuracy']:.0f}%"),
                 (i18n.t("avg_read"), i18n.t("seconds", s=f"{s['avg_read']:.0f}"))]
        tw = (rect.w - 48 - 20) // 3
        for i, (label, value) in enumerate(tiles):
            r = pygame.Rect(rect.x + 24 + i * (tw + 10), rect.y + 52, tw, 74)
            pygame.draw.rect(surf, (244, 240, 254), r, border_radius=14)
            ui.text(surf, value, (r.centerx, r.y + 8), 28, INK, True, "midtop")
            size = 14
            while size > 10 and ui.font(size, True).size(label)[0] > r.w - 10:
                size -= 1
            ui.text(surf, label, (r.centerx, r.bottom - 8), size, INK_SOFT, True, "midbottom")
        y = rect.y + 140
        ui.text(surf, i18n.t("best_level"), (rect.x + 24, y), 16, INK_SOFT, True)
        y += 26
        for d in ("easy", "medium", "hard"):
            lv = s["progress"][d]
            ui.text(surf, i18n.t(d), (rect.x + 24, y + 10), 16, INK, True, "midleft")
            bar = pygame.Rect(rect.x + 140, y + 2, rect.w - 230, 16)
            pygame.draw.rect(surf, (236, 232, 244), bar, border_radius=8)
            if lv:
                fill = bar.copy()
                fill.w = max(16, int(bar.w * lv / LEVELS))
                pygame.draw.rect(surf, ui.DIFF_COLORS[d], fill, border_radius=8)
            ui.text(surf, f"{lv}/{LEVELS}", (rect.right - 24, y + 10), 16, INK, True, "midright")
            y += 26
