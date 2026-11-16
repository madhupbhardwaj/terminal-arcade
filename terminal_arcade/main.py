"""Terminal Arcade main menu and command-line entry point."""

import argparse
import sys

from . import __version__, scores
from .games import hangman, merge, mines, snake, tictactoe
from .term import BOLD, DOWN, ENTER, ESC, RESET, REVERSE, SPACE, UP, Terminal, center, color

GAMES = [snake, merge, mines, tictactoe, hangman]
SLUGS = {"snake": snake, "merge": merge, "2048": merge, "mines": mines, "minesweeper": mines,
         "tictactoe": tictactoe, "ttt": tictactoe, "hangman": hangman}

LOGO = [
    "╔╦╗╔═╗╦═╗╔╦╗╦╔╗╔╔═╗╦    ╔═╗╦═╗╔═╗╔═╗╔╦╗╔═╗",
    " ║ ║╣ ╠╦╝║║║║║║║╠═╣║    ╠═╣╠╦╝║  ╠═╣ ║║║╣ ",
    " ╩ ╚═╝╩╚═╩ ╩╩╝╚╝╩ ╩╩═╝  ╩ ╩╩╚═╚═╝╩ ╩═╩╝╚═╝",
]
LOGO_COLORS = [51, 45, 39]


def best_label(game):
    if game is mines:
        parts = [f"{d[0]}: {scores.get_best('mines_' + d[0].lower())}s"
                 for d in mines.DIFFICULTIES.values() if scores.get_best("mines_" + d[0].lower()) is not None]
        return ", ".join(parts)
    key = {snake: "snake", merge: "merge", hangman: "hangman"}.get(game)
    best = scores.get_best(key) if key else None
    return f"{best}" if best else ""


def menu(term):
    selected = 0
    while True:
        lines = [color(row, LOGO_COLORS[i], bold=True) for i, row in enumerate(LOGO)]
        lines += [color(f"v{__version__} · pick a game", 245), ""]
        for i, g in enumerate(GAMES):
            label = f" {i + 1}. {g.NAME:<13}"
            if i == selected:
                lines.append(REVERSE + BOLD + label + RESET + "  " + g.DESCRIPTION)
            else:
                lines.append(label + "  " + color(g.DESCRIPTION, 245))
            best = best_label(g)
            lines.append(" " * 20 + color(f"best: {best}", 240) if best else "")
        lines += [color("↑/↓ select · Enter play · 1-5 quick pick · Q quit", 245)]
        term.draw(center(lines))
        key = term.get_key()
        if key in ("q", ESC):
            return
        if key in (UP, "w", "k"):
            selected = (selected - 1) % len(GAMES)
        elif key in (DOWN, "s", "j"):
            selected = (selected + 1) % len(GAMES)
        elif key in (ENTER, SPACE):
            GAMES[selected].play(term)
        elif key and key.isdigit() and 1 <= int(key) <= len(GAMES):
            selected = int(key) - 1
            GAMES[selected].play(term)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="arcade", description="A collection of games for your terminal.")
    parser.add_argument("game", nargs="?", choices=sorted(SLUGS), help="jump straight into a game")
    parser.add_argument("--version", action="version", version=f"terminal-arcade {__version__}")
    parser.add_argument("--list", action="store_true", help="list the games and exit")
    args = parser.parse_args(argv)

    if args.list:
        for g in GAMES:
            print(f"{g.NAME:<13} {g.DESCRIPTION}")
        return 0
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("terminal-arcade needs an interactive terminal.", file=sys.stderr)
        return 1
    try:
        with Terminal() as term:
            if args.game:
                SLUGS[args.game].play(term)
            else:
                menu(term)
    except KeyboardInterrupt:
        pass
    print("Thanks for playing Terminal Arcade!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
