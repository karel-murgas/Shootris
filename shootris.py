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

    display.status.write(TEXT_WON) if status == 'win' else display.status.write(TEXT_LOST)
    pyg.time.set_timer(FADE_EVENT, 0)


def image_label(filename):
    """Turn a background filename into a display label, e.g. 'pirate.jpg' -> 'Pirate'"""
    return filename.rsplit('.', 1)[0].capitalize()


def run_settings_menu(screen, clock, defaults):
    """Blocking full-window settings screen: pick background theme/image and color scheme, then START GAME"""

    themes = ['random'] + sorted(BACKGROUNDS)
    theme_option = MenuOption('Theme', themes, labels=[t.capitalize() for t in themes])
    if defaults['theme'] in themes:
        theme_option.index = themes.index(defaults['theme'])

    color_choices = ['standard', 'colorblind']
    color_option = MenuOption('Colors', color_choices, labels=[c.capitalize() for c in color_choices])
    if defaults['color_scheme'] in color_choices:
        color_option.index = color_choices.index(defaults['color_scheme'])

    restrict_choices = [False, True]
    restrict_option = MenuOption('Endgame Ammo', restrict_choices, labels=['Any Color', 'Board Only'])
    restrict_option.index = restrict_choices.index(defaults['restrict_final_colors'])

    image_options = {}  # theme name -> its MenuOption, built lazily and remembered while cycling themes

    def image_option_for(theme):
        if theme not in image_options:
            choices = ['random'] + BACKGROUNDS[theme]
            option = MenuOption('Image', choices, labels=['Random'] + [image_label(c) for c in BACKGROUNDS[theme]])
            if theme == defaults['theme'] and defaults['image'] in choices:
                option.index = choices.index(defaults['image'])
            image_options[theme] = option
        return image_options[theme]

    def current_options():
        options = [theme_option]
        if theme_option.value != 'random':
            options.append(image_option_for(theme_option.value))
        options.append(color_option)
        options.append(restrict_option)
        return options

    menu = Menu(screen, screen.get_rect(), options=current_options(), actions=['START GAME', 'TUTORIAL'],
               title='SHOOTRIS')

    chosen_action = None
    waiting = True
    while waiting:
        event = pyg.event.poll()
        changed = False

        if event.type == pyg.QUIT:
            exit()
        elif event.type == pyg.KEYDOWN:
            if event.key == pyg.K_ESCAPE:
                exit()
            elif event.key == pyg.K_UP:
                menu.move(-1)
            elif event.key == pyg.K_DOWN:
                menu.move(1)
            elif event.key == pyg.K_LEFT:
                menu.change(-1)
                changed = True
            elif event.key == pyg.K_RIGHT:
                menu.change(1)
                changed = True
            elif event.key in (pyg.K_RETURN, pyg.K_SPACE):
                activated = menu.activate()
                if activated == 'START GAME':
                    chosen_action = 'play'
                    waiting = False
                elif activated == 'TUTORIAL':
                    chosen_action = 'tutorial'
                    waiting = False
        elif event.type == pyg.MOUSEBUTTONDOWN and event.button == 1:
            action = menu.click(event.pos)
            changed = True
            if action == 'START GAME':
                chosen_action = 'play'
                waiting = False
            elif action == 'TUTORIAL':
                chosen_action = 'tutorial'
                waiting = False

        if changed and waiting:
            menu.options = current_options()
            menu.layout()

        if waiting:
            menu.draw()  # every frame, so hover highlighting follows the mouse live
            pyg.display.update()
        clock.tick(60)  # max 60 fps

    return {
        'theme': theme_option.value,
        'image': image_options[theme_option.value].value if theme_option.value != 'random' else 'random',
        'color_scheme': color_option.value,
        'restrict_final_colors': restrict_option.value,
        'action': chosen_action,
    }


def run_end_screen(screen, clock):
    """Blocking modal after a round ends: REPLAY or RETURN TO MENU, final frame stays frozen behind it"""

    panel_rect = pyg.Rect(0, 0, 340, 180)
    panel_rect.center = ((INFO_LEFT + INFOWIDTH / 2) * CS, screen.get_rect().centery)  # over the info
    menu = Menu(screen, panel_rect, actions=['REPLAY', 'RETURN TO MENU'])            # panel, not the picture

    choice = None
    while choice is None:
        event = pyg.event.poll()

        if event.type == pyg.QUIT:
            exit()
        elif event.type == pyg.KEYDOWN:
            if event.key == pyg.K_ESCAPE:
                exit()
            elif event.key == pyg.K_UP:
                menu.move(-1)
            elif event.key == pyg.K_DOWN:
                menu.move(1)
            elif event.key in (pyg.K_RETURN, pyg.K_SPACE):
                choice = menu.activate()
        elif event.type == pyg.MOUSEBUTTONDOWN and event.button == 1:
            choice = menu.click(event.pos)

        if choice is None:
            menu.draw()  # every frame, so hover highlighting follows the mouse live
            pyg.display.update()
        clock.tick(60)  # max 60 fps

    return 'replay' if choice == 'REPLAY' else 'menu'


def explode_effect(screen, clock, mb, deadpool, bg, wave_speed=EXPLODE_WAVE_SPEED, frame=None):
    """Kill deadpool cells wave by wave, from the shot outward, flashing each wave before it dies"""

    waves = mb.group_by_wave(deadpool)
    pyg.time.set_timer(EXPLODE_EVENT, wave_speed)

    flashing = []
    next_wave = 0
    waiting = True
    while waiting:

        event = pyg.event.poll()
        if event.type == EXPLODE_EVENT:
            mb.ready_to_die(flashing, True, bg)  # cells flashed last wave now die
            if next_wave < len(waves):
                flashing = waves[next_wave]
                for cell in flashing:
                    cell.colorate(EXPLODE_FLASH_COLOR)  # brief flash before dying
                next_wave += 1
            else:
                waiting = False

        if frame:  # the tutorial repaints its whole frame (veil, popup) around the explosion
            frame()
        else:
            ALL_SPRITES.clear(screen, bg.act)
            ALL_SPRITES.draw(screen)
        pyg.display.update()
        clock.tick(60)  # max 60 fps

    pyg.time.set_timer(EXPLODE_EVENT, 0)


def draw_tutorial_frame(screen, display, bg, overlay, mb, shooter, score_state, highlights, text, prompt=None):
    """Repaint one whole tutorial frame from scratch: live board, info labels, then veil and popup.

    A full repaint every frame is essential - the veil is an alpha blit, so darkening the previous
    frame's pixels again each frame would accumulate to pure black on anything not redrawn (this
    happened for real: magazine, score and the TUTORIAL header all faded to invisibility).
    """

    screen.blit(bg.act, (0, 0))  # whole game field, including revealed picture patches
    ALL_SPRITES.draw(screen)
    if text is None:  # None = plain game view - erase any popup/highlight border before labels redraw
        overlay.clear()
    display.status.write(TEXT_TUT_HEADER)
    display.magazine_label.write(TEXT_AMMO_HEADER)  # static, but the veil dims it - repaint it too
    display.progress.write(str(mb.generated_rows) + ' / ' + str(mb.max_rows))
    display.score.write(score_state['score'])
    display.magazine.show_ammo(shooter.magazine, shooter.maxammo)
    if text is not None:
        overlay.draw(highlights() if callable(highlights) else highlights, text, prompt)


def tutorial_watch(screen, display, clock, bg, overlay, mb, ub, shooter, score_state, text, highlights, *,
                   timers, until, speeds=None):
    """Let selected real-game timers run until `until()` says stop; player input has no effect here"""

    periods = {MAIN_BLOB_MOVE_EVENT: MAIN_BLOB_SPEED, UP_BLOB_MOVE_EVENT: TUT_UP_BLOB_SPEED,
               ADD_AMMO_EVENT: ADD_AMMO_SPEED}
    if speeds:
        periods.update(speeds)
    for event_type in timers:
        pyg.time.set_timer(event_type, periods[event_type])

    leave = False
    waiting = True
    while waiting:
        event = pyg.event.poll()

        if event.type == pyg.QUIT:
            exit()
        elif event.type == pyg.KEYDOWN and event.key == pyg.K_ESCAPE:
            leave = True
            waiting = False
        elif event.type == MAIN_BLOB_MOVE_EVENT:
            if not mb.move():  # safety net: the scripted board is authored to never reach the wall mid-tutorial
                pyg.time.set_timer(MAIN_BLOB_MOVE_EVENT, 0)
        elif event.type == UP_BLOB_MOVE_EVENT:
            ub = ub.move()
        elif event.type == ADD_AMMO_EVENT:
            shooter.add_ammo(mb, ub)

        if until():
            waiting = False

        draw_tutorial_frame(screen, display, bg, overlay, mb, shooter, score_state, highlights, text)
        pyg.display.update()
        clock.tick(60)

    for event_type in timers:
        pyg.time.set_timer(event_type, 0)
    return ub, leave


def tutorial_act(screen, display, clock, bg, overlay, mb, ub, shooter, score_state, text, highlights, *,
                  accept=None, allow_swap=False, allow_continue=False, require_front=None, require_target=None):
    """Freeze time and wait for exactly the taught action; anything else is inert"""

    prompt = TEXT_TUT_CONTINUE if allow_continue else None
    cursor = Point()
    leave = False

    waiting = True
    while waiting:
        event = pyg.event.poll()

        if event.type == pyg.QUIT:
            exit()
        elif event.type == pyg.KEYDOWN:
            if event.key == pyg.K_ESCAPE:
                leave = True
                waiting = False
            elif allow_continue and event.key == pyg.K_SPACE:
                waiting = False
        elif event.type == pyg.MOUSEBUTTONDOWN:
            if event.button == 1 and allow_continue:
                waiting = False
            elif event.button == 1 and accept and GAME_FIELD.collidepoint(pyg.mouse.get_pos()):
                cursor.update(pyg.mouse.get_pos())
                front = shooter.magazine[0] if shooter.magazine else None
                on_target = require_target is None or pyg.sprite.spritecollideany(cursor, require_target, None)
                if (require_front is None or front == require_front) and on_target:  # else inert: no bullet spent
                    deadpool = pyg.sprite.Group()
                    sc, status, _ = shooter.shoot(cursor, mb, ub, deadpool)  # win is unused: not wired up here
                    if sc > 0:
                        score_state['score'] += sc
                    if SOUND_EFFECTS_ON and SOUND[status]:
                        SOUND[status].play()
                    if len(deadpool) > 0:
                        explode_effect(screen, clock, mb, deadpool, bg,
                                       frame=lambda: draw_tutorial_frame(screen, display, bg, overlay, mb,
                                                                         shooter, score_state, highlights,
                                                                         text, prompt))
                    if status in accept:
                        waiting = False
            elif event.button == 3 and allow_swap:
                shooter.change_ammo()

        draw_tutorial_frame(screen, display, bg, overlay, mb, shooter, score_state, highlights, text, prompt)
        pyg.display.update()
        clock.tick(60)

    return leave


def tutorial_finish(screen, display, clock, bg, mb, ub, shooter, score_state):
    """Hand back real, unrestricted gameplay so the player finishes the board and wins on their own"""

    screen.blit(bg.act, (0, 0))  # wipe the tutorial veil before resuming plain incremental rendering
    ALL_SPRITES.draw(screen)

    pyg.time.set_timer(MAIN_BLOB_MOVE_EVENT, MAIN_BLOB_SPEED)
    pyg.time.set_timer(UP_BLOB_MOVE_EVENT, UP_BLOB_SPEED)
    pyg.time.set_timer(ADD_AMMO_EVENT, TUT_FINISH_AMMO_SPEED)
    shooter.script.clear()  # the scripted plan is spent - genuine random ammo from here on
    shooter.maxammo = MAXAMMO
    # by now every scripted lesson has emptied its own color everywhere on the board (colors 0
    # and 2 are extinct, 4 never appears here) - restrict ammo to colors still standing, so every
    # arrival is useful instead of mostly wasted draws from colors that no longer exist
    shooter.restrict_final_colors = True
    display.magazine.show_ammo(shooter.magazine, shooter.maxammo)

    deadpool = pyg.sprite.Group()
    cursor = Point()
    result = None
    while result is None:
        event = pyg.event.poll()

        if event.type == pyg.QUIT:
            exit()
        elif event.type == pyg.KEYDOWN and event.key == pyg.K_ESCAPE:
            result = 'leave'
        elif event.type == pyg.MOUSEBUTTONDOWN:
            if event.button == 1 and GAME_FIELD.collidepoint(pyg.mouse.get_pos()):
                cursor.update(pyg.mouse.get_pos())
                sc, status, win = shooter.shoot(cursor, mb, ub, deadpool)
                display.magazine.show_ammo(shooter.magazine, shooter.maxammo)
                if sc > 0:
                    score_state['score'] += sc
                    display.score.write(score_state['score'])
                if SOUND_EFFECTS_ON and SOUND[status]:
                    SOUND[status].play()
                if len(deadpool) > 0:
                    explode_effect(screen, clock, mb, deadpool, bg)
                if win:
                    ub.reset()  # kill any up-blob cells still on screen so the win fade shows a clean picture
                    result = 'win'
            elif event.button == 3:
                if shooter.change_ammo() == 'reload':
                    display.magazine.show_ammo(shooter.magazine, shooter.maxammo)
        elif event.type == MAIN_BLOB_MOVE_EVENT:
            if not mb.move():
                result = 'game_over'
            display.progress.write(str(mb.generated_rows) + ' / ' + str(mb.max_rows))
        elif event.type == UP_BLOB_MOVE_EVENT:
            ub = ub.move()
        elif event.type == ADD_AMMO_EVENT:
            if shooter.add_ammo(mb, ub) == 'added':
                display.magazine.show_ammo(shooter.magazine, shooter.maxammo)

        ALL_SPRITES.clear(screen, bg.act)
        ALL_SPRITES.draw(screen)
        pyg.display.update()
        clock.tick(60)

    pyg.time.set_timer(MAIN_BLOB_MOVE_EVENT, 0)
    pyg.time.set_timer(UP_BLOB_MOVE_EVENT, 0)
    pyg.time.set_timer(ADD_AMMO_EVENT, 0)
    return result


def run_tutorial(screen, display, clock, settings):
    """Scripted lessons on one live, prebuilt board; the player acts only in frozen, guided moments"""

    screen.fill(BLACK)
    ALL_SPRITES.empty()
    ALL_SPRITES.add(wall.sprites(), layer=LAYER_WALL)
    bg = Background(screen, MAXCOL + 2, FIELDLENGTH + 2, theme=settings['theme'], pic=settings['image'], size=CS)
    overlay = TutorialOverlay(screen)
    rnd.seed(TUT_SEED)  # board and ammo are scripted; the seed pins the few remaining random picks

    mb = ScriptedBlob([[COLORS[i] for i in row] for row in TUT_MB_SCRIPT])
    ub = UpBlob(-2)
    # left counts screen columns (the wall is column 0), so 7 puts it under board columns 6-8,
    # where three cells of mixed colors survive the earlier lessons for the covers-anything demo
    ub.load_layout([[COLORS[4]] * 3], left=7, top_row=FIELDLENGTH + 2, image=UP_IMG, alpha=UP_BLOB_ALPHA)
    ub.color = COLORS[4]
    shooter = Gun(maxammo=TUT_MAXAMMO, script=[COLORS[i] for i in TUT_AMMO])
    shooter.magazine.extend(COLORS[i] for i in TUT_START_AMMO)
    score_state = {'score': 0}

    display.action.write('')
    display.highscore.pre_text = ''  # hide the whole label, not just the value - restored on leave
    display.highscore.write('')
    display.tips_header.write('')  # the startup tips would show through the per-frame repaints
    display.tips.write('')

    all_timers = [MAIN_BLOB_MOVE_EVENT, UP_BLOB_MOVE_EVENT, ADD_AMMO_EVENT]
    # Highlight frames: the magazine one hugs the actual slots (the label is much wider), the
    # text labels get a little breathing room so the frame doesn't sit on the glyphs
    mag_rect = pyg.Rect(display.magazine.rect.left, display.magazine.rect.top,
                        2 * CS * shooter.maxammo, display.magazine.rect.height).inflate(8, 8)
    score_rect = display.score.rect.inflate(10, 14)
    progress_rect = pyg.Rect(display.progress.rect.left, display.progress.rect.top,
                             6 * CS, display.progress.rect.height).inflate(10, 14)  # the label rect spans the panel
    bottom_wall = pyg.Rect(0, GAME_FIELD.bottom, (MAXCOL + 2) * CS, CS)
    field_and_wall = GAME_FIELD.union(bottom_wall)  # one rect, not two - two adjacent outlines
    # double up right where they meet and look like a rendering glitch at the field's bottom edge
    whole_field = GAME_FIELD.inflate(2 * CS, 2 * CS)  # field + all four wall edges, for excluding
    # the picture reveal from the veil entirely - field_and_wall above only covers the bottom edge

    def leave_tutorial():
        for event_type in all_timers:
            pyg.time.set_timer(event_type, 0)
        ALL_SPRITES.empty()
        ALL_SPRITES.add(wall.sprites(), layer=LAYER_WALL)
        display.highscore.pre_text = 'HIGHSCORE: '  # hand the borrowed labels back to the normal game
        display.tips_header.write(TEXT_TIPS_HEADER)
        display.tips.change_text(TIPS)

    # Beat 1: freeze right away for the welcome - the threat, the wall, the progress counter
    leave = tutorial_act(screen, display, clock, bg, overlay, mb, ub, shooter, score_state, TEXT_TUT_WELCOME,
                         [field_and_wall, progress_rect], allow_continue=True)
    if leave:
        leave_tutorial()
        return

    # ...then let the game actually run for a while before the first shooting lesson
    ub, leave = tutorial_watch(screen, display, clock, bg, overlay, mb, ub, shooter, score_state, None, None,
                               timers=[MAIN_BLOB_MOVE_EVENT, UP_BLOB_MOVE_EVENT],
                               until=lambda: mb.generated_rows >= TUT_RISE_ROWS)
    if leave:
        leave_tutorial()
        return

    # Beat 2: freeze - shoot the highlighted region with the preloaded matching bullet
    region = pyg.sprite.Group(mb.connected_same_color(mb.matrix[0][3]))  # the board's only color-0 region
    region_rects = [cell.rect.copy() for cell in region.sprites()]
    leave = tutorial_act(screen, display, clock, bg, overlay, mb, ub, shooter, score_state, TEXT_TUT_MATCH,
                         region_rects + [mag_rect], accept=['hit_success'],
                         require_front=COLORS[0], require_target=region)
    if leave:
        leave_tutorial()
        return

    # Beat 3: still frozen - the hole just shot reveals the picture and pays points
    leave = tutorial_act(screen, display, clock, bg, overlay, mb, ub, shooter, score_state, TEXT_TUT_REVEAL,
                         region_rects + [score_rect], allow_continue=True)
    if leave:
        leave_tutorial()
        return

    # Beat 4: the game resumes silently; watch the scripted bullets arrive
    ub, leave = tutorial_watch(screen, display, clock, bg, overlay, mb, ub, shooter, score_state, None, None,
                               timers=all_timers, until=lambda: len(shooter.magazine) >= TUT_AMMO_DEMO)
    if leave:
        leave_tutorial()
        return

    # ...then freeze to explain what just happened
    leave = tutorial_act(screen, display, clock, bg, overlay, mb, ub, shooter, score_state, TEXT_TUT_AMMO,
                         [mag_rect], allow_continue=True)
    if leave:
        leave_tutorial()
        return

    # Beat 5: freeze - the front bullet mismatches; swap it away, then shoot the color-1 region
    region = pyg.sprite.Group(mb.connected_same_color(mb.matrix[1][9]))
    region_rects = [cell.rect.copy() for cell in region.sprites()]
    leave = tutorial_act(screen, display, clock, bg, overlay, mb, ub, shooter, score_state, TEXT_TUT_SWAP,
                         region_rects + [mag_rect], accept=['hit_success'], allow_swap=True,
                         require_front=COLORS[1], require_target=region)
    if leave:
        leave_tutorial()
        return

    # Beat 6: watch the magazine fill to the brim, silently...
    ub, leave = tutorial_watch(screen, display, clock, bg, overlay, mb, ub, shooter, score_state, None, None,
                               timers=all_timers, until=lambda: len(shooter.magazine) >= shooter.maxammo)
    if leave:
        leave_tutorial()
        return

    # ...then freeze to explain, before wasting the useless bullet
    leave = tutorial_act(screen, display, clock, bg, overlay, mb, ub, shooter, score_state, TEXT_TUT_FULL,
                         [mag_rect], allow_continue=True)
    if leave:
        leave_tutorial()
        return

    # ...the front color is extinct on the board, so waste it anywhere to make room
    leave = tutorial_act(screen, display, clock, bg, overlay, mb, ub, shooter, score_state, TEXT_TUT_WASTE,
                         [GAME_FIELD, mag_rect], accept=['miss', 'hit_fail'], require_front=COLORS[0])
    if leave:
        leave_tutorial()
        return

    # Beat 7: freeze to prime the player for what is about to happen, then let it happen silently
    leave = tutorial_act(screen, display, clock, bg, overlay, mb, ub, shooter, score_state, TEXT_TUT_UP_RISE,
                         [], allow_continue=True)
    if leave:
        leave_tutorial()
        return

    ub, leave = tutorial_watch(screen, display, clock, bg, overlay, mb, ub, shooter, score_state, None, None,
                               timers=all_timers, until=lambda: covers_any(ub.sprites(), mb.sprites()))
    if leave:
        leave_tutorial()
        return

    # ...then freeze - shooting it kills every covered cell, whatever its color
    ub_rects = [u.rect.copy() for u in ub.sprites()]
    leave = tutorial_act(screen, display, clock, bg, overlay, mb, ub, shooter, score_state, TEXT_TUT_UP_SHOOT,
                         ub_rects + [mag_rect], accept=['hit_success'],
                         allow_swap=True, require_front=COLORS[4], require_target=ub)
    if leave:
        leave_tutorial()
        return

    # Beat 8: freeze to prime the player for the next up-blob, then let it approach silently
    left_block = mb.connected_same_color(mb.matrix[4][2])
    right_block = mb.connected_same_color(mb.matrix[4][9])
    leave = tutorial_act(screen, display, clock, bg, overlay, mb, ub, shooter, score_state, TEXT_TUT_UP_SPAWN,
                         [cell.rect.copy() for cell in left_block + right_block], allow_continue=True)
    if leave:
        leave_tutorial()
        return

    # A new scripted up-blob spawns and hurries toward the two color-2 blocks it will bridge
    ub = UpBlob(-2)
    ub.load_layout([[COLORS[2]] * 8], left=3, top_row=FIELDLENGTH + 2, image=UP_IMG, alpha=UP_BLOB_ALPHA)
    ub.color = COLORS[2]
    ub, leave = tutorial_watch(screen, display, clock, bg, overlay, mb, ub, shooter, score_state, None, None,
                               timers=all_timers, speeds={UP_BLOB_MOVE_EVENT: TUT_UP_FAST_SPEED},
                               until=lambda: touches_any(ub.sprites(), left_block) and
                                             touches_any(ub.sprites(), right_block))
    if leave:
        leave_tutorial()
        return

    # ...then freeze - one shot on the bridge sets off both blocks at once. Recompute the blocks'
    # rects here too, not just the up-blob's - the main blob keeps sinking during the watch above,
    # so a rect snapshot taken before it would already be stale (pointing at empty space) by now
    ub_rects = [u.rect.copy() for u in ub.sprites()]
    block_rects = [cell.rect.copy() for cell in left_block + right_block]
    leave = tutorial_act(screen, display, clock, bg, overlay, mb, ub, shooter, score_state, TEXT_TUT_UP_CONNECT,
                         ub_rects + block_rects + [mag_rect], accept=['hit_success'],
                         allow_swap=True, require_front=COLORS[2], require_target=ub)
    if leave:
        leave_tutorial()
        return

    # Beat 9: hand full control back and let the player finish the board themselves
    # ub is empty (its cells died in the last shot) but still carries the bridging demo's
    # left/width, which would give a future UpBlob.reset() an invalid, partly off-field spawn
    # range - replace it with a properly-defaulted up-blob, exactly as a real game constructs one
    ub = UpBlob(-2, UP_LEFTSTICK, UP_BOTTOMSTICK, left=1, top=FIELDLENGTH + 2, max_rows=100, width=MAXCOL)
    leave = tutorial_act(screen, display, clock, bg, overlay, mb, ub, shooter, score_state, TEXT_TUT_FINISH,
                         [], allow_continue=True)
    if leave:
        leave_tutorial()
        return

    result = tutorial_finish(screen, display, clock, bg, mb, ub, shooter, score_state)
    if result == 'leave':
        leave_tutorial()
        return

    if SOUND_EFFECTS_ON:
        SOUND[result].play()  # result is 'win' or 'game_over', both valid SOUND keys
    if result == 'win':
        bg.act.blit(bg.image, GAME_FIELD, GAME_FIELD)  # fade() doesn't persist into bg.act - do it here,
        # so the next frame's redraw shows the full picture instead of stomping it with the pre-fade state
    fade(clock, bg, result, FADE_STEPS)

    # on a win, keep the veil off the just-unveiled picture - same as the regular game's end
    # screen, whose panel sits only over the info side and never dims the picture
    done_highlights = [whole_field] if result == 'win' else []
    tutorial_act(screen, display, clock, bg, overlay, mb, ub, shooter, score_state,
                TEXT_TUT_DONE if result == 'win' else TEXT_TUT_DONE_LOSE, done_highlights,
                allow_continue=True)

    leave_tutorial()


def play(screen, display, clock, highscore, settings):
    """Runs the main loop with game"""

    # Game initialization #

    # Events
    pyg.time.set_timer(MAIN_BLOB_MOVE_EVENT, MAIN_BLOB_SPEED)
    pyg.time.set_timer(UP_BLOB_MOVE_EVENT, UP_BLOB_SPEED)
    pyg.time.set_timer(ADD_AMMO_EVENT, ADD_AMMO_SPEED)
    pyg.time.set_timer(MAGAZINE_FLASH_EVENT, MAGAZINE_FLASH_SPEED)

    # Game objects
    mb = Blob(1, LEFTSTICK, BOTTOMSTICK, left=1, top=0, max_rows=MAXROW)
    ub = UpBlob(-2, UP_LEFTSTICK, UP_BOTTOMSTICK, left=1, top=FIELDLENGTH+2, max_rows=100, width=MAXCOL)
    deadpool = pyg.sprite.Group()
    cursor = Point()
    shooter = Gun(maxammo=6, restrict_final_colors=settings['restrict_final_colors'])

    # Sound
    if SOUND_BGM_ON:
        SOUND['bg_music'].play(loops=-1)

    # Display
    screen.fill(BLACK)  # wipe whatever the settings menu / end screen painted outside sprite/Label rects
    bg = Background(screen, MAXCOL + 2, FIELDLENGTH + 2, theme=settings['theme'], pic=settings['image'], size=CS)
    score = 0
    display.magazine.show_ammo(shooter.magazine, shooter.maxammo)
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
                    sc, status, win = shooter.shoot(cursor, mb, ub, deadpool)  # test hit
                    display.magazine.show_ammo(shooter.magazine, shooter.maxammo)
                    if sc > 0:  # got some points
                        score += sc
                        if score < highscore:
                            display.score.write(score, color=WHITE)
                        else:
                            display.score.write(score, color=GREEN)
                    if SOUND_EFFECTS_ON and SOUND[status]:  # sound ON and effect is defined
                        SOUND[status].play()
                    if len(deadpool) > 0:  # cells staged - explode outward from the shot
                        explode_effect(screen, clock, mb, deadpool, bg)
                    if win:  # won
                        pyg.event.post(pyg.event.Event(END_EVENT, {'status': 'win'}))
                if display.magazine.rect.collidepoint(pyg.mouse.get_pos()):  # reload by clicking magazine
                    if shooter.change_ammo() == 'reload':
                        display.magazine.show_ammo(shooter.magazine, shooter.maxammo)
            if event.button == 3:  # reload by rightclick
                if shooter.change_ammo() == 'reload':
                    display.magazine.show_ammo(shooter.magazine, shooter.maxammo)

        # Text events
        elif event.type == TIPS_EVENT:
            display.tips.change_text(TIPS)
        elif event.type == MAGAZINE_FLASH_EVENT:
            display.magazine.blink_full()

        # Timed events
        elif event.type == MAIN_BLOB_MOVE_EVENT:
            if not mb.move():
                pyg.event.post(pyg.event.Event(END_EVENT, {'status': 'game_over'}))
            display.progress.write(str(mb.generated_rows) + ' / ' + str(mb.max_rows))
        elif event.type == UP_BLOB_MOVE_EVENT:
            ub = ub.move()
        elif event.type == ADD_AMMO_EVENT:
            if shooter.add_ammo(mb, ub) == 'added':
                display.magazine.show_ammo(shooter.magazine, shooter.maxammo)

        # End of game
        elif event.type == END_EVENT:
            SOUND['bg_music'].stop()
            if SOUND_EFFECTS_ON:
                SOUND[event.status].play()
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
    pyg.time.set_timer(MAGAZINE_FLASH_EVENT, 0)
    ALL_SPRITES.empty()
    ALL_SPRITES.add(wall.sprites(), layer=LAYER_WALL)

    choice = run_end_screen(screen, clock)
    return score, choice


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

pyg.time.set_timer(TIPS_EVENT, TIPS_TIME)
pyg.time.set_timer(BLINK_EVENT, BLINK_TIME)
highscore = 0
settings = {'theme': 'random', 'image': 'random', 'color_scheme': 'standard', 'restrict_final_colors': True}

# settings menu <-> play loop #
while True:
    settings = run_settings_menu(screen, clock, settings)
    apply_color_scheme(settings['color_scheme'])
    if settings['action'] == 'tutorial':
        run_tutorial(screen, display, clock, settings)
        continue
    replaying = True
    while replaying:
        score, choice = play(screen, display, clock, highscore, settings)
        highscore = max(highscore, score)
        replaying = (choice == 'replay')

