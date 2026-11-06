"""Sound effects and the ambient background music. Silent (never fatal) without a sound card."""
import os

import pygame

from . import paths

SOUNDS = ("click", "hover", "correct", "wrong", "tick", "page", "start", "level_clear", "fanfare",
          "time_up", "count", "reveal", "new_record", "type")
TRACKS = {"title": "bgm_title.wav", "game": "bgm_game.wav"}


class Audio:
    def __init__(self, bgm_on=True):
        self.ok = False
        self.sounds = {}
        self.bgm_on = bgm_on
        self.track = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 2, 1024)
            pygame.mixer.set_num_channels(16)
            self.ok = True
        except pygame.error:
            return
        for name in SOUNDS:
            path = paths.asset("audio", name + ".wav")
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                except pygame.error:
                    pass
        volumes = {"hover": 0.25, "tick": 0.5, "type": 0.35, "count": 0.35, "click": 0.6}
        for name, snd in self.sounds.items():
            snd.set_volume(volumes.get(name, 0.75))

    def play(self, name):
        snd = self.sounds.get(name)
        if snd:
            snd.play()

    def music(self, track):
        """Switch the looping background track (title / game)."""
        if track == self.track and (pygame.mixer.music.get_busy() or not self.bgm_on):
            return
        self.track = track
        if not self.ok or not self.bgm_on:
            return
        path = paths.asset("audio", TRACKS[track])
        if not os.path.exists(path):
            return
        try:
            pygame.mixer.music.fadeout(400)
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.55)
            pygame.mixer.music.play(-1, fade_ms=1800)
        except pygame.error:
            pass

    def set_bgm(self, on):
        self.bgm_on = on
        if not self.ok:
            return
        if on:
            track, self.track = self.track or "title", None
            self.music(track)
        else:
            pygame.mixer.music.fadeout(500)

    def stop(self):
        if self.ok:
            pygame.mixer.music.stop()
            pygame.mixer.stop()
