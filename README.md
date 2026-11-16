# Terminal Arcade

Five games that run right in your terminal on **Windows, macOS and Linux**.
Pure Python, no dependencies — just Python 3.9 or newer.

| Game | How to play |
|---|---|
| **Snake** | Steer with arrows/WASD, eat the red dots, don't hit walls or yourself. `P` pauses. |
| **Merge Tiles** | Slide the 4×4 grid; equal numbers merge. Aim for 2048 and beyond. `R` restarts. |
| **Minesweeper** | Easy / Medium / Hard. Space/Enter reveals, `F` flags. Your first reveal is always safe. Reveal a number again to clear around it when its flags are placed. |
| **Tic-Tac-Toe** | Play an unbeatable, normal or easy computer, or a friend on the same keyboard. Arrows or keys 1–9. |
| **Hangman** | Guess the word letter by letter. Build a winning streak. |

Your best scores are saved in `~/.terminal_arcade_scores.json`.

## Install (one command)

**macOS / Linux** — paste into Terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/madhupbhardwaj/terminal-arcade/main/install.sh | sh
```

**Windows** — paste into PowerShell or Windows Terminal:

```powershell
irm https://raw.githubusercontent.com/madhupbhardwaj/terminal-arcade/main/install.ps1 | iex
```

The installer finds Python 3.9+ (installing it if needed: via `winget` on Windows, Homebrew or Apple's command line tools on macOS),
installs the games into a private folder (`~/.terminal-arcade`), and adds the `arcade` command.
Run the same command again to update.

**Uninstall:** delete the `.terminal-arcade` folder in your home folder (and `~/.local/bin/arcade` on macOS/Linux).

**Manual install:** if you already have Python, `pip install .` from this folder (or `pipx install .`) works too.

## Play

```bash
arcade
```

Or jump straight into a game: `arcade snake`, `arcade merge`, `arcade mines`, `arcade ttt`, `arcade hangman`.
`arcade --list` lists them. If the `arcade` command isn't found, run `python -m terminal_arcade` instead.

**Windows tip:** use Windows Terminal (default on Windows 11) for the best colours and box drawing.

## Development

```bash
pip install pytest
python -m pytest
```

Build a wheel to share: `pip install build && python -m build` — the installable file appears in `dist/`.
