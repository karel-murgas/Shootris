#############
# Libraries #
#############

from blobs import *


##################
# Initialization #
##################

tips_of_day = [
    'New row is based on the row below it',
    'Right click moves first color to the end',
    'You can pause the game with SPACE',
    'The game can be beated, it is not endless',
    'Highscore lasts only for current session',
    'Game starts by clicking right half of screen'
]


########################
# Function definitions #
########################

class Infopanel:
    def __init__(self, screen):
        self.position = INFO_FIELD
        self.score_position =INFO_FIELD[1] + 5 * CELLSIZE
        self.highscore_position = INFO_FIELD[1] + 7 * CELLSIZE
        self.text_position = INFO_FIELD[1] + FIELDLENGTH * CELLSIZE / 2
        self.text_flash_position = INFO_FIELD[1] + (FIELDLENGTH + 2) * CELLSIZE / 2
        self.tips_header_position = INFO_FIELD[1] + (FIELDLENGTH + 8) * CELLSIZE / 2
        self.tips_text_position = INFO_FIELD[1] + (FIELDLENGTH + 10) * CELLSIZE / 2
        self.text_flesh_visible = True
        self.score = 0
        self.highscore = 0
        self.screen = screen
        self.flash_timer = pyg.time.set_timer(FLASH_EVENT, TEXT_FLESH_TIME)
        self.tips_timer = pyg.time.set_timer(TIPS_EVENT, TIPS_TIME)

    def write(self, text, surf_top, surf_left=INFO_FIELD[0] + CELLSIZE, surf_size=((INFOWIDTH - 1) * CELLSIZE, CELLSIZE), color=WHITE, size=CELLSIZE):
        font = pyg.font.SysFont(pyg.font.get_default_font(), size)
        surf_start = (surf_left, surf_top)
        self.screen.blit(pyg.Surface(surf_size), surf_start)
        self.screen.blit(font.render(text, 1, color), surf_start)
        pyg.display.update(pyg.Rect(surf_start, surf_size))

    def message(self, text):
        self.write(text, self.text_position)

    def message_flash(self, text):
        self.write(text, self.text_flash_position)

    def message_tips_header(self, text):
        self.write(text, self.tips_header_position)

    def message_tips(self, text):
        self.write(text, self.tips_text_position, size=(CELLSIZE * 4) // 5)

    def add_score(self, score):
        self.score += score
        col = WHITE if self.score < self.highscore else GREEN
        self.write('SCORE: ' + str(self.score), self.score_position, color=col)

    def resetscore(self):
        if self.score >= self.highscore:
            self.write('HIGHSCORE: ' + str(self.score), self.highscore_position, color=RED)
            self.highscore = self.score
        self.score = 0
        self.write('SCORE: 0', self.score_position)


class Magazine:
    def __init__(self, screen, max_ammo=MAXAMMO, event=ADD_AMMO_EVENT, speed=AMMO_REPLENISH_SPEED):
        self.maxammo = max_ammo
        self.screen = screen
        self.position = pyg.Rect(INFO_FIELD[0] + CELLSIZE, INFO_FIELD[1] + CELLSIZE, (INFOWIDTH - 1) * CELLSIZE, 2 * CELLSIZE)
        self.content = deque([])
        self.add_ammo()
        self.event = event
        self.timer = pyg.time.set_timer(event, speed)

    def add_ammo(self):
        if len(self.content) < self.maxammo:
            self.content.append(get_random_element())
            self.draw()

    def color_bullet(self, cell, color):
        """Colors one 'bullet' cell"""
        cell.fill(color)
        return cell

    def draw(self):
        self.screen.blit(pyg.Surface(((INFOWIDTH - 1) * CELLSIZE, 2 * CELLSIZE)), self.position)
        cell = pyg.Surface((2 * CELLSIZE, 2 * CELLSIZE))
        for i, color in enumerate(self.content):
            self.screen.blit(self.color_bullet(cell, color), (INFO_FIELD[0] + (1 + 2 * i) * CELLSIZE, INFO_FIELD[1] + CELLSIZE))
        pyg.display.update(self.position)

    def shoot(self):
        if not self.is_empty():
            bullet = self.content.popleft()
            self.draw()
            return bullet
        else:
            return None

    def destroy(self):
        self.timer = pyg.time.set_timer(self.event, 0)
        self.content = deque([])
        self.draw()
        del self

    def is_empty(self):
        return len(self.content) == 0

    def reload(self):
        if not self.is_empty():
            bullet = self.content.popleft()
            self.content.append(bullet)
            self.draw()