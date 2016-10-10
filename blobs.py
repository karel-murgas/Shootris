#############
# Libraries #
#############

import random as rnd
# import pygame as pyg
from constants import *
from collections import deque


##################
# Initialization #
##################

CELL = pyg.Surface((CELLSIZE, CELLSIZE))


########################
# Function definitions #
########################

def roll(pst):
    """Tests random value [0,1) against given probability"""
    return True if (rnd.random() < pst) else False


def get_random_element(source = COLORS):
    """Returns random element from list (default is random color)"""
    return source[rnd.randint(0, len(source) - 1)]


def color_cell(cell,color):
    """Fills cell with color"""
    cell.fill(color)
    return cell


def draw_cell(screen, r, c, color, row_fraction=0,):
    """Blits cell to surface"""
    if color is None:
        color = BLACK
    screen.blit(color_cell(CELL, color), (c*CELLSIZE, r * CELLSIZE - rest_of_cell(row_fraction)))


def draw_blob(screen, field, area, start_row, row_fraction=0):
    """Draws blob on the surface"""
    for r in range(len(area)):
        for c in range(len(area[r])):
            draw_cell(screen, r + start_row, c, area[r][c], row_fraction,)
    pyg.display.update(field)


def rest_of_cell(fraction, total=CELLSIZE):
    if fraction == 0:
        return 0
    else:
        return total - fraction


#####################
# Class definitions #
#####################

class Blob:
    """Defines blob - now only for main blob - to be expanded later"""
    def __init__(self, screen, field, event, speed):
        self.cols = MAXCOL
        self.max_rows = MAXROW
        self.top = 0
        self.left = 0
        self.ls = LEFTSTICK
        self.bs = BOTTOMSTICK
        self.content = deque([])
        self.generated_rows = 0
        self.append_row()
        self.screen = screen
        self.field = field
        self.speed = speed
        self.timer = pyg.time.set_timer(event, speed)
        self.event = event
        self.row_fraction = 0

        # oveř prádzný spodek
        # zahoď spodek

    def get_rect(self):
        top_line = 0 if self.top == 0 else self.top * CELLSIZE - rest_of_cell(self.row_fraction)
        bottom_len = len(self.content) * CELLSIZE
        if self.top == 0:
            bottom_len -= rest_of_cell(self.row_fraction)
        return pyg.Rect(self.left * CELLSIZE, top_line, self.cols * CELLSIZE, bottom_len)

    def get_bottom(self):
        """Returns row index of bottom row"""
        return self.top + len(self.content) - 1  # index of top row + number of rows - correction

    def create_cell(self, r, c):
        """Creates content of the cell - colors the cell regarding left and bottom neighbours"""
        if c > 0 and roll(self.ls) and self.content[r][c - 1] is not None:
            return self.content[r][c - 1]  # color by left cell
        elif r < len(self.content) - 1 and roll(self.bs) and self.content[r + 1][c] is not None:
            return self.content[r + 1][c]  # color by bottom cell
        else:
            return get_random_element()  # randomColor

    def append_row(self):
        """Appends new row to the start of the blob"""
        self.content.appendleft([])
        self.generated_rows += 1
        for c in range(self.cols):
            self.content[0].append(self.create_cell(0, c))

    def clearRow(self, row):
        draw_blob(self.screen, self.field, [[None]*self.cols], row)

    def destroy(self):
        self.timer = pyg.time.set_timer(self.event, 0)
        pyg.event.post(pyg.event.Event(LOOSE_EVENT))
        del self

    def win(self):
        self.timer = pyg.time.set_timer(self.event, 0)
        pyg.event.post(pyg.event.Event(WIN_EVENT))
        del self

    def move(self):
        """Moves the blob down"""
        if self.get_bottom() >= FIELDLENGTH - 1 and self.row_fraction == 0:
            self.destroy()
        else:
            if self.generated_rows < self.max_rows:  # there is new line in the buffer
                if self.row_fraction == 0:
                    self.append_row()
            else:  # clear the top line
                self.screen.blit(pyg.Surface((self.cols * CELLSIZE, 1)), (0, self.top * CELLSIZE - rest_of_cell(self.row_fraction), self.cols * CELLSIZE, 1))
                if self.row_fraction == 0:
                    self.top += 1

            self.row_fraction = (self.row_fraction + 1) % CELLSIZE
            draw_blob(self.screen, self.field, self.content, self.top, self.row_fraction)

    def damage(self, r, c, color):
        """Deletes content of this cell and all direct neighbours"""
        score = 0
        if self.content[r][c] == color:
            self.content[r][c] = None
            score += 1
            if c > 0 and self.content[r][c - 1] == color:  # left
                score += self.damage(r, c - 1, color)
            if c < self.cols - 1 and self.content[r][c + 1] == color:  # right
                score += self.damage(r, c + 1, color)
            if r > 0 and self.content[r - 1][c] == color:  # top
                score += self.damage(r - 1, c, color)
            if r < len(self.content) - 1 and self.content[r + 1][c] == color:  # bottom
                score += self.damage(r + 1, c, color)
        return score

    def hit(self, c, r, color):
        if self.content[r][c] == color:
            score = self.damage(r, c, color)
            draw_blob(self.screen, self.field, self.content, self.top, self.row_fraction)
            while len(self.content) > 0 and self.content[len(self.content) - 1] == [None]*self.cols:
                self.content.pop()
            if len(self.content) == 0 and self.max_rows == self.generated_rows:
                self.win()
            return score
        else:
            return 0
