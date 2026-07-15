"""Defines user interface elements for Shootris"""
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

from classes import *


#######################
# Classes definitions #
#######################

class Infopanel():
    """For information manipulation and displaying"""

    def __init__(self, screen, left=INFO_LEFT, top=1, width=INFOWIDTH, height=FIELDLENGTH):
        self.magazine = Magazine(screen, top=top+1, height=2)
        self.progress = Label(screen, top=top+4, pre_text='Progress: ')
        self.score = Label(screen, top=top+6, pre_text='SCORE: ', width=6)
        self.highscore = Label(screen, top=top+6, l_shift=8, pre_text='HIGHSCORE: ', width=7, font_color=RED)
        self.status = Label(screen, top=top+height/2)
        self.action = Label(screen, top=top+height/2+2)
        self.tips_header = Label(screen, top=top+height/2+6)
        self.tips = Label(screen, top=top+height/2+7, font_size=(4*CS)//5)


class Label:
    """Texts and other informative user interface stuff"""

    def __init__(self, screen, top, l_shift=1, pre_text='', width=None, height=1, info_left=INFO_LEFT,
                 font_color=WHITE, font_size=CS):
        self.left = l_shift + info_left
        self.top = top
        self.width = width if width else INFOWIDTH - l_shift
        self.height = height
        self.rect = pyg.Rect(self.left * CS, self.top * CS, self.width * CS, self.height * CS)
        self.screen = screen
        self.pre_text = pre_text
        self.font_size = font_size
        self.text = ''
        self.visible = True
        self.font_color = font_color

    def blink(self, text):
        """If text is visible, hide it; if invisible, show it"""

        if self.visible:
            self.write('')
        else:
            self.write(text)
        self.visible = not self.visible  # changes visibility

    def change_text(self, source):
        """Choose text from source which is different than current"""

        text = change_element(self.text, source)
        self.write(text)

    def write(self, text='', color=None):
        """Write given text"""

        if color is None:
            color = self.font_color
        self.text = text
        text_full = self.pre_text + str(text)
        font = pyg.font.SysFont(pyg.font.get_default_font(), self.font_size)
        surf_size = (self.width * CS, self.height * CS)
        surf_start = (self.left * CS, self.top * CS)
        self.screen.blit(pyg.Surface(surf_size), surf_start)  # clear the area
        self.screen.blit(font.render(text_full, 1, color), surf_start)  # write in the area

    def draw(self, surf, l_shift=0, t_shift=0):
        """Draw given surface"""

        self.screen.blit(surf, ((self.left + l_shift) * CS, (self.top + t_shift) * CS))


class Button:
    """A clickable rectangle with a label, highlighted on hover or keyboard focus"""

    def __init__(self, screen, rect, text, fill=MENU_BUTTON_FILL, hover_fill=GREEN,
                 border=WHITE, text_color=WHITE, font_size=CS):
        self.screen = screen
        self.rect = rect
        self.text = text
        self.fill = fill
        self.hover_fill = hover_fill
        self.border = border
        self.text_color = text_color
        self.font_size = font_size

    def draw(self, focused=False):
        """Fill + border + centered text; uses hover_fill when focused"""
        pyg.draw.rect(self.screen, self.hover_fill if focused else self.fill, self.rect)
        pyg.draw.rect(self.screen, self.border, self.rect, 2)
        font = pyg.font.SysFont(pyg.font.get_default_font(), self.font_size)
        text_surf = font.render(self.text, True, self.text_color)
        self.screen.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def is_hovered(self, pos):
        """Whether pos (mouse coordinates) is inside this button"""
        return self.rect.collidepoint(pos)


class Menu:
    """A self-contained settings screen or modal: title + MenuOption rows + action buttons.

    Owns a rectangle (the whole window for a full settings screen, or a small centered panel
    for a modal) and repaints that whole rectangle on every draw() - a shrinking row count can
    never leave stale pixels behind, since nothing outside a full wipe-and-redraw is relied on.
    """

    def __init__(self, screen, rect, options=None, actions=None, title=None,
                 row_height=50, spacing=16, chevron_width=44, label_ratio=0.4):
        self.screen = screen
        self.rect = rect
        self.options = options if options else []
        self.actions = actions if actions else []
        self.title = title
        self.row_height = row_height
        self.spacing = spacing
        self.chevron_width = chevron_width
        self.label_ratio = label_ratio
        self.focus = 0
        self.rows = []  # (label_rect, left_button, right_button, value_rect) per option
        self.action_buttons = []
        self.layout()

    def row_count(self):
        """Total navigable rows: options followed by actions"""
        return len(self.options) + len(self.actions)

    def layout(self):
        """(Re)computes every row/button rect from self.rect - call after changing options/actions.

        Content is capped to a comfortable max width and centered both horizontally and vertically
        within self.rect, so a Menu can own anything from a small modal panel to the whole window.
        """
        title_h = self.row_height + self.spacing if self.title else 0
        content_width = min(self.rect.width - 2 * self.spacing, 520)
        content_left = self.rect.centerx - content_width // 2
        content_height = title_h + self.row_count() * (self.row_height + self.spacing) - self.spacing
        top = self.rect.centery - content_height // 2
        self.title_top = top
        top += title_h

        self.rows = []
        for _ in self.options:
            row_rect = pyg.Rect(content_left, top, content_width, self.row_height)
            label_width = int(content_width * self.label_ratio)
            label_rect = pyg.Rect(row_rect.left, row_rect.top, label_width, self.row_height)
            control_rect = pyg.Rect(row_rect.left + label_width, row_rect.top,
                                     row_rect.width - label_width, self.row_height)
            left_btn = Button(self.screen, pyg.Rect(control_rect.left, control_rect.top,
                                                      self.chevron_width, self.row_height), '<')
            right_btn = Button(self.screen, pyg.Rect(control_rect.right - self.chevron_width, control_rect.top,
                                                      self.chevron_width, self.row_height), '>')
            value_rect = pyg.Rect(control_rect.left + self.chevron_width, control_rect.top,
                                   control_rect.width - 2 * self.chevron_width, self.row_height)
            self.rows.append((label_rect, left_btn, right_btn, value_rect))
            top += self.row_height + self.spacing

        self.action_buttons = []
        for action in self.actions:
            btn_rect = pyg.Rect(content_left, top, content_width, self.row_height)
            self.action_buttons.append(Button(self.screen, btn_rect, action))
            top += self.row_height + self.spacing

        self.focus = min(self.focus, self.row_count() - 1)

    def draw(self):
        """Wipe self.rect and redraw the title, option rows and action buttons from scratch"""
        pyg.draw.rect(self.screen, MENU_BG, self.rect)
        pyg.draw.rect(self.screen, WHITE, self.rect, 3)

        font = pyg.font.SysFont(pyg.font.get_default_font(), CS)
        if self.title:
            title_surf = font.render(self.title, True, WHITE)
            self.screen.blit(title_surf, title_surf.get_rect(midtop=(self.rect.centerx, self.title_top)))

        mouse_pos = pyg.mouse.get_pos()
        for i, (option, (label_rect, left_btn, right_btn, value_rect)) in enumerate(zip(self.options, self.rows)):
            row_focused = (i == self.focus)
            label_surf = font.render(option.name, True, GREEN if row_focused else WHITE)
            self.screen.blit(label_surf, label_surf.get_rect(midleft=(label_rect.left, label_rect.centery)))

            left_btn.draw(focused=row_focused or left_btn.is_hovered(mouse_pos))
            right_btn.draw(focused=row_focused or right_btn.is_hovered(mouse_pos))

            value_surf = font.render(str(option.label), True, WHITE)
            self.screen.blit(value_surf, value_surf.get_rect(center=value_rect.center))

        for i, button in enumerate(self.action_buttons):
            row_focused = (i + len(self.options) == self.focus)
            button.draw(focused=row_focused or button.is_hovered(mouse_pos))

    def move(self, direction):
        """Change focused row, wrapping around"""
        self.focus = (self.focus + direction) % self.row_count()

    def change(self, direction):
        """Cycle the focused row's option value, if it is an option row"""
        if self.focus < len(self.options):
            self.options[self.focus].cycle(direction)

    def activate(self):
        """Return the focused action, if the focused row is an action row, else None"""
        if self.focus >= len(self.options):
            return self.actions[self.focus - len(self.options)]
        return None

    def click(self, pos):
        """Handle a mouse click at pos: cycle a chevron, or return the clicked action"""
        for i, (label_rect, left_btn, right_btn, value_rect) in enumerate(self.rows):
            if left_btn.is_hovered(pos):
                self.focus = i
                self.options[i].cycle(-1)
                return None
            if right_btn.is_hovered(pos):
                self.focus = i
                self.options[i].cycle(1)
                return None
        for i, button in enumerate(self.action_buttons):
            if button.is_hovered(pos):
                self.focus = i + len(self.options)
                return self.actions[i]
        return None


class Magazine(Label):
    """Displays status of magazine"""

    def __init__(self, screen, l_shift=1, top=2, height=2):
        Label.__init__(self, screen, top, l_shift, height=height)
        self.show_ammo([])

    def show_ammo(self, magazine):
        self.draw(pyg.Surface((self.width * CS, self.height * CS)), 0, 0)
        for i, col in enumerate(magazine):
            bullet = pyg.Surface((2 * CS, 2 * CS))
            bullet.fill(col)
            self.draw(bullet, 2 * i, 0)


class Background:
    """Background image and it's properties"""

    def __init__(self, screen, width, height, area=GAME_FIELD, theme='random', pic='random', source=BACKGROUNDS,
                 path=IMG_FOLD+BG_IMG_FOLD, size=CS):
        self.clear = pyg.Surface((width * size, height * size))
        self.act = pyg.Surface((width * size, height * size))
        self.image = pyg.Surface((width * size, height * size))
        self.image.blit(self.load_image(path, theme, pic, source), area)
        self.img_area = area
        self.screen = screen
        self.redraw(self.clear)  # clear gamefield

    def load_image(self, path, theme, pic, source):
        """Load background image - randomly or with given theme / picture filename"""

        if theme == 'random':
            theme = rnd.choice(list(source))
        if pic == 'random':
            pic = rnd.choice(source[theme])
        return pyg.image.load(path + theme + '/' + pic)

    def reveal(self, rect):
        """Reveal background in the area of destroyed cells"""

        self.act.blit(self.image, rect, rect)

    def fade(self, f_type, step, max_step, group=ALL_SPRITES):
        """Draw background or image with alpha depending on fade step -> show or hide"""

        if f_type == 'in':
            image = self.image  # show
        elif f_type == 'out':
            image = self.clear  # hide

        self.screen.blit(self.act, (0, 0))
        image.set_alpha((step * 255) // max_step)
        self.redraw(image, group)

    def redraw(self, img, group=ALL_SPRITES):
        """Change background without covering sprites"""

        self.screen.blit(img, (0, 0))
        if group:
           group.draw(self.screen)