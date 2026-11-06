# RecallQuest — リコールクエスト

**Read a silly story. Remember everything!**
へんてこなお話を読んで、ぜんぶおぼえよう！

RecallQuest is a bilingual (English / Japanese) reading comprehension game.
Each level makes a brand-new silly story. You have 120 seconds to read it.
Then you answer three questions by pointing at the right character, animal,
object or place.

- **Recommended ages:** 10+
- **Version:** v0.1.0 (released 2026-11-07)
- **Platforms:** Linux (`.deb`) and Windows (`.exe`)
- **License:** GNU GPL v3.0 (see `LICENSE`)

## How to play

1. On the title screen, pick a language (English / 日本語), turn the music on or off,
   and pick a difficulty: **Easy**, **Medium** or **Hard**.
2. Press **Play**. Read the story before the countdown timer at the top reaches zero.
3. Press **I'm done reading!** when you finish. **Every unused second is worth 100 points.**
4. Answer 3 questions by clicking the right picture (or pressing keys 1–6).
   - A correct answer scores points (Easy 500, Medium 750, Hard 1000; half on the second try).
   - **A wrong answer takes points away** (Easy 300, Medium 400, Hard 500).
     After two misses the answer is shown.
5. There are 10 levels in a run. Each level's story is longer and trickier.
   A high final score goes into the **Top 10**.

Keys: `Esc` pauses (the story hides while paused), `F11` switches to full screen,
`Enter` confirms.

## Difficulty

| | Easy | Medium | Hard |
|---|---|---|---|
| Story length (level 1 → 10) | about 50 → 115 words | about 90 → 190 words | about 160 → 270 words |
| Characters | 1–2 | 2–3, with silly names | 3–4, with silly names |
| Pictures per question | 3–4, labelled | 4–5, labelled | 6, no labels |
| Question types | who / what / where | + colors, numbers, names | + first/last, "who went with", "NOT in the story", trick sentences |

## Stories

Every story is generated offline, in English and Japanese together, from word lists and
sentence patterns inside the game (`recallquest/story.py`). There are 23 characters and
animals, 27 foods and objects, 9 places, 7 colors and 28 silly names. Questions come
only from facts with exactly one correct answer.
**No story ever repeats.** The game remembers the stories already read, even between sessions.

## For Parents

The **For Parents** screen shows this computer's record. It includes levels played,
first-try accuracy, average reading time, average time per level, total mistakes,
best score and total play time. It also has a chart of the last 20 levels, progress
by difficulty and a table of recent levels (date, reading time, total time, words,
mistakes, score). A summary also appears on the title screen. **Reset all data**
clears everything (it asks first).

Saved data lives in `~/.local/share/recallquest/` (Linux) or `%APPDATA%\RecallQuest\`
(Windows). Set `RECALLQUEST_DATA` to use another folder.

## Install

- **Linux (Debian/Ubuntu):** `sudo apt install ./dist/recallquest_v0.1.0_amd64.deb`, then run
  `recallquest` or open RecallQuest from the Games menu.
- **Windows:** run `dist/RecallQuest-v0.1.0.exe` (one file, nothing to install).

## Run from source

```bash
python3 -m pip install -r requirements.txt
python3 run_game.py            # --windowed, --version, --smoke-test <file>
```

## Build

```bash
./build.sh                     # both installers into dist/
packaging/build_linux.sh       # dist/recallquest_v0.1.0_amd64.deb
packaging/build_windows.sh     # dist/RecallQuest-v0.1.0.exe (built under Wine)
```

The Windows build downloads Python for Windows into a private Wine prefix in `build/` on its
first run. It needs `wine`, `xvfb-run` and `curl`. Each build unpacks the result and runs the
automatic self-test (`--smoke-test`), which plays all 10 levels on every difficulty in both languages.

Developer tools (need `requirements-dev.txt`):

```bash
python3 -m pytest              # story generator and save-data tests
python3 tools/make_audio.py    # regenerate the music and sound effects
python3 tools/make_icon.py     # regenerate the icon
```

## Project layout

```
recallquest/      game code (story.py generator, art.py pictures, scenes/ screens)
assets/           fonts, generated audio, icon
packaging/        PyInstaller spec, .desktop file, build scripts
tools/            audio and icon generators
tests/            pytest suite
```

## Credits

- **Creator:** Shawn Rapaz
- **Developed with:** Claude Code (Anthropic)
- **Website:** https://shoukugames.org/
- **Email:** info@shoukugames.org
- **Font:** M PLUS Rounded 1c, SIL Open Font License 1.1 (`assets/fonts/MPLUSRounded1c-OFL.txt`)
- **Music, sounds and pictures:** original, generated in code

Found a bug? See [BUGREPORT.md](BUGREPORT.md).

## License

Copyright (C) 2026 Shawn Rapaz.
This program is free software: you can redistribute it and/or modify it under the terms of the
GNU General Public License as published by the Free Software Foundation, version 3 of the
License or (at your option) any later version. It is distributed WITHOUT ANY WARRANTY.
See `LICENSE` for the full text.
