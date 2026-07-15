"""Unit tests for Blob and Gun logic in classes.py"""
#    Copyright (C) 2016  Karel "laird Odol" Murgas
#    karel.murgas@gmail.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


#############
# Libraries #
#############

import random as rnd
from collections import deque

import pygame as pyg

from classes import Blob, ScriptedBlob, UpBlob, Gun, Point
from constants import RED, GREEN, BLUE, MAXCOL, CS


###########
# Helpers #
###########

def make_solid_blob(rows, color=RED):
    """Build a Blob of `rows` rows, all cells recolored to one known color"""
    blob = Blob(1, 0.7, 0.5)
    for _ in range(rows):
        blob.add_row(image=None)
    for row in blob.matrix:
        for cell in row:
            cell.colorate(color)
    return blob


#########
# Tests #
#########

def test_add_row_fills_matrix():
    """Each added row holds MAXCOL cells and bumps generated_rows"""
    blob = Blob(1, 0.7, 0.5)
    blob.add_row(image=None)
    blob.add_row(image=None)
    assert blob.generated_rows == 2
    assert len(blob.matrix) == 2
    assert all(len(row) == MAXCOL for row in blob.matrix)


def test_explode_marks_whole_connected_region():
    """A same-colored, connected blob is fully consumed from a single hit"""
    blob = make_solid_blob(3)
    ub = UpBlob(-2)
    deadpool = pyg.sprite.Group()
    gun = Gun()

    gun.explode(blob, ub, deadpool, deque([blob.matrix[1][1]]), RED)

    assert len(deadpool) == 3 * MAXCOL  # every cell was reached
    assert all(cell is None for row in blob.matrix for cell in row)  # matrix emptied


def test_explode_records_wave_distance():
    """Cells farther from the hit should carry a larger time_to_live than the hit cell.

    This is the groundwork the new_core_code explosion feature depends on.
    """
    blob = make_solid_blob(3)
    ub = UpBlob(-2)
    deadpool = pyg.sprite.Group()
    gun = Gun()

    start = blob.matrix[0][0]  # a corner, so distances span the whole region
    gun.explode(blob, ub, deadpool, deque([start]), RED)

    assert max(cell.time_to_live for cell in deadpool) > 1


def test_all_dead_true_only_once_matrix_is_empty():
    """all_dead() reflects matrix bookkeeping, independent of whether sprites were killed yet"""
    blob = make_solid_blob(2)
    ub = UpBlob(-2)
    deadpool = pyg.sprite.Group()
    gun = Gun()

    assert blob.all_dead() is False

    gun.explode(blob, ub, deadpool, deque([blob.matrix[0][0]]), RED)

    assert blob.all_dead() is True  # matrix is empty...
    assert len(blob.sprites()) == 2 * MAXCOL  # ...even though nothing has been killed yet


def test_group_by_wave_orders_by_distance_from_shot():
    """group_by_wave returns cells bucketed by time_to_live, in ascending wave order"""
    blob = make_solid_blob(3)
    ub = UpBlob(-2)
    deadpool = pyg.sprite.Group()
    gun = Gun()

    start = blob.matrix[0][0]
    gun.explode(blob, ub, deadpool, deque([start]), RED)
    waves = blob.group_by_wave(deadpool)

    assert [cell.time_to_live for cell in waves[0]] == [0]  # the hit cell is its own wave 0
    distances = [wave[0].time_to_live for wave in waves]
    assert distances == sorted(distances)  # waves come out from the shot outward
    assert sum(len(wave) for wave in waves) == len(deadpool)  # every cell accounted for


def test_colors_present_reflects_only_living_cells():
    """colors_present ignores killed (None) matrix slots and dedupes repeated colors"""
    blob = make_solid_blob(2)  # every cell RED
    assert blob.colors_present() == {RED}

    gun = Gun()
    ub = UpBlob(-2)
    deadpool = pyg.sprite.Group()
    gun.explode(blob, ub, deadpool, deque([blob.matrix[0][0]]), RED)

    assert blob.colors_present() == set()  # whole blob was one connected RED region


def test_pick_ammo_color_unrestricted_before_last_row():
    """restrict_final_colors has no effect until mb's last row has spawned"""
    blob = make_solid_blob(1)
    blob.max_rows = blob.generated_rows + 1  # more rows still to come
    for cell in blob.matrix[0]:
        cell.colorate(RED)
    gun = Gun(restrict_final_colors=True)

    colors = {gun.pick_ammo_color(blob) for _ in range(50)}

    assert len(colors) > 1  # not restricted to the single on-board color


def test_pick_ammo_color_restricted_once_last_row_spawned():
    """Once mb.generated_rows reaches mb.max_rows, ammo is limited to colors still on the board"""
    blob = make_solid_blob(1)
    blob.max_rows = blob.generated_rows  # last row already spawned
    for cell in blob.matrix[0]:
        cell.colorate(RED)
    gun = Gun(restrict_final_colors=True)

    colors = {gun.pick_ammo_color(blob) for _ in range(50)}

    assert colors == {RED}


def test_pick_ammo_color_falls_back_when_board_is_clear():
    """If restriction is on but no cells remain, fall back to the full color pool instead of crashing"""
    blob = make_solid_blob(1)
    blob.max_rows = blob.generated_rows
    for cell in blob.matrix[0]:
        cell.colorate(RED)
    gun = Gun(restrict_final_colors=True)
    ub = UpBlob(-2)
    deadpool = pyg.sprite.Group()
    gun.explode(blob, ub, deadpool, deque([blob.matrix[0][0]]), RED)

    assert blob.colors_present() == set()
    assert gun.pick_ammo_color(blob) is not None  # get_random_color() fallback, no exception


def test_add_ammo_respects_restriction():
    """add_ammo(mb) plumbs mb through to pick_ammo_color instead of always drawing from the full pool"""
    blob = make_solid_blob(1)
    blob.max_rows = blob.generated_rows
    for cell in blob.matrix[0]:
        cell.colorate(RED)
    gun = Gun(maxammo=10, restrict_final_colors=True)

    for _ in range(10):
        gun.add_ammo(blob)

    assert set(gun.magazine) == {RED}


def test_pick_ammo_color_pools_in_up_blob_color_once_restricted():
    """Once restricted, the pool also includes ub's color so the up-blob stays a valid target"""
    blob = make_solid_blob(1)
    blob.max_rows = blob.generated_rows
    for cell in blob.matrix[0]:
        cell.colorate(RED)
    gun = Gun(restrict_final_colors=True)
    ub = UpBlob(-2)
    ub.color = GREEN  # distinct from the board's only remaining color

    colors = {gun.pick_ammo_color(blob, ub) for _ in range(50)}

    assert colors == {RED, GREEN}


def test_add_ammo_pools_in_up_blob_color():
    """add_ammo(mb, ub) plumbs ub through too, so the magazine can include ub's color once restricted"""
    blob = make_solid_blob(1)
    blob.max_rows = blob.generated_rows
    for cell in blob.matrix[0]:
        cell.colorate(RED)
    gun = Gun(maxammo=50, restrict_final_colors=True)
    ub = UpBlob(-2)
    ub.color = GREEN

    for _ in range(50):
        gun.add_ammo(blob, ub)

    assert set(gun.magazine) <= {RED, GREEN}
    assert GREEN in set(gun.magazine)  # with 50 draws from a 2-color pool, near-certain


def test_shoot_defers_kill_but_computes_score_and_win_immediately():
    """Score and win are correct right after shoot(), even though hit cells are still alive"""
    blob = make_solid_blob(1)  # one full row, all RED
    blob.max_rows = blob.generated_rows  # pretend this was the last row to spawn
    ub = UpBlob(-2)
    deadpool = pyg.sprite.Group()
    gun = Gun()
    gun.magazine.append(RED)

    cursor = Point()
    cursor.update(blob.matrix[0][0].rect.topleft)

    score, status, win = gun.shoot(cursor, blob, ub, deadpool)

    assert status == 'hit_success'
    assert score == MAXCOL  # whole row destroyed
    assert win is True  # matrix bookkeeping already shows the blob is gone
    assert len(blob.sprites()) == MAXCOL  # ...but sprites weren't killed yet
    assert blob.all_dead() is True


def test_load_layout_builds_matrix_shape_and_colors():
    """load_layout fills a rectangular matrix with the given colors, leaving None holes"""
    blob = Blob(1, 0.7, 0.5)
    layout = [
        [RED, None],
        [None, GREEN],
    ]

    blob.load_layout(layout, left=2, top_row=3)

    assert blob.generated_rows == 2
    assert blob.max_rows == 2
    assert blob.max_cols == 2
    assert len(blob.matrix) == 2 and all(len(row) == 2 for row in blob.matrix)
    assert len(blob.sprites()) == 2  # only the two non-None cells were created


def test_load_layout_maps_top_written_row_to_highest_matrix_row():
    """The first (top) layout row lands on the highest matrix row and the smallest rect.top"""
    blob = Blob(1, 0.7, 0.5)
    layout = [
        [RED],   # written first -> top of screen -> should be the higher matrix row
        [GREEN],  # written second -> bottom of screen -> lower matrix row
    ]

    blob.load_layout(layout, left=0, top_row=0)

    top_cell = blob.matrix[1][0]  # higher matrix row
    bottom_cell = blob.matrix[0][0]  # lower matrix row
    assert top_cell.color == RED
    assert bottom_cell.color == GREEN
    assert top_cell.rect.top < bottom_cell.rect.top  # visually above


def test_load_layout_places_cells_at_expected_pixel_positions():
    """Cell rects follow (left+col)*CS, (top_row+i)*CS, using the on-screen row index i"""
    blob = Blob(1, 0.7, 0.5)
    layout = [[RED, GREEN]]

    blob.load_layout(layout, left=5, top_row=7)

    cell = blob.matrix[0][1]  # col 1
    assert cell.rect.left == (5 + 1) * CS
    assert cell.rect.top == 7 * CS


def test_scripted_blob_spawns_planned_rows_in_order():
    """ScriptedBlob's move() spawns exactly the scripted rows, first row lowest in the matrix"""
    script = [[RED] * 3, [GREEN] * 3]
    blob = ScriptedBlob(script)

    for _ in range(2 * CS):  # enough move() ticks to spawn both rows (one row per CS ticks)
        blob.move()

    assert blob.generated_rows == 2
    assert blob.max_rows == 2  # stops growing once the script is spent
    assert [cell.color for cell in blob.matrix[0]] == [RED] * 3
    assert [cell.color for cell in blob.matrix[1]] == [GREEN] * 3


def test_scripted_blob_consumes_no_randomness():
    """Spawning scripted rows must not advance the RNG - the tutorial's determinism relies on it"""
    blob = ScriptedBlob([[RED] * 5, [GREEN] * 5])
    rnd.seed(42)
    state = rnd.getstate()

    blob.add_row()
    blob.add_row()

    assert rnd.getstate() == state


def test_gun_scripted_ammo_arrives_in_order_then_falls_back():
    """add_ammo serves the planned bullets first, then falls back to the random pool"""
    gun = Gun(maxammo=3, script=[RED, GREEN])

    assert gun.add_ammo() == 'added'
    assert gun.add_ammo() == 'added'
    assert list(gun.magazine) == [RED, GREEN]

    assert gun.add_ammo() == 'added'  # script spent - random fallback, no crash
    assert len(gun.magazine) == 3
    assert gun.add_ammo() == 'full'


def test_connected_same_color_excludes_isolated_same_color_cells():
    """The region one shot would take: connected same-color cells only, accents excluded"""
    blob = Blob(1, 0.7, 0.5)
    layout = [
        [RED, RED, None, RED],   # cols 0-1 form a region; col 3 is an isolated accent
        [RED, BLUE, None, None],
    ]
    blob.load_layout(layout, left=0, top_row=0)

    region = blob.connected_same_color(blob.matrix[1][0])  # top-left RED

    assert len(region) == 3  # the three connected REDs
    assert blob.matrix[1][3] not in region  # the accent stays out
    assert all(cell.color == RED for cell in region)
    """A blob built via load_layout behaves identically to one grown organically under Gun.shoot"""
    blob = Blob(1, 0.7, 0.5)
    layout = [
        [RED, RED],
        [RED, None],
    ]
    blob.load_layout(layout, left=0, top_row=0)
    blob.max_rows = blob.generated_rows

    ub = UpBlob(-2)
    deadpool = pyg.sprite.Group()
    gun = Gun()
    gun.magazine.append(RED)

    cursor = Point()
    cursor.update(blob.matrix[1][0].rect.topleft)  # top-left RED cell

    score, status, win = gun.shoot(cursor, blob, ub, deadpool)

    assert status == 'hit_success'
    assert score == 3  # all three RED cells chain-exploded
    assert win is True
