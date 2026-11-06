#!/usr/bin/env python3
"""Draw the game icon from the game's own art: assets/icon.png and assets/icon.ico (needs Pillow)."""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)

import pygame  # noqa: E402
from PIL import Image  # noqa: E402

from recallquest import art, ui  # noqa: E402

pygame.init()
pygame.display.set_mode((16, 16))
SIZE = 512
canvas = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
back = ui.gradient((SIZE, SIZE), (255, 170, 110), (255, 120, 150)).convert_alpha()
mask = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=110)
back.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
canvas.blit(back, (0, 0))
for x, y, r in ((90, 90, 30), (420, 120, 22), (110, 400, 18)):
    art.circ(canvas, (255, 240, 170), x, y, r, 0)
canvas.blit(art.picture("owl", 360), (76, 20))
canvas.blit(art.picture("book", 230, "blue"), (140, 270))
pygame.draw.rect(canvas, (255, 255, 255), canvas.get_rect(), 10, border_radius=110)
out = os.path.join(ROOT, "assets")
pygame.image.save(canvas, os.path.join(out, "icon.png"))
img = Image.open(os.path.join(out, "icon.png"))
img.save(os.path.join(out, "icon.ico"), sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("icon written")
