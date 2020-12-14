import sys
import pygame

import constants as c

# Initialise screen
pygame.init()
flags = pygame.DOUBLEBUF #| pygame.FULLSCREEN
# screen = pygame.display.set_mode((0, 0), flags)
screen = pygame.display.set_mode((c.width, c.height), flags)
pygame.display.set_caption("Tetrix")

# Fill background
bg = pygame.Surface(screen.get_size())
bg = bg.convert()
bg.fill(c.BLACK)

# ØØØØØ
FPS = 60
clock = pygame.time.Clock()

# Main menu w/ level select
def menu():

    cursor = pygame.sprite.Sprite()
    ###

    def updateDisplay():
        pygame.display.flip()

def game():

    # TODO: Game variables

    def updateDisplay():
        # TODO: Draw stuff
        pygame.display.update()

    while 1: # Game loop
        ### INSERT GAME HERE :P
        break
