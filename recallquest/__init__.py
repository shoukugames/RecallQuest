"""RecallQuest - a bilingual reading comprehension game for ages 10+."""
__version__ = "0.1.0"
RELEASE_DATE = "2026-11-07"

# True when running in a web browser (pygbag / WebAssembly).
import sys as _sys
WEB = _sys.platform == "emscripten"
