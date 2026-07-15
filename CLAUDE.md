# Shootris

A hand-made Tetris/shooter hybrid in Python + pygame, started in 2016 by Karel "laird Odol" Murgas
as a project to learn Python. Being revived for continued vibecoding.

## What it is

Colored cell blobs ("main blob") grow upward from the bottom of the field, row by row, threatening
to reach the top. The player aims a crosshair and left-clicks to shoot the color currently loaded
in the magazine at a cell. Shooting a cell of the matching color kills it and chain-kills same-color
neighbours (flood fill), revealing a background image behind destroyed cells. A second "up-going
blob" of a single random color rises from the field and can be shot for bonus destruction, or left
to reach the ceiling (harmless). Right-click cycles the magazine. Win by destroying the whole main
blob; lose if any main-blob cell reaches the bottom wall.

## Running it

```
python shootris.py
```

Requires `pygame` (see `requirements.txt` — currently pinned to `2.6.1`; note the file is saved with
a non-UTF-8 encoding, likely from `Out-File` without `-Encoding utf8` — re-save as plain UTF-8 if you
regenerate it).

## Testing

There is a `pytest` unit-test suite under `tests/`, covering the pure logic (utilities, `Blob`/`Gun`
mechanics) — not the rendering or the event loop, which stay manual (run the game, play it).

```
pip install -r requirements-dev.txt   # once — adds pytest on top of runtime deps
python -m pytest                        # run from the project root
```

How it works: `constants.py` runs `pyg.init()` / `pyg.mixer.init()` and loads every sound at import
time, so importing any game module normally needs a display and audio device. The repo-root
`conftest.py` sidesteps this by setting `SDL_VIDEODRIVER=dummy` / `SDL_AUDIODRIVER=dummy` **before**
the test modules import pygame, and `os.chdir`-ing to the project root so the relative sound/image
paths resolve. This is why tests must be collected through pytest (which loads `conftest.py` first)
and must never import `shootris.py` (importing it runs the game's module-level main loop) — test
against `utilities`, `classes`, and `ui_classes` only.

Convention for tests: mirror the source style — GPLv3 header, banner comments, one-line docstrings.
A genuine bug that can't be fixed yet is pinned with `@pytest.mark.xfail(reason=...)` so the suite
stays green but the bug is recorded and will announce itself (as an unexpected pass) once fixed.

### Testing is part of the workflow, not an afterthought

When adding or changing any logic in `utilities.py` or `classes.py` (the testable layers):
1. Add or update a test alongside the change, in the same commit/session — not "later".
2. Run `python -m pytest` before considering the change done. It's ~0.2s; there's no excuse to skip it.
3. If a change surfaces a bug you're not fixing right now, pin it with `xfail` (see above) rather
   than leaving it undocumented — that's what happened with the `time_to_live` bug below before it
   was fixed.
4. Rendering/event-loop code in `shootris.py` and the visual parts of `ui_classes.py` can't be unit
   tested (see "How it works" above) — those still need a manual playthrough, but anything that's a
   plain function or a `Blob`/`Gun`/`Cell` method should get a test.

## Architecture

Five modules, each importing everything from the previous one with `from X import *`:
`constants.py → utilities.py → classes.py → ui_classes.py → shootris.py`. Game/simulation logic
(`Cell`, `Blob`, `UpBlob`, `Wall`, `Gun`) lives in `classes.py`; rendering-only pieces
(`Infopanel`, `Label`, `Magazine`, `Background`) live in `ui_classes.py`.

For the full per-module tour, the grid/pixel coordinate system, the `Gun.explode` BFS mechanic
(including the `time_to_live` re-stamping caveat), and the `new_core_code` branch goal/status —
see **[`docs/architecture.md`](docs/architecture.md)**. Read it before touching the explosion/kill
mechanic or the wave-based staggering feature.

## Conventions to preserve

This is a solo hobby project the user knows well and wants to keep recognizable — match existing
style rather than modernizing it:

- Banner-style section comments, e.g.:
  ```python
  #############
  # Libraries #
  #############
  ```
  used consistently to separate imports / functions / classes / settings within a file.
- One-line docstrings on every class and method (`"""Does X"""`), no multi-line docstrings.
- GPLv3 header block at the top of every source file — keep it when adding new files.
- Plain, direct code: free functions in `utilities.py`, small classes in `classes.py`, minimal
  abstraction. Don't introduce frameworks, type hints, dataclasses, or heavy OOP patterns that
  aren't already in use — keep new code readable at the same level as the surrounding code, not
  more "clever".
- Existing `print(...)` debug statements (e.g. in `Gun.shoot`/`change_ammo`) are left-in debugging
  aids, not accidental leftovers to silently strip — leave them unless the user asks to clean them
  up specifically.
- Constants belong in `constants.py`, not hardcoded inline, matching the existing pattern of
  `ALL_CAPS` tunables.

## Known backlog (see `Shootris_notes.txt`)

Kept in a plain-text notes file rather than an issue tracker. Highlights:
- Bug: shots occasionally return `hit_fail` when they shouldn't (possibly a lag/reload race).
- No settings persistence (highscore resets every session by design, per a TIP).
- Sound on/off toggle (`s` key) not implemented.
- PyInstaller packaging has never worked for this project.
- A whole "RPG model" (levels, points, upgrades, skills) is speculative/deadpool — do not build this
  unprompted, it's a maybe-someday idea list.
