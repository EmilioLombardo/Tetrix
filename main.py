import sys
import random
from numpy import array
from math import ceil

try:
    import pygame
    pygame.mixer.pre_init(buffer=32)
    pygame.init()

except:
    print("\n! ERROR !\nFant ikke pygame-modulen.\n"
        + "Hvordan installere pygame:\n\n"
        + "WINDOWS: pip install pygame\n"
        + "    MAC: pip3 install pygame\n\n"
        + "(Bruker du Linux antar jeg du klarer å finne ut av dette selv)")

    sys.exit()

import constants as c
from tetrimino import *

# ------ Class for level icons on level selection screen ------ #
class NumIcon(pygame.sprite.Sprite):
    bg_col = c.BLUE_GREY
    bg_col_selected = c.WHITE
    w = int(c.cell_size * 2)
    font = pygame.font.Font("fonts/Montserrat-Bold.ttf", int(40 * c.scale))

    def __init__(self, num, x, y, selected):
        super().__init__()
        self.num = str(num)
        self.selected = selected

        self.rect = (x, y, self.w, self.w)
        self.image = pygame.Surface((self.w, self.w - 1))

        if selected:
            self.image.fill(self.bg_col_selected)
        else:
            self.image.fill(self.bg_col)

        self.text = self.font.render(self.num, True, c.WHITE)

        # Centre text within self.rect
        text_w = self.text.get_width()
        text_h = self.text.get_height()
        self.text_pos = ((self.w - text_w)/2, (self.w - text_h)/2)

    def update(self):

        if self.selected:
            # Make bg white and text blue
            self.image.fill(c.WHITE)
            self.text = self.font.render(
                    self.num, True, self.bg_col)
            self.image.blit(self.text, self.text_pos)

        else:
            # Make bg blue and text white
            self.image.fill(c.BLUE_GREY)
            self.text = self.font.render(
                    self.num, True, c.WHITE)
            self.image.blit(self.text, self.text_pos)

# ------ Class for displaying text ------ #
class Text:

    def get_pos(cls, column, row, w):
        """
        Returns pixel coords for positioning text in given column and row.
        """
        margin = 40 * c.scale
        left_column_offset = 180 * c.scale

        return {
            "left" : (c.field_pos[0] - left_column_offset - 1,
                      c.field_pos[1] + margin + row * margin),

            "right" : (c.field_pos[0] + c.field_width + margin,
                       c.field_pos[1] + margin + row * margin),

            "centre" : (c.field_pos[0] + (c.field_width - w)//2,
                        c.field_pos[1] + margin + row * margin)

            }[column]

    def __init__(self, text, font, colour, column, row):

        self.text = text
        self.font = font
        self.colour = colour

        self.column = column # "left", "right" or "centre"
        self.row = row

        self.render = self.font.render(self.text, True, self.colour)

    def display(self, dest_surf, bg, new_text=None):
        """Method to blit text to a surface. Returns dirty rect."""

        w = self.render.get_width()

        if new_text is not None:
            new_render = self.font.render(new_text, True, self.colour)

            # Make sure text rect is wide enough to overwrite preexisting text
            w = max(w, new_render.get_width())

            self.render = new_render
            self.text = new_text

        pos = self.get_pos(self.column, self.row, w)

        h = self.render.get_height()

        text_rect = (*pos, w, h)

        # Draw bg over text (bg can be a pygame surface or a solid colour)
        if type(bg) is pygame.Surface:
            bg_surf = bg
            dest_surf.set_clip(text_rect)
            dest_surf.blit(bg_surf, (0, 0))
            dest_surf.set_clip()

        elif type(bg) in [tuple, list] and len(bg) == 3:
            bg_colour = bg
            pygame.draw.rect(dest_surf, bg_colour, text_rect)

        else:
            raise Exception("bg argument not valid: "
                    + "bg must be either a pygame surface or an RGB colour")

        # Draw text
        dest_surf.blit(self.render, pos)

        return text_rect

    def clear(self, dest_surf, bg_surf):
        """Method to clear text from surface. Returns dirty rect."""

        w = self.render.get_width()
        h = self.render.get_height()
        pos = self.get_pos(self.column, self.row, w)

        rect = (*pos, w, h)

        # Draw bg over text
        dest_surf.set_clip(rect)
        dest_surf.blit(bg_surf, rect)
        dest_surf.set_clip()

        return rect


# --- Initialise screen --- #
if c.fullscreen:
    flags = pygame.DOUBLEBUF | pygame.FULLSCREEN
else:
    flags = pygame.DOUBLEBUF

screen = pygame.display.set_mode((c.width, c.height), flags)
pygame.display.set_caption("Tetrix")

# --- Make background --- #
def draw_field_border(surface, colour, w=1):
    dirty_rects = []

    x0 = c.field_pos[0] - w
    y0 = c.field_pos[1]
    x1 = c.field_pos[0] + c.field_width
    y1 = c.field_pos[1] + c.field_height

    dirty_rects.append(
            pygame.draw.line(surface, colour, (x0, y0), (x0, y1), w))
    dirty_rects.append(
            pygame.draw.line(surface, colour, (x0, y1), (x1, y1), w))
    dirty_rects.append(
            pygame.draw.line(surface, colour, (x1, y0), (x1, y1), w))

    return dirty_rects

bg = pygame.Surface(screen.get_size())
bg = bg.convert()
bg.fill(c.BLUE_GREY)
draw_field_border(bg, c.GREY)

# Draw grid
line_w = 1
for col in range(c.COLS):
    x = c.field_pos[0] + col * c.cell_size
    y1, y2 = c.field_pos[1], c.field_pos[1] + c.field_height - 1
    pygame.draw.line(bg, c.LIGHT_BLUE_GREY, (x, y1), (x, y2), line_w)

for row in range(c.ROWS):
    x1, x2 = c.field_pos[0], c.field_pos[0] + c.field_width - 1
    y = c.field_pos[1] + row * c.cell_size
    pygame.draw.line(bg, c.LIGHT_BLUE_GREY, (x1, y), (x2, y), line_w)

# --- Global timing stuff --- #
FPS = 60
clock = pygame.time.Clock()

# --- Fonts --- #
title_font = pygame.font.Font(
        "fonts/Montserrat-Black.ttf", int(60 * c.scale))
info_font = pygame.font.Font(
        "fonts/Montserrat-BoldItalic.ttf", int(30 * c.scale))
number_font = pygame.font.Font(
        "fonts/Montserrat-Medium.ttf", int(30 * c.scale))

def randomiser(prev):
    """
    Randomiser with bias against same two pieces in a row
    (This is the same randomiser used in NES Tetris)
    """
    roll = random.randint(0, len(c.tetriminos)) # 0-7

    if roll == len(c.tetriminos) or roll == prev:
        # If roll is 7 or same as previous, reroll 0-6
        roll = random.randint(0, len(c.tetriminos) - 1)

    return roll # A value 0-6

def point_in_rect(point, rect):
    """Check if point is within rect."""

    x, y = point
    x1, y1, w, h = rect
    x2, y2 = x1 + w, y1 + h

    if (x1 < x < x2) and (y1 < y < y2):
        return True

    return False

# ------ Title screen w/ level select ------ #
def menu(selected_lvl):

    pygame.key.set_repeat(300, 100)
    pygame.mouse.set_visible(True)

    # --- Level select grid --- #

    level_icons = []
    lvl_range = 20 # One can choose to start on levels 0-19
    lvl_grid_cols = 10
    lvl_grid_rows = ceil(lvl_range / lvl_grid_cols)
    lvl_grid_rect = (
            (c.width - NumIcon.w * lvl_grid_cols)/2,
            c.field_pos[1] + (c.field_height - lvl_grid_rows*NumIcon.w)/2,
            lvl_grid_cols * NumIcon.w,
            lvl_grid_rows * NumIcon.w)

    # Make sure selected level is within the level range
    if selected_lvl >= lvl_range or selected_lvl < 0:
        selected_lvl = 0

    # Create the level icons and position them
    for num in range(lvl_range):
        x = lvl_grid_rect[0]
        x += NumIcon.w * (num % lvl_grid_cols)
        y = lvl_grid_rect[1]
        y += NumIcon.w * (num // lvl_grid_cols)

        selected = True if num == selected_lvl else False

        level_icons.append(NumIcon(num, x, y, selected))

    lvl_select_group = pygame.sprite.Group()
    lvl_select_group.add(level_icons)

    # --- Title text --- #
    title_text = title_font.render("TETRIX", True, c.WHITE)
    title_pos = ((c.width - title_text.get_width())//2,
                 c.field_pos[1] + c.cell_size*3 - title_text.get_height()//2)

    # --- Blit stuff to the screen --- #

    screen.blit(bg, (0, 0))
    screen.blit(title_text, title_pos)

    # Draw line above and below level grid
    x0 = c.field_pos[0]
    y0 = lvl_grid_rect[1] - 1
    x1 = c.field_pos[0] + c.field_width - 1
    y1 = lvl_grid_rect[1] + lvl_grid_rect[3]

    pygame.draw.line(screen, c.LIGHT_BLUE_GREY, (x0, y0), (x1, y0), 1)
    pygame.draw.line(screen, c.LIGHT_BLUE_GREY, (x0, y1), (x1, y1), 1)

    pygame.display.flip()

    def update_display():
        pygame.draw.rect(screen, c.BLUE_GREY, lvl_grid_rect)
        lvl_select_group.update()
        lvl_select_group.draw(screen)
        pygame.display.flip()

    # --- Menu loop --- #

    on_menu_screen = True
    while on_menu_screen:

        # Reset which icon is selected every frame
        for icn in level_icons:
            icn.selected = False

        mouse_pos = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()
        events = pygame.event.get()

        for event in events:
            # Allow user to quit
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type in [pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN]:
                for icn in level_icons:
                    if not point_in_rect(mouse_pos, icn.rect):
                        continue
                    # If mouse is on an icon, make that icon selected
                    if selected_lvl != int(icn.num):
                        c.shift_sound.play()
                        selected_lvl = int(icn.num)

            # If mouse button 1 is pressed on an icon
            if (event.type == pygame.MOUSEBUTTONUP and event.button == 1 and
                point_in_rect(mouse_pos, level_icons[selected_lvl].rect)):
                # Start game
                on_menu_screen = False
                c.rot_sound.play()

            if event.type != pygame.KEYDOWN:
                continue

            if event.key in c.CONFIRM_KEYS:
                # Start game
                on_menu_screen = False
                c.rot_sound.play()

            # Quit with ESCAPE
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            # --- Level selection control --- #

            if event.key in c.RIGHT_KEYS:
                c.shift_sound.play()
                selected_lvl = (selected_lvl + 1) % lvl_range

            if event.key in c.LEFT_KEYS:
                c.shift_sound.play()
                selected_lvl = (selected_lvl - 1) % lvl_range

            if event.key in c.UP_KEYS:
                c.shift_sound.play()
                selected_lvl = (selected_lvl - lvl_grid_cols) % lvl_range

            if event.key in c.DOWN_KEYS:
                c.shift_sound.play()
                selected_lvl = (selected_lvl + lvl_grid_cols) % lvl_range

        level_icons[selected_lvl].selected = True

        update_display()

        if not on_menu_screen:
            for _ in range(10): clock.tick(FPS) # Small delay
            c.level_up_sound.play()

            key_mods = pygame.key.get_mods()

            # Hold shift to add 10 to level selection :o
            if key_mods & pygame.KMOD_SHIFT:
                selected_lvl = min(selected_lvl + 10, c.max_level)
            # Hold CTRL to start at lvl 30 :o
            elif key_mods & pygame.KMOD_CTRL:
                selected_lvl = c.max_level

            start_game(selected_lvl)

        clock.tick(FPS)

# ------ The actual gameplay stuff ------ #
def start_game(start_level):

    pygame.key.set_repeat() # Disable key repeat, that will be handled manually

    # --- Game variables --- #

    max_spawn_freeze = 31 # Max freeze frames after piece has spawned.
                          # Freeze frames are cancelled by any keypress

    spawn_freeze_timer = max_spawn_freeze
    frame_counter = 1 # Counter to control tetrimino falling
    text_flash_counter = 0 # Counter to control timing for flashing text
    DAS_counter = 0 # For control of horisontal auto-shift delays

    level = start_level # Controls falling speed and point bonuses
    lines = 0
    points = 0

    soft_drop = False # If True, piece falls and locks faster than normal

    # Soft drop falling speed in frames per cell ("fpc")
    if c.frames_per_cell[level] > 3:
        soft_drop_fpc = 2
    else:
        soft_drop_fpc = 1

    # --- Text initialisation --- #

    lines_text = Text("LINES", info_font, c.WHITE, "left", 0)
    lines_num_text = Text(str(lines), number_font, c.WHITE, "left", 1)

    level_text = Text("LEVEL", info_font, c.WHITE, "left", 4)
    level_num_text = Text(str(level), number_font, c.WHITE, "left", 5)

    paused_text = Text("PAUSED", info_font, c.WHITE, "centre", 4)
    game_over_text = Text("GAME OVER", info_font, c.RED, "centre", 4)

    score_text = Text("SCORE", info_font, c.WHITE, "right", 0)
    points_num_text = Text(str(points), number_font, c.WHITE, "right", 1)

    next_text = Text("NEXT", info_font, c.WHITE, "right", 4)

    # --- Tetrimino, next piece and dead mino sprite group --- #

    tetrimino = Tetrimino(random.randint(0, 6), c.spawn_pos)
    next_piece = Tetrimino(randomiser(tetrimino.type_ID), array((12.5, 10)))

    dead_group = pygame.sprite.LayeredDirty() # Sprite group for dead minos
    dead_group.set_clip(c.field_rect)

    def complete_rows(dead_minos):
        """Returns a list of which rows of the playfield are filled in."""

        complete_rows = []

        for row_n in range(c.ROWS):
            dead_minos_in_row = [
                    d for d in dead_minos
                    if d.grid_y == row_n
                    ]

            if len(dead_minos_in_row) >= c.COLS:
                complete_rows.append(row_n)

        return complete_rows

    def update_display(dirty_rects):
        """
        Draw current tetrimino and next piece, and update any dirty rects.
        """

        dirty_rects += tetrimino.draw(screen)
        dirty_rects += next_piece.draw(screen)

        pygame.display.update(dirty_rects)

    # --- Draw all game screen stuff --- #

    screen.blit(bg, (0, 0))

    lines_text.display(screen, bg)
    lines_num_text.display(screen, bg)
    level_text.display(screen, bg)
    level_num_text.display(screen, bg)
    score_text.display(screen, bg)
    points_num_text.display(screen, bg)
    next_text.display(screen, bg)

    pygame.display.flip()

    # --- Game loop --- #

    dirty_rects = []
    paused = False
    in_game = True
    game_over = 0
    while in_game:

        events = pygame.event.get()
        for event in events:
            # Allow user to quit
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ESC -> Exit to menu
            if (event.type == pygame.KEYDOWN and
                event.key == pygame.K_ESCAPE):
                in_game = False
                break

            # If game is over, press CONFIRM or mouse click to quit to menu
            if game_over:
                if (event.type == pygame.KEYDOWN and
                    event.key in c.CONFIRM_KEYS) or (
                    event.type == pygame.MOUSEBUTTONUP and
                    event.button == 1):

                    c.rot_sound.play()
                    in_game = False
                    break

                continue # Don't check any gameplay-related inputs

            # Hide mouse while GAMING B^)
            if event.type == pygame.KEYDOWN:
                pygame.mouse.set_visible(False)
            elif event.type == pygame.MOUSEMOTION:
                pygame.mouse.set_visible(True)

            # Pausing
            if (event.type == pygame.KEYDOWN and
                event.key in c.PAUSE_KEYS):
                # Toggle paused = True/False
                paused = (False == paused)

                if not paused:
                    # Redraw dead minos and grid

                    screen.set_clip(c.field_rect)

                    screen.blit(bg, (0, 0)) # Grid
                    dead_group.repaint_rect(screen.get_rect())
                    dead_group.draw(screen)

                    screen.set_clip()
                    pygame.display.update(c.field_rect)

                else:
                    next_piece.clear(screen, bg)
                    # Draw over the entire field with bg colour
                    pygame.draw.rect(screen, c.BLUE_GREY, c.field_rect)
                    paused_text.display(screen, c.BLUE_GREY)

                    pygame.display.update(c.field_rect)

            # --- Register DOWN release for soft drop control --- #
            if (event.type == pygame.KEYUP and
                event.key in c.DOWN_KEYS):
                soft_drop = False

            if paused:
                # Don't check for shifting and rotating inputs while paused
                continue

            if not (event.type == pygame.KEYDOWN and
                    tetrimino.lock_timer > 0):
                # If tetrimino has locked,
                # don't check inputs related to tetrimino control
                continue

            # --- Register DOWN press for soft drop control --- #
            if event.key in c.DOWN_KEYS:
                soft_drop = True
                spawn_freeze_timer = 0

            # --- Shifting on LEFT/RIGHT keypress --- #

            if event.key in c.LEFT_KEYS:
                c.shift_sound.play()
                tetrimino.clear(screen, bg)
                tetrimino.shift("left", dead_group)
                DAS_counter = 0

                spawn_freeze_timer = min(c.frames_per_cell[level],
                                         spawn_freeze_timer)

            if event.key in c.RIGHT_KEYS:
                c.shift_sound.play()
                tetrimino.clear(screen, bg)
                tetrimino.shift("right", dead_group)
                DAS_counter = 0

                spawn_freeze_timer = min(c.frames_per_cell[level],
                                         spawn_freeze_timer)

            # --- Rotation on keypress --- #

            if event.key in c.CW_KEYS:
                tetrimino.clear(screen, bg)
                tetrimino.rotate("cw", dead_group)
                c.rot_sound.play()

                spawn_freeze_timer = min(c.frames_per_cell[level],
                                         spawn_freeze_timer)

            if event.key in c.CCW_KEYS:
                tetrimino.clear(screen, bg)
                tetrimino.rotate("ccw", dead_group)
                c.rot_sound.play()

                spawn_freeze_timer = min(c.frames_per_cell[level],
                                         spawn_freeze_timer)

        if not in_game:
            # Quit to menu
            menu(start_level)
            break

        # --- Game over screen w/ animation --- #
        if game_over:
            if game_over == 2:
                # If animation has already played, don't play it again.
                # Also, don't proceed to gameplay section of game loop
                continue

            pygame.mouse.set_visible(True)
            pygame.event.clear()

            c.game_over_sound.play()

            # Small delay before animation
            for _ in range(30): clock.tick(FPS)

            # Animation (screen wipe, reveal GAME OVER text)
            step = c.field_rect.height / 75
            h = int(step)
            y = c.field_rect[1] + c.field_rect.height - h
            while y > c.field_rect[1]:
                pygame.event.pump()
                animation_dirty_rects = []

                animation_dirty_rects.append(
                        pygame.draw.rect(
                                screen,
                                c.BLUE_GREY,
                                (c.field_pos[0], y, c.field_width, h)))

                game_over_text.display(screen, c.BLUE_GREY)

                pygame.display.update(animation_dirty_rects)
                y -= step
                h += step
                clock.tick(FPS)

            for _ in range(30): clock.tick(FPS) # Small delay
            pygame.event.clear()

            game_over = 2 # Animation has played
            continue # Don't proceed to gameplay section of game loop

        # --- Make level number flash when you level up --- #
        if text_flash_counter >= 0:
            if text_flash_counter % 40 == 0: # Show text
                dirty_rects.append(
                        level_num_text.display(screen, bg))

            elif text_flash_counter % 40 == 20: # Hide text
                dirty_rects.append(
                        level_num_text.clear(screen, bg))

            text_flash_counter -= 1

        if paused:
            clock.tick(FPS)
            pygame.display.update(dirty_rects)
            dirty_rects = []
            continue # Don't proceed to gameplay section of game loop

        # --- Manage auto-shift --- #

        keys_held = pygame.key.get_pressed()

        dir_held = None

        # Check if LEFT or RIGHT is held
        left_held = bool(
                [k for k in c.LEFT_KEYS if keys_held[k]])
        right_held = bool(
                [k for k in c.RIGHT_KEYS if keys_held[k]])

        if not (left_held == right_held):
            # If only one direction is held
            dir_held = "left" if left_held else "right"

        if dir_held and tetrimino.lock_timer > 0:
            DAS_counter += 1
            spawn_freeze_timer = 0
            if DAS_counter == c.DAS:
                tetrimino.clear(screen, bg)
                shifted = tetrimino.shift(dir_held, dead_group)
                DAS_counter = c.DAS - c.ARR
                # If tetrimino has actually moved, play shift sonud
                if shifted: c.shift_sound.play()

        # --- Falling and landing --- #

        # If soft dropping, make lock delay 2 frames
        if soft_drop and tetrimino.lock_timer > 2:
            tetrimino.lock_timer = 2

        # If tetrimino has landed, start locking timer
        if tetrimino.landed(dead_group):
            tetrimino.lock_timer -= 1

        # Make tetrimino fall
        if not (tetrimino.lock_timer > 0 and spawn_freeze_timer <= 0):
            # Don't make tetrimino fall if it has locked or is in spawn freeze
            pass

        elif not soft_drop and frame_counter % c.frames_per_cell[level] == 0:
            tetrimino.clear(screen, bg)
            tetrimino.fall(dead_group, level)

        elif soft_drop and frame_counter % soft_drop_fpc == 0:
            tetrimino.clear(screen, bg)
            tetrimino.fall(dead_group, level)

            # Pushdown points (1 point for each frame during soft drop)
            points += 1
            # Update points text
            dirty_rects.append(
                    points_num_text.display(screen, bg, new_text=str(points)))

        # --- Drawing stuff and updating screen --- #

        # Make tetrimino flash when it locks
        if tetrimino.lock_timer == 0:
            c.lock_sound.play()
            for spr in tetrimino:
                spr.image.fill(c.WHITE)

        elif tetrimino.lock_timer <= -3:
            for spr in tetrimino:
                spr.image.fill(spr.colour)

        # --- Update display --- #
        update_display(dirty_rects)
        dirty_rects = []

        # --- After tetrimino has locked and flashed --- #
        if tetrimino.lock_timer <= -4:
            # If the tetrimino locks above the playing field; Game over :o
            if max(tetrimino.minos[:,1]) < 0:
                next_piece.clear(screen, bg)
                game_over = 1
                continue

            dead_group.add(tetrimino)
            soft_drop = False

            # --- Line clearing w/ animation --- #

            rows_to_clear = complete_rows(dead_group)

            if rows_to_clear:

                # Play sound
                if len(rows_to_clear) == 4:
                    c.tetris_sound.play()
                else:
                    c.clear_sound.play()

                # Find which minos should move down after line clearing

                dead_minos_above = []

                for row_n in rows_to_clear:
                    dead_minos_above += [
                            d for d in dead_group
                            if (d.grid_y < row_n and
                                d.grid_y not in rows_to_clear and
                                d not in dead_minos_above)
                            ]

                # Animation

                x = c.field_pos[0] + c.field_width // 2 - 1
                w = 2
                step = c.field_width / 42
                i = 0
                while x >= c.field_pos[0]: # Animation loop
                    pygame.event.pump()
                    animation_dirty_rects = []

                    for row_n in rows_to_clear:
                        h = Mino.get_size(0, row_n)[1]
                        y = int(c.cell_size * row_n + c.field_pos[1])
                        rectangle = pygame.Rect(x, y, w, h)

                        # Draw bg over part of the filled row
                        screen.set_clip(rectangle)
                        screen.blit(bg, (0, 0))

                        animation_dirty_rects.append(rectangle)

                    screen.set_clip()

                    # Make field border flash if you get a tetris
                    if len(rows_to_clear) != 4:
                        pass

                    elif i % 4 == 0:
                        animation_dirty_rects += draw_field_border(
                                screen, c.CYAN, w=2)

                    elif i % 4 == 2:
                        animation_dirty_rects += draw_field_border(
                                screen, c.BLUE_GREY, w=2)
                        draw_field_border(screen, c.GREY)

                    pygame.display.update(animation_dirty_rects)

                    w += 2 * step
                    x -= step
                    i += 1

                    clock.tick(FPS)

                # Reset field border
                dirty_rects += draw_field_border(screen, c.BLUE_GREY, w=2)
                draw_field_border(screen, c.GREY)

                # Erase all dead minos from the screen before moving any
                dead_group.clear(screen, bg)

                # Remove dead minos in cleared rows from dead_group
                dead_minos_to_remove = [
                        d for d in dead_group
                        if d.grid_y in rows_to_clear
                        ]

                dead_group.remove(dead_minos_to_remove)

                # Update display to reflect erasing of all dead minos
                pygame.display.update(dead_group.draw(screen))

                # Move dead minos above the cleared rows down
                for d in dead_minos_above:
                    displacement = 0
                    for row_n in rows_to_clear:
                        if d.grid_y < row_n:
                            # If mino is above a cleared row
                            displacement += 1

                    d.grid_y += displacement
                    d.update()

                # Finally, redraw all dead minos (some in their new positions)
                pygame.display.update(dead_group.draw(screen))

                # Update points, lines and level variables
                lines += len(rows_to_clear)
                points += c.clear_points[len(rows_to_clear)] * (level + 1)
                if lines // 10 > level < c.max_level:
                    level += 1
                    c.level_up_sound.play()
                    if c.frames_per_cell[level] <= 3:
                        soft_drop_fpc = 1

                    dirty_rects.append(
                            level_num_text.display(
                                    screen, bg, new_text=str(level)))

                    # Start flashing of level text
                    level_num_text.clear(screen, bg)
                    text_flash_counter = 60

                # Update points and lines text
                dirty_rects.append(
                        points_num_text.display(
                                screen, bg, new_text=str(points)))

                dirty_rects.append(
                        lines_num_text.display(
                                screen, bg, new_text=str(lines)))

            # --- Spawn new tetrimino and next piece --- #

            dirty_rects += next_piece.draw(screen)
            next_piece.clear(screen, bg)

            tetrimino = Tetrimino(next_piece.type_ID, c.spawn_pos)
            next_piece = Tetrimino(randomiser(tetrimino.type_ID),
                                   array((12.5, 10)))

            spawn_freeze_timer = max_spawn_freeze

            # If the new piece spawns overlapping any dead minos; Game over :o
            if tetrimino.colliding(dead_group):
                pygame.display.update(tetrimino.draw(screen))
                game_over = 1

        # --- Time stuff --- #

        if spawn_freeze_timer > 0:
            spawn_freeze_timer -= 1
            frame_counter = 0
        else:
            frame_counter += 1

        clock.tick(FPS)

        # Performance monitoring
        actual_fps = round(clock.get_fps(), 2)
        perf_info = ":/" if int(actual_fps) > FPS else "  "
        sys.stdout.write(f"FPS: {actual_fps} {perf_info}   \r")


menu(0)
