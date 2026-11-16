"""Snake: eat the food, grow longer, don't bite yourself or the walls."""

import random
import time

from .. import scores
from ..term import (BOLD, DIRECTION_KEYS, DOWN, ESC, LEFT, RIGHT, UP, center,
                    color, fg, RESET)

NAME = "Snake"
DESCRIPTION = "Eat, grow, survive. Arrows/WASD to steer, P to pause."

W, H = 30, 16
OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}
DELTA = {UP: (0, -1), DOWN: (0, 1), LEFT: (-1, 0), RIGHT: (1, 0)}


class SnakeGame:
    def __init__(self, width=W, height=H, rng=None):
        self.w, self.h = width, height
        self.rng = rng or random.Random()
        cx, cy = width // 2, height // 2
        self.body = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = RIGHT
        self.pending = RIGHT
        self.score = 0
        self.alive = True
        self.food = self._place_food()

    def _place_food(self):
        free = [(x, y) for x in range(self.w) for y in range(self.h) if (x, y) not in self.body]
        return self.rng.choice(free) if free else None

    def turn(self, d):
        if d != OPPOSITE[self.direction]:
            self.pending = d

    def step(self):
        self.direction = self.pending
        dx, dy = DELTA[self.direction]
        hx, hy = self.body[0]
        head = (hx + dx, hy + dy)
        grows = head == self.food
        body_to_check = self.body if grows else self.body[:-1]
        if not (0 <= head[0] < self.w and 0 <= head[1] < self.h) or head in body_to_check:
            self.alive = False
            return
        self.body.insert(0, head)
        if grows:
            self.score += 10
            self.food = self._place_food()
            if self.food is None:  # board full - you win!
                self.alive = False
        else:
            self.body.pop()

    @property
    def delay(self):
        return max(0.05, 0.15 - len(self.body) * 0.002)

    def render(self, best, paused):
        body = set(self.body[1:])
        lines = [color("S N A K E", 46, bold=True) + f"   Score: {BOLD}{self.score}{RESET}   Best: {best}", ""]
        border = fg(240)
        lines.append(border + "┌" + "──" * self.w + "┐")
        for y in range(self.h):
            row = border + "│" + RESET
            for x in range(self.w):
                p = (x, y)
                if p == self.body[0]:
                    row += fg(226) + "██"
                elif p in body:
                    row += fg(40) + "██"
                elif p == self.food:
                    row += fg(196) + "● "
                else:
                    row += "  "
            lines.append(row + RESET + border + "│")
        lines.append(border + "└" + "──" * self.w + "┘")
        lines.append("")
        lines.append(color("PAUSED - press P to resume" if paused else "Arrows/WASD move · P pause · Q quit", 245))
        return lines


def play(term):
    game = SnakeGame()
    best = scores.get_best("snake") or 0
    paused = False
    next_tick = time.monotonic()
    while game.alive:
        term.draw(center(game.render(best, paused)))
        key = term.get_key(timeout=max(0.0, next_tick - time.monotonic()))
        if key in ("q", ESC):
            break
        if key == "p":
            paused = not paused
        elif key in DIRECTION_KEYS and not paused:
            game.turn(DIRECTION_KEYS[key])
        if paused:
            next_tick = time.monotonic() + game.delay
            continue
        if time.monotonic() >= next_tick:
            game.step()
            next_tick = time.monotonic() + game.delay
    record = scores.submit("snake", game.score)
    lines = game.render(max(best, game.score), False)
    lines[-1] = color(f"GAME OVER - score {game.score}" + ("  ★ NEW BEST! ★" if record else ""), 196, bold=True)
    lines.append(color("Press any key to return to the menu", 245))
    term.draw(center(lines))
    time.sleep(0.4)
    term.flush_input()
    term.get_key()
