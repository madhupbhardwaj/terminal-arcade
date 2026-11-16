"""Hangman: guess the hidden word one letter at a time."""

import random
import string

from .. import scores
from ..term import BOLD, ESC, RESET, center, color

NAME = "Hangman"
DESCRIPTION = "Guess the word before the gallows is complete."

WORDS = {
    "Animals": ["elephant", "giraffe", "penguin", "kangaroo", "octopus", "cheetah", "dolphin",
                "hedgehog", "flamingo", "squirrel", "tortoise", "chameleon", "porcupine", "jaguar"],
    "Food": ["pancake", "avocado", "broccoli", "spaghetti", "burrito", "croissant", "pretzel",
             "dumpling", "pineapple", "mushroom", "cinnamon", "lasagna", "omelette", "biscuit"],
    "Computers": ["keyboard", "terminal", "variable", "function", "compiler", "algorithm", "database",
                  "network", "monitor", "software", "processor", "recursion", "python", "browser"],
    "Places": ["mountain", "volcano", "library", "airport", "desert", "harbour", "castle",
               "lighthouse", "waterfall", "village", "island", "canyon", "glacier", "museum"],
}

GALLOWS = [
    ["", "", "", "", "", "", "═════════"],
    ["", "   │", "   │", "   │", "   │", "   │", "═══╧═════"],
    ["   ┌─────┐", "   │", "   │", "   │", "   │", "   │", "═══╧═════"],
    ["   ┌─────┐", "   │     │", "   │", "   │", "   │", "   │", "═══╧═════"],
    ["   ┌─────┐", "   │     │", "   │     O", "   │", "   │", "   │", "═══╧═════"],
    ["   ┌─────┐", "   │     │", "   │     O", "   │     │", "   │", "   │", "═══╧═════"],
    ["   ┌─────┐", "   │     │", "   │     O", "   │    /│", "   │", "   │", "═══╧═════"],
    ["   ┌─────┐", "   │     │", "   │     O", "   │    /│\\", "   │", "   │", "═══╧═════"],
    ["   ┌─────┐", "   │     │", "   │     O", "   │    /│\\", "   │    /", "   │", "═══╧═════"],
    ["   ┌─────┐", "   │     │", "   │     O", "   │    /│\\", "   │    / \\", "   │", "═══╧═════"],
]
MAX_MISSES = len(GALLOWS) - 1


class HangmanGame:
    def __init__(self, word, category):
        self.word = word.lower()
        self.category = category
        self.guessed = set()

    @property
    def misses(self):
        return len(self.guessed - set(self.word))

    @property
    def won(self):
        return set(self.word) <= self.guessed

    @property
    def lost(self):
        return self.misses >= MAX_MISSES

    def guess(self, letter):
        if letter in string.ascii_lowercase and not (self.won or self.lost):
            self.guessed.add(letter)

    def masked(self):
        return " ".join(c.upper() if c in self.guessed or self.lost else "_" for c in self.word)


def render(game, streak, best, message):
    lines = [color("H A N G M A N", 203, bold=True),
             f"Streak: {BOLD}{streak}{RESET}   Best streak: {best}   Category: {color(game.category, 81)}", ""]
    stage = GALLOWS[min(game.misses, MAX_MISSES)]
    lines += [color(row, 250) for row in stage]
    lines.append("")
    word_color = 46 if game.won else 196 if game.lost else 255
    lines.append("   " + color(game.masked(), word_color, bold=True))
    lines.append("")
    letters = ""
    for c in string.ascii_lowercase:
        if c in game.guessed:
            letters += color(c.upper(), 46 if c in game.word else 238) + " "
        else:
            letters += BOLD + c.upper() + RESET + " "
    lines.append(letters)
    lines.append(f"Misses left: {MAX_MISSES - game.misses}")
    lines += ["", message]
    return lines


def play(term):
    rng = random.Random()
    streak = 0
    while True:
        category = rng.choice(list(WORDS))
        game = HangmanGame(rng.choice(WORDS[category]), category)
        while True:
            best = scores.get_best("hangman") or 0
            if game.won:
                streak += 1
                record = scores.submit("hangman", streak)
                msg = color("You got it! " + ("★ NEW BEST STREAK! ★ " if record else ""), 46, bold=True)
            elif game.lost:
                streak = 0
                msg = color("Out of guesses!", 196, bold=True)
            else:
                msg = color("Type letters to guess · Esc quit", 245)
            if game.won or game.lost:
                term.draw(center(render(game, streak, max(best, streak), msg + color(" Any key: next word · Esc: quit", 245))))
                if term.get_key() == ESC:
                    return
                break
            term.draw(center(render(game, streak, best, msg)))
            key = term.get_key()
            if key == ESC:
                return
            if key and len(key) == 1:
                game.guess(key)
