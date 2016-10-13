"""Defines classes for Shootris"""
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
from utilities import *


class Cell(pyg.sprite.Sprite):
    """Default class for all cells"""

    def __init__(self, color, cell_type, left, top):
        pyg.sprite.Sprite.__init__(self)
        self.image = cell_type
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.move_ip(left, top)

    def update(self, screen, action, direction=0):
        if action == 'move':
            self. rect = self.rect.move(0, direction)
        if action == 'destroy':
            self.kill()


class Blob(pyg.sprite.RenderUpdates):
    """Areas containing cells"""

    def __init__(self, direction):
        pyg.sprite.Group.__init__(self)
        self.direction = direction

    def generate_cell(self, left, top, w_cor=0, h_cor=0):
        return Cell(get_random_color(),
                    pyg.Surface((CS + 2 * w_cor, CS + 2 * h_cor)),
                    left * CS - w_cor,
                    top * CS - h_cor)

    def add_row(self, left=0, top=-1, width=MAXCOL):
        for i in range(left, width):
            self.add(self.generate_cell(i + left, top))
