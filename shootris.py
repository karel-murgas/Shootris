"""Maim script for Shootris. Covers gameplay."""
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

from sys import exit
from classes import *


########################
# Function definitions #
########################

def init_screen():
    """Gets the screen ready and draws environment"""
    total_width = (MAXCOL + INFOWIDTH + 1)
    pyg.display.set_icon(pyg.image.load(IMG_PATH + '/icon_crosshair.gif'))
    screen_ = pyg.display.set_mode((total_width * CS, FIELDLENGTH * CS))
    pyg.display.set_caption('Shootris')
#    for r in range(FIELDLENGTH):
#        draw_cell(screen_, r, MAXCOL, WHITE)
    pyg.display.update()
    pyg.mouse.set_cursor(*pyg.cursors.load_xbm(IMG_PATH + '/cursor_crosshair.xbm', IMG_PATH + '/cursor_crosshair-mask.xbm'))
    return screen_


def pause_game():
    """Pauses game until SPACE is pressed"""

    waiting = True
    while waiting:
        event = pyg.event.poll()
        if event.type == pyg.KEYDOWN:
            if event.key == pyg.K_SPACE:
                #info.message_flash('')
                waiting = False
            elif event.key == pyg.K_ESCAPE:
                exit()


def play(screen):
    """Runs the main loop with game"""

    bg = Background(MAXCOL * CS, MAXROW * CS, theme='cats')

    #   if SOUND_BGM_ON:
 #       sound_bgm.play(loops=-1)
    clock = pyg.time.Clock()

    mb = Blob(1, LEFTSTICK, BOTTOMSTICK)
    for i in range(MAXROW):
        mb.add_row(0, -1 * i, MAXCOL)

    # main cycle #
    waiting = True
    while waiting:
        event = pyg.event.poll()
        if event.type == pyg.QUIT:
            exit()
        elif event.type == pyg.KEYDOWN:
            if event.key == pyg.K_ESCAPE:
                exit()
        #    if event.key == pyg.K_DOWN:  # for manual testing
        #        main_blob.move()
            elif event.key == pyg.K_SPACE:
                pause_game()
        mb.update(screen, 'move', mb.direction)
        mb.clear(screen, bg.image)
        mb.draw(screen)
        # pyg.display.flip()
        pyg.display.update()
        clock.tick(60)


################
# Main program #
################

# sets up screen and so on - needs code cleaning #
pyg.event.set_blocked([pyg.MOUSEMOTION, pyg.MOUSEBUTTONUP, pyg.KEYUP])
screen = init_screen()

# waiting for starting a game #
waiting = True
while waiting:
    event = pyg.event.poll()

    if event.type == pyg.QUIT:
        exit()
    elif event.type == pyg.KEYDOWN:
        if event.key == pyg.K_ESCAPE:
            exit()
        elif event.key == pyg.K_SPACE:
            play(screen)
    elif event.type == pyg.MOUSEBUTTONDOWN:
        if event.button == 1 or event.button == 3:
            if INFO_FIELD.collidepoint(pyg.mouse.get_pos()):
                play(screen)
