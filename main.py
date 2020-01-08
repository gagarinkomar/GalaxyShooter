import pygame
import os
import sys
import sqlite3
from random import random, randint, choice


WIDTH, HEIGHT = 600, 800
FPS = 60

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('GalaxyShooter')
clock = pygame.time.Clock()
connection = sqlite3.connect(os.path.join('data', 'Config.db'))
cursor = connection.cursor()

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

def load_ship():
    numberOfShip = cursor.execute('SELECT Value FROM UserData WHERE Information = \'numberOfShip\'').fetchone()[0]
    nameOfShip = cursor.execute('SELECT Source FROM Sources WHERE Name = \'Ship\'').fetchone()[0]
    nameOfShip = nameOfShip[:-4] + str(numberOfShip) + nameOfShip[-4:]
    Ship = load_image(nameOfShip, -1)
    bigShip = pygame.transform.scale(Ship, (Ship.get_width() * 2, Ship.get_height() * 2))
    return Ship, bigShip


def load_graphics():
    nameOfBackgroundMenu = cursor.execute('SELECT Source FROM Sources WHERE Name = \'BackgroundMenu\'').fetchone()[0]
    BackgroundMenu = load_image(nameOfBackgroundMenu)
    nameOfBackgroundGame = cursor.execute('SELECT Source FROM Sources WHERE Name = \'BackgroundGame\'').fetchone()[0]
    BackgroundGame = load_image(nameOfBackgroundGame)
    nameOfMeteor1 = cursor.execute('SELECT Source FROM Sources WHERE Name = \'Meteor1\'').fetchone()[0]
    Meteor1 = load_image(nameOfMeteor1, -1)
    nameOfMeteor2 = cursor.execute('SELECT Source FROM Sources WHERE Name = \'Meteor2\'').fetchone()[0]
    Meteor2 = load_image(nameOfMeteor2, -1)
    nameOfspaceAstronaut1_1 = cursor.execute('SELECT Source FROM Sources WHERE Name = \'spaceAstronaut1_1\'').fetchone()[0]
    spaceAstronaut1_1 = load_image(nameOfspaceAstronaut1_1, -1)
    nameOfspaceAstronaut1_2 = cursor.execute('SELECT Source FROM Sources WHERE Name = \'spaceAstronaut1_2\'').fetchone()[0]
    spaceAstronaut1_2 = load_image(nameOfspaceAstronaut1_2, -1)
    nameOfspaceAstronaut2_1 = cursor.execute('SELECT Source FROM Sources WHERE Name = \'spaceAstronaut2_1\'').fetchone()[0]
    spaceAstronaut2_1 = load_image(nameOfspaceAstronaut2_1, -1)
    nameOfspaceAstronaut2_2 = cursor.execute('SELECT Source FROM Sources WHERE Name = \'spaceAstronaut2_2\'').fetchone()[0]
    spaceAstronaut2_2 = load_image(nameOfspaceAstronaut2_2, -1)
    nameOfspaceSatellite1 = cursor.execute('SELECT Source FROM Sources WHERE Name = \'spaceSatellite1\'').fetchone()[0]
    spaceSatellite1 = pygame.transform.scale(load_image(nameOfspaceSatellite1, -1), (110, 44))
    nameOfspaceSatellite2 = cursor.execute('SELECT Source FROM Sources WHERE Name = \'spaceSatellite2\'').fetchone()[0]
    spaceSatellite2 = pygame.transform.scale(load_image(nameOfspaceSatellite2, -1), (110, 44))
    # Выше потом тоже сделаю через цикл
    enemys = []
    for i in range(1, 7):
        nameOfEnemy = cursor.execute(f'SELECT Source FROM Sources WHERE Name = \'Enemy{i}\'').fetchone()[0]
        enemy = load_image(nameOfEnemy, -1)
        enemy = pygame.transform.scale(enemy, (int(enemy.get_rect().w // 1.25), int(enemy.get_rect().h // 1.25)))
        enemys.append(enemy)
    Enemy1, Enemy2, Enemy3, Enemy4, Enemy5, Enemy6 = enemys
    lasers = []
    for i in range(1, 4):
        for laserType in(['laserBig', 'laserMedium', 'laserSmall']):
            nameOflaser = cursor.execute(f'SELECT Source FROM Sources WHERE Name = \'{laserType}{i}\'').fetchone()[0]
            laser = load_image(nameOflaser, -1)
            lasers.append(laser)
    laserBig1, laserMedium1, laserSmall1, laserBig2, laserMedium2, laserSmall2, laserBig3, laserMedium3, laserSmall3 = lasers
    return BackgroundMenu, BackgroundGame, Meteor1, Meteor2, spaceAstronaut1_1, spaceAstronaut1_2, spaceAstronaut2_1, spaceAstronaut2_2, spaceSatellite1, spaceSatellite2, Enemy1, Enemy2, Enemy3, Enemy4, Enemy5, Enemy6, laserBig1, laserMedium1, laserSmall1, laserBig2, laserMedium2, laserSmall2, laserBig3, laserMedium3, laserSmall3


def load_enemySettings():
    settingsEnemy = []
    complexity = cursor.execute('SELECT Value FROM UserData WHERE Information = \'complexity\'').fetchone()[0]
    for i in range(1, 7):
        settingEnemy = cursor.execute(f'SELECT nowSettings FROM enemySettings WHERE Name = \'Enemy{i}\'').fetchone()[0].split(', ')
        settingEnemy = list(map(int, settingEnemy[:-1])) + [settingEnemy[-1]]
        settingEnemy = [settingEnemy[0] * (1 + 0.2 * complexity)] + [settingEnemy[1] * (1 + 0.2 * complexity)] + settingEnemy[2:]
        settingsEnemy.append(settingEnemy)
    return settingsEnemy


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
    return 'Exit2'


def screenMainmenu():
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
                    return 'Exit4'
                elif buttonСustomization.isPressed():
                    return 'Exit3'

        screen.blit(BackgroundMenu, (0, 0))

        all_sprites.draw(screen)
        all_sprites.update()

        pygame.display.flip()

        clock.tick(FPS)


def screenChooseLevel():
    all_sprites = pygame.sprite.Group()
    buttonLevel1 = ButtonWithText(all_sprites, (pygame.Color('#00BFFF'), pygame.Color('#87CEFA')), (200, 50), (300, 350), ('Уровень 1', 30, pygame.Color('White')))
    buttonLevel2 = ButtonWithText(all_sprites, (pygame.Color('#00BFFF'), pygame.Color('#87CEFA')), (200, 50), (300, 410), ('Уровень 2', 30, pygame.Color('White')))
    buttonLevel3 = ButtonWithText(all_sprites, (pygame.Color('#00BFFF'), pygame.Color('#87CEFA')), (200, 50), (300, 470), ('Уровень 3', 30, pygame.Color('White')))
    buttonLevel4 = ButtonWithText(all_sprites, (pygame.Color('#00BFFF'), pygame.Color('#87CEFA')), (200, 50), (300, 530), ('Уровень 4', 30, pygame.Color('White')))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONUP:
                if buttonLevel1.isPressed():
                    return ('Exit5', 123)
                elif buttonLevel2.isPressed():
                    pass
                elif buttonLevel3.isPressed():
                    pass
                elif buttonLevel4.isPressed():
                    pass

        screen.blit(BackgroundMenu, (0, 0))

        draw_text(screen, 'Выберите уровень', 50, 300, 200, pygame.Color('White'))

        all_sprites.draw(screen)
        all_sprites.update()

        pygame.display.flip()

        clock.tick(FPS)

def screenGame(level):
    settingsEnemy1, settingsEnemy2, settingsEnemy3, settingsEnemy4, settingsEnemy5, settingsEnemy6 = load_enemySettings()
    Ship = load_ship()[0]

    camera = Camera()
    all_sprites = pygame.sprite.Group()
    background1_sprites = pygame.sprite.Group()
    background2_sprites = pygame.sprite.Group()
    player_sprite = pygame.sprite.Group()
    game_sprites = pygame.sprite.Group()
    Background(all_sprites, background1_sprites, isFirst=True)
    Background(all_sprites, background1_sprites)
    player = Player(player_sprite, centerX=WIDTH // 2, centerY=700, image=Ship)

    #тесты
    Enemy(all_sprites, game_sprites, settings=settingsEnemy1, image=Enemy1, posCenterX=300)

    #конец

    lastMeteor = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONUP:
                pass

        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)

        background1_sprites.draw(screen)
        background2_sprites.draw(screen)
        game_sprites.draw(screen)
        player_sprite.draw(screen)
        all_sprites.update()
        player_sprite.update()

        if random() * 1000 > 995 and pygame.time.get_ticks() - lastMeteor > 5000:
            lastMeteor = pygame.time.get_ticks()
            if random() * 100 > 50:
                MeteorWithAstronaut(all_sprites, background2_sprites, posCenterX=randint(-200 + camera.dx + 50, 800 + camera.dx - 50))
            else:
                Satellite(all_sprites, background2_sprites, posCenterX=randint(-200 + camera.dx + 50, 800 + camera.dx - 50))

        if len(background1_sprites) == 1:
            Background(all_sprites, background1_sprites)

        pygame.display.flip()

        clock.tick(FPS)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, *spriteGroups, settings, image, posCenterX):
        super().__init__(*spriteGroups)

        self.spriteGroups = spriteGroups
        self.hp = settings[0]
        self.damage = settings[1]
        self.countGuns = settings[2]
        self.speedShooting = settings[3]
        self.movingX = settings[4]
        self.movingY = settings[5]

        if settings[6] == 'small':
            self.imageLaser = choice([laserSmall1, laserSmall2, laserSmall3])
        elif settings[6] == 'medium':
            self.imageLaser = choice([laserMedium1, laserMedium2, laserMedium3])
        else:
            self.imageLaser = choice([laserBig1, laserBig2, laserBig3])

        self.lastLaser = pygame.time.get_ticks()
        self.image = image
        self.rect = self.image.get_rect().move(0, -100)
        self.rect.centerx = posCenterX
        self.posX = self.rect.x

    def update(self):
        if (self.movingY < 0 and self.rect.centery + self.movingY < 50) or (self.movingY > 0 and self.rect.centery + self.movingY > HEIGHT // 2):
            self.movingY = -self.movingY
        self.rect.y += self.movingY
        if (self.posX + self.rect.w // 2 + self.movingX < WIDTH // 2 - BackgroundGame.get_rect().w // 2 + 50) or (self.posX + self.rect.w // 2 + self.movingX > WIDTH + BackgroundGame.get_rect().w // 2 - WIDTH // 2 - 50):
            print(self.posX + self.rect.w // 2 + self.movingX,  WIDTH // 2 - BackgroundGame.get_rect().w // 2 + 50, self.posX + self.rect.w // 2 + self.movingX, BackgroundGame.get_rect().w // 2 - WIDTH // 2 - 50)
            self.movingX = -self.movingX
        self.posX += self.movingX

        if pygame.time.get_ticks() - self.lastLaser > self.speedShooting:
            self.lastLaser = pygame.time.get_ticks()
            if self.countGuns == 1:
                Laser(self, self.rect.w // 2, self.rect.bottom)
            else:
                Laser(self, self.rect.w // 3, self.rect.bottom)
                Laser(self, self.rect.w // 3 * 2, self.rect.bottom)


class Laser(pygame.sprite.Sprite):
    def __init__(self, enemy, posShiftX, posCenterY):
        super().__init__(*enemy.groups())

        self.damage = enemy.damage
        self.movingY = 5
        self.image = enemy.imageLaser
        self.rect = self.image.get_rect()
        self.rect.centerx = enemy.posX + posShiftX
        self.rect.centery = posCenterY
        self.posX = self.rect.x

    def update(self):
        self.rect.y += self.movingY


class Background(pygame.sprite.Sprite):
    def __init__(self, *spriteGroups, isFirst=False):
        super().__init__(*spriteGroups)
        self.posX = WIDTH // 2 - BackgroundGame.get_rect().w // 2

        self.image = BackgroundGame
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        if isFirst:
            self.rect.bottom = HEIGHT
        else:
            self.rect.bottom = HEIGHT - self.image.get_rect().height

    def update(self):
        self.rect.y += 2
        if self.rect.top >= HEIGHT:
            self.kill()


class Camera:
    def __init__(self):
        self.dx = 0

    def apply(self, object):
        object.rect.x = object.posX + self.dx

    def isCameraMoving(self, target):
        if target.movingX > 0:
            if WIDTH // 2 - BackgroundGame.get_rect().w // 2 > self.dx - target.movingX:
                return False
            if self.dx - target.movingX - target.rect.centerx > -(WIDTH - BackgroundGame.get_rect().w // 2):
                return False
            return True

        else:
            if self.dx - target.movingX > BackgroundGame.get_rect().w // 2 - WIDTH // 2:
                return False
            if target.rect.centerx - (self.dx - target.movingX) > BackgroundGame.get_rect().w // 2:
                return False
            return True


    def tryCameraMoving(self, target):
        if self.isCameraMoving(target):
            self.dx -= target.movingX
            return True
        else:
            return False

    def update(self, target):
        if not self.tryCameraMoving(target):
            target.rect.x += target.movingX
        target.rect.y += target.movingY
        target.rect.centerx = max(50, target.rect.centerx)
        target.rect.centerx = min(WIDTH - 50, target.rect.centerx)
        target.rect.centery = max(50, target.rect.centery)
        target.rect.centery = min(HEIGHT - 50, target.rect.centery)


class Player(pygame.sprite.Sprite):
    def __init__(self, *spriteGroup, centerX, centerY, image):
        super().__init__(*spriteGroup)
        self.movingX = 0
        self.movingY = 0

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.centerx = centerX
        self.rect.centery = centerY

    def update(self):
        self.movingX = 0
        self.movingY = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_a]:
            self.movingX = -10
        if keystate[pygame.K_d]:
            self.movingX = 10
        if keystate[pygame.K_w]:
            self.movingY = -10
        if keystate[pygame.K_s]:
            self.movingY = 10


class MeteorWithAstronaut(pygame.sprite.Sprite):
    def __init__(self, *spriteGroups, posCenterX):
        super().__init__(*spriteGroups)

        self.image = pygame.Surface(Meteor1.get_size(), pygame.SRCALPHA)
        self.imageMeteor = choice((Meteor1, Meteor2))
        numberOfAstronaut = choice((1, 2))
        self.isMirrored = False
        if random() * 100 > 50:
            self.isMirrored = True
            if numberOfAstronaut == 1:
                self.imagesAstronaut = [pygame.transform.flip(spaceAstronaut1_1, True, False), pygame.transform.flip(spaceAstronaut1_2, True, False)]
            else:
                self.imagesAstronaut = [pygame.transform.flip(spaceAstronaut2_1, True, False), pygame.transform.flip(spaceAstronaut2_2, True, False)]
        else:
            if numberOfAstronaut == 1:
                self.imagesAstronaut = [spaceAstronaut1_1, spaceAstronaut1_2]
            else:
                self.imagesAstronaut = [spaceAstronaut2_1, spaceAstronaut2_2]
        self.rect = self.image.get_rect().move(0, -100)
        self.rect.centerx = posCenterX
        self.posX = self.rect.x
        self.imageAstronaut = self.imagesAstronaut[1]

        astronautRect = self.imageAstronaut.get_rect()
        astronautRect.center = self.image.get_rect().center
        if self.isMirrored:
            self.limit = astronautRect.right
        else:
            self.limit = astronautRect.left
        self.image.blit(self.imageMeteor, (0, 0))
        self.image.blit(self.imageAstronaut, astronautRect)
        self.lastUpdate = pygame.time.get_ticks()

    def update(self):
        self.rect.y += 2
        if self.rect.y > HEIGHT:
            self.kill()

        if pygame.time.get_ticks() - self.lastUpdate > 1000:
            self.lastUpdate = pygame.time.get_ticks()
            self.imageAstronaut = list(set(self.imagesAstronaut) - {self.imageAstronaut})[0]
        self.image.blit(self.imageMeteor, (0, 0))
        astronautRect = self.imageAstronaut.get_rect()
        astronautRect.centery = self.image.get_rect().centery
        if self.isMirrored:
            astronautRect.right = self.limit
        else:
            astronautRect.left = self.limit
        self.image.blit(self.imageAstronaut, astronautRect)


class Satellite(pygame.sprite.Sprite):
    def __init__(self, *spriteGroups, posCenterX):
        super().__init__(*spriteGroups)

        self.image = choice((spaceSatellite1, spaceSatellite2))
        self.rect = self.image.get_rect().move(0, 100)
        self.posX = self.rect.x

    def update(self):
        self.rect.y += 2
        if self.rect.y > HEIGHT:
            self.kill()


def screenСustomization():
    bigShip = load_ship()[1]

    all_sprites = pygame.sprite.Group()
    buttonLeft = ButtonWithArrow(all_sprites, (pygame.Color('#00BFFF'), pygame.Color('#87CEFA'), pygame.Color('White')), (200, 100), (180, 400), (((90, 10), (10, 50), (90, 90)), 0), ((90, 35, 80, 30), 0))
    buttonRight = ButtonWithArrow(all_sprites, (pygame.Color('#00BFFF'), pygame.Color('#87CEFA'), pygame.Color('White')), (200, 100), (420, 400), (((110, 10), (190, 50), (110, 90)), 0), ((30, 35, 80, 30), 0))
    buttonReturn = ButtonWithArrow(all_sprites, (pygame.Color('Black'), pygame.Color('Grey'), pygame.Color('Red')), (100, 100), (540, 740), (((90, 10), (10, 50), (90, 90)), 0), None)
    bigShipRect = bigShip.get_rect(center=(300, 600))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONUP:
                change = False
                numberOfShip = cursor.execute('SELECT Value FROM UserData WHERE Information = \'numberOfShip\'').fetchone()[0]
                if buttonLeft.isPressed():
                    numberOfShip = (numberOfShip + 12 - 1 - 1) % 12 + 1
                    change = True
                elif buttonRight.isPressed():
                    numberOfShip = (numberOfShip + 12 - 1 + 1) % 12 + 1
                    change = True
                elif buttonReturn.isPressed():
                    return 'Exit2'
                if change:
                    cursor.execute(f'UPDATE UserData SET Value = {numberOfShip} WHERE Information = \'numberOfShip\'')
                    connection.commit()
                    bigShip = load_ship()[1]
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
    def __init__(self, spriteGroup, colors, size, posCenter, polygonInfo, rectInfo):
        super().__init__(spriteGroup, colors, size, posCenter)
        self.polygonInfo = polygonInfo
        self.rectInfo = rectInfo

        self.draw()

    def draw(self):
        if self.polygonInfo:
            pygame.draw.polygon(self.image, self.colors[2], *self.polygonInfo)
        if self.rectInfo:
            pygame.draw.rect(self.image, self.colors[2],  *self.rectInfo)


if __name__ == '__main__':
    BackgroundMenu, BackgroundGame, Meteor1, Meteor2, spaceAstronaut1_1, spaceAstronaut1_2, spaceAstronaut2_1, spaceAstronaut2_2, spaceSatellite1, spaceSatellite2, Enemy1, Enemy2, Enemy3, Enemy4, Enemy5, Enemy6, laserBig1, laserMedium1, laserSmall1, laserBig2, laserMedium2, laserSmall2, laserBig3, laserMedium3, laserSmall3 = load_graphics()

    resultDict = {'Exit1': screenIntro, 'Exit2': screenMainmenu, 'Exit3': screenСustomization, 'Exit4': screenChooseLevel, 'Exit5': screenGame}
    result = ('Exit5', 123)
    while result:
        if type(result) is tuple:
            result = resultDict[result[0]](result[1])
        else:
            result = resultDict[result]()
    connection.close()