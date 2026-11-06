"""Window, main loop and screen switching."""
import os
import sys

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame  # noqa: E402

from . import __version__, i18n, paths, ui  # noqa: E402
from .audio import Audio  # noqa: E402
from .storage import Store  # noqa: E402


class Scene:
    music = "title"

    def __init__(self, app):
        self.app = app
        self.time = 0.0

    def enter(self):
        self.app.audio.music(self.music)

    def handle(self, event):
        pass

    def update(self, dt):
        self.time += dt

    def draw(self, surf):
        pass


class App:
    def __init__(self, windowed=False, smoke=False):
        pygame.init()
        pygame.display.set_caption(f"RecallQuest v{__version__}")
        try:
            pygame.display.set_icon(pygame.image.load(paths.asset("icon.png")))
        except (pygame.error, FileNotFoundError):
            pass
        flags = pygame.SCALED | pygame.RESIZABLE
        try:
            self.canvas = pygame.display.set_mode((ui.W, ui.H), flags, vsync=0 if smoke else 1)
        except pygame.error:
            self.canvas = pygame.display.set_mode((ui.W, ui.H), flags)
        self.smoke = smoke
        self.store = Store()
        i18n.LANG["current"] = self.store.settings["lang"]
        self.audio = Audio(self.store.settings["bgm"])
        self.clock = pygame.time.Clock()
        self.running = True
        self.scene = None
        if not windowed and not smoke and self.store.settings.get("fullscreen"):
            pygame.display.toggle_fullscreen()

    def set_language(self, lang):
        i18n.LANG["current"] = lang
        self.store.set("lang", lang)

    def switch(self, scene):
        self.scene = scene
        scene.enter()

    def present(self):
        pygame.display.flip()

    def run(self):
        from .scenes.title import TitleScene
        self.switch(TitleScene(self))
        while self.running:
            dt = min(self.clock.tick(60) / 1000.0, 0.05)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                    self.store.set("fullscreen", not self.store.settings.get("fullscreen", False))
                else:
                    self.scene.handle(event)
            self.scene.update(dt)
            self.scene.draw(self.canvas)
            self.present()
        self.audio.stop()
        pygame.quit()


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--version" in argv:
        print(f"RecallQuest {__version__}")
        return 0
    if "--smoke-test" in argv:
        i = argv.index("--smoke-test")
        out = argv[i + 1] if i + 1 < len(argv) else None
        from .smoke import smoke_test
        return smoke_test(out)
    App(windowed="--windowed" in argv).run()
    return 0
