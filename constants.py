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

import os
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
# Colors
cb = {  # colors for colorblind
    'orange': (230, 159, 0),
    'blue_light': (86, 180, 233),
    'green': (0, 158, 115),
    'yellow': (240, 228, 66),
    'blue_dark': (0, 114, 178),
    'red': (213, 94, 0),
    'pink': (204, 121, 167),
}
RED = (128, 0, 0)
GREEN = (0, 128, 0)
BLUE = (0, 128, 128)
WHITE = (255, 255, 255)
YELLOW = (128, 128, 0)
PINK = (128, 0, 128)
BLACK = (0, 0, 0)
COLOR_SCHEMES = {
    'standard': [RED, GREEN, BLUE, PINK, YELLOW],
    'colorblind': [cb['red'], cb['green'], cb['blue_dark'], cb['pink'], cb['yellow'], cb['blue_light']],
}
COLORS = list(COLOR_SCHEMES['standard'])  # mutated in place by apply_color_scheme()


UP_BLOB_ALPHA = 192
EXPLODE_FLASH_COLOR = WHITE  # cells flash this color for one wave before the explosion kills them
MENU_BG = (24, 24, 30)  # dedicated menu screens' background, distinct from the game field's black
MENU_BUTTON_FILL = (45, 45, 54)  # unfocused button fill; GREEN is used for hover/keyboard focus
MAGAZINE_EMPTY_SLOT = MENU_BUTTON_FILL  # fill for an unloaded capacity slot in the magazine display
MAGAZINE_FULL_WARN = WHITE  # border flashed around the magazine once it can hold no more ammo; not a bullet color, so it never blends in
TUT_DIM_ALPHA = 140  # opacity of the tutorial's dark veil; highlighted rects are punched back to full brightness
CS = 30
BG_IMG_FOLD = 'backgrounds/'
TEXT_IMG_FOLD = 'textures/'
IMG_FOLD = 'images/'
WALL_IMG = 'squares_big_black.gif'
BLOB_IMG = 'squares_many_black.gif'
UP_IMG = 'squares_big_white.gif'
BACKGROUNDS = {}  # theme folder name -> sorted list of image filenames, scanned from disk
for _theme in sorted(os.listdir(IMG_FOLD + BG_IMG_FOLD)):
    _theme_path = IMG_FOLD + BG_IMG_FOLD + _theme
    if os.path.isdir(_theme_path):
        BACKGROUNDS[_theme] = sorted(os.listdir(_theme_path))
LAYER_WALL = 3  # most visible
LAYER_UP = 2
LAYER_MAIN = 1  # most hidden
FADE_STEPS = 100

# Sound #
SOUND = {
    # Game sounds
    'game_over': pyg.mixer.Sound('sound/game_over.wav'),
    'win': pyg.mixer.Sound('sound/win.wav'),
    'bg_music': pyg.mixer.Sound('sound/background.wav'),
    # Shooting effects
    'hit_success': pyg.mixer.Sound('sound/hit_success.wav'),
    'hit_fail': pyg.mixer.Sound('sound/hit_fail.wav'),  # a little bit louder would be better
    'reload': pyg.mixer.Sound('sound/reload.ogg'),
    'miss': pyg.mixer.Sound('sound/miss.wav'),
    'empty': pyg.mixer.Sound('sound/empty.wav')
}

# Texts #
TEXT_TIPS_HEADER = 'DID YOU KNOW?'
TEXT_AMMO_HEADER = 'AMMO'
TEXT_WELCOME = 'Welcome!'
TEXT_PAUSE_INFO = 'The game is PAUSED'
TEXT_UNPAUSE = 'Press SPACE to unpause'
TEXT_WON = 'YOU WON! Congratulations.'
TEXT_LOST = 'GAME OVER'
TEXT_INSTRUCTIONS = 'LEFT shoot, RIGHT change'
TIPS = [
    'New row is based on the row below it',
    'Right click moves first color in the magazine to the end',
    'You can pause the game with SPACE',
    'The game can be beaten, it is not endless',
    'Highscore lasts only for current session',
    'Game starts by clicking anywhere in right half of screen',
    'Full magazine will not get new colors',
    'ESCAPE will end the game instantly',
    'Up-going blob will destroy covered cells if shot',
    'Shoot up-going blob to spawn a new one',
    'If you win, whole background will uncover',
    'You have to win to enjoy view of the background',
    'Shooting up-going blob does not uncover background',
    'You gain one point for any destroyed cell',
    'Up-going blobs are perfect for destroying lonely cells',
    'Progress shows how many rows were already spawned',
    'To beat the game destroy all down-going cells',
    'Up-going cells can hit the ceiling, it\'s OK',
    'You lose if any cell from top hits the bottom',
    'Don\'t conserve ammo, this is not Shadowrun.',
    'You can reload also by clicking / tapping the magazine',
    'This game supports hotseat multiplayer'
]

# Tutorial texts #
TEXT_TUT_HEADER = 'TUTORIAL'
TEXT_TUT_CONTINUE = 'Click or press SPACE to continue'
TEXT_TUT_WELCOME = ('Welcome! The blob above grows and sinks toward the bottom wall - if any cell '
                    'reaches it, you lose. Progress counts the spawned rows. The pale shape rising '
                    'from the floor is an up-going blob; more on it later.')
TEXT_TUT_MATCH = ('Time is frozen - only here in the tutorial, so you can read in peace. A real '
                  'game never waits for you. The front bullet of your magazine matches the '
                  'highlighted cells - left-click one of them. All touching cells of that color '
                  'explode together.')
TEXT_TUT_REVEAL = ('Destroyed cells uncover the picture hiding behind the field - every cell in '
                   'the chain reveals its patch, not just the one you clicked - and each is '
                   'worth one point, see the SCORE.')
TEXT_TUT_AMMO = ('Ammo refills on its own over time, up to the magazine size - you just watched '
                 'new bullets appear.')
TEXT_TUT_SWAP = ('The front bullet does not match the highlighted cells. Right-click anywhere to send it '
                 'to the back - once the matching color is in front, shoot.')
TEXT_TUT_FULL = ('The magazine just filled to the brim. A full magazine takes no new colors - and '
                 'the front bullet matches nothing on the board anymore.')
TEXT_TUT_WASTE = ('Hoarding a useless bullet just clogs the magazine. Fire it anywhere - even '
                  'into empty space - to make room for a fresh color.')
TEXT_TUT_UP_RISE = ('Remember the pale up-going blob? Time will run again for a moment while it '
                    'crawls over some leftover cells - it is harmless on its own, even if it hits '
                    'the ceiling.')
TEXT_TUT_UP_SHOOT = ('Shoot the up-going blob! It destroys every cell it covers, of ANY color - '
                     'perfect for clearing lonely leftovers. Up-going cell kills do not uncover the '
                     'picture, though.')
TEXT_TUT_UP_SPAWN = ('Every up-going blob you shoot makes room for a new one. Time will run again '
                     'while a fresh one heads for these two highlighted blocks below.')
TEXT_TUT_UP_CONNECT = ('An up-going blob sets off every connected block of its own color it '
                       'touches when shot - even separate blobs go up together, bridged into '
                       'one chain reaction.')
TEXT_TUT_FINISH = ('You know it all now! Full control is yours from here - finish the board '
                   'yourself and reveal the whole picture. Good luck!')
TEXT_TUT_DONE = ('You did it! The picture is fully revealed - that is a win, same as in a real '
                 'game. Pause anytime with SPACE. Enjoy Shootris!')
TEXT_TUT_DONE_LOSE = ('A cell reached the bottom - that is a loss, same as in a real game. No '
                      'matter, you know the ropes now. Go try a real round!')

# Events #
END_EVENT = pyg.USEREVENT + 1
ADD_AMMO_EVENT = pyg.USEREVENT + 2
MAIN_BLOB_MOVE_EVENT = pyg.USEREVENT + 3
UP_BLOB_MOVE_EVENT = pyg.USEREVENT + 4
BLINK_EVENT = pyg.USEREVENT + 5
TIPS_EVENT = pyg.USEREVENT + 6
FADE_EVENT = pyg.USEREVENT + 7
EXPLODE_EVENT = pyg.USEREVENT + 8
MAGAZINE_FLASH_EVENT = pyg.USEREVENT + 9


############
# Settings #
############

# Screen #
FIELDLENGTH = 25  # how long will game field be, also defines screen height
INFOWIDTH = 16  # how wide will info filed be

# Sound #
SOUND_EFFECTS_ON = True
SOUND_BGM_ON = True

# Gameplay #
MAXCOLORS = 5  # how many of defined colors will be used
MAXROW = 100  # how many lines will be generated per game
MAXCOL = 15  # width of game field
MAXAMMO = 5  # length of magazine
LEFTSTICK = 0.7  # probability of taking color from left cell
BOTTOMSTICK = 0.5  # probability of taking color from left cell
UP_LEFTSTICK = 0.4
UP_BOTTOMSTICK = 0.75

# Tutorial #
TUT_SEED = 20160521  # fixed RNG seed pinning the few remaining random picks (background, fallback ammo)
TUT_RISE_ROWS = 4  # rows the main blob spawns while it watches, right after the welcome/threat popup
TUT_AMMO_DEMO = 2  # bullets to wait for during the ammo-generation demo
TUT_MAXAMMO = 4  # smaller magazine than a real game, so the full-magazine lesson arrives quickly
TUT_UP_BLOB_SPEED = 75  # ms per up-blob step; slower than UP_BLOB_SPEED so it crawls into position on cue
TUT_UP_FAST_SPEED = 20  # the second up-blob hurries toward the bridge demo instead
TUT_FINISH_AMMO_SPEED = 800  # faster than ADD_AMMO_SPEED - generous ammo so finishing the board feels quick
# The prebuilt board: one list per spawned row, first row spawns first and ends up lowest on screen.
# Values index into COLORS. The layout is authored around the lessons: color 0 forms the single
# region for the first shot (and must appear nowhere else - the waste-a-bullet lesson relies on
# color 0 being extinct after that shot), color 1 forms the swap-lesson region (plus harmless lone
# accents), color 2 forms exactly the two separated blocks the up-blob bridges, color 3 is filler,
# and color 4 never appears - it is reserved for the first up-blob so shooting it can't chain.
TUT_MB_SCRIPT = [
    [3, 3, 0, 0, 0, 0, 3, 1, 3, 3, 3, 3, 1, 3, 3],
    [3, 3, 0, 0, 0, 0, 3, 3, 3, 1, 1, 1, 1, 3, 3],
    [1, 3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 1],
    [3, 3, 3, 1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    [3, 3, 2, 2, 3, 1, 3, 3, 3, 2, 2, 3, 3, 1, 3],
    [3, 1, 2, 2, 3, 3, 3, 1, 3, 2, 2, 3, 1, 3, 3],
    [3, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 1, 3, 3, 3],
]
# Planned bullet arrivals (indices into COLORS), ordered so the right color is at the front for
# each lesson: c0+c1 arrive for the swap lesson, then c4+c2+c3 fill the magazine (front c0 is
# extinct by then - the bullet to waste), c4 shoots the first up-blob, c2 the bridging one.
TUT_AMMO = [0, 1, 4, 2, 3, 3, 3, 3, 3, 3]
TUT_START_AMMO = [0]  # preloaded magazine: one bullet matching the first target region

# Frequencies #
ADD_AMMO_SPEED = 1500
MAIN_BLOB_SPEED = 90
UP_BLOB_SPEED = 40
BLINK_TIME = 500
MAGAZINE_FLASH_SPEED = 150  # ms between magazine full-warning toggles - snappier than BLINK_TIME on purpose
TIPS_TIME = 8000
EXPLODE_WAVE_SPEED = 45  # ms between explosion waves, from the shot outward


##############
# Calculated #
##############

GAME_FIELD = pyg.Rect(1 * CS, 1 * CS, MAXCOL * CS, FIELDLENGTH * CS)  # used for background
INFO_LEFT = MAXCOL + 2
ALL_SPRITES = pyg.sprite.LayeredUpdates()  # Group for updating gamefield
FADE_SPEED = 3000 // FADE_STEPS
