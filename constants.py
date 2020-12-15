import pygame

pygame.init()
displayInfo = pygame.display.Info()

# width = displayInfo.current_w
# height = displayInfo.current_h
width = 720
height = 720
print(width, "x", height)

COLS = 10
ROWS = 20
fieldWidth = 300
fieldHeight = (ROWS//COLS) * fieldWidth
fieldPos = ( # (x, y) for top-left corner of playing field
    (width // 2) - (fieldWidth // 2),
    (height // 2) - (fieldHeight // 2)
    )
cellSize = fieldWidth // COLS

DAS = 8 # Delayed auto-shift (frames)
ARR = 3 # Auto repeat rate (in frames/cell)

UP_KEYS = [pygame.K_UP, pygame.K_w]
DOWN_KEYS = [pygame.K_DOWN, pygame.K_s]
LEFT_KEYS = [pygame.K_LEFT, pygame.K_a]
RIGHT_KEYS = [pygame.K_RIGHT, pygame.K_d]

CONFIRM_KEYS = [pygame.K_SPACE, pygame.K_RETURN, pygame.K_k]

# Define some colours
PURPLE = (180, 40, 140)
BLUE = (40, 80, 230)
GREEN = (40, 225, 20)
YELLOW = (230, 230, 0)
RED = (230, 0, 0)
ORANGE = (240, 150, 10)
CYAN = (0, 200, 230)
WHITE = (255, 255, 255)
GREY = (130, 130, 130)
BLUE_GRAY = (20, 50, 70)

# What colours to use for the various tetriminos. Index represents piece type
colours = (PURPLE, BLUE, GREEN, YELLOW, RED, ORANGE, CYAN)

# Falling speeds for different levels
framesPerCell = [52, 48, 44, 40, 36, 32, 27, 21, 16, 10,
                 9, 8, 7, 6, 5, 5, 4, 4, 3, 3,
                 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
                 1]

### 14 + 14 + 14 -- line clear animation
### 32 -- lock delay
### 4 -- locking animation before next spawn
### max 31 -- freeze frames after spawn, set to 0 when any key is pressed
### (after freeze frames comes fall delay)
