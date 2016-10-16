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


def collide_cell_touch(*args):
    """Return True if cells touch or intersect (except corner touch)"""
    try:
        s1, s2 = args
    except ValueError:
        print("Wrong number of arguments for collision function: " + str(args))
        return False
    size = CS  # I don't know how to pass it right
    l1, l2 = s1.rect.left, s2.rect.left
    t1, t2 = s1.rect.top, s2.rect.top

    # Too much far (including top and bottom sides and corners)
    if abs(l1 - l2) > size or abs(t1 - t2) > size:
        return False
    # Corner touch
    elif abs(l1 - l2) == size and abs(t1 - t2) == size:
        return False
    # Side or inside touch
    else:
        return True


def roll(prob):
    """Tests random value [0,1) against given probability"""
    return True if (rnd.random() < prob) else False


def get_random_color(colors=COLORS, stop=MAXCOLORS):
    """Returns random color from list, list can be shortened"""
    return colors[rnd.randrange(stop)]


# still unused
def get_random_tip(tips=TIPS, forbidden=-1):
    """Returns random tip from list, it can omit previous tip"""
    num = rnd.randrange(len(tips))  # if forbidden, take next (cycle through)
    if num == forbidden:
        num = (num + 1) % len(tips)
    return num, tips[num]
