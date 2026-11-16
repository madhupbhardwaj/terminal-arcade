import random

from terminal_arcade import scores
from terminal_arcade.games.hangman import HangmanGame, MAX_MISSES
from terminal_arcade.games.merge import MergeGame, slide_row_left
from terminal_arcade.games.mines import MinesGame
from terminal_arcade.games.snake import SnakeGame
from terminal_arcade.games.tictactoe import computer_move, winner
from terminal_arcade.term import visible_len, color


def test_slide_row():
    assert slide_row_left([2, 2, 2, 2]) == ([4, 4, 0, 0], 8)
    assert slide_row_left([0, 2, 0, 2]) == ([4, 0, 0, 0], 4)
    assert slide_row_left([4, 4, 8, 0]) == ([8, 8, 0, 0], 8)
    assert slide_row_left([2, 4, 8, 16]) == ([2, 4, 8, 16], 0)


def test_merge_moves_all_directions():
    g = MergeGame(rng=random.Random(1))
    g.grid = [[2, 0, 0, 2], [0] * 4, [0] * 4, [0] * 4]
    assert g.move("LEFT")
    assert g.grid[0][0] == 4 and g.score == 4
    g.grid = [[2, 0, 0, 0], [2, 0, 0, 0], [0] * 4, [0] * 4]
    g.move("DOWN")
    assert g.grid[3][0] == 4
    g.grid = [[2, 4, 2, 4], [4, 2, 4, 2], [2, 4, 2, 4], [4, 2, 4, 2]]
    assert not g.can_move()


def test_snake_grows_and_dies():
    g = SnakeGame(10, 10, rng=random.Random(0))
    head = g.body[0]
    g.food = (head[0] + 1, head[1])
    g.step()
    assert len(g.body) == 4 and g.score == 10
    g.turn("LEFT")  # reversing is ignored
    assert g.pending == "RIGHT"
    for _ in range(20):
        g.step()
    assert not g.alive


def test_mines_first_click_safe_and_win():
    for seed in range(20):
        g = MinesGame(9, 9, 10, rng=random.Random(seed))
        g.reveal((4, 4))
        assert not g.lost and len(g.mines) == 10
        for x in range(9):
            for y in range(9):
                if (x, y) not in g.mines:
                    g.reveal((x, y))
        assert g.won


def test_tictactoe_ai_never_loses():
    rng = random.Random(3)
    for _ in range(30):
        board, turn = [""] * 9, "X"
        while not winner(board)[0]:
            if turn == "O":
                board[computer_move(board, "O", "hard")] = "O"
            else:
                board[rng.choice([i for i in range(9) if not board[i]])] = "X"
            turn = "O" if turn == "X" else "X"
        assert winner(board)[0] != "X"


def test_hangman():
    g = HangmanGame("cat", "Animals")
    for c in "cat":
        g.guess(c)
    assert g.won
    g = HangmanGame("cat", "Animals")
    for c in "zyxwvuqrs"[:MAX_MISSES]:
        g.guess(c)
    assert g.lost


def test_scores(tmp_path, monkeypatch):
    monkeypatch.setattr(scores, "SCORE_FILE", tmp_path / "s.json")
    assert scores.get_best("x") is None
    assert scores.submit("x", 10)
    assert not scores.submit("x", 5)
    assert scores.submit("t", 30, lower_is_better=True)
    assert scores.submit("t", 20, lower_is_better=True)
    assert scores.get_best("t") == 20


def test_visible_len():
    assert visible_len(color("hello", 10, bold=True)) == 5
