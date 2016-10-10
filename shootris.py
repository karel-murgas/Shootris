<<<<<<< HEAD
#############
# Libraries #
#############

from sys import exit
from infopanel import *
from math import ceil


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

    # main cycle
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
            info.message('GAME OVER')
            magazine.destroy()
            waiting = False
        elif event.type == WIN_EVENT:
            info.message('YOU WON! Congratulations.')
            magazine.destroy()
            waiting = False
        elif event.type == pyg.MOUSEBUTTONDOWN:
            if event.button == 1:
                color = magazine.shoot()
                if main_blob.get_rect().collidepoint(event.pos):
                    row = event.pos[1] // CELLSIZE - main_blob.top
                    if event.pos[1] % CELLSIZE > main_blob.row_fraction != 0:
                        row += 1
                    info.add_score(main_blob.hit(event.pos[0] // CELLSIZE, row, color))
            elif event.button == 3:
                magazine.reload()

################
# Main program #
################

pyg.init()
pyg.event.set_blocked([pyg.MOUSEMOTION, pyg.MOUSEBUTTONUP, pyg.KEYUP])
SCREEN = init_screen()
info = Infopanel(SCREEN)
info.message('Welcome!')
info.message_flash(STARTGAME_TEXT)


# wating for starting a game
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
        if event.button == 1 or event.key == 3:
            if info.text_flash_position.collidepoint(pyg.mouse.get_pos()):
                play()
    elif event.type == FLASH_EVENT:
        if info.text_flesh_visible:
            info.message_flash('')
        else:
            info.message_flash(STARTGAME_TEXT)
        info.text_flesh_visible = not info.text_flesh_visible
=======
#############
# Libraries #
#############

from sys import exit
from infopanel import *
from math import ceil


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

    # main cycle
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
            info.message('GAME OVER')
            magazine.destroy()
            waiting = False
        elif event.type == WIN_EVENT:
            info.message('YOU WON! Congratulations.')
            magazine.destroy()
            waiting = False
        elif event.type == pyg.MOUSEBUTTONDOWN:
            if event.button == 1:
                color = magazine.shoot()
                if main_blob.get_rect().collidepoint(event.pos):
                    row = event.pos[1] // CELLSIZE - main_blob.top
                    if event.pos[1] % CELLSIZE > main_blob.row_fraction != 0:
                        row += 1
                    info.add_score(main_blob.hit(event.pos[0] // CELLSIZE, row, color))
            elif event.button == 3:
                magazine.reload()

################
# Main program #
################

pyg.init()
pyg.event.set_blocked([pyg.MOUSEMOTION, pyg.MOUSEBUTTONUP, pyg.KEYUP])
SCREEN = init_screen()
info = Infopanel(SCREEN)
info.message('Welcome!')
info.message_flash(STARTGAME_TEXT)


# wating for starting a game
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
        if event.button == 1 or event.key == 3:
            if info.text_flash_position.collidepoint(pyg.mouse.get_pos()):
                play()
    elif event.type == FLASH_EVENT:
        if info.text_flesh_visible:
            info.message_flash('')
        else:
            info.message_flash(STARTGAME_TEXT)
        info.text_flesh_visible = not info.text_flesh_visible
>>>>>>> d72fab28ca57042986d1990a54d846639220a228
