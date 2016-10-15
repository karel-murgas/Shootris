"""Main script for Shootris. Covers gameplay."""
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
    total_width = (MAXCOL + INFOWIDTH + 2)  # game field width + info field width + walls
    total_height = (FIELDLENGTH + 2)  # game field height + 2
    pyg.display.set_icon(pyg.image.load(IMG_PATH + '/icon_crosshair.gif'))
    screen_ = pyg.display.set_mode((total_width * CS, total_height * CS))
    pyg.display.set_caption('Shootris')
#    for r in range(FIELDLENGTH):
#        draw_cell(screen_, r, MAXCOL, WHITE)
    pyg.display.update()
    pyg.mouse.set_cursor(*pyg.cursors.load_xbm(IMG_PATH + '/cursor_crosshair.xbm',
                                               IMG_PATH + '/cursor_crosshair-mask.xbm'))
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

    bg = Background(MAXCOL + 2, FIELDLENGTH + 2, theme='cats', size=CS)
    if SOUND_BGM_ON:
        sound_bgm.play(loops=-1)

    clock = pyg.time.Clock()

    mb = Blob(1, LEFTSTICK, BOTTOMSTICK, left=1, top=0, max_rows=MAXROW)
    ub = Up_blob(-1, UP_LEFTSTICK, UP_BOTTOMSTICK, left=1, top=FIELDLENGTH+2, max_rows=100, width=MAXCOL)
    pyg.time.set_timer(MAIN_BLOB_MOVE_EVENT, MAIN_BLOB_SPEED)
    pyg.time.set_timer(UP_BLOB_MOVE_EVENT, UP_BLOB_SPEED)

    cursor = Point()
    shooter = Gun()

    # Main cycle #
    waiting = True
    while waiting:
        event = pyg.event.poll()

        if event.type == pyg.QUIT:  # end program
            exit()
        elif event.type == pyg.KEYDOWN:
            if event.key == pyg.K_ESCAPE:  # end program
                exit()
            elif event.key == pyg.K_SPACE:  # pause game
                pause_game()
        elif event.type == pyg.MOUSEBUTTONDOWN:
            if event.button == 1:
                cursor.update(event.pos)
                print(shooter.shoot(pyg.sprite.spritecollide(cursor, mb, 0)))
        elif event.type == MAIN_BLOB_MOVE_EVENT:
            if not mb.move():
                pyg.event.post(pyg.event.Event(LOSE_EVENT))
        elif event.type == UP_BLOB_MOVE_EVENT:
            ub = ub.move()
        elif event.type == LOSE_EVENT:
            print('Game over')
            pyg.time.set_timer(MAIN_BLOB_MOVE_EVENT, 0)
            pyg.time.set_timer(UP_BLOB_MOVE_EVENT, 0)

        # Draws everything
        ALL_SPRITES.clear(screen, bg.image)
        ALL_SPRITES.draw(screen)
        pyg.display.update()
        clock.tick(60)  # max 60 fps


################
# Main program #
################

# sets up screen and so on - needs code cleaning #
pyg.event.set_blocked([pyg.MOUSEMOTION, pyg.MOUSEBUTTONUP, pyg.KEYUP])
screen = init_screen()
wall = Wall()
wall.create_wall(0, 0, width=MAXCOL, height=FIELDLENGTH, image=WALL_IMG, color=WHITE, size=CS)
wall.draw(screen)
pyg.display.update()

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
