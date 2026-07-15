"""Pytest bootstrap: run the game headless so logic can be unit tested"""
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


############################
# Headless test environment #
############################

# Force SDL to dummy drivers BEFORE any game module imports pygame, so importing
# constants.py (which runs pyg.init() and loads the sounds) needs no screen or
# audio device. Must happen at collection time, before the test modules import.
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

# constants.py loads sounds / images by relative path, so tests must run from the
# project root regardless of where pytest was launched.
os.chdir(os.path.dirname(os.path.abspath(__file__)))
