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
def menu(selected_lvl):
    title_font = pygame.font.Font("fonts/Montserrat-Black.ttf", 60)
    title_text = title_font.render("TETRIX", True, c.WHITE)
    pygame.key.set_repeat(300, 100)

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
            textW = self.text.get_width()
            textH = self.text.get_height()
            self.text_rect = (self.w//2-textW//2, self.w//2-textH//2)

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

    level_icons = []
    lvl_range = 10 # One can choose to start on levels 0-9
    for i in range(lvl_range):
        num = i
        x = c.width//2 - (Level_icon.w * lvl_range)//2 + i * Level_icon.w
        y = 300
        selected = True if num == selected_lvl else False
        level_icons.append(Level_icon(num, x, y, selected))

    lvl_select_group = pygame.sprite.Group()
    lvl_select_group.add(*level_icons)

    def updateDisplay():
        screen.blit(bg, (0, 0))
        screen.blit(title_text, (c.width//2 - title_text.get_width()//2, 100))
        lvl_select_group.update()
        lvl_select_group.draw(screen)
        pygame.display.flip()

    on_menu_screen = True
    while on_menu_screen: # Game loop for menu screen
        updateDisplay()

        for icn in level_icons:
            icn.selected = False

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

            if event.key in c.CONFIRM_KEYS:
                on_menu_screen = False
                game(selected_lvl)

        level_icons[selected_lvl].selected = True

        clock.tick(FPS)


def game(start_level):

    pygame.key.set_repeat()

    # TODO: Game variables

    def draw_field_border(surface, colour):
        x0 = c.fieldPos[0]
        y0 = c.fieldPos[1]
        x1 = c.fieldPos[0] + c.fieldWidth + 1
        y1 = c.fieldPos[1] + c.fieldHeight + 1
        pygame.draw.line(surface, colour,
                         (x0, y0), (x1, y0))
        pygame.draw.line(surface, colour,
                         (x0, y0), (x0, y1))
        pygame.draw.line(surface, colour,
                         (x0, y1), (x1, y1))
        pygame.draw.line(surface, colour,
                         (x1, y0), (x1, y1))

    def updateDisplay():
        pygame.display.update()

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

            if event.type != pygame.KEYDOWN:
                continue

            # Allow user to exit the screen
            if event.key == pygame.K_ESCAPE:
                in_game = False

        if in_game == False:
            menu(start_level)
            break

        updateDisplay()
        clock.tick(FPS)


menu(0)
