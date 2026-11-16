"""Merge Tiles: slide the grid, merge equal numbers, reach 2048."""

import random

from .. import scores
from ..term import BOLD, DIRECTION_KEYS, DOWN, ESC, LEFT, RESET, RIGHT, UP, bg, center, color, fg

NAME = "Merge Tiles"
DESCRIPTION = "Slide and merge matching numbers. Can you reach 2048?"

SIZE = 4
TILE_COLORS = {
    0: (237, 240), 2: (255, 234), 4: (223, 234), 8: (215, 255), 16: (209, 255),
    32: (203, 255), 64: (196, 255), 128: (228, 234), 256: (227, 234),
    512: (226, 234), 1024: (220, 234), 2048: (214, 255),
}


def slide_row_left(row):
    """Slide and merge a single row to the left. Returns (new_row, points)."""
    tiles = [v for v in row if v]
    out, points, i = [], 0, 0
    while i < len(tiles):
        if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
            out.append(tiles[i] * 2)
            points += tiles[i] * 2
            i += 2
        else:
            out.append(tiles[i])
            i += 1
    return out + [0] * (len(row) - len(out)), points


class MergeGame:
    def __init__(self, size=SIZE, rng=None):
        self.n = size
        self.rng = rng or random.Random()
        self.grid = [[0] * size for _ in range(size)]
        self.score = 0
        self.won = False
        self.spawn()
        self.spawn()

    def spawn(self):
        empty = [(r, c) for r in range(self.n) for c in range(self.n) if not self.grid[r][c]]
        if empty:
            r, c = self.rng.choice(empty)
            self.grid[r][c] = 4 if self.rng.random() < 0.1 else 2

    @staticmethod
    def _transpose(g):
        return [list(r) for r in zip(*g)]

    def _moved_grid(self, direction):
        g = self.grid
        if direction in (UP, DOWN):
            g = self._transpose(g)
        if direction in (RIGHT, DOWN):
            g = [r[::-1] for r in g]
        new, points = [], 0
        for row in g:
            r, p = slide_row_left(row)
            new.append(r)
            points += p
        if direction in (RIGHT, DOWN):
            new = [r[::-1] for r in new]
        if direction in (UP, DOWN):
            new = self._transpose(new)
        return new, points

    def move(self, direction):
        new, points = self._moved_grid(direction)
        if new == self.grid:
            return False
        self.grid = new
        self.score += points
        if any(2048 in r for r in new):
            self.won = True
        self.spawn()
        return True

    def can_move(self):
        return any(self._moved_grid(d)[0] != self.grid for d in (UP, DOWN, LEFT, RIGHT))

    def render(self, best, message=""):
        lines = [color("M E R G E   T I L E S", 214, bold=True),
                 f"Score: {BOLD}{self.score}{RESET}   Best: {best}", ""]
        for row in self.grid:
            cells_top, cells_mid = "", ""
            for v in row:
                b, f = TILE_COLORS.get(v, (93, 255))
                text = str(v) if v else "·"
                cells_top += bg(b) + " " * 8 + RESET + " "
                cells_mid += bg(b) + fg(f) + BOLD + text.center(8) + RESET + " "
            lines += [cells_top, cells_mid, cells_top, ""]
        lines.append(message or color("Arrows/WASD slide · R restart · Q quit", 245))
        return lines


def play(term):
    game = MergeGame()
    best = scores.get_best("merge") or 0
    announced_win = False
    while True:
        msg = ""
        if game.won and not announced_win:
            msg = color("★ You made 2048! Keep going for a higher score. ★", 226, bold=True)
        over = not game.can_move()
        if over:
            record = scores.submit("merge", game.score)
            msg = color("No moves left! " + ("★ NEW BEST! ★ " if record else "") +
                        "R to play again, Q to quit", 196, bold=True)
        term.draw(center(game.render(max(best, game.score), msg)))
        key = term.get_key()
        if key in ("q", ESC):
            scores.submit("merge", game.score)
            return
        if key == "r":
            scores.submit("merge", game.score)
            best = scores.get_best("merge") or 0
            game, announced_win = MergeGame(), False
            continue
        if over:
            continue
        if key in DIRECTION_KEYS:
            if game.won:
                announced_win = True
            game.move(DIRECTION_KEYS[key])
