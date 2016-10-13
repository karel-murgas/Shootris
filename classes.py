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

    def __init__(self, cell_type, left, top):
        pyg.sprite.Sprite.__init__(self)
        self.image = cell_type
        self.color = None
        self.rect = self.image.get_rect()
        self.rect.move_ip(left, top)

    def update(self, screen, action, direction=0):
        if action == 'move':
            self. rect = self.rect.move(0, direction)
        if action == 'destroy':
            self.kill()

    def colorate(self, color):
        self.image.fill(color)
        self.color = color

    def load_image(self, image, path=IMG_PATH):
        img = pyg.image.load(path + '/' + image)
        self.image.blit(img, (0, 0))


class Blob(pyg.sprite.RenderUpdates):
    """Areas containing cells"""

    def __init__(self, direction, ls, bs):
        pyg.sprite.RenderUpdates.__init__(self)
        self.direction = direction
        self.l_prob = ls
        self.t_prob = bs

    def generate_cell_color(self, cell):
        """Generate color with regards to other cells in blob"""
        ln = pyg.sprite.spritecollide(cell, self, 0, collided=collide_cell_touch_width)  # left neighbour
        bn = pyg.sprite.spritecollide(cell, self, 0, collided=collide_cell_touch_height)  # bottom neighbour

        if ln and (ln[0].color is not None) and roll(self.l_prob):
            color = ln[0].color
        elif bn and (bn[0].color is not None) and roll(self.t_prob):
            color = bn[0].color
        else:
            color = get_random_color()
        return color

    def generate_cell(self, left, top, size=CS):
        where = pyg.Surface((size, size))
        cell = Cell(where, left * size, top * size)
        cell.colorate(self.generate_cell_color(cell))
        return cell

    def add_row(self, left=0, top=-1, width=MAXCOL):
        for i in range(left, width + left):
            self.add(self.generate_cell(i, top))


class Wall(pyg.sprite.Group):
    """Contains and draws wall cells"""

    def __init__(self):
        pyg.sprite.Group.__init__(self)

    def generate_cell(self, left, top, image, color, size):
        where = pyg.Surface((size, size))
        cell = Cell(where, left * size, top * size)
        cell.colorate(color)
        cell.load_image(image)
        return cell

    def create_wall(self, left, top, width=MAXCOL, height=FIELDLENGTH, size=CS, image=WALL_IMG, color=WHITE):
        for i in range(width + 1):
            self.add(self.generate_cell(left + i, top, image, color, size))
        for j in range(height + 1):
            self.add(self.generate_cell(left + i + 1, top + j, image, color, size))
        for i in reversed(range(width + 1)):
            self.add(self.generate_cell(left + i + 1, top + j + 1, image, color, size))
        for j in range(height + 1):
            self.add(self.generate_cell(left, top + j + 1, image, color, size))


class Background():
    """Background image and it's properties"""

    def __init__(self, width, height, area=GAME_FIELD, theme='random', pic='random', source=BACKGROUNDS, path=IMG_PATH, size=CS):
        self.clear = pyg.Surface((width * size, height * size))
        self.clear.fill(BLACK)
        self.image = self.clear
        self.image.blit(self.load_image(path, theme, pic, source), area)
        self.act = self.clear
        self.img_area = area

    def load_image(self, path, theme, pic, source):
        if theme == 'random':
            theme = rnd.choice(list(source))
        if pic == 'random':
            pic = rnd.randrange(len(source[theme]))
        return pyg.image.load(path + '/' + theme + '/' + source[theme][pic])

    def reveal(self, rect):
        self.act.blit(self.image, rect, rect)

