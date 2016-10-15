"""Initializes global variables and settings for Shootris"""
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

import pygame as pyg


##########################
# Global initializations #
##########################

pyg.font.init()
pyg.mixer.pre_init(44100, -16, 2, 2048)  # to fix sound delay
pyg.mixer.init()
pyg.init()


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
UP_BLOB_ALPHA = 192
CS = 30
IMG_PATH = 'images'
WALL_IMG = 'wall_texture.gif'
BACKGROUNDS = {
    'girls': ['bed.jpg', 'blond.jpg', 'bent.jpg'],
    'cats': ['double.jpg', 'white.jpg', 'beige.jpg']
}
LAYER_WALL = 3  # most visible
LAYER_UP = 2
LAYER_MAIN = 1  # most hidden

# Sound #
sound_game_over = pyg.mixer.Sound('sound/game_over.wav')
sound_win = pyg.mixer.Sound('sound/win.wav')
sound_bgm = pyg.mixer.Sound('sound/background.wav')
sound_hit_success = pyg.mixer.Sound('sound/hit_success.wav')
sound_hit_fail = pyg.mixer.Sound('sound/hit_fail.wav')  # a little bit louder would be better
sound_reload = pyg.mixer.Sound('sound/reload.ogg')
sound_miss = pyg.mixer.Sound('sound/miss.wav')
sound_empty = pyg.mixer.Sound('sound/empty.wav')

# Texts #
TEXT_STARTGAME = 'CLICK HERE or press SPACE'
TIPS = [
    'New row is based on the row below it',
    'Right click moves first color to the end',
    'You can pause the game with SPACE',
    'The game can be beated, it is not endless',
    'Highscore lasts only for current session',
    'Game starts by clicking right half of screen',
    'Full magazine will not get new colors',
    'ESCAPE will end the game instantly'
]

# Gameplay #
COLORS = [RED, GREEN, BLUE, PINK, YELLOW]

# Events #
WIN_EVENT = pyg.USEREVENT + 1
ADD_AMMO_EVENT = pyg.USEREVENT + 2
LOSE_EVENT = pyg.USEREVENT + 3
MAIN_BLOB_MOVE_EVENT = pyg.USEREVENT + 4
UP_BLOB_MOVE_EVENT = pyg.USEREVENT + 5
FLASH_EVENT = pyg.USEREVENT + 6
TIPS_EVENT = pyg.USEREVENT + 7


############
# Settings #
############

# Screen #
FIELDLENGTH = 25  # how long will game field be, also defines screen height
INFOWIDTH = 13  # how wide will info filed be

# Sound #
SOUND_EFFECTS_ON = True
SOUND_BGM_ON = False

# Gameplay #
MAXCOLORS = 5  # how many of defined colors will be used
MAXROW = 10  # how many lines will be generated per game
MAXCOL = 15  # width of game field
MAXAMMO = 5  # length of magazine
LEFTSTICK = 0.7  # probability of taking color from left cell
BOTTOMSTICK = 0.5  # probability of taking color from left cell
UP_LEFTSTICK = 0.4
UP_BOTTOMSTICK = 0.75

# Frequencies #
AMMO_REPLENISH_SPEED = 1500
MAIN_BLOB_SPEED = 80
UP_BLOB_SPEED = 25
TEXT_FLESH_TIME = 500
TIPS_TIME = 8000


##############
# Calculated #
##############

GAME_FIELD = pyg.Rect(1 * CS, 1 * CS, MAXCOL * CS, FIELDLENGTH * CS)
INFO_FIELD = pyg.Rect((MAXCOL + 2) * CS, 1 * CS, INFOWIDTH * CS, FIELDLENGTH * CS)
ALL_SPRITES = pyg.sprite.LayeredUpdates()
