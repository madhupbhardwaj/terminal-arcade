"""Minesweeper: clear the field without stepping on a mine."""

import random
import time

from .. import scores
from ..term import BOLD, DIRECTION_KEYS, ENTER, ESC, RESET, SPACE, REVERSE, center, color, fg

NAME = "Minesweeper"
DESCRIPTION = "Reveal every safe square. Numbers count neighbouring mines."

DIFFICULTIES = {"1": ("Easy", 9, 9, 10), "2": ("Medium", 16, 12, 30), "3": ("Hard", 24, 14, 60)}
NUMBER_COLORS = {1: 33, 2: 34, 3: 196, 4: 93, 5: 124, 6: 37, 7: 250, 8: 244}
DELTA = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}


class MinesGame:
    def __init__(self, width, height, mines, rng=None):
        self.w, self.h, self.mine_count = width, height, mines
        self.rng = rng or random.Random()
        self.mines = set()
        self.revealed = set()
        self.flags = set()
        self.cursor = (width // 2, height // 2)
        self.started = False
        self.lost = False
        self.start_time = None
        self.end_time = None

    def neighbours(self, x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if (dx or dy) and 0 <= nx < self.w and 0 <= ny < self.h:
                    yield nx, ny

    def count(self, x, y):
        return sum((n in self.mines) for n in self.neighbours(x, y))

    def _lay_mines(self, safe):
        # first click is always safe, and so are its neighbours where possible
        forbidden = {safe, *self.neighbours(*safe)}
        cells = [(x, y) for x in range(self.w) for y in range(self.h) if (x, y) not in forbidden]
        if len(cells) < self.mine_count:
            cells = [(x, y) for x in range(self.w) for y in range(self.h) if (x, y) != safe]
        self.mines = set(self.rng.sample(cells, self.mine_count))
        self.started = True
        self.start_time = time.monotonic()

    def reveal(self, pos):
        if pos in self.flags or self.lost or self.won:
            return
        if not self.started:
            self._lay_mines(pos)
        if pos in self.revealed:
            # "chord": reveal neighbours if the number of flags matches
            nbrs = list(self.neighbours(*pos))
            if sum(n in self.flags for n in nbrs) == self.count(*pos):
                for n in nbrs:
                    if n not in self.revealed and n not in self.flags:
                        self._open(n)
        else:
            self._open(pos)
        if self.lost or self.won:
            self.end_time = time.monotonic()

    def _open(self, pos):
        if pos in self.mines:
            self.lost = True
            self.revealed.add(pos)
            return
        stack = [pos]
        while stack:
            p = stack.pop()
            if p in self.revealed or p in self.flags:
                continue
            self.revealed.add(p)
            if self.count(*p) == 0:
                stack.extend(n for n in self.neighbours(*p) if n not in self.revealed)

    def toggle_flag(self, pos):
        if pos not in self.revealed and not self.lost and not self.won:
            self.flags ^= {pos}

    @property
    def won(self):
        return self.started and not self.lost and len(self.revealed) == self.w * self.h - self.mine_count

    @property
    def elapsed(self):
        if not self.start_time:
            return 0
        return int((self.end_time or time.monotonic()) - self.start_time)

    def cell(self, pos):
        if self.lost or self.won:
            if pos in self.mines:
                if pos in self.flags:
                    return color("⚑ ", 46, bold=True)  # correctly flagged
                return color("✹ ", 196 if pos in self.revealed else 208, bold=True)
            if pos in self.flags:
                return color("✗ ", 244)  # wrong flag
        elif pos in self.flags:
            return color("⚑ ", 196, bold=True)
        if pos in self.revealed:
            n = self.count(*pos)
            return color(f"{n} ", NUMBER_COLORS[n], bold=True) if n else fg(238) + "· " + RESET
        return fg(250) + "■ " + RESET

    def render(self, label, best):
        status = f"Mines: {self.mine_count - len(self.flags):>3}   Time: {self.elapsed:>4}s"
        if best is not None:
            status += f"   Best: {best}s"
        lines = [color("M I N E S W E E P E R", 39, bold=True) + f"  ({label})", status, ""]
        lines.append(fg(240) + "┌" + "──" * self.w + "─┐" + RESET)
        for y in range(self.h):
            row = fg(240) + "│ " + RESET
            for x in range(self.w):
                c = self.cell((x, y))
                if (x, y) == self.cursor and not (self.lost or self.won):
                    c = REVERSE + c + RESET
                row += c
            lines.append(row + fg(240) + "│" + RESET)
        lines.append(fg(240) + "└" + "──" * self.w + "─┘" + RESET)
        lines.append("")
        if self.lost:
            lines.append(color("BOOM! You hit a mine.  R retry · Q menu", 196, bold=True))
        elif self.won:
            lines.append(color(f"Field cleared in {self.elapsed}s!  R retry · Q menu", 46, bold=True))
        else:
            lines.append(color("Arrows/WASD move · Space/Enter reveal · F flag · Q quit", 245))
        return lines


def choose_difficulty(term):
    while True:
        lines = [color("M I N E S W E E P E R", 39, bold=True), "", "Choose difficulty:", ""]
        for k, (label, w, h, m) in DIFFICULTIES.items():
            lines.append(f"  {BOLD}{k}{RESET}  {label:<7} {w}x{h}, {m} mines")
        lines += ["", color("Q to go back", 245)]
        term.draw(center(lines))
        key = term.get_key()
        if key in DIFFICULTIES:
            return key
        if key in ("q", ESC):
            return None


def play(term):
    choice = choose_difficulty(term)
    if not choice:
        return
    label, w, h, m = DIFFICULTIES[choice]
    score_key = f"mines_{label.lower()}"
    game = MinesGame(w, h, m)
    recorded = False
    while True:
        if game.won and not recorded:
            scores.submit(score_key, game.elapsed, lower_is_better=True)
            recorded = True
        best = scores.get_best(score_key)
        term.draw(center(game.render(label, best)))
        key = term.get_key(timeout=1.0 if game.started and not (game.lost or game.won) else None)
        if key is None:
            continue
        if key in ("q", ESC):
            return
        if key == "r" and (game.lost or game.won):
            game, recorded = MinesGame(w, h, m), False
            continue
        if key in DIRECTION_KEYS:
            dx, dy = DELTA[DIRECTION_KEYS[key]]
            x, y = game.cursor
            game.cursor = ((x + dx) % game.w, (y + dy) % game.h)
        elif key in (SPACE, ENTER):
            game.reveal(game.cursor)
        elif key == "f":
            game.toggle_flag(game.cursor)
