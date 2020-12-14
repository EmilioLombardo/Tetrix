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
bg.fill(c.BLUE_GRAY)

# ØØØØØ
FPS = 60
clock = pygame.time.Clock()

# Main menu w/ level select
def menu():
    title_font = pygame.font.Font("fonts/Montserrat-Black.ttf", 60)

    titleText = title_font.render("TETRIX", True, c.WHITE)

    class Level_icon(pygame.sprite.Sprite):
        w = 50
        level_font = pygame.font.Font("fonts/Montserrat-Bold.ttf", 40)

        def __init__(self, num, x, y, selected):
            super().__init__()
            self.num = str(num)
            self.selected = selected

            self.image = pygame.Surface((self.w, self.w))
            self.image.fill(c.CYAN)
            self.rect = (x, y, self.w, self.w)

            self.text = self.level_font.render(self.num, True, c.WHITE)

        def update(self):
            if self.selected:
                self.image.fill(c.WHITE)
                self.text = self.level_font.render(self.num, True, c.BLUE_GRAY)
                self.image.blit(self.text,(0, 0))
            else:
                self.image.fill(c.BLUE_GRAY)
                self.text = self.level_font.render(self.num, True, c.WHITE)
                self.image.blit(self.text,(0, 0))

    selected_lvl = 0

    level_icons = []
    lvl_range = 10 # One can choose to start on levels 0-9
    for i in range(lvl_range):
        num = i
        x = i*Level_icon.w
        y = 300
        selected = True if num == selected_lvl else False
        level_icons.append(Level_icon(num, x, y, selected))

    lvl_select_group = pygame.sprite.Group()
    lvl_select_group.add(*level_icons)

    def updateDisplay():
        screen.blit(bg, (0, 0))
        lvl_select_group.update()
        lvl_select_group.draw(screen)
        pygame.display.flip()

    while 1:
        for icn in level_icons:
            icn.selected = False

        # Allows user to exit the screen
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if event.key in c.RIGHT_KEYS:
                selected_lvl = (selected_lvl + 1) % lvl_range

            if event.key in c.LEFT_KEYS:
                selected_lvl = (selected_lvl - 1) % lvl_range

        level_icons[selected_lvl].selected = True

        updateDisplay()
        clock.tick(FPS)


def game():

    # TODO: Game variables

    def updateDisplay():
        # TODO: Draw stuff
        pygame.display.update()

    while 1: # Game loop
        ### INSERT GAME HERE :P
        break

menu()
