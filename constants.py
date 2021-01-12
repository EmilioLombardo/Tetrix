import pygame
from numpy import array, linspace

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
                         field_pos[1] - 3 * cell_size,
                         field_width,
                         field_height + 3 * cell_size)

# ------ Controls ------ #

UP_KEYS = [pygame.K_UP, pygame.K_w]
DOWN_KEYS = [pygame.K_DOWN, pygame.K_s]
LEFT_KEYS = [pygame.K_LEFT, pygame.K_a]
RIGHT_KEYS = [pygame.K_RIGHT, pygame.K_d]

CW_KEYS = [pygame.K_UP, pygame.K_w, pygame.K_k, pygame.K_x, pygame.K_PERIOD]
CCW_KEYS = [pygame.K_j, pygame.K_z, pygame.K_COMMA]

CONFIRM_KEYS = [pygame.K_SPACE, pygame.K_RETURN]
PAUSE_KEYS = [pygame.K_SPACE, pygame.K_RETURN, pygame.K_TAB]

# ------ Sounds ------ #
rot_sound = pygame.mixer.Sound("alt_sounds/rot_sound.wav")
shift_sound = pygame.mixer.Sound("alt_sounds/shift_sound.wav")
shift_sound.set_volume(0.8)
lock_sound = pygame.mixer.Sound("alt_sounds/lock_sound.wav")
clear_sound = pygame.mixer.Sound("alt_sounds/clear_sound.wav")
tetris_sound = pygame.mixer.Sound("alt_sounds/tetris_sound.wav")
level_up_sound = pygame.mixer.Sound("alt_sounds/level_up_sound.wav")
game_over_sound = pygame.mixer.Sound("alt_sounds/game_over_sound.wav")

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
BLUE_GREY = (17, 28, 36)
LIGHT_BLUE_GREY = (35, 45, 55)

# What colours to use for the various tetriminos. Index represents piece type
colours = (PURPLE, BLUE, RED, GREEN, ORANGE, YELLOW, CYAN)

# ------ Level progression and scoring ------ #

# Falling speeds for different levels. Index represents level
frames_per_cell = [52, 48, 44, 40, 36, 32, 27, 21, 16, 10,
                 9, 8, 7, 6, 5, 5, 4, 4, 3, 3,
                 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
                 1]

max_level = 30

# List of lock delays for different levels
lock_delay = [int(t) for t in linspace(31, 15, 31)]

clear_points = [0, 40, 100, 300, 1200]
    # 1 line: 40 points, 2 lines: 300 points etc.

# ------ Spawning, shifting and SRS stuff ------ #

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

# --- SRS offset data --- #

# https://harddrop.com/wiki/SRS

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
