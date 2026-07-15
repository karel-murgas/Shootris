"""Invariant checks for the tutorial's prebuilt board and ammo plan in constants.py"""
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

from classes import ScriptedBlob
from constants import COLORS, MAXCOL, TUT_MB_SCRIPT, TUT_AMMO, TUT_START_AMMO, TUT_MAXAMMO


###########
# Helpers #
###########

def build_full_board():
    """Spawn every scripted row at once, so region checks see the finished board"""
    blob = ScriptedBlob([[COLORS[i] for i in row] for row in TUT_MB_SCRIPT])
    for _ in range(len(TUT_MB_SCRIPT)):
        blob.add_row()
    return blob


def cells_of_color(blob, color):
    """All living cells of the given color"""
    return [cell for row in blob.matrix for cell in row if cell is not None and cell.color == color]


#########
# Tests #
#########

def test_board_rows_are_full_width():
    """Every scripted row spans the whole field, like organically grown rows do"""
    assert all(len(row) == MAXCOL for row in TUT_MB_SCRIPT)


def test_board_never_uses_color_four():
    """Color 4 is reserved for the first up-blob, so shooting it can never chain into the board"""
    assert all(i != 4 for row in TUT_MB_SCRIPT for i in row)


def test_color_zero_forms_a_single_region():
    """The first lesson's shot must take ALL color-0 cells - the waste lesson relies on their extinction"""
    blob = build_full_board()
    zeros = cells_of_color(blob, COLORS[0])

    region = blob.connected_same_color(zeros[0])

    assert len(region) == len(zeros)  # one connected region covers every color-0 cell


def test_color_two_forms_exactly_two_separated_blocks():
    """The bridge lesson needs two color-2 blocks that only the up-blob can connect"""
    blob = build_full_board()
    twos = cells_of_color(blob, COLORS[2])

    first_block = blob.connected_same_color(twos[0])
    outside = [cell for cell in twos if cell not in first_block]
    second_block = blob.connected_same_color(outside[0])

    assert len(first_block) + len(second_block) == len(twos)  # exactly two regions...
    assert len(first_block) > 1 and len(second_block) > 1  # ...both worth bridging


def test_swap_lesson_region_exists():
    """The color-1 region seeded at matrix[1][9] is a real multi-cell region"""
    blob = build_full_board()

    region = blob.connected_same_color(blob.matrix[1][9])

    assert blob.matrix[1][9].color == COLORS[1]
    assert len(region) > 1


def test_ammo_plan_matches_the_lessons():
    """The scripted arrivals put the right color at the front for each frozen lesson"""
    magazine = list(COLORS[i] for i in TUT_START_AMMO)
    arrivals = [COLORS[i] for i in TUT_AMMO]

    assert magazine[0] == COLORS[0]  # beat 2: preloaded bullet matches the color-0 region

    magazine.pop(0)  # beat 2 shot
    magazine += arrivals[:2]  # beat 4: two arrivals
    assert COLORS[1] in magazine  # beat 5 is completable after swapping
    magazine.remove(COLORS[1])  # beat 5 shot (after cycling it to the front)

    fill = arrivals[2:2 + TUT_MAXAMMO - len(magazine)]  # beat 6: fill to the brim
    magazine += fill
    assert len(magazine) == TUT_MAXAMMO
    assert magazine[0] == COLORS[0]  # the bullet to waste - its color is extinct on the board

    magazine.pop(0)  # the waste shot
    next_arrival = arrivals[2 + len(fill)]
    magazine.append(next_arrival)  # tops back up during the approach watch
    assert COLORS[4] in magazine  # beat 7: the first up-blob's color is on hand
    magazine.remove(COLORS[4])  # beat 7 shot

    assert COLORS[2] in magazine  # beat 8: the bridging up-blob's color is on hand
