"""Tic-Tac-Toe against an unbeatable (or easy) computer, or a friend."""

import random

from ..term import BOLD, DIRECTION_KEYS, ENTER, ESC, RESET, REVERSE, SPACE, center, color

NAME = "Tic-Tac-Toe"
DESCRIPTION = "Three in a row. Play the computer or a friend."

LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
DELTA = {"UP": -3, "DOWN": 3, "LEFT": -1, "RIGHT": 1}


def winner(board):
    for a, b, c in LINES:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a], (a, b, c)
    if all(board):
        return "draw", ()
    return None, ()


def minimax(board, player, me):
    """Return (score, move) from `me`'s perspective with `player` to move."""
    w, _ = winner(board)
    if w == me:
        return 1, None
    if w == "draw":
        return 0, None
    if w:
        return -1, None
    other = "O" if player == "X" else "X"
    best = None
    for i in range(9):
        if not board[i]:
            board[i] = player
            score, _ = minimax(board, other, me)
            board[i] = ""
            if best is None or (score > best[0] if player == me else score < best[0]):
                best = (score, i)
    return best


def computer_move(board, me, difficulty, rng=random):
    free = [i for i in range(9) if not board[i]]
    if difficulty == "easy" or (difficulty == "normal" and rng.random() < 0.3):
        return rng.choice(free)
    if len(free) == 9:
        return rng.choice([0, 2, 4, 6, 8])
    return minimax(board, me, me)[1]


def render(board, cursor, status, win_line, header):
    def cell(i):
        mark = board[i] or " "
        code = 39 if mark == "X" else 208
        text = color(f" {mark} ", code, bold=True) if board[i] else "   "
        if i in win_line:
            text = color(f" {mark} ", 46, bold=True)
        if i == cursor:
            text = REVERSE + text + RESET
        return text

    lines = [color("T I C - T A C - T O E", 141, bold=True), header, ""]
    for r in range(3):
        lines.append(" " + "│".join(cell(r * 3 + c) for c in range(3)))
        if r < 2:
            lines.append(" ───┼───┼───")
    lines += ["", status, "", color("Arrows/WASD or 1-9 · Enter/Space place · Q quit", 245)]
    return lines


def choose_mode(term):
    options = {"1": ("You vs Computer (hard)", "hard"), "2": ("You vs Computer (normal)", "normal"),
               "3": ("You vs Computer (easy)", "easy"), "4": ("Two players", None)}
    while True:
        lines = [color("T I C - T A C - T O E", 141, bold=True), "", "Choose a mode:", ""]
        lines += [f"  {BOLD}{k}{RESET}  {label}" for k, (label, _) in options.items()]
        lines += ["", color("Q to go back", 245)]
        term.draw(center(lines))
        key = term.get_key()
        if key in options:
            return options[key][1], key == "4"
        if key in ("q", ESC):
            return None, None


def play(term):
    difficulty, two_player = choose_mode(term)
    if difficulty is None and not two_player:
        return
    tally = {"X": 0, "O": 0, "draw": 0}
    human_first = True
    while True:
        board = [""] * 9
        cursor = 4
        turn = "X"
        human = "X" if human_first or two_player else "O"
        computer = "O" if human == "X" else "X"
        result, line = None, ()
        while True:
            result, line = winner(board)
            if result:
                break
            if not two_player and turn == computer:
                board[computer_move(board, computer, difficulty)] = computer
                turn = human
                continue
            who = f"Player {turn}" if two_player else "Your move"
            header = f"X: {tally['X']}  O: {tally['O']}  Draws: {tally['draw']}"
            term.draw(center(render(board, cursor, f"{who} ({turn})", (), header)))
            key = term.get_key()
            if key in ("q", ESC):
                return
            if key in DIRECTION_KEYS:
                d = DIRECTION_KEYS[key]
                nxt = cursor + DELTA[d]
                if d in ("LEFT", "RIGHT") and nxt // 3 != cursor // 3:
                    continue
                if 0 <= nxt < 9:
                    cursor = nxt
            elif key and key in "123456789" and len(key) == 1:
                cursor = int(key) - 1
                if not board[cursor]:
                    board[cursor] = turn
                    turn = "O" if turn == "X" else "X"
            elif key in (ENTER, SPACE) and not board[cursor]:
                board[cursor] = turn
                turn = "O" if turn == "X" else "X"
        tally[result] += 1
        if result == "draw":
            msg = color("It's a draw!", 226, bold=True)
        elif two_player:
            msg = color(f"Player {result} wins!", 46, bold=True)
        elif result == human:
            msg = color("You win!", 46, bold=True)
        else:
            msg = color("The computer wins!", 196, bold=True)
        header = f"X: {tally['X']}  O: {tally['O']}  Draws: {tally['draw']}"
        term.draw(center(render(board, -1, msg + "  Any key: play again · Q: quit", line, header)))
        if term.get_key() in ("q", ESC):
            return
        human_first = not human_first
