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


#######################
# Classes definitions #
#######################

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
        self.time_to_live = 0
        layer_group.add(self, layer=layer)

    def update(self, direction=0):
        """Move the cell in given direction"""

        self.rect = self.rect.move(0, direction)

    def rat_neighbour(self, mb, ub, color, lifetime):
        """Find neighbours, with given color and report if same color upgoing-blob is in the way"""

        upkill = False
        to_die = []

        # Living left neighbour
        if self.col > 0 and mb.matrix[self.row][self.col - 1] is not None:
            c = mb.matrix[self.row][self.col - 1]
            if c.color == color:  # of right color
                c.time_to_die = lifetime
                to_die.append(c)

        # Living top neighbour of right color
        if self.row < mb.generated_rows - 1 and mb.matrix[self.row + 1][self.col] is not None:
            c = mb.matrix[self.row + 1][self.col]
            if c.color == color:  # of right color
                c.time_to_die = lifetime
                to_die.append(c)

        # Living right neighbour of right color
        if self.col < mb.max_cols - 1 and mb.matrix[self.row][self.col + 1] is not None:
            c = mb.matrix[self.row][self.col + 1]
            if c.color == color:  # of right color
                c.time_to_die = lifetime
                to_die.append(c)

        # Living bottom neighbour of right color
        if self.row > 0 and mb.matrix[self.row - 1][self.col] is not None:
            c = mb.matrix[self.row - 1][self.col]
            if c.color == color:  # of right color
                c.time_to_die = lifetime
                to_die.append(c)

        if ub.color == color and ub.generated_rows != 0:
            if pyg.sprite.spritecollideany(self, ub, collide_cell_touch):
                upkill = True

        return to_die, upkill

    def colorate(self, color):
        """Fill cell with given color"""
        self.image.fill(color)
        self.color = color

    def load_image(self, image, path=IMG_FOLD+TEXT_IMG_FOLD):
        """Load image with given path into this cell"""
        img = pyg.image.load(path + image)
        self.image.blit(img, (0, 0))


class Point(pyg.sprite.Sprite):
    """Simple point enabling to test collisions"""

    def __init__(self):
        pyg.sprite.Sprite.__init__(self)
        self.rect = pyg.Rect(0, 0, 1, 1)

    def update(self, target):
        """Update position (rect) of Point"""
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

    def generate_cell(self, left, top, col, row, size=CS, alpha=255, image=None):
        """Generate new cell for the blob, called by ad_row method"""

        where = pyg.Surface((size, size))
        cell = Cell(where, left * size, top * size, col, row, self.layer, alpha)
        cell.colorate(self.generate_cell_color(cell))
        if image is not None:
            cell.load_image(image)
        return cell

    def add_row(self, image=None):
        """Ad new row into the blob and fill it with cels"""

        self.matrix.append([])
        for i in range(self.left, self.max_cols + self.left):
            cell = self.generate_cell(i, self.top, i - self.left, self.generated_rows, image=image)
            self.add(cell)
            self.matrix[self.generated_rows].append(cell)
        self.generated_rows += 1

    def test_destroy(self):

        """If any cell is at bottom of game field, return true"""
        for cell in iter(self):
            if cell.rect.top == FIELDLENGTH * CS:
                return True
        return False

    def move(self):
        """Move the blob. If it is needed, generate new row. If game should end, return False."""

        if self.offset == 0 and self.generated_rows < self.max_rows:  # when the time is right, add new row
            self.add_row(image=BLOB_IMG)
        self.update(self.direction)  # update cells
        self.offset = (self.offset + self.direction) % CS
        if self.offset == 0:
            if self.test_destroy():
                return False
        return True  # move is OK

    def ready_to_die(self, cells, reveal, background=None):
        """Kill cells in iterative variable, count score, reveal background, check winning"""

        score = 0
        for c in cells:
            if reveal and background:
                background.reveal(c.rect)
            c.kill()
            score += 1
        return score


class UpBlob(Blob):
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

    def add_row(self, image=UP_IMG):
        i = 0
        while roll(self.l_prob) and self.center - i > self.left:  # generate left
            i += 1
            self.add(self.generate_cell(self.center - i,  self.top, self.center - i, self.generated_rows,
                                        alpha=UP_BLOB_ALPHA, image=image))

        self.add(self.generate_cell(self.center,  self.top, self.center, self.generated_rows,
                                    alpha=UP_BLOB_ALPHA, image=image))  # generate center

        i = 0
        while roll(self.l_prob) and self.center + i < self.left + self.max_cols - 1:  # generate right
            i += 1
            self.add(self.generate_cell(self.center + i,  self.top, self.center + i, self.generated_rows,
                                        alpha=UP_BLOB_ALPHA, image=image))

    def test_destroy(self):
        for cell in iter(self):
            if cell.rect.top < 0:
                cell.kill()
        if len(self) > 0:
            return False
        else:
            return True

    def reset(self):
        for cell in iter(self):
            cell.kill()
        return UpBlob(self.direction, self.l_prob, self.b_prob, self.left, self.top, self.layer, self.max_rows_orig,
                      self.width)

    def move(self):
        if self.offset == 0 and self.generated_rows < self.max_rows:
            if roll(self.b_prob):
                self.add_row()
                self.generated_rows += 1
            else:
                self.max_rows = self.generated_rows  # stop generating

        self.update(self.direction)  # update cells
        self.offset = (self.offset + self.direction) % CS
        if self.offset == 0:
            if self.test_destroy():
                return self.reset()
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


class Background:
    """Background image and it's properties"""

    def __init__(self, screen, width, height, area=GAME_FIELD, theme='random', pic='random', source=BACKGROUNDS,
                 path=IMG_FOLD+BG_IMG_FOLD, size=CS):
        self.clear = pyg.Surface((width * size, height * size))
        self.act = pyg.Surface((width * size, height * size))
        self.image = pyg.Surface((width * size, height * size))
        self.image.blit(self.load_image(path, theme, pic, source), area)
        self.img_area = area
        self.screen = screen

    def load_image(self, path, theme, pic, source):
        if theme == 'random':
            theme = rnd.choice(list(source))
        if pic == 'random':
            pic = rnd.randrange(len(source[theme]))
        return pyg.image.load(path + '/' + theme + '/' + source[theme][pic])

    def reveal(self, rect):
        self.act.blit(self.image, rect, rect)

    def fade_in(self, group=ALL_SPRITES):
        self.screen.blit(self.image, (0, 0))
        group.draw(self.screen)

    def fade_out(self, group=ALL_SPRITES):
        self.screen.blit(self.clear, (0, 0))
        group.draw(self.screen)


class Gun:
    """Define attributes and methods used for shooting"""

    def __init__(self, maxammo=MAXAMMO):
        self.maxammo = maxammo
        self.magazine = deque([])

    def explode(self, mb, ub, deadpool, to_die, color):
        """Breadth-first search to identify all cells with the same color and return their distance from hit"""

        explode_ub = False

        while to_die:
            cell = to_die.popleft()
            if mb.matrix[cell.row][cell.col] is not None:  # still living cell
                mb.matrix[cell.row][cell.col] = None  # consider it dead
                deadpool.add(cell)

                volunteers, collision = cell.rat_neighbour(mb, ub, color, cell.time_to_live + 1)  # get new cells to die
                if collision:  # the up-going blob is to die too
                    explode_ub = True
                to_die.extend(volunteers)

        return explode_ub

    def shoot(self, cursor, mb, ub, deadpool, background):
        score = 0
        status = None
        if len(self.magazine) > 0:  # have amoo
            bullet = self.magazine.popleft()
            upkill = False
            up_hit = pyg.sprite.spritecollideany(cursor, ub, 0)

            # Hit upgoing blob
            if up_hit:
                if ub.color == bullet:  # hit right color
                    upkill = True
                else:  # hit wrong color
                    status = 'hit_fail'
            else:
                mb_hit = pyg.sprite.spritecollideany(cursor, mb, 0)

                # Hit main blob
                if mb_hit:
                    if mb_hit.color == bullet:  # hit right color
                        upkill = self.explode(mb, ub, deadpool, deque([mb_hit]), bullet)
                        score += mb.ready_to_die(iter(deadpool), True, background)
                        status = 'hit_successful'
                    else:  # hit wrong color
                        status = 'hit_fail'
                else:  # missed everything
                    status = 'miss'

            # Upgoing blob was hit
            if upkill:
                mb_to_die = set(pyg.sprite.groupcollide(mb, ub, 0, 0))  # directly covered - color doesn't matter
                mb_neighbours = pyg.sprite.groupcollide(mb, ub, 0, 0, collide_cell_touch)  # neighbours of ub

                score += ub.ready_to_die(iter(ub), False)  # destroy cells and count score
                ub.reset()  # reset ub

                neighbours_to_die = set([cell for cell in mb_neighbours if cell.color == bullet])
                mb_to_die |= neighbours_to_die
                self.explode(mb, ub, deadpool, deque(mb_to_die), bullet)
                score += mb.ready_to_die(iter(deadpool), True, background)
                status = 'hit_successful'
        else:
            status = 'empty'

        # Check for winning
        if status == 'hit_successful' and mb.max_rows == mb.generated_rows and len(mb.sprites()) == 0:  # mb is destroyed
            win = True
        else:
            win = False

        return score, status, win

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
