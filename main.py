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
    w = c.cellSize

    def grid_to_pixel(cls, grid_x, grid_y):
        pixel_x = c.cellSize * grid_x + c.fieldPos[0]
        pixel_y = c.cellSize * grid_y + c.fieldPos[1]
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
        self.rect = (self.pixel_x, self.pixel_y, self.w, self.w)

    def update(self):
        prev = self.image, self.rect

        self.image.fill(self.colour)

        self.pixel_x, self.pixel_y = self.grid_to_pixel(self.grid_x,
                                                        self.grid_y)
        self.rect = (self.pixel_x, self.pixel_y, self.w, self.w)

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

        self.landed = False
        self.lock_timer = 32

        if type_ID == 5:
            self.offsets = c.offsets_I
        elif type_ID == 6:
            self.offsets = c.offsets_O
        else:
            self.offsets = c.offsets_TJZSL

        self.rot_index = 0 # Rotation index (0-3 for the four rotations)

        self.minos_rel = [] # List with coordinate pairs for each mino
                            # (Coordinates are relative to centre_pos)

        for mino_XY in c.tetriminos[self.type_ID]:
            self.minos_rel.append(mino_XY)

        self.minos_rel = array(self.minos_rel)

        # minos_abs is like minos_rel, but with coords relative to grid origin
        self.minos_abs = self.minos_rel + self.centre_pos
        self.minos_abs += self.offsets[self.rot_index][0]

        # --- Sprite/group stuff --- #

        colour = c.colours[self.type_ID]

        # Add sprites to self
        for mino_XY in self.minos_abs:
            self.add(Mino(colour, *mino_XY))

        self.sprite_list = self.sprites()

        self.update_minos()
        self.update_sprites()

    # Method to update coords of minos_abs according to centre_pos
    def update_minos(self):
        self.minos_abs = self.minos_rel + self.centre_pos
        self.minos_abs += self.offsets[self.rot_index][0]

    def update_sprites(self):
        i = 0
        for mino_XY in self.minos_abs:
            self.sprite_list[i].grid_x, self.sprite_list[i].grid_y = mino_XY
            i += 1

        self.update() # Calls update method of sprites

    def shift(self, dir, dead_minos):
        prev = self.centre_pos[0]

        if dir == "left":
            self.centre_pos[0] -= 1

        elif dir == "right":
            self.centre_pos[0] += 1

        self.update_minos()

        if self.colliding(dead_minos):
            self.centre_pos[0] = prev
            self.update_minos()
            return

        self.update_sprites()

    def fall(self, dead_minos):
        self.centre_pos[1] += 1
        self.update_minos()

        if self.colliding(dead_minos):
            self.centre_pos[1] -= 1
            self.update_minos()
            self.landed = True
            return

        self.landed = False
        self.lock_timer = 32
        self.update_sprites()

    def colliding(self, dead_minos):
        for m in self.minos_abs:
            # Collision with floor
            if m[1] >= c.ROWS:
                return True

            # Collision with walls
            if not 0 <= m[0] < c.COLS:
                return True

            # Collision with dead minos
            for dead in dead_minos:
                if list(m) == [dead.grid_x, dead.grid_y]:
                    return True

        return False


# ------ Setup ------ #

# Initialise screen
pygame.init()
flags = pygame.DOUBLEBUF #| pygame.FULLSCREEN
# screen = pygame.display.set_mode((0, 0), flags)
screen = pygame.display.set_mode((c.width, c.height), flags)
pygame.display.set_caption("Tetrix")

# Fill background
bg = pygame.Surface(screen.get_size())
bg = bg.convert()
bg.fill(c.BLUE_GRAY)

# ØØØØØ
FPS = 60
clock = pygame.time.Clock()

# ------ Title screen w/ level select ------ #
def menu(selected_lvl):
    title_font = pygame.font.Font("fonts/Montserrat-Black.ttf", 60)
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

        keys = pygame.key.get_pressed()
        events = pygame.event.get()
        for event in events:
            # Allow user to exit the screen
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type != pygame.KEYDOWN:
                continue

            # Allow user to exit the screen
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if event.key in c.RIGHT_KEYS:
                selected_lvl = (selected_lvl + 1) % lvl_range

            if event.key in c.LEFT_KEYS:
                selected_lvl = (selected_lvl - 1) % lvl_range

            if event.key in c.UP_KEYS:
                selected_lvl = (selected_lvl - lvl_grid_cols) % lvl_range

            if event.key in c.DOWN_KEYS:
                selected_lvl = (selected_lvl + lvl_grid_cols) % lvl_range

            if event.key in c.CONFIRM_KEYS:
                on_menu_screen = False
                start_game(selected_lvl)

        level_icons[selected_lvl].selected = True

        clock.tick(FPS)

# ------ The actual gameplay ------ #
def start_game(start_level):

    pygame.key.set_repeat()

    # TODO: Game variables
    frame_counter = 0
    DAS_counter = 0 # For control of horisontal movement delays
    level = start_level

    tetrimino = Tetrimino(random.randint(0, 6), c.spawn_pos)
    next_piece = Tetrimino(random.randint(0, 6), array((12.5, 10)))

    dead_group = pygame.sprite.LayeredDirty()

    def draw_field_border(surface, colour):
        x0 = c.fieldPos[0] - 1
        y0 = c.fieldPos[1]
        x1 = c.fieldPos[0] + c.fieldWidth
        y1 = c.fieldPos[1] + c.fieldHeight

        pygame.draw.line(surface, colour,
                         (x0, y0), (x0, y1))
        pygame.draw.line(surface, colour,
                         (x0, y1), (x1, y1))
        pygame.draw.line(surface, colour,
                         (x1, y0), (x1, y1))

    def update_display():
        dirty_rects = []

        dirty_rects += tetrimino.draw(screen)
        dirty_rects += next_piece.draw(screen)

        pygame.display.update(dirty_rects)

    screen.blit(bg, (0, 0))
    draw_field_border(screen, c.GREY)
    pygame.display.flip()

    in_game = True
    while in_game: # Game loop

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

            # --- Shifting on left/right keypress --- #

            # If one of the shifting keys are released, reset DAS counter
            if (event.type == pygame.KEYUP and
                event.key in [pygame.K_a, pygame.K_d]):

                DAS_counter = 0

            if event.type != pygame.KEYDOWN:
                continue

            if event.key in c.LEFT_KEYS:
                tetrimino.clear(screen, bg)
                tetrimino.shift("left", dead_group.sprites())
                DAS_counter = 0

            elif event.key in c.RIGHT_KEYS:
                tetrimino.clear(screen, bg)
                tetrimino.shift("right", dead_group.sprites())
                DAS_counter = 0

        if in_game == False:
            menu(start_level)
            break

        # --- Manage auto-shift --- #
        keys = pygame.key.get_pressed()

        for k in c.LEFT_KEYS:
            if keys[k]: # If LEFT is held
                DAS_counter += 1
                if DAS_counter == c.DAS:
                    tetrimino.clear(screen, bg)
                    tetrimino.shift("left", dead_group.sprites())
                    DAS_counter = c.DAS - c.ARR

        for k in c.RIGHT_KEYS:
            if keys[k]: # If RIGHT is held
                DAS_counter += 1
                if DAS_counter == c.DAS:
                    tetrimino.clear(screen, bg)
                    tetrimino.shift("right", dead_group.sprites())
                    DAS_counter = c.DAS - c.ARR

        if tetrimino.landed:
            tetrimino.lock_timer -= 1

        if frame_counter % c.frames_per_cell[level] == 0:
            tetrimino.clear(screen, bg)
            tetrimino.fall(dead_group.sprites())

        if tetrimino.lock_timer <= 0:
            dead_group.add(tetrimino.sprites())
            next_piece.clear(screen, bg)
            tetrimino = Tetrimino(next_piece.type_ID, c.spawn_pos)
            next_piece = Tetrimino(random.randint(0, 6), array((12.5, 10)))

        update_display()

        frame_counter += 1
        clock.tick(FPS)
        sys.stdout.write( ### performance monitoring
                f"{clock.get_rawtime() if clock.get_rawtime() > 16 else '   '}"
                + "\r")


menu(0)
