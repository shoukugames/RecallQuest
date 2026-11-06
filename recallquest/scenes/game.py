"""One run: ten levels of read-the-story-then-point-at-the-answer."""
import math
import random

import pygame

from .. import art, i18n, story, ui
from ..app import Scene
from ..ui import INK, INK_SOFT, PAPER, WHITE, W, H

TIME_LIMIT = 120
BONUS_PER_SECOND = 100
CORRECT_POINTS = {"easy": 500, "medium": 750, "hard": 1000}
WRONG_POINTS = {"easy": 300, "medium": 400, "hard": 500}
MAX_WRONG = 2                     # after this many misses the answer is shown
SECONDS_PER_WORD = 0.1            # the shortest believable read before "done" unlocks

CARD = pygame.Rect(70, 84, 1140, 548)
TEXT_AREA = pygame.Rect(118, 168, 1044, 444)


class GameScene(Scene):
    music = "game"

    def __init__(self, app, difficulty, seed=None):
        super().__init__(app)
        self.diff = difficulty
        self.rng = random.Random(seed)
        self.level = 1
        self.total = 0
        self.cleared = 0
        self.run_seen = set()
        self.confetti = ui.Confetti()
        self.floats = ui.FloatText()
        self.bg = ui.Background("mint" if difficulty == "easy" else "day" if difficulty == "medium" else "dusk", seed=7)
        self.paused = False
        self.pause_btn = ui.Button((1206, 16, 56, 50), "II", ui.INK_SOFT, 22)
        self.resume_btn = ui.Button((490, 360, 300, 64), lambda: i18n.t("resume"), ui.GREEN, 26)
        self.quit_btn = ui.Button((490, 446, 300, 64), lambda: i18n.t("quit_title"), ui.RED, 24)
        self.start_btn = ui.Button((470, 520, 340, 72), lambda: i18n.t("play"), ui.ACCENT, 32, sound="start")
        self.done_btn = ui.Button((450, 646, 380, 62), lambda: i18n.t("done_reading"), ui.GREEN, 28, sound="page")
        self.next_btn = ui.Button((470, 560, 340, 66), lambda: i18n.t("next"), ui.ACCENT, 28)
        self.save_btn = ui.Button((340, 590, 280, 64), lambda: i18n.t("save"), ui.GREEN, 26, sound="new_record")
        self.title_btn = ui.Button((660, 590, 280, 64), lambda: i18n.t("to_title"), ui.BLUE, 24)
        self.new_level()

    # ------------------------------------------------------------ level flow
    def new_level(self):
        seen = set(self.app.store.seen) | self.run_seen
        self.story = story.generate(self.diff, self.level, self.rng, seen)
        self.run_seen.add(self.story.signature)
        self.app.store.remember(self.story.signature)
        self.state = "ready"
        self.state_time = 0.0
        self.time_left = float(TIME_LIMIT)
        self.read_time = 0.0
        self.total_time = 0.0
        self.bonus = 0
        self.correct_pts = 0
        self.penalty = 0
        self.errors = 0
        self.first_try = 0
        self.qi = 0
        self.timed_out = False
        self.last_tick = None
        self.min_read = max(5.0, self.story.words * SECONDS_PER_WORD)
        self.story_surface = None
        self.story_lang = None
        self.confetti.parts.clear()
        self.floats.items.clear()
        self.app.audio.play("page")

    def start_reading(self):
        self.state = "reading"
        self.state_time = 0.0

    def finish_reading(self, timed_out=False):
        self.read_time = min(TIME_LIMIT, self.state_time)
        self.timed_out = timed_out
        self.bonus = 0 if timed_out else int(self.time_left) * BONUS_PER_SECOND
        if timed_out:
            self.app.audio.play("time_up")
            self.state = "timeup"
        else:
            self.state = "questions"
            self.begin_question(0)
        self.state_time = 0.0

    def begin_question(self, i):
        self.qi = i
        self.q = self.story.questions[i]
        self.wrong = 0
        self.disabled = set()
        self.shake = {}
        self.resolved = None          # "correct" / "reveal"
        self.resolve_time = 0.0
        self.layout_cards()

    def layout_cards(self):
        n = len(self.q.options)
        labels = self.diff != "hard"
        if n <= 4:
            cols, rows = n, 1
            cw, ch = (250, 290) if labels else (250, 250)
        else:
            cols, rows = 3, 2
            cw, ch = (230, 212) if labels else (230, 200)
        gap = 28
        area_top, area_bottom = 252, 700
        total_h = rows * ch + (rows - 1) * gap
        y0 = area_top + (area_bottom - area_top - total_h) // 2
        self.cards = []
        for i in range(n):
            r, c = divmod(i, cols)
            in_row = min(cols, n - r * cols)
            x0 = (W - (in_row * cw + (in_row - 1) * gap)) // 2
            self.cards.append(pygame.Rect(x0 + c * (cw + gap), y0 + r * (ch + gap), cw, ch))
        self.hover_card = None
        self.card_lift = [0.0] * n

    def choose(self, i):
        if self.resolved or i in self.disabled or i >= len(self.q.options):
            return
        rect = self.cards[i]
        if i == self.q.answer:
            pts = CORRECT_POINTS[self.diff] // (1 if self.wrong == 0 else 2)
            self.correct_pts += pts
            if self.wrong == 0:
                self.first_try += 1
            self.resolved = "correct"
            self.app.audio.play("correct")
            self.floats.add(f"+{pts}", (rect.centerx, rect.y - 10), ui.GREEN, 44)
            self.confetti.burst(rect.center, 46)
        else:
            pen = WRONG_POINTS[self.diff]
            self.penalty += pen
            self.errors += 1
            self.wrong += 1
            self.disabled.add(i)
            self.shake[i] = 0.5
            self.app.audio.play("wrong")
            self.floats.add(f"-{pen}", (rect.centerx, rect.y - 10), ui.RED, 40)
            if self.wrong >= MAX_WRONG:
                self.resolved = "reveal"
                self.app.audio.play("reveal")
        self.resolve_time = 0.0

    def level_score(self):
        return max(0, self.bonus + self.correct_pts - self.penalty)

    def end_level(self):
        self.total_time = self.read_time + self.question_time
        score = self.level_score()
        self.total += score
        self.cleared = self.level
        self.app.store.add_level({
            "difficulty": self.diff, "level": self.level, "read_time": round(self.read_time, 1),
            "total_time": round(self.total_time, 1), "score": score, "errors": self.errors,
            "first_try": self.first_try, "questions": len(self.story.questions), "words": self.story.words,
            "timed_out": self.timed_out,
        })
        self.state = "result"
        self.state_time = 0.0
        self.floats.items.clear()
        self.rows_shown = 0
        self.app.audio.play("level_clear")
        self.confetti.rain(70)
        self.next_btn.label = (lambda: i18n.t("next")) if self.level < story.LEVELS else (lambda: i18n.t("results"))

    def go_final(self):
        self.state = "final"
        self.state_time = 0.0
        self.name = ""
        self.saved = False
        self.qualifies = self.app.store.qualifies(self.total)
        self.paused = False
        if self.qualifies:
            pygame.key.start_text_input()
            self.app.audio.play("new_record")
        else:
            self.app.audio.play("fanfare" if self.cleared >= story.LEVELS else "level_clear")
        if self.cleared >= story.LEVELS:
            self.confetti.rain(160)
        self.save_btn.visible = self.qualifies
        self.title_btn.rect.x = 660 if self.qualifies else 500

    def save_score(self):
        if self.saved:
            return
        self.app.store.add_score(self.name or "???", self.total, self.diff, self.cleared)
        self.saved = True
        pygame.key.stop_text_input()
        self.to_title()

    def to_title(self):
        from .title import TitleScene
        pygame.key.stop_text_input()
        self.app.switch(TitleScene(self.app))

    def quit_run(self):
        if self.total > 0:
            self.go_final()
        else:
            self.to_title()

    # ----------------------------------------------------------------- input
    def handle(self, event):
        if self.paused:
            if self.resume_btn.clicked(event, self.app) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.paused = False
            elif self.quit_btn.clicked(event, self.app):
                self.paused = False
                self.quit_run()
            return
        if self.state in ("ready", "reading", "questions", "timeup") and (
                self.pause_btn.clicked(event, self.app) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
            self.paused = True
            return
        if self.state == "ready":
            if self.start_btn.clicked(event, self.app) or (
                    event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE)):
                self.start_reading()
        elif self.state == "reading":
            self.done_btn.enabled = self.state_time >= self.min_read
            if self.done_btn.clicked(event, self.app) or (
                    self.done_btn.enabled and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                self.finish_reading()
        elif self.state == "questions":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(self.cards):
                    if rect.collidepoint(event.pos):
                        self.choose(i)
            elif event.type == pygame.KEYDOWN and pygame.K_1 <= event.key <= pygame.K_9:
                self.choose(event.key - pygame.K_1)
        elif self.state == "result":
            if self.state_time > 0.6 and (self.next_btn.clicked(event, self.app) or (
                    event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE))):
                if self.level >= story.LEVELS:
                    self.go_final()
                else:
                    self.level += 1
                    self.new_level()
        elif self.state == "final":
            if self.qualifies and not self.saved:
                if event.type == pygame.TEXTINPUT:
                    for ch in event.text:
                        if len(self.name) < 12 and ch.isprintable():
                            self.name += ch
                            self.app.audio.play("type")
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.name = self.name[:-1]
                    elif event.key == pygame.K_RETURN:
                        self.save_score()
                if self.save_btn.clicked(event, self.app):
                    self.save_score()
            if self.title_btn.clicked(event, self.app):
                self.to_title()

    # ---------------------------------------------------------------- update
    def update(self, dt):
        super().update(dt)
        self.bg.update(dt)
        self.confetti.update(dt)
        self.floats.update(dt)
        buttons = [self.pause_btn]
        if self.paused:
            for b in (self.resume_btn, self.quit_btn):
                b.update(dt, self.app)
            return
        self.state_time += dt
        if self.state == "ready":
            buttons.append(self.start_btn)
        elif self.state == "reading":
            self.time_left = max(0.0, TIME_LIMIT - self.state_time)
            self.done_btn.enabled = self.state_time >= self.min_read
            self.done_btn.progress = self.state_time / self.min_read
            buttons.append(self.done_btn)
            sec = math.ceil(self.time_left)
            if sec <= 10 and sec != self.last_tick and sec > 0:
                self.last_tick = sec
                self.app.audio.play("tick")
            if self.time_left <= 0:
                self.finish_reading(timed_out=True)
        elif self.state == "timeup":
            if self.state_time > 1.6:
                self.state = "questions"
                self.state_time = 0.0
                self.begin_question(0)
        elif self.state == "questions":
            mouse = pygame.mouse.get_pos()
            hov = None
            for i, rect in enumerate(self.cards):
                if rect.collidepoint(mouse) and i not in self.disabled and not self.resolved:
                    hov = i
            if hov is not None and hov != self.hover_card:
                self.app.audio.play("hover")
            self.hover_card = hov
            for i in range(len(self.cards)):
                target = 1.0 if i == hov else 0.0
                self.card_lift[i] += (target - self.card_lift[i]) * min(1.0, dt * 14)
            for k in list(self.shake):
                self.shake[k] -= dt
                if self.shake[k] <= 0:
                    del self.shake[k]
            if self.resolved:
                self.resolve_time += dt
                if self.resolve_time > (1.3 if self.resolved == "correct" else 2.0):
                    if self.qi + 1 < len(self.story.questions):
                        self.begin_question(self.qi + 1)
                    else:
                        self.question_time = self.state_time
                        self.end_level()
        elif self.state == "result":
            buttons.append(self.next_btn)
            shown = min(5, int(self.state_time / 0.4))
            if shown > self.rows_shown:
                self.rows_shown = shown
                self.app.audio.play("count")
        elif self.state == "final":
            buttons += [self.save_btn, self.title_btn]
        for b in buttons:
            b.update(dt, self.app)

    # ------------------------------------------------------------------ draw
    def draw(self, surf):
        self.bg.draw(surf, hills=self.state in ("result", "final", "ready"))
        if self.state in ("ready", "reading", "timeup"):
            self.draw_reading(surf)
        elif self.state == "questions":
            self.draw_questions(surf)
        elif self.state == "result":
            self.draw_result(surf)
        elif self.state == "final":
            self.draw_final(surf)
        if self.state != "final":
            self.draw_hud(surf)
        self.confetti.draw(surf)
        self.floats.draw(surf)
        if self.paused:
            self.draw_pause(surf)

    def draw_hud(self, surf):
        diff_col = ui.DIFF_COLORS[self.diff]
        ui.chip(surf, i18n.t("level_of", n=self.level, total=story.LEVELS), (18, 18), diff_col, 22)
        ui.chip(surf, i18n.t(self.diff), (24, 62), ui.darker(diff_col, 0.8), 16, pad=(12, 3))
        live = self.total + (self.level_score() if self.state in ("questions",) else 0)
        r = ui.chip(surf, f"{i18n.t('score')}  {live:,}", (1192, 18), ui.GOLD, 22, "topright", INK)
        del r
        if self.state in ("ready", "reading", "questions", "timeup"):
            self.pause_btn.draw(surf)
        if self.state in ("ready", "reading", "timeup"):
            self.draw_timer(surf)
        elif self.state == "questions":
            for i in range(3):
                c = (640 - 40 + i * 40, 40)
                done = i < self.qi or (i == self.qi and self.resolved)
                col = ui.GREEN if done else (ui.ACCENT if i == self.qi else (220, 214, 232))
                pygame.draw.circle(surf, WHITE, c, 15)
                pygame.draw.circle(surf, col, c, 11)
            ui.text(surf, i18n.t("question_n", n=self.qi + 1), (640, 70), 18, INK, True, "midtop", outline=WHITE)

    def draw_timer(self, surf):
        bar = pygame.Rect(360, 24, 600, 34)
        frac = self.time_left / TIME_LIMIT
        if frac > 0.5:
            col = ui.mix((255, 196, 60), ui.GREEN, (frac - 0.5) * 2)
        else:
            col = ui.mix(ui.RED, (255, 196, 60), frac * 2)
        img, pad = ui.shadow(bar.w, bar.h, bar.h // 2, 8, 40)
        surf.blit(img, (bar.x - pad, bar.y - pad + 4))
        pygame.draw.rect(surf, WHITE, bar, border_radius=bar.h // 2)
        inner = bar.inflate(-8, -8)
        fill = inner.copy()
        fill.w = max(fill.h, int(inner.w * frac))
        if frac > 0:
            pygame.draw.rect(surf, col, fill, border_radius=fill.h // 2)
            gloss = pygame.Rect(fill.x + 6, fill.y + 3, max(0, fill.w - 12), fill.h // 3)
            pygame.draw.rect(surf, ui.lighter(col, 0.45), gloss, border_radius=gloss.h // 2)
        sec = math.ceil(self.time_left)
        pulse = 1.0 + (0.12 * abs(math.sin(self.state_time * math.pi)) if sec <= 10 and self.state == "reading" else 0)
        c = (bar.x - 6, bar.centery)
        r = int(30 * pulse)
        pygame.draw.circle(surf, ui.darker(col, 0.7), (c[0], c[1] + 3), r + 4)
        pygame.draw.circle(surf, WHITE, c, r + 4)
        pygame.draw.circle(surf, col, c, r)
        ui.text(surf, str(sec), c, int(26 * pulse), WHITE, True, "center", shadow=ui.darker(col, 0.6))

    # -- reading
    def build_story_surface(self):
        lang = i18n.lang()
        paras = self.story.text(lang)
        ja = lang == "ja"
        area = TEXT_AREA
        for size in (32, 30, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16):
            spacing = 1.72 if ja else 1.55
            lh = int(size * spacing)
            gap = int(lh * 0.45)
            wrapped = [ui.wrap(p, size, area.w - int(size * 1.5)) for p in paras]
            height = sum(len(w) for w in wrapped) * lh + gap * (len(wrapped) - 1)
            if height <= area.h:
                break
        surf = pygame.Surface(area.size, pygame.SRCALPHA)
        y = 0
        self.ruled = []
        for wi, lines in enumerate(wrapped):
            for li, ln in enumerate(lines):
                indent = (size * (1 if ja else 1.5)) if li == 0 else 0
                ui.text(surf, ln if not (ja and li == 0) else ln, (indent if li == 0 else 0, y + (lh - size) // 2 - 2),
                        size, INK, False)
                self.ruled.append(area.y + y + lh - 4)
                y += lh
            y += gap
        self.story_surface = surf
        self.story_lang = lang
        self.line_height = lh

    def draw_paper(self, surf, rect):
        ui.panel(surf, rect, PAPER, 26)
        pygame.draw.rect(surf, ui.PAPER_EDGE, rect, 3, border_radius=26)
        # a ribbon bookmark
        rib = pygame.Rect(rect.right - 90, rect.y - 8, 36, 64)
        pygame.draw.rect(surf, ui.RED, rib)
        pygame.draw.polygon(surf, ui.PAPER, [(rib.x, rib.bottom), (rib.centerx, rib.bottom - 14), (rib.right, rib.bottom)])

    def draw_reading(self, surf):
        rect = CARD
        self.draw_paper(surf, rect)
        if self.state == "ready" or self.paused:
            self.draw_ready(surf)
            return
        if self.story_surface is None or self.story_lang != i18n.lang():
            self.build_story_surface()
        title = self.story.title(i18n.lang())
        ui.text(surf, title, (rect.centerx, rect.y + 26), 34, ui.darker(ui.ACCENT, 0.8), True, "midtop")
        pygame.draw.line(surf, ui.PAPER_EDGE, (rect.x + 40, rect.y + 76), (rect.right - 40, rect.y + 76), 3)
        for y in self.ruled:
            pygame.draw.line(surf, (226, 232, 246), (rect.x + 36, y), (rect.right - 36, y), 1)
        pygame.draw.line(surf, (250, 200, 206), (TEXT_AREA.x - 18, rect.y + 84), (TEXT_AREA.x - 18, rect.bottom - 18), 2)
        surf.blit(self.story_surface, TEXT_AREA)
        if self.state == "reading":
            self.done_btn.draw(surf)
            label = i18n.t("read_prompt") if self.state_time < 8 else i18n.t("read_prompt2")
            ui.owl_guide(surf, (8, 630), self.time, 84, label, 300, 16)
            if not self.done_btn.enabled:
                ui.text(surf, i18n.t("keep_reading"), (self.done_btn.rect.right + 16, self.done_btn.rect.centery), 18,
                        INK_SOFT, True, "midleft", outline=WHITE)
        elif self.state == "timeup":
            veil = pygame.Surface((W, H), pygame.SRCALPHA)
            veil.fill((40, 20, 60, 110))
            surf.blit(veil, (0, 0))
            s = 1.0 + 0.1 * math.sin(self.state_time * 8)
            ui.text(surf, i18n.t("time_up"), (W // 2, H // 2), int(84 * s), ui.RED, True, "center", outline=WHITE)

    def draw_ready(self, surf):
        rect = CARD
        diff_col = ui.DIFF_COLORS[self.diff]
        ui.text(surf, i18n.t("level_n", n=self.level), (rect.centerx, rect.y + 60), 70, diff_col, True, "midtop",
                shadow=ui.darker(diff_col, 0.6), outline=WHITE)
        ui.chip(surf, i18n.t(self.diff), (rect.centerx, rect.y + 160), diff_col, 24, "midtop")
        if self.paused:
            ui.text(surf, i18n.t("story_hidden"), (rect.centerx, rect.y + 240), 24, INK_SOFT, True, "midtop")
            return
        # a little row of story pictures, just for fun (never the answers' order)
        names = sorted(self.story.mentions)
        random.Random(self.story.signature).shuffle(names)
        pics = [n for n in names if n not in art.PLACES][:5]
        x0 = rect.centerx - (len(pics) * 96) // 2
        for i, n in enumerate(pics):
            bob = math.sin(self.time * 2 + i) * 6
            surf.blit(art.picture(n, 84), (x0 + i * 96 + 6, rect.y + 236 + bob))
        ui.text(surf, i18n.t("read_prompt"), (rect.centerx, rect.y + 352), 26, INK, True, "midtop")
        ui.text(surf, i18n.t("read_prompt2"), (rect.centerx, rect.y + 392), 22, INK_SOFT, True, "midtop")
        self.start_btn.rect.centerx = rect.centerx
        self.start_btn.rect.y = rect.y + 448
        self.start_btn.draw(surf)

    # -- questions
    def draw_questions(self, surf):
        q = self.q
        ui.owl_guide(surf, (40, 96), self.time, 130, q.text(i18n.lang()), 1010, 30)
        labels = self.diff != "hard"
        for i, (rect, opt) in enumerate(zip(self.cards, q.options)):
            r = rect.copy()
            lift = int(self.card_lift[i] * 8)
            r.y -= lift
            if i in self.shake:
                r.x += int(math.sin(self.shake[i] * 60) * 10 * self.shake[i] * 2)
            is_answer = i == q.answer
            state = None
            if self.resolved and is_answer:
                state = "right"
            elif i in self.disabled:
                state = "wrong"
            border = None
            if state == "right":
                glow = 0.5 + 0.5 * math.sin(self.resolve_time * 8)
                border = ui.GREEN if self.resolved == "correct" else ui.mix(ui.GOLD, ui.ACCENT, glow)
            elif self.hover_card == i:
                border = ui.ACCENT
            ui.panel(surf, r, WHITE, 22, border=border, border_w=6 if border else 3)
            pic_size = min(r.w - 40, r.h - (70 if labels else 36))
            if opt.count:
                img = art.count_picture(opt.art, opt.count, pic_size)
            else:
                img = art.picture(opt.art, pic_size, opt.color)
            py = r.y + 16 if labels else r.centery - pic_size // 2
            surf.blit(img, img.get_rect(midtop=(r.centerx, py)))
            if labels:
                label = opt.ja if i18n.lang() == "ja" else opt.en
                size = 24
                while size > 14 and ui.font(size, True).size(label)[0] > r.w - 24:
                    size -= 1
                ui.text(surf, label, (r.centerx, r.bottom - 34), size, INK, True, "center")
            badge = (r.x + 22, r.y + 22)
            pygame.draw.circle(surf, ui.lighter(ui.INK_SOFT, 0.6), badge, 15)
            ui.text(surf, str(i + 1), badge, 17, WHITE, True, "center")
            if state == "wrong":
                veil = pygame.Surface(r.size, pygame.SRCALPHA)
                pygame.draw.rect(veil, (255, 255, 255, 150), veil.get_rect(), border_radius=22)
                surf.blit(veil, r)
                c = r.center
                for d in ((-1, -1, 1, 1), (-1, 1, 1, -1)):
                    pygame.draw.line(surf, ui.RED, (c[0] + d[0] * 40, c[1] + d[1] * 40), (c[0] + d[2] * 40, c[1] + d[3] * 40), 12)
            if state == "right":
                c = (r.right - 24, r.y + 24)
                pygame.draw.circle(surf, WHITE, c, 24)
                pygame.draw.circle(surf, ui.GREEN if self.resolved == "correct" else ui.GOLD, c, 20)
                pygame.draw.lines(surf, WHITE, False, [(c[0] - 10, c[1]), (c[0] - 3, c[1] + 8), (c[0] + 11, c[1] - 8)], 5)
        if self.resolved:
            msg = i18n.t("correct") if self.resolved == "correct" else i18n.t("reveal")
            col = ui.GREEN if self.resolved == "correct" else ui.ACCENT
            ui.text(surf, msg, (W // 2, 236), 34, col, True, "center", outline=WHITE)
        elif self.wrong:
            ui.text(surf, i18n.t("wrong"), (W // 2, 236), 28, ui.RED, True, "center", outline=WHITE)
        else:
            ui.text(surf, i18n.t("point"), (W // 2, 236), 22, INK_SOFT, True, "center", outline=WHITE)

    # -- results
    def draw_result(self, surf):
        rect = pygame.Rect(300, 96, 680, 548)
        ui.panel(surf, rect, PAPER, 30)
        stars = 3 if self.errors == 0 else 2 if self.errors <= 2 else 1
        for i in range(3):
            t = max(0.0, min(1.0, (self.state_time - i * 0.2) * 3))
            r = int((30 if i != 1 else 40) * (0.4 + 0.6 * t) + 4 * math.sin(self.time * 3 + i))
            c = (rect.centerx + (i - 1) * 90, rect.y + 58 - (12 if i == 1 else 0))
            ui.star(surf, c, r, ui.GOLD if i < stars else (220, 214, 228))
        ui.text(surf, i18n.t("level_clear", n=self.level), (rect.centerx, rect.y + 110), 46,
                ui.ACCENT, True, "midtop", shadow=ui.darker(ui.ACCENT, 0.6))
        rows = [
            (i18n.t("time_bonus", s=self.bonus // BONUS_PER_SECOND), f"+{self.bonus:,}", ui.TEAL),
            (i18n.t("correct_pts"), f"+{self.correct_pts:,}", ui.GREEN),
            (i18n.t("mistakes", n=self.errors), f"-{self.penalty:,}", ui.RED),
            (i18n.t("level_score"), f"{self.level_score():,}", INK),
            (i18n.t("total"), f"{self.total:,}", ui.darker(ui.ACCENT, 0.8)),
        ]
        y = rect.y + 190
        for i, (label, value, col) in enumerate(rows[: self.rows_shown]):
            if i == 3:
                pygame.draw.line(surf, ui.PAPER_EDGE, (rect.x + 60, y - 6), (rect.right - 60, y - 6), 3)
            big = i >= 3
            ui.text(surf, label, (rect.x + 70, y), 28 if big else 24, INK if big else INK_SOFT, True)
            ui.text(surf, value, (rect.right - 70, y), 32 if big else 26, col, True, "topright")
            y += 58 if big else 50
        if self.state_time > 0.6:
            self.next_btn.rect.centerx = rect.centerx
            self.next_btn.rect.y = rect.bottom - 90
            self.next_btn.draw(surf)

    def draw_final(self, surf):
        rect = pygame.Rect(240, 70, 800, 600)
        ui.panel(surf, rect, PAPER, 30)
        done = self.cleared >= story.LEVELS
        ui.title_logo(surf, (rect.centerx, rect.y + 60), self.time, 50)
        head = i18n.t("complete") if done else i18n.t("run_over")
        ui.text(surf, head, (rect.centerx, rect.y + 110), 40, ui.ACCENT, True, "midtop", shadow=ui.darker(ui.ACCENT, 0.6))
        ui.text(surf, i18n.t("final_score"), (rect.centerx, rect.y + 180), 24, INK_SOFT, True, "midtop")
        s = 1 + 0.03 * math.sin(self.time * 4)
        ui.text(surf, f"{self.total:,}", (rect.centerx, rect.y + 250), int(72 * s), ui.GOLD, True, "center",
                shadow=ui.darker(ui.GOLD, 0.6), outline=WHITE)
        ui.chip(surf, f"{i18n.t(self.diff)}  ·  {i18n.t('levels_cleared', n=self.cleared)}", (rect.centerx, rect.y + 300),
                ui.DIFF_COLORS[self.diff], 22, "midtop")
        if self.qualifies and not self.saved:
            ui.text(surf, i18n.t("new_record"), (rect.centerx, rect.y + 370), 26, ui.darker(ui.GREEN, 0.8), True, "midtop")
            box = pygame.Rect(rect.centerx - 220, rect.y + 416, 440, 64)
            pygame.draw.rect(surf, WHITE, box, border_radius=16)
            pygame.draw.rect(surf, ui.GREEN, box, 4, border_radius=16)
            caret = "|" if int(self.time * 2) % 2 == 0 else " "
            ui.text(surf, self.name + caret, box.center, 32, INK, True, "center")
        else:
            for i in range(5):
                ui.star(surf, (rect.centerx + (i - 2) * 70, rect.y + 430 + 8 * math.sin(self.time * 3 + i)), 24,
                        ui.GOLD if i < max(1, round(self.cleared / 2)) else (220, 214, 228))
        self.save_btn.rect.y = self.title_btn.rect.y = rect.bottom - 100
        self.save_btn.draw(surf)
        self.title_btn.draw(surf)

    def draw_pause(self, surf):
        veil = pygame.Surface((W, H), pygame.SRCALPHA)
        veil.fill((30, 20, 50, 150))
        surf.blit(veil, (0, 0))
        rect = pygame.Rect(400, 200, 480, 350)
        ui.panel(surf, rect, PAPER, 28)
        ui.text(surf, i18n.t("paused"), (rect.centerx, rect.y + 40), 46, ui.ACCENT, True, "midtop")
        ui.text(surf, i18n.t("story_hidden"), (rect.centerx, rect.y + 104), 18, INK_SOFT, True, "midtop")
        self.resume_btn.draw(surf)
        self.quit_btn.draw(surf)
