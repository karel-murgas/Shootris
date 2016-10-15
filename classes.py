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

    def __init__(self, cell_type, left, top, col, row, layer, alpha=255, layer_group=ALL_SPRITES):
        pyg.sprite.Sprite.__init__(self)
        self.image = cell_type
        self.color = None
        self.image.set_alpha(alpha)
        self.rect = self.image.get_rect()
        self.rect.move_ip(left, top)
        self.col = col
        self.row = row
        self.layer = layer
        layer_group.add(self, layer=layer)

    def update(self, action, direction=0):
        if action == 'move':
            self.rect = self.rect.move(0, direction)
        if action == 'destroy':
            # check for neighbours to share joy with
            # check for other group touch collision to share the joy with
            # return list of all killed + iteration win which they were killed
            # main loop then kills them?
            self.kill()

    def colorate(self, color):
        self.image.fill(color)
        self.color = color

    def load_image(self, image, path=IMG_PATH):
        img = pyg.image.load(path + '/' + image)
        self.image.blit(img, (0, 0))


class Point(pyg.sprite.Sprite):
    """Simple point enabling to test collisions"""

    def __init__(self):
        pyg.sprite.Sprite.__init__(self)
        self.rect = pyg.Rect(0, 0, 1, 1)

    def update(self, target):
        self.rect = pyg.Rect(target, (1, 1))


class Blob(pyg.sprite.RenderUpdates):
    """Areas containing cells"""

    def __init__(self, direction, ls, bs, left=1, top=0, max_rows=MAXROW, max_cols=MAXCOL, layer=LAYER_MAIN):
        pyg.sprite.RenderUpdates.__init__(self)
        self.direction = direction
        self.l_prob = ls
        self.b_prob = bs
        self.offset = 0
        self.max_rows = max_rows
        self.max_cols = max_cols
        self.generated_rows = 0
        self.matrix = []
        self.left = left
        self.top = top
        self.layer = layer

    def generate_cell_color(self, cell):
        """Generate color with regards to other cells in blob"""

        if roll(self.l_prob) and cell.col > 0 and self.matrix[cell.row][cell.col - 1] is not None:
            color = self.matrix[cell.row][cell.col - 1].color
        elif roll(self.b_prob) and cell.row > 0 and self.matrix[cell.row - 1][cell.col] is not None:
            color = self.matrix[cell.row - 1][cell.col].color
        else:
            color = get_random_color()
        return color

    def generate_cell(self, left, top, col, row, size=CS, alpha=255):
        where = pyg.Surface((size, size))
        cell = Cell(where, left * size, top * size, col, row, self.layer, alpha)
        cell.colorate(self.generate_cell_color(cell))
        return cell

    def add_row(self):
        self.matrix.append([])
        for i in range(self.left, self.max_cols + self.left):
            cell = self.generate_cell(i, self.top, i - self.left, self.generated_rows)
            self.add(cell)
            self.matrix[self.generated_rows].append(cell)
        self.generated_rows += 1

    def test_destroy(self):
        for cell in iter(self):
            if cell.rect.top == FIELDLENGTH * CS:
                return True
        return False

    def destroy(self):
        return False

    def move(self):
        if self.offset == 0 and self.generated_rows < self.max_rows:  # when the time is right, add new row
            self.add_row()
        self.update('move', self.direction)  # update cells
        self.offset = (self.offset + self.direction) % CS
        if self.offset == 0:
            if self.test_destroy():
                return self.destroy()
        return True  # move is OK


class Up_blob(Blob):
    """Blob going upward"""

    def __init__(self, direction, ls=UP_LEFTSTICK, bs=UP_BOTTOMSTICK, left=1, top=FIELDLENGTH+2, layer=LAYER_UP,
                 max_rows=MAXROW, width=MAXCOL):
        Blob.__init__(self, direction, ls, bs, left, top, max_rows, layer=layer)
        self.max_rows_orig = max_rows
        self.color = get_random_color()
        self.width = width
        self.center = rnd.randrange(left, left + width)

    def generate_cell_color(self, *args):
        return self.color

    def add_row(self):
        i = 0
        while roll(self.l_prob) and self.center - i > self.left:  # generate left
            i += 1
            self.add(self.generate_cell(self.center - i,  self.top, self.center - i, self.generated_rows,
                                        alpha=UP_BLOB_ALPHA))

        self.add(self.generate_cell(self.center,  self.top, self.center, self.generated_rows,
                                    alpha=UP_BLOB_ALPHA))  # generate center

        i = 0
        while roll(self.l_prob) and self.center + i < self.left + self.max_cols - 1:  # generate right
            i += 1
            self.add(self.generate_cell(self.center + i,  self.top, self.center + i, self.generated_rows,
                                        alpha=UP_BLOB_ALPHA))

    def test_destroy(self):
        for cell in iter(self):
            if cell.rect.top < 0:
                cell.kill()
        if len(self) > 0:
            return False
        else:
            return True

    def destroy(self):
        return Up_blob(self.direction, self.l_prob, self.b_prob, self.left, self.top, self.layer, self.max_rows_orig, self.width)

    def move(self):
        if self.offset == 0 and self.generated_rows < self.max_rows:
            if roll(self.b_prob):
                self.add_row()
                self.generated_rows += 1
            else:
                self.max_rows = self.generated_rows  # stop generating

        self.update('move', self.direction)  # update cells
        self.offset = (self.offset + self.direction) % CS
        if self.offset == 0:
            if self.test_destroy():
                return self.destroy()
        return self  # move is OK


class Wall(pyg.sprite.Group):
    """Contains and draws wall cells"""

    def __init__(self, layer=LAYER_WALL):
        pyg.sprite.Group.__init__(self)
        self.layer = layer

    def generate_cell(self, left, top, image, color, size):
        where = pyg.Surface((size, size))
        cell = Cell(where, left * size, top * size, left, top, self.layer)
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


class Gun():
    """Define atributes and methods used for shooting"""

    def __init__(self, maxammo=MAXAMMO):
        self.maxammo = maxammo
        self.magazine = deque([])

    def shoot(self, target):
        if not target:  # missed that blob
            return 'missed'
        else:
            target[0].kill()
            return 'hit'

    def add_ammo(self):
        if len(self.magazine) < self.maxammo:
            self.magazine.append(get_random_color())
            return 'added'
        else:
            return 'full'

    def change_ammo(self):
        if len(self.magazine) > 1:
            bullet = self.magazine.popleft()
            self.magazine.append(bullet)
            return 'changed'
        else:
            return 'empty'
