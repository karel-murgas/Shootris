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
    pyg.display.set_icon(pyg.image.load('icon_crosshair.gif'))
    screen_ = pyg.display.set_mode((total_width*CELLSIZE, FIELDLENGTH*CELLSIZE))
    pyg.display.set_caption('Shootris')
    for r in range(FIELDLENGTH):
        draw_cell(screen_, r, MAXCOL, WHITE)
    pyg.display.update()
    pyg.mouse.set_cursor(*pyg.cursors.load_xbm('cursor_crosshair.xbm', 'cursor_crosshair-mask.xbm'))
    return screen_


def pause_game():
    """Pauses game until SPACE is pressed"""

    waiting = True
    while waiting:
        event = pyg.event.poll()
        if event.type == pyg.KEYDOWN:
            if event.key == pyg.K_SPACE:
                info.message_flash('')
                waiting = False
            elif event.key == pyg.K_ESCAPE:
                exit()
        elif event.type == FLASH_EVENT:
            if info.text_flesh_visible:
                info.message_flash('')
            else:
                info.message_flash('Press SPACE to unpause')
            info.text_flesh_visible = not info.text_flesh_visible


def play():
    """Runs the main loop with game"""
    SCREEN.blit(pyg.Surface((MAXCOL * CELLSIZE, FIELDLENGTH * CELLSIZE)), GAME_FIELD)
    main_blob = Blob(SCREEN, GAME_FIELD, MAIN_BLOB_MOVE_EVENT, MAIN_BLOB_SPEED)
    draw_blob(SCREEN, GAME_FIELD, main_blob.content, 0)
    magazine = Magazine(SCREEN)
    info.resetscore()
    info.message('LEFT shoot, RIGHT change')
    info.message_flash('')
    if SOUND_BGM_ON:
        sound_bgm.play(loops=-1)

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
        elif event.type == ADD_AMMO_EVENT:
            magazine.add_ammo()
        elif event.type == MAIN_BLOB_MOVE_EVENT:
            main_blob.move()
        elif event.type == LOOSE_EVENT:
            sound_bgm.stop()
            if SOUND_EFFECTS_ON:
                sound_game_over.play()
            info.message('GAME OVER')
            magazine.destroy()
            waiting = False
        elif event.type == WIN_EVENT:
            sound_bgm.stop()
            if SOUND_EFFECTS_ON:
                sound_win.play()
            info.message('YOU WON! Congratulations.')
            magazine.destroy()
            waiting = False
        elif event.type == pyg.MOUSEBUTTONDOWN:
            if event.button == 1:
                if GAME_FIELD.collidepoint(event.pos):
                    color = magazine.shoot()
                    if color != None:
                        if main_blob.get_rect().collidepoint(event.pos):
                            row = event.pos[1] // CELLSIZE - main_blob.top
                            if event.pos[1] % CELLSIZE > main_blob.row_fraction != 0:
                                row += 1
                            info.add_score(main_blob.hit(event.pos[0] // CELLSIZE, row, color))
                        else:
                            if SOUND_EFFECTS_ON:
                                sound_miss.play()
            elif event.button == 3:
                magazine.reload()
        elif event.type == TIPS_EVENT:
            info.message_tips(get_random_tip()[1])


################
# Main program #
################

# sets up screen and so on - needs code cleaning #
pyg.event.set_blocked([pyg.MOUSEMOTION, pyg.MOUSEBUTTONUP, pyg.KEYUP])
SCREEN = init_screen()
info = Infopanel(SCREEN)
info.message('Welcome!')
info.message_flash(TEXT_STARTGAME)
info.message_tips_header('DID YOU KNOW?')
info.message_tips(get_random_tip()[1])


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
            play()
    elif event.type == pyg.MOUSEBUTTONDOWN:
        if event.button == 1 or event.button == 3:
            if INFO_FIELD.collidepoint(pyg.mouse.get_pos()):
                play()
    elif event.type == FLASH_EVENT:
        if info.text_flesh_visible:
            info.message_flash('')
        else:
            info.message_flash(TEXT_STARTGAME)
        info.text_flesh_visible = not info.text_flesh_visible
    elif event.type == TIPS_EVENT:
        info.message_tips(get_random_tip()[1])
