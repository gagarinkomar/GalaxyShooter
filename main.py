import pygame
import os
import sys
import sqlite3
from random import random, randint, choice


WIDTH, HEIGHT = 600, 800
FPS = 60
FPSEffect = 30
FPSSpawnPlayer = 4

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

    regularExplosionList = []
    sonicExplosionList = []
    for i in range(1, 10):
        nameOfRegularExplosion = cursor.execute(f'SELECT Source FROM Sources WHERE Name = \'regularExplosion{i}\'').fetchone()[0]
        nameOfSonicExplosion = cursor.execute(f'SELECT Source FROM Sources WHERE Name = \'sonicExplosion{i}\'').fetchone()[0]
        regularExplosion = load_image(nameOfRegularExplosion, -1)
        sonicExplosion = load_image(nameOfSonicExplosion, -1)
        regularExplosionList.append(regularExplosion)
        sonicExplosionList.append(sonicExplosion)

    nameOfHeart = cursor.execute('SELECT Source FROM Sources WHERE Name = \'Heart\'').fetchone()[0]
    Heart = load_image(nameOfHeart, -1)
    return BackgroundMenu, BackgroundGame, Meteor1, Meteor2, spaceAstronaut1_1, spaceAstronaut1_2, spaceAstronaut2_1, spaceAstronaut2_2, spaceSatellite1, spaceSatellite2, Enemy1, Enemy2, Enemy3, Enemy4, Enemy5, Enemy6, laserBig1, laserMedium1, laserSmall1, laserBig2, laserMedium2, laserSmall2, laserBig3, laserMedium3, laserSmall3, regularExplosionList, sonicExplosionList, Heart


def load_level(name):
    fullname = os.path.join('data', 'levels', name)
    try:
        file = open(fullname, "r")
    except IOError as message:
        print('Cannot load level:', name)
        raise SystemExit(message)

    fileread = file.read().split('\n')
    file.close()
    result = []
    for line in fileread:
        if line.startswith('Boss'):
            result.append(['boss', int(line[4:])])
        else:
            resultline = ['enemys'] + list(map(lambda x: int(x[5:]), line.split(';')))
            result.append(resultline)
    return result


def load_levels():
    result = []
    for name in ['Level1', 'Level2', 'Level3', 'LevelCustom']:
        result.append(load_level(cursor.execute(f'SELECT Source FROM Sources WHERE Name = \'{name}\'').fetchone()[0]))
    return result


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
                    return ('Exit5', Level1)
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
    projectile_sprites = pygame.sprite.Group()
    explosion_sprites = pygame.sprite.Group()
    game_sprites = pygame.sprite.Group()
    player_sprite = pygame.sprite.Group()
    Background(all_sprites, background1_sprites, isFirst=True)
    Background(all_sprites, background1_sprites)
    player = Player((player_sprite, game_sprites), (all_sprites, projectile_sprites), (WIDTH // 2, 700), Ship, 1000, 3, 0, 0, 0, 2000, 2000, 3000)
    eventStatus = EventStatus([player.hideTime, player.spawnTime, player.waitTime, 0], 1)

    #тесты



    #конец
    numberOfWave = 0
    lastMeteor = 0
    running = True
    while running:
        eventStatus.update()
        print(player.lives)
        print(eventStatus.events[eventStatus.event])
        if player.lives == 0 and eventStatus.isSpawning():
            pass
            return  # game over -
        elif len(game_sprites) == 1 and eventStatus.isPlaying():
            if numberOfWave == len(level):
                pass  # game over +
                return 'Exit4'
            if level[numberOfWave][0] == 'enemys':
                for pos, enemy in enumerate(level[numberOfWave][1:]):
                    dataEnemy = {1: (settingsEnemy1, Enemy1), 2: (settingsEnemy2, Enemy2), 3: (settingsEnemy3, Enemy3), 4: (settingsEnemy4, Enemy4), 5: (settingsEnemy5, Enemy5), 6: (settingsEnemy6, Enemy6)}[enemy]
                    Enemy((all_sprites, game_sprites), (all_sprites, projectile_sprites), dataEnemy[0], (100 * (pos + 1), -HEIGHT + 100 * (pos + 1)), dataEnemy[1])
            else:
                pass #boss
            numberOfWave += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)

        background1_sprites.draw(screen)
        background2_sprites.draw(screen)
        projectile_sprites.draw(screen)
        explosion_sprites.draw(screen)
        game_sprites.draw(screen)
        for i in range(1, player.lives + 1):
            screen.blit(Heart, (WIDTH - (50 * i + Heart.get_rect().w // 2), 50 - Heart.get_rect().h // 2))


        for sprite in game_sprites:
            if pygame.sprite.collide_mask(player, sprite) and type(sprite) != Player:
                player.hpnow -= 500
                sprite.hpnow -= 500
            for explosionSettings in sprite.checkDamage(projectile_sprites):
                Explosion((all_sprites, explosion_sprites), (explosionSettings[0] - camera.dx, explosionSettings[1]), explosionSettings[2], sonicExplosionList)

        all_sprites.update()
        player_sprite.update()

        if len(game_sprites) == 1 and eventStatus.isPlaying():
            eventStatus.changeEvent()

        for sprite in game_sprites:
            if type(sprite) == Player and sprite.isDied:
                sprite.isDied = False
                Explosion((all_sprites, explosion_sprites), (sprite.rect.centerx - camera.dx, sprite.rect.centery), round(max(sprite.rect.size) * 1.5), regularExplosionList)
                numberOfWave -= 1
                for sprite in game_sprites:
                    if type(sprite) != Player:
                        sprite.kill()
                projectile_sprites.empty()
                eventStatus.changeEvent()
            elif sprite.lives == 0:
                Explosion((all_sprites, explosion_sprites), (sprite.rect.centerx - camera.dx, sprite.rect.centery), round(max(sprite.rect.size) * 1.5), regularExplosionList)
                sprite.kill()






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


class EventStatus():
    def __init__(self, times, event):
        self.events = ['Hiding', 'Spawning', 'Waiting', 'Playing']
        self.times = times
        self.event = event
        self.startEvent = pygame.time.get_ticks()

    def isHiding(self):
        return self.events[self.event] == 'Hiding'

    def isSpawning(self):
        return self.events[self.event] == 'Spawning'

    def isWaiting(self):
        return self.events[self.event] == 'Waiting'

    def isPlaying(self):
        return self.events[self.event] == 'Playing'

    def update(self):
        if not self.isPlaying() and pygame.time.get_ticks() - self.startEvent > self.times[self.event]:
            self.changeEvent()

    def changeEvent(self):
        self.event = (self.event + 1) % 4
        self.startEvent = pygame.time.get_ticks()


class GameObject(pygame.sprite.Sprite):
    def __init__(self, spriteGroups, projectileGroups, posCenter, image, hp, lives, damage, movingX, movingY):
        super().__init__(*spriteGroups)
        self.projectileGroups = projectileGroups
        self.hp = hp
        self.hpnow = self.hp
        self.lives = lives
        self.damage = damage
        self.movingX = movingX
        self.movingY = movingY

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = posCenter
        self.mask = pygame.mask.from_surface(self.image)
        self.posX = self.rect.x

    def checkDamage(self, projectileSprites):
        result = []
        for sprite in projectileSprites:
            if pygame.sprite.collide_mask(self,
                                          sprite) and sprite.type != type(
                    self):
                result.append(sprite.damageSprite(self))
        return result


class Player(GameObject):
    def __init__(self, spriteGroups, projectileGroups, posCenter, image, hp, lives, damage, movingX, movingY, hideTime, spawnTime, waitTime):
        super().__init__(spriteGroups, projectileGroups, posCenter, image, hp, lives, damage, movingX, movingY)
        self.images = (self.image, pygame.Surface(Meteor1.get_size(), pygame.SRCALPHA))
        self.numberImage = 0
        self.hideTime = hideTime
        self.spawnTime = spawnTime
        self.waitTime = waitTime
        self.died = pygame.time.get_ticks() - self.hideTime
        self.lastChangeImage = pygame.time.get_ticks()
        self.isDied = False

    def update(self):
        if self.hpnow <= 0:
            self.lives -= 1
            self.hpnow = self.hp
            self.died = pygame.time.get_ticks()
            self.isDied = True
        self.movingX = 0
        self.movingY = 0
        if pygame.time.get_ticks() - self.died <= self.hideTime:
            self.image = self.images[1]
        else:
            if pygame.time.get_ticks() - self.lastChangeImage > 1000 / FPSSpawnPlayer:
                if pygame.time.get_ticks() - self.died <= self.hideTime + self.spawnTime:
                    self.lastChangeImage = pygame.time.get_ticks()
                    self.image = self.images[self.numberImage]
                    self.numberImage = (self.numberImage + 1) % 2
                else:
                    self.image = self.images[0]
            keystate = pygame.key.get_pressed()
            if keystate[pygame.K_a]:
                self.movingX = -10
            if keystate[pygame.K_d]:
                self.movingX = 10
            if keystate[pygame.K_w]:
                self.movingY = -10
            if keystate[pygame.K_s]:
                self.movingY = 10


class Enemy(GameObject):
    def __init__(self, spriteGroups, projectileGroups, settings, posCenter, image):
        super().__init__(spriteGroups, projectileGroups, posCenter, image, settings[0], 1, settings[1], settings[4], settings[5])
        self.countGuns = settings[2]
        self.speedShooting = settings[3]

        if settings[6] == 'small':
            self.imageProjectile = choice([laserSmall1, laserSmall2, laserSmall3])
        elif settings[6] == 'medium':
            self.imageProjectile = choice([laserMedium1, laserMedium2, laserMedium3])
        else:
            self.imageProjectile = choice([laserBig1, laserBig2, laserBig3])

        self.lastProjectile = pygame.time.get_ticks()

    def update(self):
        if self.hpnow <= 0:
            self.lives -= 1
            self.hpnow = self.hp
        if (self.movingY < 0 and self.rect.centery + self.movingY < 50) or (self.movingY > 0 and self.rect.centery + self.movingY > HEIGHT // 2):
            self.movingY = -self.movingY
        self.rect.y += self.movingY
        if (self.posX + self.rect.w // 2 + self.movingX < WIDTH // 2 - BackgroundGame.get_rect().w // 2 + 50) or (self.posX + self.rect.w // 2 + self.movingX > WIDTH + BackgroundGame.get_rect().w // 2 - WIDTH // 2 - 50):
            self.movingX = -self.movingX
        self.posX += self.movingX

        if pygame.time.get_ticks() - self.lastProjectile > self.speedShooting:
            self.lastProjectile = pygame.time.get_ticks()
            if self.countGuns == 1:
                Projectile(self, self.rect.w // 2, self.rect.bottom)
            else:
                Projectile(self, self.rect.w // 3, self.rect.bottom)
                Projectile(self, self.rect.w // 3 * 2, self.rect.bottom)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, spriteGroups, posCenter, size, ExplosionList):
        super().__init__(*spriteGroups)

        self.ExplosionList = [pygame.transform.scale(explosion, (size, size),) for explosion in ExplosionList]
        self.posCenter = posCenter
        self.imageNumber = 1
        self.image = self.ExplosionList[self.imageNumber - 1]
        self.rect = self.image.get_rect()
        self.rect.center = self.posCenter
        self.posX = self.rect.x
        self.lastUpdate = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self.lastUpdate > 1000 / FPSEffect:
            self.lastUpdate = pygame.time.get_ticks()
            self.imageNumber += 1
            if self.imageNumber == len(self.ExplosionList):
                self.kill()
            else:
                self.image = self.ExplosionList[self.imageNumber - 1]
                self.rect = self.image.get_rect()
                self.rect.center = self.posCenter
                self.posX = self.rect.x


class Projectile(pygame.sprite.Sprite):
    def __init__(self, target, posShiftX, posCenterY):
        super().__init__(*target.projectileGroups)

        self.type = type(target)
        self.damage = target.damage
        self.movingY = 5
        self.create = pygame.time.get_ticks()
        self.image = target.imageProjectile
        self.rect = self.image.get_rect()
        self.rect.centerx = target.posX + posShiftX
        self.rect.centery = posCenterY
        self.mask = pygame.mask.from_surface(self.image)
        self.posX = self.rect.x

    def damageSprite(self, sprite):
        sprite.hpnow -= self.damage
        self.kill()
        return self.rect.center + (round(max(self.rect.size) * 1.5),)


    def update(self):
        self.rect.y += self.movingY
        if self.rect.top >= HEIGHT:
            self.kill()


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
        target.rect.centery = max(200, target.rect.centery)
        target.rect.centery = min(HEIGHT - 50, target.rect.centery)


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
            return

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
    Level1, Level2, Level3, LevelCustom = load_levels()
    BackgroundMenu, BackgroundGame, Meteor1, Meteor2, spaceAstronaut1_1, spaceAstronaut1_2, spaceAstronaut2_1, spaceAstronaut2_2, spaceSatellite1, spaceSatellite2, Enemy1, Enemy2, Enemy3, Enemy4, Enemy5, Enemy6, laserBig1, laserMedium1, laserSmall1, laserBig2, laserMedium2, laserSmall2, laserBig3, laserMedium3, laserSmall3, regularExplosionList, sonicExplosionList, Heart = load_graphics()

    resultDict = {'Exit1': screenIntro, 'Exit2': screenMainmenu, 'Exit3': screenСustomization, 'Exit4': screenChooseLevel, 'Exit5': screenGame}
    result = ('Exit5', Level1)
    while result:
        if type(result) == tuple:
            result = resultDict[result[0]](result[1])
        else:
            result = resultDict[result]()
    connection.close()