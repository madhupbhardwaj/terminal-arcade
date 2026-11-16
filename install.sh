#!/bin/sh
# Terminal Arcade installer for macOS and Linux.
#   curl -fsSL https://raw.githubusercontent.com/madhupbhardwaj/terminal-arcade/main/install.sh | sh
set -e

SOURCE="${ARCADE_SOURCE:-https://github.com/madhupbhardwaj/terminal-arcade/archive/refs/heads/main.zip}"
APP_DIR="$HOME/.terminal-arcade"
BIN_DIR="$HOME/.local/bin"

say() { printf '\033[1;36m==>\033[0m %s\n' "$1"; }
fail() { printf '\033[1;31mError:\033[0m %s\n' "$1" >&2; exit 1; }

# 1. Find Python 3.9+ ---------------------------------------------------------
find_python() {
    for cmd in python3 python; do
        if command -v "$cmd" >/dev/null 2>&1 &&
           "$cmd" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' >/dev/null 2>&1; then
            echo "$cmd"; return 0
        fi
    done
    return 1
}

PY="$(find_python || true)"
if [ -z "$PY" ]; then
    if [ "$(uname)" = "Darwin" ]; then
        if command -v brew >/dev/null 2>&1; then
            say "Installing Python with Homebrew..."
            brew install python
            PY="$(find_python || true)"
        else
            say "Python is needed. A window will open to install Apple's command line tools (includes Python)."
            xcode-select --install 2>/dev/null || true
            fail "Click Install in that window, wait for it to finish, then run this command again."
        fi
    else
        fail "Python 3.9 or newer is needed. Install it with your package manager (e.g. 'sudo apt install python3 python3-venv') and run this again."
    fi
fi
[ -n "$PY" ] || fail "Could not find Python 3.9+ after installing it. Open a new terminal and run this command again."
say "Using $("$PY" --version 2>&1)"

# 2. Install into a private environment ---------------------------------------
say "Installing Terminal Arcade..."
rm -rf "$APP_DIR/venv"
mkdir -p "$APP_DIR" "$BIN_DIR"
"$PY" -m venv "$APP_DIR/venv" || fail "Could not create a Python environment. On Debian/Ubuntu run 'sudo apt install python3-venv' first."
"$APP_DIR/venv/bin/python" -m pip install --quiet --disable-pip-version-check --upgrade pip
"$APP_DIR/venv/bin/python" -m pip install --quiet --disable-pip-version-check "$SOURCE"
ln -sf "$APP_DIR/venv/bin/arcade" "$BIN_DIR/arcade"

# 3. Make sure ~/.local/bin is on PATH ----------------------------------------
case ":$PATH:" in
    *":$BIN_DIR:"*) ON_PATH=1 ;;
    *) ON_PATH=0 ;;
esac
if [ "$ON_PATH" = 0 ]; then
    LINE='export PATH="$HOME/.local/bin:$PATH"'
    for rc in "$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.bash_profile"; do
        if [ -f "$rc" ] || [ "$(basename "$rc")" = ".zshrc" ]; then
            grep -qs '.local/bin' "$rc" || printf '\n# Added by Terminal Arcade\n%s\n' "$LINE" >> "$rc"
        fi
    done
fi

echo
say "Done! Terminal Arcade is installed."
if [ "$ON_PATH" = 1 ]; then
    echo "    Type:  arcade"
else
    echo "    Open a new terminal window and type:  arcade"
    echo "    (or right now:  ~/.local/bin/arcade)"
fi
