"""Defines user interface elements for Shootris"""
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

from classes import *


#######################
# Classes definitions #
#######################

class Infopanel():
    """For information manipulation and displaying"""

    def __init__(self, screen, left=INFO_LEFT, top=1, width=INFOWIDTH, height=FIELDLENGTH):
        self.magazine = Magazine(screen, l_shift=1, top=top+1, height=2)
        self.score = Label(screen, l_shift=1, top=top+5, pre_text='Score: ', width=width, height=height, info_left=left)


class Label:
    """Texts and other informative user interface stuff"""

    def __init__(self, screen, l_shift, top, pre_text='', width=INFOWIDTH, height=1, info_left=INFO_LEFT):
        self.left = l_shift + info_left
        self.top = top
        self.width = width - l_shift
        self.height = height
        self.rect = pyg.Rect(self.left * CS, self.top * CS, self.width * CS, self.height * CS)
        self.screen = screen
        self.pre_text = pre_text

    def write(self, text='', color=WHITE, font_size=CS):
        text_full = self.pre_text + str(text)
        font = pyg.font.SysFont(pyg.font.get_default_font(), font_size)
        surf_size = (self.width * CS, self.height * CS)
        surf_start = (self.left * CS, self.top * CS)
        self.screen.blit(pyg.Surface(surf_size), surf_start)  # clear the area
        self.screen.blit(font.render(text_full, 1, color), surf_start)  # write in the area

    def draw(self, surf, l_shift=0, t_shift=0):
        self.screen.blit(surf, ((self.left + l_shift) * CS, (self.top + t_shift) * CS))


class Magazine(Label):
    """Displays status of magazine"""

    def __init__(self, screen, l_shift=1, top=2, height=2):
        Label.__init__(self, screen, l_shift, top, height=height)
        self.show_ammo([])

    def show_ammo(self, magazine):
        self.draw(pyg.Surface((self.width * CS, self.height * CS)), 0, 0)
        for i, col in enumerate(magazine):
            bullet = pyg.Surface((2 * CS, 2 * CS))
            bullet.fill(col)
            self.draw(bullet, 2 * i, 0)
