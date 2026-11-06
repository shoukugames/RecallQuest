# Reporting a Bug — バグの報告

Thank you for helping make RecallQuest better!
RecallQuestをよりよくするためのご協力、ありがとうございます！

**Email:** info@shoukugames.org
**Website:** https://shoukugames.org/

## Before you report

1. Check that you have the latest version (the version is shown at the bottom right of the
   title screen, or run `recallquest --version`).
2. Try to make the problem happen again, and note the steps.

## What to include

Please copy this template into your email:

```
Subject: [RecallQuest v0.1.0] short description of the problem

Version:          (e.g. v0.1.0)
Operating system: (e.g. Ubuntu 24.04, Windows 11)
Installed from:   (.deb / .exe / source)
Language:         (English / 日本語)
Difficulty/level: (e.g. Hard, level 7)

What happened:
What I expected:
Steps to make it happen:
1.
2.
3.

Screenshot or story text (if a story or question looked wrong):
```

### A story or question looks wrong?

The stories are randomly generated, so please include:
- a screenshot of the story (or copy the text), and
- the question, the pictures shown, and which answer the game said was right.

### The game will not start?

Run it from a terminal and include anything it prints:
- Linux: `recallquest`
- Windows: `RecallQuest-v0.1.0.exe` from Command Prompt

You can also run the built-in self-test and send the result:
`recallquest --smoke-test result.txt`

### Saved data

Scores and the parents' record are stored in `~/.local/share/recallquest/` (Linux) or
`%APPDATA%\RecallQuest\` (Windows). If a save file is damaged, the game renames it to
`*.corrupt` and starts fresh. Attaching that file can help.

## Privacy

RecallQuest works fully offline and never sends any data anywhere.
Please don't include personal information about your child in a report.
