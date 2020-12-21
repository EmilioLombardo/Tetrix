import sys
import pygame
import random
from numpy import array

import constants as c


# ------ Class for level icons on level selection screen ------ #
class NumIcon(pygame.sprite.Sprite):
    w = 60
    level_font = pygame.font.Font("fonts/Montserrat-Bold.ttf", 40)

    def __init__(self, num, x, y, selected):
        super().__init__()
        self.num = str(num)
        self.selected = selected

        self.image = pygame.Surface((self.w, self.w))
        self.image.fill(c.CYAN)
        self.rect = (x, y, self.w, self.w)

        self.text = self.level_font.render(self.num, True, c.WHITE)
        text_w = self.text.get_width()
        text_h = self.text.get_height()
        self.text_rect = ((self.w - text_w)//2, (self.w - text_h)//2)

    def update(self):

        if self.selected:
            self.image.fill(c.WHITE)
            self.text = self.level_font.render(
                    self.num, True, c.BLUE_GRAY)
            self.image.blit(self.text, self.text_rect)
        else:
            self.image.fill(c.BLUE_GRAY)
            self.text = self.level_font.render(
                    self.num, True, c.WHITE)
            self.image.blit(self.text, self.text_rect)

# ------ Class for individual minos (blocks) ------ #
class Mino(pygame.sprite.DirtySprite):
    w = c.cell_size

    def grid_to_pixel(cls, grid_x, grid_y):
        pixel_x = c.cell_size * grid_x + c.field_pos[0]
        pixel_y = c.cell_size * grid_y + c.field_pos[1]
        return pixel_x, pixel_y

    def __init__(self, colour, x, y):
        super().__init__()
        self.grid_x = x
        self.grid_y = y
        self.pixel_x, self.pixel_y = self.grid_to_pixel(self.grid_x,
                                                        self.grid_y)

        self.colour = colour

        self.image = pygame.Surface((self.w, self.w))
        self.image.fill(self.colour)
        self.rect = pygame.Rect(self.pixel_x, self.pixel_y, self.w, self.w)

    def update(self):
        prev = self.image, self.rect

        self.image.fill(self.colour)

        self.pixel_x, self.pixel_y = self.grid_to_pixel(self.grid_x,
                                                        self.grid_y)
        self.rect = pygame.Rect(self.pixel_x, self.pixel_y, self.w, self.w)

        curr = self.image, self.rect

        if prev == curr:
            self.dirty = 0
            return

        self.dirty = 1

# ------ Class for tetrimino logic ------ #
class Tetrimino(pygame.sprite.RenderUpdates):
    def __init__(self, type_ID, centre_pos):
        super().__init__()
        self.type_ID = type_ID
        self.centre_pos = centre_pos.copy()

        self.lock_timer = 32

        if type_ID == 5:
            self.offsets = c.offsets_O.copy()
        elif type_ID == 6:
            self.offsets = c.offsets_I.copy()
        else:
            self.offsets = c.offsets_TJZSL.copy()

        self.rot_index = 0 # Rotation index (0-3 for the four rotations)

        self.minos = [] # List with grid coordinate pairs for each mino

        for mino_XY in c.tetriminos[self.type_ID]:
            self.minos.append(mino_XY)

        self.minos = array(self.minos)
        self.minos = self.minos + self.centre_pos
        self.minos += self.offsets[self.rot_index][0]

        # --- Sprite/group stuff --- #

        self.colour = c.colours[self.type_ID]

        # Add sprites to self
        for mino_XY in self.minos:
            self.add(Mino(self.colour, *mino_XY))

        self.sprite_list = self.sprites()

        self.update_sprites()

    def update_sprites(self):

        for i in range(len(self.minos)):
            spr = self.sprite_list[i]
            spr.grid_x, spr.grid_y = self.minos[i]

        # Call update method of sprites
        self.update()

    def rotate(self, dir, dead_minos):
        prev_rot = self.rot_index
        prev_minos = self.minos.copy()

        # --- Pure rotation --- #

        # Translate minos to origin
        self.minos -= self.centre_pos

        # Rotate minos about origin
        if dir == "cw": # Clockwise
            self.minos = array([(-m[1], m[0]) for m in self.minos])
            self.rot_index = (self.rot_index + 1) % 4

        elif dir == "ccw": # Counterclockwise
            self.minos = array([(m[1], -m[0]) for m in self.minos])
            self.rot_index = (self.rot_index - 1) % 4

        # Translate minos back
        self.minos += self.centre_pos

        # --- Wall kicks  --- #

        kick_tests = self.offsets[prev_rot] - self.offsets[self.rot_index]

        for kick in kick_tests:
            self.minos += kick
            self.centre_pos += kick
            if not self.colliding(dead_minos):
                # Wall kick was successful :)
                self.update_sprites()
                return

            # Kick failed. Undo failed kick before testing next one
            self.minos -= kick
            self.centre_pos -= kick

        # No wall kick was succesful. Reset to previous state
        self.minos = prev_minos
        self.rot_index = prev_rot

    def shift(self, dir, dead_minos):
        prev_minos = self.minos.copy()
        prev_centre = self.centre_pos.copy()

        if dir == "left":
            self.centre_pos[0] -= 1
            self.minos[:,0] -= 1

        elif dir == "right":
            self.centre_pos[0] += 1
            self.minos[:,0] += 1

        if self.colliding(dead_minos):
            self.minos = prev_minos
            self.centre_pos = prev_centre
            self.update_sprites()
            return

        self.update_sprites()

    def fall(self, dead_minos, level):

        if not self.landed(dead_minos):
            self.minos[:,1] += 1
            self.centre_pos[1] += 1
            self.lock_timer = c.lock_delay[level]
            self.update_sprites()

    def colliding(self, dead_minos):
        for m in self.minos:
            # Collision with floor
            if m[1] >= c.ROWS:
                return True

            # Collision with walls
            if not (0 <= m[0] < c.COLS):
                return True

            # Collision with dead minos
            for dead in dead_minos:
                if list(m) == [dead.grid_x, dead.grid_y]:
                    return True

        return False

    def landed(self, dead_minos):
        for m in self.minos:
            # Check if landed on floor
            if m[1] + 1 >= c.ROWS:
                return True

            # Check if landed on any dead minos
            for dead in dead_minos:
                if (m[0], m[1] + 1) == (dead.grid_x, dead.grid_y):
                    return True

        return False


# ------ Setup ------ #
pygame.mixer.pre_init(buffer=32)
pygame.init()

# --- Initialise screen --- #
flags = pygame.DOUBLEBUF #| pygame.FULLSCREEN
# screen = pygame.display.set_mode((0, 0), flags)
screen = pygame.display.set_mode((c.width, c.height), flags)
pygame.display.set_caption("Tetrix")

# --- Make background --- #
def draw_field_border(surface, colour):
    x0 = c.field_pos[0] - 1
    y0 = c.field_pos[1]
    x1 = c.field_pos[0] + c.field_width
    y1 = c.field_pos[1] + c.field_height

    pygame.draw.line(surface, colour,
                     (x0, y0), (x0, y1))
    pygame.draw.line(surface, colour,
                     (x0, y1), (x1, y1))
    pygame.draw.line(surface, colour,
                     (x1, y0), (x1, y1))

bg = pygame.Surface(screen.get_size())
bg = bg.convert()
bg.fill(c.BLUE_GRAY)
draw_field_border(bg, c.GREY)

# --- Global timing stuff --- #
FPS = 60
clock = pygame.time.Clock()

# --- Fonts --- #
title_font = pygame.font.Font("fonts/Montserrat-Black.ttf", 60)
info_font = pygame.font.Font("fonts/Montserrat-BoldItalic.ttf", 30)
number_font = pygame.font.Font("fonts/Montserrat-Medium.ttf", 30)

def randomiser(prev):
    # Randomiser with bias against same two pieces in a row
    # (This is the same randomiser used in NES Tetris)

    roll = random.randint(0, len(c.tetriminos)) # 0-7

    if roll == len(c.tetriminos) or roll == prev:
        roll = random.randint(0, len(c.tetriminos) - 1) # 0-6

    return roll # A value 0-6

# ------ Title screen w/ level select ------ #
def menu(selected_lvl):

    title_text = title_font.render("TETRIX", True, c.WHITE)
    pygame.key.set_repeat(300, 100)

    level_icons = []
    lvl_range = 20 # One can choose to start on levels 0-19
    lvl_grid_cols = 10
    for i in range(lvl_range):
        num = i
        x = (c.width - NumIcon.w * lvl_grid_cols) // 2
        x += (i % lvl_grid_cols) * NumIcon.w
        y = 300 + NumIcon.w * (i // lvl_grid_cols)
        selected = True if num == selected_lvl else False
        level_icons.append(NumIcon(num, x, y, selected))

    lvl_select_group = pygame.sprite.Group()
    lvl_select_group.add(*level_icons)

    def update_display():
        screen.blit(bg, (0, 0))
        screen.blit(title_text, ((c.width - title_text.get_width())//2, 100))
        lvl_select_group.update()
        lvl_select_group.draw(screen)
        pygame.display.flip()

    on_menu_screen = True
    while on_menu_screen:
        update_display()

        for icn in level_icons:
            icn.selected = False

        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()
        events = pygame.event.get()

        for event in events:
            # Allow user to exit the screen
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type in [pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN]:
                for icn in level_icons:
                    icn_top_left = icn.rect[:2]
                    icn_bottom_right = (icn.rect[0] + icn.w,
                                        icn.rect[1] + icn.w)

                    if (icn_top_left[0] < mouse_pos[0] < icn_bottom_right[0]
                        and
                        icn_top_left[1] < mouse_pos[1] < icn_bottom_right[1]):

                        # If mouse is on an icon, make that icon selected
                        if selected_lvl != int(icn.num):
                            c.shift_sound.play(maxtime=60)
                        selected_lvl = int(icn.num)

            if (event.type == pygame.KEYDOWN and
                event.key in c.CONFIRM_KEYS) or (
                mouse_buttons[0]):
                # Start game on selected level
                on_menu_screen = False
                c.rot_sound.play(maxtime=100)

            if event.type != pygame.KEYDOWN:
                continue

            # Allow user to exit the screen
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            # --- Level selection control --- #

            if event.key in c.RIGHT_KEYS:
                c.shift_sound.play(maxtime=60)
                selected_lvl = (selected_lvl + 1) % lvl_range

            if event.key in c.LEFT_KEYS:
                c.shift_sound.play(maxtime=60)
                selected_lvl = (selected_lvl - 1) % lvl_range

            if event.key in c.UP_KEYS:
                c.shift_sound.play(maxtime=60)
                selected_lvl = (selected_lvl - lvl_grid_cols) % lvl_range

            if event.key in c.DOWN_KEYS:
                c.shift_sound.play(maxtime=60)
                selected_lvl = (selected_lvl + lvl_grid_cols) % lvl_range

        level_icons[selected_lvl].selected = True

        if not on_menu_screen:
            update_display()
            for _ in range(10): clock.tick(FPS) # Small delay
            c.level_up_sound.play()
            start_game(selected_lvl)

        clock.tick(FPS)

# ------ The actual gameplay ------ #
def start_game(start_level):

    pygame.key.set_repeat()

    # --- Game variables --- #

    max_spawn_freeze = 31 # Max freeze frames after piece has spawned.
                          # Freeze frames are cancelled by any keypress

    spawn_freeze_timer = max_spawn_freeze
    frame_counter = 1
    DAS_counter = 0 # For control of horisontal auto-shift delays
    level = start_level # Controls falling speed and point bonuses
    lines = 0
    points = 0

    if c.frames_per_cell[level] > 3:
        soft_drop_fpc = 2 # Soft drop falling speed in frames per cell
    else:
        soft_drop_fpc = 1

    soft_drop = False # If True, piece falls and locks faster than normal

    # --- Text initialisation and drawing --- #

    points_text = info_font.render("POINTS", True, c.WHITE)
    lines_text = info_font.render("LINES", True, c.WHITE)
    level_text = info_font.render("LEVEL", True, c.WHITE)
    next_text = info_font.render("NEXT", True, c.WHITE)

    points_num_text = number_font.render(str(points), True, c.WHITE)
    lines_num_text = number_font.render(str(lines), True, c.WHITE)
    level_num_text = number_font.render(str(level), True, c.WHITE)

    # --- Tetrimino, next piece and dead mino sprite group --- #

    tetrimino = Tetrimino(random.randint(0, 6), c.spawn_pos)
    next_piece = Tetrimino(randomiser(tetrimino.type_ID), array((12.5, 10)))

    dead_group = pygame.sprite.LayeredDirty() # Sprite group for dead minos
    dead_group.set_clip(c.field_rect)

    def complete_rows(dead_minos):
        # Returns a list of which rows are filled in

        complete_rows = []

        for row_n in range(c.ROWS):
            dead_minos_in_row = [
                    d for d in dead_minos
                    if d.grid_y == row_n
                    ]

            if len(dead_minos_in_row) >= c.COLS:
                complete_rows.append(row_n)

        return complete_rows

    def draw_text(dest_surf, bg_surf, text_render, side, row):
        text_pos = c.text_position[side](row)

        w = c.left_txt_offset
        h = text_render.get_height()

        text_rect = (*text_pos, w, h)

        # Draw bg over text
        dest_surf.set_clip(text_rect)
        dest_surf.blit(bg_surf, (0, 0))
        dest_surf.set_clip()

        # Draw text
        dirty_rect = screen.blit(
                        text_render,
                        text_pos)

        return dirty_rect

    def update_display(dirty_rects):

        dirty_rects += tetrimino.draw(screen)
        dirty_rects += next_piece.draw(screen)

        pygame.display.update(dirty_rects)

    # --- Draw all game screen stuff --- #

    screen.blit(bg, (0, 0))

    # Points text
    draw_text(screen, bg, points_text, "right", 0)
    draw_text(screen, bg, points_num_text, "right", 1)
    # Next text
    draw_text(screen, bg, next_text, "right", 4)

    # Lines text
    draw_text(screen, bg, lines_text, "left", 0)
    draw_text(screen, bg, points_num_text, "left", 1)
    # Level text
    draw_text(screen, bg, level_text, "left", 4)
    draw_text(screen, bg, level_num_text, "left", 5)

    pygame.display.flip()

    # --- Game loop --- #

    dirty_rects = []
    paused = False
    in_game = True
    while in_game:

        events = pygame.event.get()
        for event in events:
            # Allow user to exit the screen
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ESC -> Exit to menu
            if (event.type == pygame.KEYDOWN and
                event.key == pygame.K_ESCAPE):
                in_game = False

            # Pausing
            if (event.type == pygame.KEYDOWN and
                event.key in c.PAUSE_KEYS):
                paused = (False == paused) # Toggle True/False
                if not paused:
                    dead_group.repaint_rect(screen.get_rect())
                    pygame.display.update(dead_group.draw(screen))
                else:
                    next_piece.clear(screen, bg)
                    # Draw over the entire field with bg colour
                    pygame.display.update(
                            pygame.draw.rect(
                                    screen, c.BLUE_GRAY, c.field_rect))
                    continue

            # --- Register DOWN release for soft drop control --- #
            if (event.type == pygame.KEYUP and
                event.key in c.DOWN_KEYS):
                soft_drop = False

            if not (event.type == pygame.KEYDOWN and
                    tetrimino.lock_timer > 0):
                continue

            # --- Register DOWN press for soft drop control --- #
            if event.key in c.DOWN_KEYS:
                soft_drop = True
                spawn_freeze_timer = 0

            # --- Shifting on LEFT/RIGHT keypress --- #
            if event.key in c.LEFT_KEYS:
                c.shift_sound.play(maxtime=60)
                tetrimino.clear(screen, bg)
                tetrimino.shift("left", dead_group)
                DAS_counter = 0

                spawn_freeze_timer = min(c.frames_per_cell[level],
                                           spawn_freeze_timer)

            if event.key in c.RIGHT_KEYS:
                c.shift_sound.play(maxtime=60)
                tetrimino.clear(screen, bg)
                tetrimino.shift("right", dead_group)
                DAS_counter = 0

                spawn_freeze_timer = min(c.frames_per_cell[level],
                                           spawn_freeze_timer)

            # --- Rotation on keypress --- #
            if event.key in c.CW_KEYS:
                tetrimino.clear(screen, bg)
                tetrimino.rotate("cw", dead_group)
                c.rot_sound.play(maxtime=100)

                spawn_freeze_timer = min(c.frames_per_cell[level],
                                         spawn_freeze_timer)

            if event.key in c.CCW_KEYS:
                tetrimino.clear(screen, bg)
                tetrimino.rotate("ccw", dead_group)
                c.rot_sound.play(maxtime=100)

                spawn_freeze_timer = min(c.frames_per_cell[level],
                                         spawn_freeze_timer)

        if not in_game:
            # Quit to menu
            menu(start_level)
            break

        if paused:
            continue

        # --- Manage auto-shift --- #
        keys = pygame.key.get_pressed()

        dir_held = None

        # Check if LEFT or RIGHT is held
        for L, R in zip(c.LEFT_KEYS, c.RIGHT_KEYS):
            if not (keys[L] == keys[R]):
                # If only one direction is held
                dir_held = "left" if keys[L] else "right"
                break

        if dir_held and tetrimino.lock_timer > 0:
            DAS_counter += 1
            spawn_freeze_timer = 0
            if DAS_counter == c.DAS:
                prev_pos = tetrimino.centre_pos.copy()
                tetrimino.clear(screen, bg)
                tetrimino.shift(dir_held, dead_group)
                DAS_counter = c.DAS - c.ARR
                if list(prev_pos) != list(tetrimino.centre_pos):
                    # If tetrimino has actually moved, play shift sonud
                    c.shift_sound.play(maxtime=60)

        # --- Falling and landing --- #

        if soft_drop and tetrimino.lock_timer > 2:
            tetrimino.lock_timer = 2

        # If tetrimino has landed, start locking timer
        if tetrimino.landed(dead_group):
            tetrimino.lock_timer -= 1

        # Make tetrimino fall
        if not (tetrimino.lock_timer > 0 and spawn_freeze_timer <= 0):
            pass

        elif not soft_drop and frame_counter % c.frames_per_cell[level] == 0:
            tetrimino.clear(screen, bg)
            tetrimino.fall(dead_group, level)

        elif soft_drop and frame_counter % soft_drop_fpc == 0:
            tetrimino.clear(screen, bg)
            tetrimino.fall(dead_group, level)

            # Pushdown points
            points += 1
            # Update points text
            points_num_text = number_font.render(str(points), True, c.WHITE)
            dirty_rects.append(
                    draw_text(screen, bg, points_num_text, "right", 1))


        # --- Drawing stuff and updating screen --- #

        # Make tetrimino flash when it locks
        if tetrimino.lock_timer == 0:
            c.lock_sound.play(maxtime=500)
            for spr in tetrimino:
                spr.image.fill(c.WHITE)

        elif tetrimino.lock_timer <= -3:
            for spr in tetrimino:
                spr.image.fill(spr.colour)

        update_display(dirty_rects)
        dirty_rects = []

        # After tetrimino has locked and flashed
        if tetrimino.lock_timer <= -4:
            # If the tetrimino locks above the playing field; Game over :o
            if max(tetrimino.minos[:,1]) < 0:
                update_display(dirty_rects)
                for _ in range(30): clock.tick(FPS)
                in_game = False
                menu(start_level)
                break

            dead_group.add(tetrimino)
            soft_drop = False

            # --- Line clearing w/ animation --- #

            rows_to_clear = complete_rows(dead_group)

            if len(rows_to_clear) != 0:
                # If there are any rows to clear
                if len(rows_to_clear) == 4:
                    c.tetris_sound.play()
                else:
                    c.clear_sound.play()

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
                while x >= c.field_pos[0]:
                    pygame.event.pump()
                    animation_dirty_rects = []

                    for row_n in rows_to_clear:
                        y = c.field_pos[1] + row_n * c.cell_size
                        rectangle = pygame.Rect(x, y, w, c.cell_size)
                        animation_dirty_rects.append(
                                pygame.draw.rect(screen,
                                        c.BLUE_GRAY,
                                        rectangle))

                    pygame.display.update(animation_dirty_rects)

                    w += 2 * step
                    x -= step

                    clock.tick(FPS)

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
                if lines // 10 > level:
                    level += 1 if level < c.max_level else 0
                    c.level_up_sound.play()
                    if c.frames_per_cell[level] <= 3:
                        soft_drop_fpc = 1

                    level_num_text = number_font.render(
                            str(level), True, c.WHITE)
                    dirty_rects.append(
                            draw_text(screen, bg, level_num_text, "left", 5))

                # Update points and lines text
                points_num_text = number_font.render(
                        str(points), True, c.WHITE)
                dirty_rects.append(
                        draw_text(screen, bg, points_num_text, "right", 1))

                lines_num_text = number_font.render(
                        str(lines), True, c.WHITE)
                dirty_rects.append(
                        draw_text(screen, bg, lines_num_text, "left", 1))


            # --- Spawn new tetrimino and next piece --- #

            next_piece.clear(screen, bg)
            tetrimino = Tetrimino(next_piece.type_ID, c.spawn_pos)
            next_piece = Tetrimino(randomiser(tetrimino.type_ID), array((12.5, 10)))

            soft_drop_started = False
            spawn_freeze_timer = max_spawn_freeze

            # If the new piece spawns overlapping any dead minos; Game over :o
            if tetrimino.colliding(dead_group):
                update_display(dirty_rects)
                for _ in range(30): clock.tick(FPS)
                in_game = False
                menu(start_level)
                break

        # --- Time stuff --- #

        if spawn_freeze_timer > 0:
            spawn_freeze_timer -= 1
            frame_counter = 0
        else:
            frame_counter += 1
        clock.tick(FPS)
        sys.stdout.write(f"        	{points}   \r") ### debug
        sys.stdout.write(f"    {tetrimino.lock_timer}   \r") ### debug
        sys.stdout.write(f"{clock.get_rawtime() if clock.get_rawtime() > 16 else ''}\r") ### performance monitoring


menu(0)
