import pygame
from numpy import array
from math import ceil

import constants as c

# ------ Class for individual minos (blocks) ------ #
class Mino(pygame.sprite.DirtySprite):

    @classmethod
    def get_size(cls, grid_x, grid_y):
        """
        Method that calculates width and height of mino at given
        position.
        (This allows for any field width, not just multiples of 10
        pixels.)

        WHY IS THIS NEEDED?
        If mino width and height were simply the same as the cell size,
        there would be graphical problems for field sizes where
        field_width/COLS is not a whole number. Then cell_size would
        not be a whole number, and certain columns and rows of the grid
        would be rendered with slightly different width and/or height
        due to rounding issues. This would lead to some ugly dark lines
        between the minos.

        This method makes sure the width and height of the mino matches
        the one of the column and row it's in, filling any gaps between
        rows/columns, thus allowing us to have an arbitrary field width,
        not just multiples of 10.

        Just trust me lol
        """
        w = c.cell_size
        h = c.cell_size

        pixel_x0, pixel_y0 = cls.grid_to_pixel(grid_x, grid_y)
        pixel_x1, pixel_y1 = cls.grid_to_pixel(grid_x + 1, grid_y + 1)
        if pixel_x0 + int(c.cell_size) < pixel_x1:
            w += 1

        if pixel_y0 + int(c.cell_size) < pixel_y1:
            h += 1

        return w, h

    @staticmethod
    def grid_to_pixel(grid_x, grid_y):
        """Converts playfield grid-coords into screen pixel-coords."""

        pixel_x = int(c.cell_size * grid_x + c.field_pos[0])
        pixel_y = int(c.cell_size * grid_y + c.field_pos[1])
        return pixel_x, pixel_y

    def __init__(self, colour, x, y):
        super().__init__()
        self.grid_x = x
        self.grid_y = y
        self.pixel_x, self.pixel_y = self.grid_to_pixel(self.grid_x,
                                                        self.grid_y)

        self.colour = colour

        self.w, self.h = self.get_size(self.grid_x, self.grid_y)
        self.image = pygame.Surface((self.w, self.h))
        self.draw_mino()

        self.rect = pygame.Rect(self.pixel_x, self.pixel_y, self.w, self.h)

    def draw_mino(self):
        border_col = c.LIGHT_BLUE_GREY
        hl_col = c.lighten(self.colour)

        self.image.fill(self.colour)

        # Point pairs for top, left, bottom and right sides
        point_pairs = lambda x0, y0, x1, y1: (
                ((x0, y0), (x1, y0)), # Top
                ((x0, y0), (x0, y1)), # Left
                ((x0, y1), (x1 + 1, y1)), # Bottom
                ((x1, y0), (x1, y1 + 1))) # Right

        # Dark border on all sides
        border_w = round(c.scale) # 1
        x0 = 0
        y0 = 0
        x1 = round(self.w - c.scale)
        y1 = round(self.h - c.scale)

        for line in point_pairs(x0, y0, x1, y1)[2:]:
            pygame.draw.line(self.image, border_col, *line, border_w)


        # Light border on top and left sides
        border_w = ceil(4 * c.scale) # 3
        x0 = border_w//2 - 1
        y0 = border_w//2 - 1
        x1 = int(self.w - 2 * c.scale)
        y1 = int(self.h - 2 * c.scale)

        for line in point_pairs(x0, y0, x1, y1)[:2]:
            pygame.draw.line(self.image, hl_col, *line, border_w)

        pygame.draw.rect(
                self.image, border_col, (0, 0, round(c.scale), round(c.scale)))

    def update(self):

        prev = self.image, self.rect

        self.pixel_x, self.pixel_y = self.grid_to_pixel(self.grid_x,
                                                        self.grid_y)

        self.w, self.h = self.get_size(self.grid_x, self.grid_y)

        self.image = pygame.Surface((self.w, self.h))
        self.draw_mino()

        self.rect = pygame.Rect(
                self.pixel_x, self.pixel_y, self.w, self.h)

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

        self.rot_index = 0 # Rotation state (0-3 for the four rotation states)

        self.minos = [] # Array with grid coordinate pairs for each mino
                        # E.g. [[3 -1] [4 -2] [4 -1] [5 -1]] (T-piece at spawn)

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
        """
        Update position of sprites according to self.minos.
        """
        # Update position of sprites according to self.minos
        for i in range(len(self.minos)):
            spr = self.sprite_list[i]
            spr.grid_x, spr.grid_y = self.minos[i]

        # Call update method of sprites
        self.update()

    def rotate(self, dir, dead_minos):
        """
        Method to rotate tetrimino clockwise ("cw") or anti-clockwise ("ccw").
        Does SRS wall-kicks.
        """
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
        """
        Method to shift tetrimino left or right. Handles collision.
        """
        prev_minos = self.minos.copy()
        prev_centre = self.centre_pos.copy()

        if dir == "left":
            self.centre_pos[0] -= 1
            self.minos[:,0] -= 1

        elif dir == "right":
            self.centre_pos[0] += 1
            self.minos[:,0] += 1

        else:
            raise Exception("dir argument must be string 'left' or 'right'")

        if self.colliding(dead_minos):
            self.minos = prev_minos
            self.centre_pos = prev_centre
            self.update_sprites()
            return False

        self.update_sprites()
        return True

    def fall(self, dead_minos, level):
        """
        Method to make tetrimino fall down one row. Handles landing.
        """
        if not self.landed(dead_minos):
            self.minos[:,1] += 1
            self.centre_pos[1] += 1
            self.lock_timer = c.lock_delay[level]
            self.update_sprites()

    def colliding(self, dead_minos):
        """
        Checks if any minos are overlapping dead minos or are out of bounds.
        """
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
        """
        Checks if tetrimino has landed (on floor or on dead minos).
        """
        for m in self.minos:
            # Check if landed on floor
            if m[1] + 1 >= c.ROWS:
                return True

            # Check if landed on any dead minos
            for dead in dead_minos:
                if (m[0], m[1] + 1) == (dead.grid_x, dead.grid_y):
                    return True

        return False
