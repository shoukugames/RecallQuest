"""Settings, the top 10 table, the parents' record and seen stories, saved as JSON.

Files live in the per-user data folder so they survive updates and the game works
from a read-only install. A damaged file is set aside, never fatal.
"""
import json
import os
import sys
import tempfile
import time

TOP_N = 10
HISTORY_KEPT = 1000
SEEN_KEPT = 3000

DEFAULT_SETTINGS = {"lang": "en", "bgm": True, "difficulty": "easy"}


def data_dir():
    override = os.environ.get("RECALLQUEST_DATA")
    if override:
        path = override
    elif sys.platform == "win32":
        path = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "RecallQuest")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
        path = os.path.join(base, "recallquest")
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        path = os.path.join(tempfile.gettempdir(), "recallquest")
        os.makedirs(path, exist_ok=True)
    return path


def _load(name, default):
    path = os.path.join(data_dir(), name)
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, type(default)):
            return data
        raise ValueError("unexpected structure")
    except FileNotFoundError:
        return default
    except (OSError, ValueError):
        try:
            os.replace(path, path + ".corrupt")
        except OSError:
            pass
        return default


def _save(name, data):
    path = os.path.join(data_dir(), name)
    temp = path + ".tmp"
    try:
        with open(temp, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=1, ensure_ascii=False)
        os.replace(temp, path)
    except OSError as error:
        print(f"Could not save {name}: {error}", file=sys.stderr)


class Store:
    def __init__(self):
        self.settings = {**DEFAULT_SETTINGS, **_load("settings.json", {})}
        if self.settings.get("lang") not in ("en", "ja"):
            self.settings["lang"] = "en"
        if self.settings.get("difficulty") not in ("easy", "medium", "hard"):
            self.settings["difficulty"] = "easy"
        self.scores = [s for s in _load("scores.json", []) if isinstance(s, dict) and "score" in s]
        self.history = [h for h in _load("history.json", []) if isinstance(h, dict)]
        self.progress = _load("progress.json", {})
        self.seen = set(x for x in _load("seen.json", []) if isinstance(x, str))
        self._seen_order = list(self.seen)

    # settings
    def set(self, key, value):
        self.settings[key] = value
        _save("settings.json", self.settings)

    # top 10
    def qualifies(self, score):
        if score <= 0:
            return False
        return len(self.scores) < TOP_N or score > min(s["score"] for s in self.scores)

    def add_score(self, name, score, difficulty, level):
        entry = {"name": (name.strip() or "???")[:12], "score": int(score), "difficulty": difficulty,
                 "level": int(level), "date": time.strftime("%Y-%m-%d")}
        self.scores.append(entry)
        self.scores.sort(key=lambda s: -s["score"])
        self.scores = self.scores[:TOP_N]
        _save("scores.json", self.scores)
        return self.scores.index(entry) if entry in self.scores else -1

    # parents' record
    def add_level(self, record):
        record = {"date": time.strftime("%Y-%m-%d %H:%M"), **record}
        self.history.append(record)
        self.history = self.history[-HISTORY_KEPT:]
        _save("history.json", self.history)
        diff = record.get("difficulty")
        if diff and record.get("level", 0) > self.progress.get(diff, 0):
            self.progress[diff] = record["level"]
            _save("progress.json", self.progress)

    def summary(self):
        h = self.history
        n = len(h)
        questions = sum(r.get("questions", 3) for r in h)
        first = sum(r.get("first_try", 0) for r in h)
        return {
            "levels": n,
            "accuracy": (first / questions * 100) if questions else 0.0,
            "avg_read": (sum(r.get("read_time", 0) for r in h) / n) if n else 0.0,
            "avg_total": (sum(r.get("total_time", 0) for r in h) / n) if n else 0.0,
            "errors": sum(r.get("errors", 0) for r in h),
            "play_time": sum(r.get("total_time", 0) for r in h),
            "best_score": max([s["score"] for s in self.scores] + [0]),
            "progress": {d: self.progress.get(d, 0) for d in ("easy", "medium", "hard")},
        }

    # stories already read, so none repeats
    def remember(self, signature):
        if signature in self.seen:
            return
        self.seen.add(signature)
        self._seen_order.append(signature)
        if len(self._seen_order) > SEEN_KEPT:
            old = self._seen_order.pop(0)
            self.seen.discard(old)
        _save("seen.json", self._seen_order)

    def reset(self):
        self.scores, self.history, self.progress = [], [], {}
        self.seen, self._seen_order = set(), []
        for name, value in (("scores.json", []), ("history.json", []), ("progress.json", {}), ("seen.json", [])):
            _save(name, value)
