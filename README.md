# MicroVerse by RashTek

A growing collection of tiny, dependency-free **apps** and **games** that run right in your browser — built and maintained on mobile. Every game is a single HTML file you can open, fork, or play offline.

**▶ Play now: [pencil77.github.io/RashTek-MicroVerse](https://pencil77.github.io/RashTek-MicroVerse/)**

## 📁 What's inside

| Section | Description |
| --- | --- |
| 🚀 **[Micro Apps](Micro_Apps/index.html)** | Utilities and tools (e.g. Hunger Box QR order cards) |
| 🎮 **[Micro Games](Micro_Games/index.html)** | 2048, Chess (incl. P2P online), Craft World, Super Run, Temple Run, Snake, Shooting Game, Vice City, Musical Chairs, Save the Dog |
| 🐍 **`python_based_*/`** | Terminal/Flask versions of the games, plus scripts that convert their HTML templates into the browser versions |

## ▶ Playing the games

Every `.html` file in `Micro_Apps/` and `Micro_Games/` is fully self-contained:

- **Online** — just open it from the GitHub Pages site linked above.
- **Offline** — download the file and open it in any browser. No build step, no server, no dependencies.

Games with touch controls (Craft, Super Run, Temple Run, etc.) work on phones; chess and most others also support keyboard/mouse.

## ✨ Adding a new app or game

1. Drop a single self-contained `my_game.html` into `Micro_Apps/` or `Micro_Games/`.
2. (Optional) Add a friendly display name and one-line description in `NAME_OVERRIDES` / `DESCRIPTIONS` at the top of [`update_microverse.py`](update_microverse.py).
3. Commit and push to `main`.

That's it — CI regenerates the section index pages and redeploys GitHub Pages automatically (see below). A back-link (`← Back to Games`) to the section index is recommended inside each game.

## 🛠 Repo scripts

| Script | Purpose |
| --- | --- |
| [`update_microverse.py`](update_microverse.py) | Regenerates `Micro_Apps/index.html` and `Micro_Games/index.html` from the files on disk. Run from the repo root: `python update_microverse.py` |
| [`Micro_Games/update_games.py`](Micro_Games/update_games.py) | Writes the HTML for the hand-authored games (P2P Chess, Craft, Super Run) from embedded source strings |
| [`Micro_Games/python_based_games/convert_games2html.py`](Micro_Games/python_based_games/convert_games2html.py) | Extracts `HTML_TEMPLATE`/`GAME_TEMPLATE` blocks from the Python games and emits browser-ready `.html` files in `Micro_Games/` |

All scripts resolve paths relative to their own location, so they work from any working directory and on any machine.

## ⚙️ CI/CD

- **`.github/workflows/update-index.yml`** — on every push that adds/changes an app or game, runs `update_microverse.py` and commits the regenerated index pages, which then triggers a fresh Pages deploy.
- **`.github/workflows/static.yml`** — deploys the whole repo to GitHub Pages on every push to `main`.

## 📦 Local Python games

The `python_based_apps/` and `python_based_games/` folders contain terminal (curses) and Flask versions. Most need only the Python standard library; the calculator needs Flask:

```bash
pip install flask
python Micro_Apps/python_based_apps/calculator.py
```

Note: the terminal chess game creates local `*.db` save files — these are git-ignored on purpose.

## 📄 License

Feel free to play, fork, and learn from the code.
