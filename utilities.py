"""Defines utility functions for Shootris"""
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
from constants import *


########################
# Function definitions #
########################

def roll(pst):
    """Tests random value [0,1) against given probability"""
    return True if (rnd.random() < pst) else False


def get_random_color(colors=COLORS, stop=MAXCOLORS):
    """Returns random color from list, list can be shortened"""
    return colors[rnd.randrange(stop)]


def get_random_tip(tips=TIPS, forbidden = -1):
    """Returns random tip from list, it can omit previous tip"""
    num = rnd.randrange(len(tips))  # if forbidden, take next (cycle through)
    if num == forbidden:
        num = (num + 1) % len(tips)
    return num, tips[num]


def color_surface(color, surf=CELL):
    """Fills surface with color and returns that surface"""
    surf.fill(color)
    return surf


def draw_cell(screen, r, c, color, row_fraction=0):
    """Blits cell to surface"""
    if color is None:
        color = BLACK
    screen.blit(color_surface(color, CELL), (c * CELLSIZE, r * CELLSIZE - rest_of_cell(row_fraction)))


def draw_blob(screen, field, area, start_row, row_fraction=0):
    """Draws blob on the surface"""
    for r in range(len(area)):
        for c in range(len(area[r])):
            draw_cell(screen, r + start_row, c, area[r][c], row_fraction,)
    pyg.display.update(field)


def rest_of_cell(fraction, total=CELLSIZE):
    """Tells how much of a cell is above line, if fraction of cell is bellow"""
    if fraction == 0:
        return 0
    else:
        return total - fraction
