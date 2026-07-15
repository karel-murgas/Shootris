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

import pygame as pyg

from utilities import (roll, get_random_color, collide_cell_touch, change_element, apply_color_scheme,
                       wrap_text, covers_any, touches_any)
from constants import COLORS, COLOR_SCHEMES, MAXCOLORS, CS


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


def test_apply_color_scheme_mutates_colors_in_place():
    """apply_color_scheme swaps the shared COLORS list's contents, so get_random_color follows suit"""
    try:
        apply_color_scheme('colorblind')
        assert COLORS == COLOR_SCHEMES['colorblind']  # same object, new contents
        allowed = COLOR_SCHEMES['colorblind'][:MAXCOLORS]
        assert all(get_random_color() in allowed for _ in range(50))
    finally:
        apply_color_scheme('standard')  # restore for other tests
    assert COLORS == COLOR_SCHEMES['standard']


def test_wrap_text_fits_each_line_within_width():
    """Every returned line renders narrower than max_width"""
    font = pyg.font.SysFont(pyg.font.get_default_font(), 20)
    text = 'This is a fairly long sentence that should wrap across several lines'
    max_width = 150

    lines = wrap_text(text, font, max_width)

    assert all(font.size(line)[0] <= max_width for line in lines)


def test_wrap_text_preserves_word_order():
    """Rejoining the wrapped lines reproduces the original words in order"""
    font = pyg.font.SysFont(pyg.font.get_default_font(), 20)
    text = 'One two three four five six seven eight nine ten'

    lines = wrap_text(text, font, 100)

    assert ' '.join(lines).split(' ') == text.split(' ')


def test_wrap_text_single_line_when_it_fits():
    """Text narrower than max_width stays on one line"""
    font = pyg.font.SysFont(pyg.font.get_default_font(), 20)

    lines = wrap_text('Short text', font, 1000)

    assert lines == ['Short text']


class RectCell:
    """Something with a real pygame Rect, which is all covers_any/touches_any read"""

    def __init__(self, left, top):
        self.rect = pyg.Rect(left, top, CS, CS)


def test_covers_any_needs_at_least_half_overlap():
    """A sliver of overlap is not covering yet; half a cell is"""
    cell = RectCell(0, 0)
    barely = RectCell(0, CS - 2)  # 2px of overlap
    halfway = RectCell(0, CS // 2)  # half a cell of overlap

    assert covers_any([barely], [cell]) is False
    assert covers_any([halfway], [cell]) is True


def test_touches_any_side_but_not_corner():
    """Side contact counts as touching, corner contact does not"""
    cell = RectCell(0, 0)

    assert touches_any([RectCell(CS, 0)], [cell]) is True  # side
    assert touches_any([RectCell(CS, CS)], [cell]) is False  # corner
    assert touches_any([RectCell(3 * CS, 0)], [cell]) is False  # far away
