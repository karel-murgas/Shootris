"""Unit tests for the free functions in utilities.py"""
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

from utilities import roll, get_random_color, collide_cell_touch, change_element
from constants import COLORS, MAXCOLORS


###############
# Cell (fake) #
###############

class FakeRect:
    """Minimal stand-in for a pygame Rect, enough for collide_cell_touch"""

    def __init__(self, left, top):
        self.left = left
        self.top = top


class FakeCell:
    """Something with a .rect, which is all collide_cell_touch reads"""

    def __init__(self, left, top):
        self.rect = FakeRect(left, top)


#########
# Tests #
#########

def test_roll_boundaries():
    """roll(1.0) is always True, roll(0.0) is always False"""
    assert all(roll(1.0) for _ in range(50))
    assert not any(roll(0.0) for _ in range(50))


def test_get_random_color_stays_in_palette():
    """Returned color is always one of the first MAXCOLORS colors"""
    allowed = COLORS[:MAXCOLORS]
    assert all(get_random_color() in allowed for _ in range(50))


def test_collide_cell_touch_side():
    """Cells sharing a side touch"""
    from constants import CS
    assert collide_cell_touch(FakeCell(0, 0), FakeCell(CS, 0)) is True


def test_collide_cell_touch_overlap():
    """Cells at the same spot overlap"""
    assert collide_cell_touch(FakeCell(5, 5), FakeCell(5, 5)) is True


def test_collide_cell_touch_corner_is_not_touch():
    """Cells meeting only at a corner do NOT count as touching"""
    from constants import CS
    assert collide_cell_touch(FakeCell(0, 0), FakeCell(CS, CS)) is False


def test_collide_cell_touch_far():
    """Cells more than one cell apart do not touch"""
    from constants import CS
    assert collide_cell_touch(FakeCell(0, 0), FakeCell(3 * CS, 0)) is False


def test_change_element_avoids_current():
    """change_element never returns the element it was told to avoid"""
    source = ['a', 'b', 'c', 'd']
    assert all(change_element('a', source) != 'a' for _ in range(50))
