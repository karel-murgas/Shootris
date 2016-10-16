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
from ui_classes import *


########################
# Function definitions #
########################

def init_screen():
    """Gets the screen ready and draws environment"""
    total_width = (MAXCOL + INFOWIDTH + 2)  # game field width + info field width + walls
    total_height = (FIELDLENGTH + 2)  # game field height + 2
    pyg.display.set_icon(pyg.image.load(IMG_FOLD + 'icon_crosshair.gif'))
    screen_ = pyg.display.set_mode((total_width * CS, total_height * CS))
    pyg.display.set_caption('Shootris')
#    for r in range(FIELDLENGTH):
#        draw_cell(screen_, r, MAXCOL, WHITE)
    pyg.display.update()
    pyg.mouse.set_cursor(*pyg.cursors.load_xbm(IMG_FOLD + 'cursor_crosshair.xbm',
                                               IMG_FOLD + 'cursor_crosshair-mask.xbm'))
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

    bg = Background(screen, MAXCOL + 2, FIELDLENGTH + 2, theme='cats', size=CS)
    if SOUND_BGM_ON:
        sound_bgm.play(loops=-1)

    clock = pyg.time.Clock()

    mb = Blob(1, LEFTSTICK, BOTTOMSTICK, left=1, top=0, max_rows=MAXROW)
    ub = UpBlob(-2, UP_LEFTSTICK, UP_BOTTOMSTICK, left=1, top=FIELDLENGTH+2, max_rows=100, width=MAXCOL)
    deadpool = pyg.sprite.Group()
    pyg.time.set_timer(MAIN_BLOB_MOVE_EVENT, MAIN_BLOB_SPEED)
    pyg.time.set_timer(UP_BLOB_MOVE_EVENT, UP_BLOB_SPEED)
    pyg.time.set_timer(ADD_AMMO_EVENT, ADD_AMMO_SPEED)

    cursor = Point()
    shooter = Gun(maxammo=6)
    ammo_display = Magazine(screen, 1, 2)
    score_display = Label(screen, 1, 6)
    score = 0

    # Main cycle #
    waiting = True
    while waiting:
        event = pyg.event.poll()

        # Controls
        if event.type == pyg.QUIT:  # end program
            exit()
        elif event.type == pyg.KEYDOWN:
            if event.key == pyg.K_ESCAPE:  # end program
                exit()
            elif event.key == pyg.K_SPACE:  # pause game
                pause_game()
        elif event.type == pyg.MOUSEBUTTONDOWN:
            if event.button == 1 and GAME_FIELD.collidepoint(pyg.mouse.get_pos()):  # shoot the gamefield
                cursor.update(event.pos)
                sc, status, win = shooter.shoot(cursor, mb, ub, deadpool, bg)
                ammo_display.show_ammo(shooter.magazine)
                if sc > 0:  # got some points
                    score += sc
                    score_display.write('Score: ' + str(score))
                    # TODO: Sounds depending on status
                if win:  # won
                    pyg.event.post(pyg.event.Event(WIN_EVENT))
            if event.button == 3:
                if shooter.change_ammo() == 'changed':
                    ammo_display.show_ammo(shooter.magazine)

        # Timed events
        elif event.type == MAIN_BLOB_MOVE_EVENT:
            if not mb.move():
                pyg.event.post(pyg.event.Event(LOSE_EVENT))
        elif event.type == UP_BLOB_MOVE_EVENT:
            ub = ub.move()
        elif event.type == ADD_AMMO_EVENT:
            if shooter.add_ammo() == 'added':
                ammo_display.show_ammo(shooter.magazine)

        # Special events
        elif event.type == LOSE_EVENT:
            print('Game over')
            pyg.time.set_timer(MAIN_BLOB_MOVE_EVENT, 0)
            pyg.time.set_timer(UP_BLOB_MOVE_EVENT, 0)
            pyg.time.set_timer(ADD_AMMO_EVENT, 0)
            bg.fade_out(ALL_SPRITES)
        elif event.type == WIN_EVENT:
            pyg.time.set_timer(MAIN_BLOB_MOVE_EVENT, 0)
            pyg.time.set_timer(UP_BLOB_MOVE_EVENT, 0)
            pyg.time.set_timer(ADD_AMMO_EVENT, 0)
            ub.reset()
            bg.fade_in(ALL_SPRITES)
            print('You won')

        # Draws everything
        ALL_SPRITES.clear(screen, bg.act)
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
