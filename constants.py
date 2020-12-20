import pygame
from numpy import array

pygame.init()
display_info = pygame.display.Info()

# ------ Display stuff and playing field dimensions ------ #

# width = display_info.current_w
# height = display_info.current_h
width = 750
height = 750
print(width, "x", height)

COLS = 10
ROWS = 20
field_width = 300
field_height = int(ROWS/COLS * field_width)
field_pos = ( # (x, y) for top-left corner of playing field
    (width // 2) - (field_width // 2),
    (height // 2) - (field_height // 2)
    )
cell_size = field_width // COLS
field_rect = pygame.Rect(field_pos[0],
                         field_pos[1] - 2 * cell_size,
                         field_width,
                         field_height + 2 * cell_size)

# ------ Controls ------ #

UP_KEYS = [pygame.K_UP, pygame.K_w]
DOWN_KEYS = [pygame.K_DOWN, pygame.K_s]
LEFT_KEYS = [pygame.K_LEFT, pygame.K_a]
RIGHT_KEYS = [pygame.K_RIGHT, pygame.K_d]

CW_KEYS = [pygame.K_UP, pygame.K_w, pygame.K_k, pygame.K_x, pygame.K_PERIOD]
CCW_KEYS = [pygame.K_j, pygame.K_z, pygame.K_COMMA]

CONFIRM_KEYS = [pygame.K_SPACE, pygame.K_RETURN, pygame.K_k]
PAUSE_KEYS = [pygame.K_SPACE, pygame.K_RETURN, pygame.K_TAB]

# ------ Colours ------ #

PURPLE = (180, 40, 140)
BLUE = (40, 80, 230)
GREEN = (40, 225, 20)
YELLOW = (230, 230, 0)
RED = (230, 0, 0)
ORANGE = (240, 150, 10)
CYAN = (0, 200, 230)
WHITE = (255, 255, 255)
GREY = (130, 130, 130)
BLUE_GRAY = (17, 28, 36)

# What colours to use for the various tetriminos. Index represents piece type
colours = (PURPLE, BLUE, RED, GREEN, ORANGE, YELLOW, CYAN)

# ------ Text stuff ------ #
margin = 40
space = 40
left_txt_offset = 130 + margin

text_position = {
        "left" : lambda row: (field_pos[0] - left_txt_offset,
                              field_pos[1] + margin + row * space),

        "right" : lambda row: (field_pos[0] + field_width + margin,
                               field_pos[1] + margin + row * space)
        }

# ------ Point rewards for line clears ------ #

clear_points = [0, 40, 100, 300, 1200]
    # 1 line: 40 points, 2 lines: 300 points etc.

# ------ Spawning, shifting and SRS stuff ------ #
# https://harddrop.com/wiki/SRS

spawn_pos = array((4, -1))

# Define the seven tetriminos. (0, 0) is anchor point for (true) rotation
tetriminos = (
        ((-1, 0), (0, -1), (0, 0), (1, 0)), # 	ID 0: T
        ((-1, -1), (-1, 0), (0, 0), (1, 0)), # 	ID 1: J
        ((-1, -1), (0, -1), (0, 0), (1, 0)), # 	ID 2: Z
        ((-1, 0), (0, 0), (0, -1), (1, -1)), # 	ID 3: S
        ((-1, 0), (0, 0), (1, 0), (1, -1)), # 	ID 4: L
        ((0, -1), (1, -1), (0, 0), (1, 0)), # 	ID 5: O
        ((-1, 0), (0, 0), (1, 0), (2, 0)) # 	ID 6: I
)

DAS = 8 # Delayed Auto-Shift (frames)
ARR = 3 # Auto Repeat Rate (in frames/cell)

# Falling speeds for different levels
frames_per_cell = [52, 48, 44, 40, 36, 32, 27, 21, 16, 10,
                 9, 8, 7, 6, 5, 5, 4, 4, 3, 3,
                 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
                 1]

# --- SRS offset data --- #

offsets_TJZSL = array((
        (( 0, 0), ( 0, 0), ( 0, 0), ( 0, 0), ( 0, 0)), # 	Rot 0 (spawn)
        (( 0, 0), (+1, 0), (+1,+1), ( 0,-2), (+1,-2)), # 	Rot R
        (( 0, 0), ( 0, 0), ( 0, 0), ( 0, 0), ( 0, 0)), # 	Rot 2
        (( 0, 0), (-1, 0), (-1,+1), ( 0,-2), (-1,-2)) # 	Rot L
))

offsets_I = array((
        (( 0, 0), (-1, 0), (+2, 0), (-1, 0), (+2, 0)), # 	Rot 0 (spawn)
        ((-1, 0), ( 0, 0), ( 0, 0), ( 0,-1), ( 0,+2)), # 	Rot R
        ((-1,-1), (+1,-1), (-2,-1), (+1, 0), (-2, 0)), # 	Rot 2
        (( 0,-1), ( 0,-1), ( 0,-1), ( 0,+1), ( 0,-2)) #		Rot L
))

offsets_O = array((
        (( 0, 0),), # 	Rot 0 (spawn)
        (( 0,+1),), # 	Rot R
        ((-1,+1),), # 	Rot 2
        ((-1, 0),) #	Rot L
))
