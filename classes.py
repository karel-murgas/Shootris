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
        """Gets rectangle containing the blob"""
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
            return get_random_color()  # random color

    def append_row(self):
        """Appends new row to the start of the blob"""
        self.content.appendleft([])
        self.generated_rows += 1
        for c in range(self.cols):
            self.content[0].append(self.create_cell(0, c))

    def clearRow(self, row):
        """Draws row as if the color was None"""
        draw_blob(self.screen, self.field, [[None]*self.cols], row)

    def destroy(self):
        """Ends the game and deletes the blob instance"""
        self.timer = pyg.time.set_timer(self.event, 0)
        pyg.event.post(pyg.event.Event(LOOSE_EVENT))
        del self

    def win(self):
        """Ends the game winning and deletes the blob instance"""
        self.timer = pyg.time.set_timer(self.event, 0)
        pyg.event.post(pyg.event.Event(WIN_EVENT))
        del self

    def move(self):
        """Moves the blob one pixel down, checks for blob boundaries"""
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
        """Determines, if hit was success. If it was, deletes cells and checks and pop out empty bottom rows"""
        if self.content[r][c] == color:
            if SOUND_EFFECTS_ON:
                sound_hit_success.play()
            score = self.damage(r, c, color)
            draw_blob(self.screen, self.field, self.content, self.top, self.row_fraction)
            while len(self.content) > 0 and self.content[len(self.content) - 1] == [None] * self.cols:
                self.content.pop()
            if len(self.content) == 0 and self.max_rows == self.generated_rows:
                self.win()
            return score
        else:
            if SOUND_EFFECTS_ON:
                if self.content[r][c] != None:
                    sound_hit_fail.play()
                else:
                    sound_miss.play()
            return 0


class Infopanel:
    def __init__(self, screen):
        self.position = INFO_FIELD
        self.score_position =INFO_FIELD[1] + 5 * CELLSIZE
        self.highscore_position = INFO_FIELD[1] + 7 * CELLSIZE
        self.text_position = INFO_FIELD[1] + FIELDLENGTH * CELLSIZE / 2
        self.text_flash_position = INFO_FIELD[1] + (FIELDLENGTH + 2) * CELLSIZE / 2
        self.tips_header_position = INFO_FIELD[1] + (FIELDLENGTH + 8) * CELLSIZE / 2
        self.tips_text_position = INFO_FIELD[1] + (FIELDLENGTH + 10) * CELLSIZE / 2
        self.text_flesh_visible = True
        self.score = 0
        self.highscore = 0
        self.screen = screen
        self.flash_timer = pyg.time.set_timer(FLASH_EVENT, TEXT_FLESH_TIME)
        self.tips_timer = pyg.time.set_timer(TIPS_EVENT, TIPS_TIME)

    def write(self, text, surf_top, surf_left=INFO_FIELD[0] + CELLSIZE, surf_size=((INFOWIDTH - 1) * CELLSIZE, CELLSIZE), color=WHITE, size=CELLSIZE):
        font = pyg.font.SysFont(pyg.font.get_default_font(), size)
        surf_start = (surf_left, surf_top)
        self.screen.blit(pyg.Surface(surf_size), surf_start)
        self.screen.blit(font.render(text, 1, color), surf_start)
        pyg.display.update(pyg.Rect(surf_start, surf_size))

    def message(self, text):
        self.write(text, self.text_position)

    def message_flash(self, text):
        self.write(text, self.text_flash_position)

    def message_tips_header(self, text):
        self.write(text, self.tips_header_position)

    def message_tips(self, text):
        self.write(text, self.tips_text_position, size=(CELLSIZE * 4) // 5)

    def add_score(self, score):
        self.score += score
        col = WHITE if self.score < self.highscore else GREEN
        self.write('SCORE: ' + str(self.score), self.score_position, color=col)

    def resetscore(self):
        if self.score >= self.highscore:
            self.write('HIGHSCORE: ' + str(self.score), self.highscore_position, color=RED)
            self.highscore = self.score
        self.score = 0
        self.write('SCORE: 0', self.score_position)


class Magazine:
    def __init__(self, screen, max_ammo=MAXAMMO, event=ADD_AMMO_EVENT, speed=AMMO_REPLENISH_SPEED):
        self.maxammo = max_ammo
        self.screen = screen
        self.position = pyg.Rect(INFO_FIELD[0] + CELLSIZE, INFO_FIELD[1] + CELLSIZE, (INFOWIDTH - 1) * CELLSIZE, 2 * CELLSIZE)
        self.content = deque([])
        self.add_ammo()
        self.event = event
        self.timer = pyg.time.set_timer(event, speed)

    def add_ammo(self):
        if len(self.content) < self.maxammo:
            self.content.append(get_random_color())
            self.draw()

    def color_bullet(self, cell, color):
        """Colors one 'bullet' cell"""
        cell.fill(color)
        return cell

    def draw(self):
        self.screen.blit(pyg.Surface(((INFOWIDTH - 1) * CELLSIZE, 2 * CELLSIZE)), self.position)
        cell = pyg.Surface((2 * CELLSIZE, 2 * CELLSIZE))
        for i, color in enumerate(self.content):
            self.screen.blit(self.color_bullet(cell, color), (INFO_FIELD[0] + (1 + 2 * i) * CELLSIZE, INFO_FIELD[1] + CELLSIZE))
        pyg.display.update(self.position)

    def shoot(self):
        if not self.is_empty():
            bullet = self.content.popleft()
            self.draw()
            return bullet
        else:
            if SOUND_EFFECTS_ON:
                sound_empty.play()
            return None

    def destroy(self):
        self.timer = pyg.time.set_timer(self.event, 0)
        self.content = deque([])
        self.draw()
        del self

    def is_empty(self):
        return len(self.content) == 0

    def reload(self):
        if not self.is_empty():
            if SOUND_EFFECTS_ON:
                sound_reload.play()
            bullet = self.content.popleft()
            self.content.append(bullet)
            self.draw()