import pygame
from numpy import array, linspace

pygame.init()
display_info = pygame.display.Info()

# ------ Display stuff and playing field dimensions ------ #

fullscreen = False
    ### Might add fullscreen/windowed toggling during runtime in the future.
    ### For now it'll just be a constant.
if fullscreen:
    width = display_info.current_w
    height = display_info.current_h
else:
    width = 750
    height = width

COLS = 10
ROWS = 20
field_width = min(width, height) / 2.5
field_height = ROWS/COLS * field_width
field_pos = ( # (x, y) for top-left corner of playing field
    (width - field_width) / 2,
    (height - field_height) / 2)
cell_size = field_width / COLS
field_rect = pygame.Rect(field_pos[0],
                         field_pos[1] - 3 * cell_size,
                         field_width,
                         field_height + 3 * cell_size)

scale = field_width / 300 # Variable used to scale visual elements
print(width, "x", height)

# ------ Controls ------ #

UP_KEYS = [pygame.K_UP, pygame.K_w]
DOWN_KEYS = [pygame.K_DOWN, pygame.K_s]
LEFT_KEYS = [pygame.K_LEFT, pygame.K_a]
RIGHT_KEYS = [pygame.K_RIGHT, pygame.K_d]

CW_KEYS = [pygame.K_UP, pygame.K_w, pygame.K_k, pygame.K_x]
CCW_KEYS = [pygame.K_j, pygame.K_z]

CONFIRM_KEYS = [pygame.K_SPACE, pygame.K_RETURN]
PAUSE_KEYS = [pygame.K_SPACE, pygame.K_RETURN, pygame.K_TAB]

# ------ Sounds ------ #
rot_sound = pygame.mixer.Sound("sounds/rot_sound.wav")
shift_sound = pygame.mixer.Sound("sounds/shift_sound.wav")
shift_sound.set_volume(0.8)
lock_sound = pygame.mixer.Sound("sounds/lock_sound.wav")
clear_sound = pygame.mixer.Sound("sounds/clear_sound.wav")
tetris_sound = pygame.mixer.Sound("sounds/tetris_sound.wav")
level_up_sound = pygame.mixer.Sound("sounds/level_up_sound.wav")
game_over_sound = pygame.mixer.Sound("sounds/game_over_sound.wav")

# ------ Colours ------ #

PURPLE = (180, 40, 140)
BLUE = (40, 80, 230)
RED = (230, 0, 0)
GREEN = (40, 225, 20)
ORANGE = (240, 150, 10)
YELLOW = (230, 230, 0)
CYAN = (0, 200, 230)

WHITE = (250, 250, 250) # Text colour
GREY = (130, 130, 130) # Field border colour
BLUE_GREY = (17, 28, 36) # BG colour
LIGHT_BLUE_GREY = (35, 45, 55) # Grid colour

# What colours to use for the various tetriminos. Index represents piece type.
colours = (PURPLE, BLUE, RED, GREEN, ORANGE, YELLOW, CYAN)

def lighten(colour_list, increase=25):
    """
    Takes an RGB colour and increases the HSL lightness.
    Returns new RGB colour.
    """

    # Get hsla-values for colour
    colour = pygame.Color(*colour_list)
    h, s, l, a = colour.hsla

    # Increase lightness
    colour.hsla = (h, s, min(l + increase, 100), a)

    # Return RGB tuple for lightened colour
    return (colour.r, colour.g, colour.b)

# ------ Level progression and scoring ------ #

# Falling speeds for different levels. Index represents level.
frames_per_cell = [52, 48, 44, 40, 36, 32, 27, 21, 16, 10,
                   9, 8, 7, 6, 5, 5, 4, 4, 3, 3,
                   2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
                   1]

max_level = 30

# List of lock delays for different levels. Index represents level.
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
