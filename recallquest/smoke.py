"""Automatic self-test: visits every screen in both languages and plays full runs.

Used by the build scripts to prove a packaged game really starts and plays:
    recallquest --smoke-test result.txt
Set RECALLQUEST_SHOTS=<folder> to also save a screenshot of each screen.
"""
import os
import random
import sys
import tempfile
import traceback


def smoke_test(out_path=None):
    os.environ.setdefault("RECALLQUEST_DATA", tempfile.mkdtemp(prefix="recallquest-smoke-"))
    shots = os.environ.get("RECALLQUEST_SHOTS")
    lines = []
    ok = True
    try:
        import pygame

        from . import story
        from .app import App
        from .scenes.game import GameScene
        from .scenes.info import CreditsScene, HowToScene, ParentsScene
        from .scenes.title import TitleScene

        app = App(windowed=True, smoke=True)
        count = {"n": 0}

        def frames(scene, n=10, name=None):
            for _ in range(n):
                pygame.event.pump()
                scene.update(1 / 60)
                scene.draw(app.canvas)
                app.present()
            if shots and name:
                os.makedirs(shots, exist_ok=True)
                count["n"] += 1
                pygame.image.save(app.canvas, os.path.join(shots, f"{count['n']:02d}_{name}.png"))

        played = 0
        for language in ("en", "ja"):
            app.set_language(language)
            for diff in story.DIFFICULTIES:
                game = GameScene(app, diff, seed=hash((language, diff)) & 0xFFFF)
                app.switch(game)
                rng = random.Random(3)
                for level in range(1, story.LEVELS + 1):
                    snap = level in (1, 10) and (language == "en" or diff == "hard")
                    frames(game, 3, f"{language}_{diff}_{level}_ready" if snap and level == 1 else None)
                    game.start_reading()
                    frames(game, 5, f"{language}_{diff}_{level}_read" if snap else None)
                    game.state_time = game.min_read + 1
                    game.finish_reading()
                    for qi in range(3):
                        assert game.state == "questions" and game.qi == qi
                        if rng.random() < 0.4:
                            game.choose((game.q.answer + 1) % len(game.q.options))
                        frames(game, 4, f"{language}_{diff}_{level}_q{qi}" if snap and qi == 0 else None)
                        if not game.resolved:
                            game.choose(game.q.answer)
                        game.resolve_time = 9
                        frames(game, 2)
                    assert game.state == "result", game.state
                    game.state_time = 3
                    frames(game, 3, f"{language}_{diff}_{level}_result" if snap else None)
                    played += 1
                    if level < story.LEVELS:
                        game.level += 1
                        game.new_level()
                game.go_final()
                game.name = "SMOKE"
                frames(game, 4, f"{language}_{diff}_final" if language == "en" else None)
                if game.qualifies:
                    game.save_score()
            for cls in (TitleScene, HowToScene, CreditsScene, ParentsScene):
                scene = cls(app)
                app.switch(scene)
                frames(scene, 10, f"{language}_{cls.__name__}")
        lines.append(f"played {played} levels")
        assert len(app.store.scores) >= 1, "no score saved"
        assert len(app.store.history) == played, "levels not recorded"

        # a timed-out level still goes on to the questions with no time bonus
        game = GameScene(app, "easy", seed=5)
        app.switch(game)
        game.start_reading()
        game.state_time = 200
        frames(game, 2)
        assert game.state == "timeup" and game.bonus == 0
        frames(game, 110)
        assert game.state == "questions"
        lines.append("timeout ok")

        seen = set()
        r = random.Random(11)
        for i in range(600):
            story.generate(story.DIFFICULTIES[i % 3], i % 10 + 1, r, seen)
        assert len(seen) == 600
        lines.append("generator ok")
        app.set_language("en")
        app.audio.stop()
        pygame.quit()
    except Exception:  # noqa: BLE001 - report every failure
        ok = False
        lines.append("FAILED\n" + traceback.format_exc())
    text = ("OK " if ok else "") + "; ".join(lines)
    if out_path:
        with open(out_path, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    print(text, file=sys.stdout if ok else sys.stderr)
    return 0 if ok else 1
