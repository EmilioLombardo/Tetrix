import pygame
from numpy import array

import constants as c

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
            return False

        self.update_sprites()
        return True

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
