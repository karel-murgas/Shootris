"""Unit tests for MenuOption in classes.py"""
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

from classes import MenuOption


#########
# Tests #
#########

def test_starts_on_first_choice():
    """A fresh MenuOption starts at index 0"""
    option = MenuOption('Theme', ['random', 'girls', 'cats'])
    assert option.value == 'random'
    assert option.label == 'random'


def test_cycle_forward_wraps_around():
    """Cycling past the last choice wraps back to the first"""
    option = MenuOption('Theme', ['random', 'girls', 'cats'])
    option.cycle(1)
    option.cycle(1)
    assert option.value == 'cats'
    option.cycle(1)
    assert option.value == 'random'


def test_cycle_backward_wraps_around():
    """Cycling backward from the first choice wraps to the last"""
    option = MenuOption('Theme', ['random', 'girls', 'cats'])
    option.cycle(-1)
    assert option.value == 'cats'


def test_labels_track_choices_by_default():
    """Without explicit labels, label is just str(choice)"""
    option = MenuOption('Colors', ['standard', 'colorblind'])
    option.cycle(1)
    assert option.value == 'colorblind'
    assert option.label == 'colorblind'


def test_custom_labels_stay_in_sync_with_value():
    """Explicit labels are looked up by the same index as the raw choice"""
    option = MenuOption('Colors', ['standard', 'colorblind'], labels=['Standard', 'Colorblind'])
    assert option.label == 'Standard'
    option.cycle(1)
    assert option.value == 'colorblind'
    assert option.label == 'Colorblind'
