"""Tiny high-score store kept in the user's home directory."""

import json
import os
from pathlib import Path

SCORE_FILE = Path(os.environ.get("TERMINAL_ARCADE_SCORES", Path.home() / ".terminal_arcade_scores.json"))


def _load():
    try:
        return json.loads(SCORE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def get_best(game):
    """Return the stored best for `game`, or None if it has never been played."""
    return _load().get(game)


def submit(game, score, lower_is_better=False):
    """Record `score` if it beats the stored best. Returns True on a new record."""
    data = _load()
    old = data.get(game)
    better = old is None or (score < old if lower_is_better else score > old)
    if not better or (not lower_is_better and score <= 0):
        return False
    data[game] = score
    try:
        SCORE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except OSError:
        pass
    return True
