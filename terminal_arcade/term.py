"""Cross-platform terminal helpers (Windows + macOS + Linux), standard library only.

Provides raw keyboard input with optional timeout, ANSI colours and
flicker-free full-screen drawing.
"""

import os
import shutil
import sys
import time

IS_WINDOWS = os.name == "nt"

if IS_WINDOWS:
    import msvcrt
else:
    import select
    import termios
    import tty

# Normalised key names
UP, DOWN, LEFT, RIGHT = "UP", "DOWN", "LEFT", "RIGHT"
ENTER, ESC, BACKSPACE, SPACE = "ENTER", "ESC", "BACKSPACE", "SPACE"

RESET = "\x1b[0m"
BOLD = "\x1b[1m"
DIM = "\x1b[2m"
REVERSE = "\x1b[7m"


def fg(code):
    """256-colour foreground escape."""
    return f"\x1b[38;5;{code}m"


def bg(code):
    """256-colour background escape."""
    return f"\x1b[48;5;{code}m"


def color(text, code, bold=False):
    return f"{BOLD if bold else ''}{fg(code)}{text}{RESET}"


def _enable_windows_ansi():
    """Turn on VT100 escape processing in the Windows console."""
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
    except Exception:
        os.system("")  # fallback trick that also enables ANSI on most Windows 10+ consoles


class Terminal:
    """Context manager that puts the terminal into game mode.

    Usage:
        with Terminal() as t:
            key = t.get_key(timeout=0.1)
            t.draw(["line 1", "line 2"])
    """

    def __enter__(self):
        if IS_WINDOWS:
            _enable_windows_ansi()
            try:
                sys.stdout.reconfigure(encoding="utf-8")
            except Exception:
                pass
        else:
            self._fd = sys.stdin.fileno()
            self._old = termios.tcgetattr(self._fd)
            tty.setcbreak(self._fd)
        # alternate screen, hide cursor, clear
        self.write("\x1b[?1049h\x1b[?25l\x1b[2J\x1b[H")
        return self

    def __exit__(self, *exc):
        self.write(RESET + "\x1b[?25h\x1b[?1049l")
        if not IS_WINDOWS:
            termios.tcsetattr(self._fd, termios.TCSADRAIN, self._old)
        return False

    # ----- output -------------------------------------------------------
    @staticmethod
    def write(s):
        sys.stdout.write(s)
        sys.stdout.flush()

    @staticmethod
    def size():
        s = shutil.get_terminal_size((80, 24))
        return s.columns, s.lines

    def draw(self, lines):
        """Redraw the whole screen without flicker."""
        out = ["\x1b[H"]
        for line in lines:
            out.append(line + RESET + "\x1b[K\n")
        out.append("\x1b[J")
        self.write("".join(out))

    # ----- input --------------------------------------------------------
    def get_key(self, timeout=None):
        """Return a normalised key, or None if `timeout` seconds pass with no input.

        timeout=None blocks until a key is pressed.
        """
        if IS_WINDOWS:
            return self._get_key_windows(timeout)
        return self._get_key_unix(timeout)

    def flush_input(self):
        while self.get_key(timeout=0) is not None:
            pass

    @staticmethod
    def _get_key_windows(timeout):
        deadline = None if timeout is None else time.monotonic() + timeout
        while not msvcrt.kbhit():
            if deadline is not None and time.monotonic() >= deadline:
                return None
            time.sleep(0.01)
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):
            code = msvcrt.getwch()
            return {"H": UP, "P": DOWN, "K": LEFT, "M": RIGHT}.get(code)
        return _normalise(ch)

    def _get_key_unix(self, timeout):
        ready, _, _ = select.select([self._fd], [], [], timeout)
        if not ready:
            return None
        ch = os.read(self._fd, 1).decode("utf-8", "ignore")
        if ch == "\x1b":
            # Possibly an escape sequence (arrow keys): read what's immediately available
            seq = ""
            while select.select([self._fd], [], [], 0.02)[0]:
                seq += os.read(self._fd, 1).decode("utf-8", "ignore")
                if len(seq) >= 2 and seq[-1].isalpha():
                    break
            if not seq:
                return ESC
            return {"[A": UP, "[B": DOWN, "[D": LEFT, "[C": RIGHT,
                    "OA": UP, "OB": DOWN, "OD": LEFT, "OC": RIGHT}.get(seq)
        return _normalise(ch)


def _normalise(ch):
    if ch in ("\r", "\n"):
        return ENTER
    if ch == "\x1b":
        return ESC
    if ch in ("\x7f", "\x08"):
        return BACKSPACE
    if ch == " ":
        return SPACE
    if ch == "\x03":
        raise KeyboardInterrupt
    return ch.lower()


# WASD / vim keys map onto arrows for convenience
DIRECTION_KEYS = {
    UP: UP, "w": UP, "k": UP,
    DOWN: DOWN, "s": DOWN, "j": DOWN,
    LEFT: LEFT, "a": LEFT, "h": LEFT,
    RIGHT: RIGHT, "d": RIGHT, "l": RIGHT,
}


def center(lines, width=None):
    """Pad lines on the left so the block is roughly centred.

    Visible width ignores ANSI escapes.
    """
    width = width or Terminal.size()[0]
    widest = max((visible_len(l) for l in lines), default=0)
    pad = " " * max(0, (width - widest) // 2)
    return [pad + l for l in lines]


def visible_len(s):
    n, i = 0, 0
    while i < len(s):
        if s[i] == "\x1b":
            while i < len(s) and not s[i].isalpha():
                i += 1
            i += 1
            continue
        n += 1
        i += 1
    return n
