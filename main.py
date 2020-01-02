import pygame
import os
import sys


WIDTH, HEIGHT = 600, 800
FPS = 60

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('GalaxyShooter')
clock = pygame.time.Clock()


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, color_key=None):
    fullname = os.path.join('data', 'images', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def load_sound(name):
    fullname = os.path.join('data', 'sounds', name)
    pass


def draw_text(screen, text, size, x, y, color):
    font = pygame.font.Font(None, size)
    string_rendered = font.render(text, 1, color)
    intro_rect = string_rendered.get_rect()
    intro_rect.midtop = (x, y)
    screen.blit(string_rendered, intro_rect)


def screenIntro():
    background = load_image('background_intro.png')
    color = pygame.Color('White')
    hsv = color.hsva
    color.hsva = (hsv[0], hsv[1], 0, hsv[3])
    valuechanging = 1

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        screen.blit(background, (0, 0))
        draw_text(screen, 'GK', 50, WIDTH // 2, HEIGHT // 2 - 100, color)
        draw_text(screen, 'Production', 50, WIDTH // 2, HEIGHT // 2 - 50,
                  color)
        draw_text(screen, 'Present', 50, WIDTH // 2, HEIGHT // 2, color)

        hsv = color.hsva

        if valuechanging == 1 and (hsv[2] + valuechanging) > 60:
            valuechanging = -1
        elif valuechanging == -1 and (hsv[2] + valuechanging) < 1:
            break

        color.hsva = (hsv[0], hsv[1], hsv[2] + valuechanging, hsv[3])

        pygame.display.flip()

        clock.tick(20)


def screenMainmenu():
    background = load_image('background_mainmenu.png')
    buttonFunctions = {1: screenChooseLevel}
    all_sprites = pygame.sprite.Group()
    buttonPlay = Button(all_sprites, (pygame.Color('#00BFFF'), pygame.Color('#87CEFA')), (200, 100), (300, 400), ('Выбрать уровень', 30, pygame.Color('White')))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONUP:
                if buttonPlay.isPressed():
                    pressedButton = 1
                    running = False

        screen.blit(background, (0, 0))

        all_sprites.draw(screen)
        all_sprites.update()

        pygame.display.flip()

        clock.tick(FPS)

    buttonFunctions[pressedButton](123)


def screenChooseLevel(a):
    background = load_image('background_mainmenu.png')
    all_sprites = pygame.sprite.Group()

    pass







class Button(pygame.sprite.Sprite):
    def __init__(self, spriteGroup, colors, size, posCenter, textInfo):
        super().__init__(spriteGroup)
        self.colors = colors
        self.size = size
        self.posCenter = posCenter
        self.textInfo = textInfo


        self.image = pygame.Surface(self.size)
        self.image.fill(self.colors[0])
        self.rect = self.image.get_rect()
        self.rect.centerx = self.posCenter[0]
        self.rect.centery = self.posCenter[1]
        draw_text(self.image, self.textInfo[0], self.textInfo[1], self.rect.width // 2, self.rect.height // 2 - self.textInfo[1] // 4, self.textInfo[2])

    def isPressed(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def update(self):
        if self.isPressed():
            self.image.fill(self.colors[1])
        else:
            self.image.fill(self.colors[0])
        draw_text(self.image, self.textInfo[0], self.textInfo[1], self.rect.width // 2, self.rect.height // 2 - self.textInfo[1] // 4, self.textInfo[2])


def main():
    #screenIntro()
    screenMainmenu()

main()

