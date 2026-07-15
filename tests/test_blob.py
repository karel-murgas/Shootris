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

from collections import deque

import pygame as pyg

from classes import Blob, UpBlob, Gun, Point
from constants import RED, MAXCOL


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
