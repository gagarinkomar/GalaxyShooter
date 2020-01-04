import pygame
import os
import sys
import sqlite3


WIDTH, HEIGHT = 600, 800
FPS = 60

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('GalaxyShooter')
clock = pygame.time.Clock()

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


connection = sqlite3.connect(os.path.join('data', 'Config.db'))
cursor = connection.cursor()

nameOfBackgroundMenu = cursor.execute('SELECT Source FROM Sources WHERE Name = \'BackgroundMenu\'').fetchone()[0]
BackgroundMenu = load_image(nameOfBackgroundMenu)


def terminate():
    pygame.quit()
    connection.close()
    sys.exit()


def draw_text(screen, text, size, x, y, color):
    font = pygame.font.Font(None, size)
    string_rendered = font.render(text, 1, color)
    intro_rect = string_rendered.get_rect()
    intro_rect.midtop = (x, y)
    screen.blit(string_rendered, intro_rect)


def screenIntro():
    color = pygame.Color('White')
    hsv = color.hsva
    color.hsva = (hsv[0], hsv[1], 0, hsv[3])
    valuechanging = 1

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        screen.fill(pygame.Color('Black'))
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
    buttonFunctions = {1: screenChooseLevel, 2: screenСustomization}
    all_sprites = pygame.sprite.Group()
    buttonChooseLevel = ButtonWithText(all_sprites, (pygame.Color('#00BFFF'), pygame.Color('#87CEFA')), (200, 100), (300, 350), ('Выбрать уровень', 30, pygame.Color('White')))
    buttonСustomization = ButtonWithText(all_sprites, (pygame.Color('#00BFFF'), pygame.Color('#87CEFA')), (200, 100), (300, 500), ('Кастомизация', 30, pygame.Color('White')))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONUP:
                if buttonChooseLevel.isPressed():
                    pressedButton = 1
                    running = False
                elif buttonСustomization.isPressed():
                    pressedButton = 2
                    running = False

        screen.blit(BackgroundMenu, (0, 0))

        all_sprites.draw(screen)
        all_sprites.update()

        pygame.display.flip()

        clock.tick(FPS)

    buttonFunctions[pressedButton]()


def screenChooseLevel():
    all_sprites = pygame.sprite.Group()

    pass

def screenСustomization():
    numberOfShip = cursor.execute('SELECT Value FROM UserData WHERE Information = \'numberOfShip\'').fetchone()[0]
    nameOfShip = cursor.execute('SELECT Source FROM Sources WHERE Name = \'Ship\'').fetchone()[0]
    nameOfShip = nameOfShip[:-4] + str(numberOfShip) + nameOfShip[-4:]
    Ship = load_image(nameOfShip, -1)
    bigShip = pygame.transform.scale(Ship, (Ship.get_width() * 2, Ship.get_height() * 2))

    all_sprites = pygame.sprite.Group()
    buttonLeft = ButtonWithArrow(all_sprites, (pygame.Color('#00BFFF'), pygame.Color('#87CEFA')), (200, 100), (180, 400), (pygame.Color('White'), ((190, 10), (10, 50), (190, 90)), 0))
    buttonRight = ButtonWithArrow(all_sprites, (pygame.Color('#00BFFF'), pygame.Color('#87CEFA')), (200, 100), (420, 400), (pygame.Color('White'), ((10, 10), (190, 50), (10, 90)), 0))
    bigShipRect = bigShip.get_rect(center=(300, 600))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONUP:
                change = False
                if buttonLeft.isPressed():
                    numberOfShip = (numberOfShip + 12 - 1 - 1) % 12 + 1
                    change = True
                elif buttonRight.isPressed():
                    numberOfShip = (numberOfShip + 12 - 1 + 1) % 12 + 1
                    change = True
                if change:
                    cursor.execute(f'UPDATE UserData SET Value = {numberOfShip} WHERE Information = \'numberOfShip\'')
                    connection.commit()

                    nameOfShip = cursor.execute('SELECT Source FROM Sources WHERE Name = \'Ship\'').fetchone()[0]
                    nameOfShip = nameOfShip[:-4] + str(numberOfShip) + nameOfShip[-4:]
                    Ship = load_image(nameOfShip, -1)
                    bigShip = pygame.transform.scale(Ship, (Ship.get_width() * 2, Ship.get_height() * 2))


        screen.blit(BackgroundMenu, (0, 0))
        screen.blit(bigShip, bigShipRect)

        draw_text(screen, 'Выберите звездолёт', 50, 300, 200, pygame.Color('White'))

        all_sprites.draw(screen)
        all_sprites.update()

        pygame.display.flip()

        clock.tick(FPS)


class Button(pygame.sprite.Sprite):
    def __init__(self, spriteGroup, colors, size, posCenter):
        super().__init__(spriteGroup)
        self.colors = colors
        self.size = size
        self.posCenter = posCenter

        self.image = pygame.Surface(self.size)
        self.image.fill(self.colors[0])
        self.rect = self.image.get_rect()
        self.rect.centerx = self.posCenter[0]
        self.rect.centery = self.posCenter[1]

    def isPressed(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def update(self):
        if self.isPressed():
            self.image.fill(self.colors[1])
        else:
            self.image.fill(self.colors[0])
        self.draw()


class ButtonWithText(Button):
    def __init__(self, spriteGroup, colors, size, posCenter, textInfo):
        super().__init__(spriteGroup, colors, size, posCenter)
        self.textInfo = textInfo

        self.draw()

    def draw(self):
        draw_text(self.image, self.textInfo[0], self.textInfo[1], self.rect.width // 2, self.rect.height // 2 - self.textInfo[1] // 4, self.textInfo[2])

class ButtonWithArrow(Button):
    def __init__(self, spriteGroup, colors, size, posCenter, arrowInfo):
        super().__init__(spriteGroup, colors, size, posCenter)
        self.arrowInfo = arrowInfo

        self.draw()

    def draw(self):
        pygame.draw.polygon(self.image, *self.arrowInfo)


def main():
    #screenIntro()
    screenMainmenu()

main()

