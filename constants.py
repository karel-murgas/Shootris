#############
# Libraries #
#############

import pygame as pyg


##########################
# Global initializations #
##########################

pyg.init()
pyg.font.init()
pyg.mixer.init()


#########
# Fixed #
#########

# Visual #
RED = (128, 0, 0)
GREEN = (0, 128, 0)
BLUE = (0, 0, 128)
WHITE = (255, 255, 255)
YELLOW = (128, 128, 0)
PINK = (128, 0, 128)
BLACK = (0, 0, 0)
CELLSIZE = 30

# Sound #
sound_game_over = pyg.mixer.Sound('sound/game_over.wav')
sound_win = pyg.mixer.Sound('sound/win.wav')

# Texts #
STARTGAME_TEXT = 'CLICK HERE or press SPACE'

# Gameplay #
COLORS = [RED, GREEN, BLUE, PINK, YELLOW]

# Events #
WIN_EVENT = pyg.USEREVENT + 1
ADD_AMMO_EVENT = pyg.USEREVENT + 2
LOOSE_EVENT = pyg.USEREVENT + 3
MAIN_BLOB_MOVE_EVENT = pyg.USEREVENT + 4
# SMALL_BLOB_MOVE_EVENT = pyg.USEREVENT + 5
FLASH_EVENT = pyg.USEREVENT + 6
TIPS_EVENT = pyg.USEREVENT + 7


############
# Settings #
############

# Screen #
FIELDLENGTH = 25
INFOWIDTH = 13

# Sound #
SOUND_ON = True

# Gameplay #
MAXROW = 100
MAXCOL = 15
MAXAMMO = 5
LEFTSTICK = 0.7  # probability of taking color from left cell
BOTTOMSTICK = 0.5  # probability of taking color from left cell

# Frequencies #
AMMO_REPLENISH_SPEED = 1500
MAIN_BLOB_SPEED = 80
# SMALL_BLOB_SPEED = 500
TEXT_FLESH_TIME = 500
TIPS_TIME = 8000


##############
# Calculated #
##############
GAME_FIELD = pyg.Rect(0, 0, MAXCOL*CELLSIZE, FIELDLENGTH*CELLSIZE)
INFO_FIELD = pyg.Rect((MAXCOL + 1) * CELLSIZE, 0, INFOWIDTH*CELLSIZE, FIELDLENGTH*CELLSIZE)