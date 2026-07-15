# Architecture

Five modules, each importing everything from the previous one with `from X import *`, so
`shootris.py` transitively has every name in scope:

```
constants.py  →  utilities.py  →  classes.py  →  ui_classes.py  →  shootris.py
```

- **`constants.py`** — pygame init, colors, image/sound paths, `SOUND` dict, all `TEXT_*` strings,
  the `TIPS` list, custom pygame user events (`END_EVENT`, `MAIN_BLOB_MOVE_EVENT`, etc.), gameplay
  tuning constants (`MAXCOL`, `MAXROW`, `MAXAMMO`, `*_SPEED`, `*STICK` probabilities), and derived
  globals (`GAME_FIELD`, `ALL_SPRITES`). This is the single place to tune game feel.
- **`utilities.py`** — small free functions: `collide_cell_touch` (custom pygame collision predicate,
  side/overlap touch but not corner touch), `roll` (probability check), `get_random_color`,
  `change_element` (pick a different random element, used for cycling tips).
- **`classes.py`** — game/simulation logic, no rendering decisions beyond blitting cell surfaces:
  - `MenuOption` — one cyclable settings row (name + choices + current index), no pygame
    dependency; used by `ui_classes.Menu` to back the settings/end-of-round screens.
  - `Cell` — one grid square; tracks `col`/`row` (matrix position) separately from `rect`
    (pixel position = grid position × `CS`); `rat_neighbour` looks up same-color living neighbours.
  - `Blob` (`pyg.sprite.RenderUpdates`) — the main blob. Owns `matrix`, a list-of-rows of `Cell` or
    `None` (dead), mirroring the sprite group so neighbour lookups are O(1). Grows one row per
    `move()` tick per `MAIN_BLOB_SPEED`.
  - `UpBlob(Blob)` — the single-color rising blob; regenerates itself (`reset()`) after being shot
    or reaching the ceiling.
  - `Wall` — static border cells.
  - `Gun` — magazine (`deque` of colors) and `shoot()` / `explode()` (see below) / `add_ammo()` /
    `change_ammo()`.
- **`ui_classes.py`** — `Infopanel`, `Label`, `Magazine`, `Background` (theme art, fade in/out,
  progressive reveal of the picture behind destroyed cells), `Menu` (renders a list of
  `MenuOption` rows plus plain action rows, drives selection/cycling, used for both the
  pre-game settings screen and the end-of-round REPLAY / RETURN TO MENU screen).
- **`shootris.py`** — entry point: builds the screen and wall once, then loops between
  `run_settings_menu()` (pick background theme/image and color scheme) and `play()`, which
  runs the actual game's event loop (player input, timed move/spawn events, end-of-game fade,
  `run_end_screen()`, redraw + `clock.tick(60)`).

## Screen clearing: sprites and Labels only erase what they already track

`ALL_SPRITES.clear(screen, bgd)` + `.draw(screen)` only erases/redraws the rects it
already has bookkeeping for (each sprite's current/previous position); `Label.write()`
only clears its own small rect. Neither ever repaints arbitrary pixels something else
put on `screen` outside those areas. `ui_classes.Menu` (the settings/end-of-round
screens) paints directly onto the full `screen` surface — its own `draw()` wipes its
*own* rectangle every call, but nothing else knows to clean up after it once it hands
control back to normal gameplay drawing. `play()` therefore does an explicit
`screen.fill(BLACK)` right before it (re)builds `Background`/`Infopanel` each round —
skip that and leftover menu text/buttons stay visible forever in whatever gaps the
sprite/Label redraws don't cover (this happened for real: stale "SHOOTRIS" title and
option-row text bled into the info panel after clicking START GAME, until the fill was
added). Any future full/partial-screen overlay needs the same treatment at the point it
hands back to normal rendering.

## Coordinate system

Two coordinate spaces are used throughout and should not be mixed up:
- **Grid space**: `col`/`row` indices into `Blob.matrix`.
- **Pixel space**: `rect.left`/`rect.top`, always grid coordinate × `CS` (cell size in pixels).

## Explosion / flood-fill mechanic (`Gun.explode`)

`Gun.explode` is a breadth-first search over `mb.matrix` starting from the hit cell: it pops a cell
from a `deque`, kills it (removes from `matrix`, adds to `deadpool`), asks `Cell.rat_neighbour` for
same-color living neighbours, and enqueues them, stamping each with `cell.time_to_live` = its wave
distance from the original shot (fixed 2026-07-15 — `rat_neighbour` used to write a stray
`time_to_die` attribute that `explode` never read, so the distance never accumulated; see
`tests/test_blob.py::test_explode_records_wave_distance`).

So every dead cell now correctly carries its distance-from-the-shot. What still does *not* exist is
anything that *uses* `time_to_live` for timing or visuals — `Blob.ready_to_die()` kills the whole
`deadpool` in one synchronous loop, all in the same frame. That's the remaining work for this branch.

A design note for whoever builds the staggering: a cell can be re-discovered by a farther neighbour
before it's processed (BFS re-visits), and the current code re-stamps `time_to_live` unconditionally
on every discovery, so a later, larger stamp can overwrite an earlier, correct, smaller one. For
clean concentric waves, stamp only once (e.g. only if the cell doesn't already have a smaller
`time_to_live`) or compute the wave from the parent at dequeue time instead of at enqueue time.

## Current branch: `new_core_code`

Goal (per the user, not yet implemented): when a blob explodes, cells should die starting from the
shot origin and progressively outward, with a small per-wave delay and a graphical effect, instead
of the whole same-color region vanishing in one frame.

The BFS in `Gun.explode` now correctly computes the wave number needed for this (`cell.time_to_live`,
fixed 2026-07-15 — see above). What's missing is turning it into staggered kills: roughly, group
`deadpool` by `time_to_live`, and release one wave per tick of a new timer event (similar to
`FADE_EVENT`/`fade()` in `shootris.py`, which already staggers a multi-step visual over time and is
the closest existing pattern to imitate) instead of calling `ready_to_die()` once with the whole
pool. A per-cell flash/brighten effect before killing (mentioned as a TODO in `Shootris_notes.txt`:
"When destroying cell, brighter flash for a moment (50ms?)") fits naturally into the same
staggered-wave mechanism. Read the re-stamping caveat above before relying on `time_to_live` as-is.

Also relevant: `Blob.ready_to_die()` has a standing TODO/bug noting the game briefly freezes the
first time it's called for a nontrivial number of cells, cause unknown — worth keeping an eye on
once this method is reworked to be wave-based, since the freeze may or may not survive the rewrite.

There is currently no diff between `master` and `new_core_code` in the actual code (git history is
identical) — the feature has not been started yet in this branch.
