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


def pause_game(display, clock):
    """Pauses game until SPACE is pressed"""

    display.status.write(TEXT_PAUSE_INFO)

    waiting = True
    while waiting:

        # Player controls
        event = pyg.event.poll()
        if event.type == pyg.KEYDOWN:
            if event.key == pyg.K_SPACE:
                waiting = False
            elif event.key == pyg.K_ESCAPE:
                exit()

        # Text events
        elif event.type == BLINK_EVENT:
            display.action.blink(TEXT_UNPAUSE)
        elif event.type == TIPS_EVENT:
            display.tips.change_text(TIPS)

        # Draw it + fps control
        pyg.display.update()
        clock.tick(60)  # max 60 fps

    # Clear display
    display.action.write('')  # Clears action area of display
    display.status.write(TEXT_INSTRUCTIONS)


def fade(clock, bg, status, last_step=FADE_STEPS):
    """Slowly hides / shows background; used when game ends"""

    pyg.time.set_timer(FADE_EVENT, FADE_SPEED)
    f_type = 'in' if status == 'win' else 'out'
    fade_step = 0

    waiting = True
    while waiting:

        event = pyg.event.poll()
        if event.type == FADE_EVENT:
            fade_step += 1
            bg.fade(f_type, fade_step, last_step, ALL_SPRITES)
            if fade_step == FADE_STEPS:
                waiting = False

        pyg.display.update()
        clock.tick(60)  # max 60 fps

    pyg.time.set_timer(FADE_EVENT, 0)


def play(screen, display, clock, highscore):
    """Runs the main loop with game"""

    # Game initialization #

    # Events
    pyg.time.set_timer(MAIN_BLOB_MOVE_EVENT, MAIN_BLOB_SPEED)
    pyg.time.set_timer(UP_BLOB_MOVE_EVENT, UP_BLOB_SPEED)
    pyg.time.set_timer(ADD_AMMO_EVENT, ADD_AMMO_SPEED)

    # Game objects
    mb = Blob(1, LEFTSTICK, BOTTOMSTICK, left=1, top=0, max_rows=MAXROW)
    ub = UpBlob(-2, UP_LEFTSTICK, UP_BOTTOMSTICK, left=1, top=FIELDLENGTH+2, max_rows=100, width=MAXCOL)
    deadpool = pyg.sprite.Group()
    cursor = Point()
    shooter = Gun(maxammo=6)

    # Sound
    if SOUND_BGM_ON:
        SOUND['bg_music'].play(loops=-1)

    # Display
    bg = Background(screen, MAXCOL + 2, FIELDLENGTH + 2, theme='girls', size=CS)
    score = 0
    display.magazine.show_ammo(shooter.magazine)
    display.score.write(score)
    display.highscore.write(highscore)
    display.action.write('')  # Clears action area of display
    display.status.write(TEXT_INSTRUCTIONS)
    fade_step = 0

    # Main cycle #
    waiting = True
    while waiting:
        event = pyg.event.poll()

        # Player controls
        if event.type == pyg.QUIT:  # end program
            exit()
        elif event.type == pyg.KEYDOWN:
            if event.key == pyg.K_ESCAPE:  # end program
                exit()
            elif event.key == pyg.K_SPACE:  # pause game
                pause_game(display, clock)
        elif event.type == pyg.MOUSEBUTTONDOWN:
            if event.button == 1:
                if GAME_FIELD.collidepoint(pyg.mouse.get_pos()):  # shot the gamefield
                    cursor.update(event.pos)
                    sc, status, win = shooter.shoot(cursor, mb, ub, deadpool, bg)  # test hit
                    display.magazine.show_ammo(shooter.magazine)
                    if sc > 0:  # got some points
                        score += sc
                        if score < highscore:
                            display.score.write(score, color=WHITE)
                        else:
                            display.score.write(score, color=GREEN)
                    if SOUND_EFFECTS_ON and SOUND[status]:  # sound ON and effect is defined
                        SOUND[status].play()
                    if win:  # won
                        pyg.event.post(pyg.event.Event(END_EVENT, {'status': 'win'}))
                if display.magazine.rect.collidepoint(pyg.mouse.get_pos()):  # clicked or tapped magazine
                    if shooter.change_ammo() == 'reload':
                        display.magazine.show_ammo(shooter.magazine)
            if event.button == 3:
                if shooter.change_ammo() == 'reload':
                    display.magazine.show_ammo(shooter.magazine)

        # Text events
        elif event.type == TIPS_EVENT:
            display.tips.change_text(TIPS)

        # Timed events
        elif event.type == MAIN_BLOB_MOVE_EVENT:
            if not mb.move():
                pyg.event.post(pyg.event.Event(END_EVENT, {'status': 'game_over'}))
            display.progress.write(str(mb.generated_rows) + ' / ' + str(mb.max_rows))
        elif event.type == UP_BLOB_MOVE_EVENT:
            ub = ub.move()
        elif event.type == ADD_AMMO_EVENT:
            if shooter.add_ammo() == 'added':
                display.magazine.show_ammo(shooter.magazine)

        # End of game
        elif event.type == END_EVENT:
            SOUND['bg_music'].stop()
            if SOUND_EFFECTS_ON:
                SOUND[event.status].play()
            display.status.write(TEXT_WON) if event == 'win' else display.status.write(TEXT_LOST)
            if event.status == 'win':
                ub.reset()
            fade(clock, bg, event.status, FADE_STEPS)
            waiting = False  # end loop

        # Draws everything
        if fade_step == 0:  # if game still runs
            ALL_SPRITES.clear(screen, bg.act)
            ALL_SPRITES.draw(screen)
        pyg.display.update()
        clock.tick(60)  # max 60 fps

    # Game ended
    pyg.time.set_timer(MAIN_BLOB_MOVE_EVENT, 0)
    pyg.time.set_timer(UP_BLOB_MOVE_EVENT, 0)
    pyg.time.set_timer(ADD_AMMO_EVENT, 0)
    ALL_SPRITES.empty()
    ALL_SPRITES.add(wall.sprites(), layer=LAYER_WALL)

    return(score)


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
clock = pyg.time.Clock()
display = Infopanel(screen, INFO_LEFT, 1, INFOWIDTH, FIELDLENGTH)
display.tips_header.write(TEXT_TIPS_HEADER)
display.tips.change_text(TIPS)
display.status.write(TEXT_WELCOME)

pyg.time.set_timer(TIPS_EVENT, TIPS_TIME)
pyg.time.set_timer(BLINK_EVENT, BLINK_TIME)
highscore = 0

# waiting for starting a game #
waiting = True
while waiting:
    event = pyg.event.poll()

    # Player controls
    if event.type == pyg.QUIT:
        exit()
    elif event.type == pyg.KEYDOWN:
        if event.key == pyg.K_ESCAPE:
            exit()
        elif event.key == pyg.K_SPACE:  # start game
            highscore = max(highscore, play(screen, display, clock, highscore))
    elif event.type == pyg.MOUSEBUTTONDOWN:
        if event.button == 1 or event.button == 3:  # start game
            if INFO_FIELD.collidepoint(pyg.mouse.get_pos()):
                highscore = max(highscore, play(screen, display, clock, highscore))

    # Autoevents
    elif event.type == BLINK_EVENT:
        display.action.blink(TEXT_STARTGAME)
    elif event.type == TIPS_EVENT:
        display.tips.change_text(TIPS)

    # Draw everything
    pyg.display.update()
    clock.tick(60)  # max 60 fps

