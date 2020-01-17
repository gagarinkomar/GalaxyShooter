import pygame
import os
import sys
import sqlite3
from random import random, randint, choice


WIDTH, HEIGHT = 600, 800
FPS = 60
FPS2 = 30
FPSSpawnPlayer = 4

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('GalaxyShooter')
clock = pygame.time.Clock()
connection = sqlite3.connect(os.path.join('data', 'Config.db'))
cursor = connection.cursor()

def load_image(name, color_key=None):  # Загрузка картинки
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


def load_sound(name):  # Загрузка звука
    fullname = os.path.join('data', 'sounds', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error as message:
        print('Cannot load sound:', name)
        raise SystemExit(message)
    return sound


def load_sounds():  # Загрузка всех звуков
    result = [load_sound(cursor.execute(f'SELECT Source FROM Sources WHERE Name = \'{name}\'').fetchone()[0]) for name in ['spawnEnemy', 'spawnPlayer', 'shieldDown', 'shieldUp', 'shieldUp', 'rocketShoot', 'playerDie', 'pickupBonus', 'laserShoot', 'explosionSonic', 'explosionRegular', 'enemyDie', 'clickButton']]
    music = cursor.execute('SELECT Source FROM Sources WHERE Name = \'music\'').fetchone()[0]
    try:
        pygame.mixer.music.load(os.path.join('data', 'sounds', music))
    except pygame.error as message:
        print('Cannot load music:', music)
        raise SystemExit(message)
    return result


def load_ship():  # Загрузка корабля игрока
    numberOfShip = cursor.execute('SELECT Value FROM UserData WHERE Information = \'numberOfShip\'').fetchone()[0]
    nameOfShip = cursor.execute('SELECT Source FROM Sources WHERE Name = \'Ship\'').fetchone()[0]
    nameOfShip = nameOfShip[:-4] + str(numberOfShip) + nameOfShip[-4:]
    Ship = load_image(nameOfShip, -1)
    bigShip = pygame.transform.scale(Ship, (Ship.get_width() * 2, Ship.get_height() * 2))
    return Ship, bigShip


def load_graphics():  # Загрузка всех картинок
    images = [load_image(cursor.execute(f'SELECT Source FROM Sources WHERE Name = \'{name}\'').fetchone()[0], -1) for name in ['Meteor1', 'Meteor2', 'spaceAstronaut1_1', 'spaceAstronaut1_2', 'spaceAstronaut2_1', 'spaceAstronaut2_2', 'spaceSatellite1', 'spaceSatellite2', 'Shield', 'Heart']]
    images[6] = pygame.transform.scale(images[6], (110, 44))
    images[7] = pygame.transform.scale(images[7], (110, 44))
    backgrounds = [load_image(cursor.execute(f'SELECT Source FROM Sources WHERE Name = \'{name}\'').fetchone()[0]) for name in ['BackgroundMenu1', 'BackgroundMenu2', 'BackgroundGame']]
    enemys = []
    for i in range(1, 7):
        nameOfEnemy = cursor.execute(f'SELECT Source FROM Sources WHERE Name = \'Enemy{i}\'').fetchone()[0]
        enemy = load_image(nameOfEnemy, -1)
        enemy = pygame.transform.scale(enemy, (int(enemy.get_rect().w // 1.25), int(enemy.get_rect().h // 1.25)))
        enemys.append(enemy)
    lasers = []
    for i in range(1, 4):
        for laserType in(['laserBig', 'laserMedium', 'laserSmall']):
            nameOflaser = cursor.execute(f'SELECT Source FROM Sources WHERE Name = \'{laserType}{i}\'').fetchone()[0]
            lasers.append(load_image(nameOflaser, -1))
    regularExplosionList = [load_image(cursor.execute(f'SELECT Source FROM Sources WHERE Name = \'regularExplosion{i}\'').fetchone()[0], -1) for i in range(1, 10)]
    sonicExplosionList = [load_image(cursor.execute(f'SELECT Source FROM Sources WHERE Name = \'sonicExplosion{i}\'').fetchone()[0], -1) for i in range(1, 10)]
    spaceMissileList = [load_image(cursor.execute(f'SELECT Source FROM Sources WHERE Name = \'spaceMissile{i}\'').fetchone()[0], -1) for i in range(1, 4)]
    bonuses = [load_image(cursor.execute(f'SELECT Source FROM Sources WHERE Name = \'{name}\'').fetchone()[0], -1) for name in ['playerShield', 'playerSpeed', 'playerCountGuns', 'playerSpeedShooting']]
    return backgrounds[0], backgrounds[1],  backgrounds[2], images[0], images[1], images[2], images[3], images[4], images[5], images[6], images[7], images[8], images[9], enemys, lasers, regularExplosionList, sonicExplosionList, spaceMissileList, bonuses


def load_level(name):  # Загрузка уровня
    fullname = cursor.execute(f'SELECT Source FROM Sources WHERE Name = \'{name}\'').fetchone()[0]
    fullname = os.path.join('data', 'levels', fullname)
    try:
        file = open(fullname, "r")
    except IOError as message:
        print('Cannot load level:', name)
        raise SystemExit(message)

    fileread = file.read().split('\n')
    file.close()
    result = [name] + [list(map(lambda x: int(x[5:]), line.split(';'))) for line in fileread]
    return result


def load_levels():  # Загрузка всех уровней
    result = [load_level(name) for name in ['Level1', 'Level2', 'Level3', 'Level4', 'Level5', 'Level6', 'Level7', 'Level8', 'LevelCustom']]
    return result


def load_enemySettings():  # Загрузка настроек для врагов
    settingsEnemy = []
    complexity = cursor.execute('SELECT Value FROM UserData WHERE Information = \'complexity\'').fetchone()[0]
    for i in range(1, 7):
        settingEnemy = cursor.execute(f'SELECT nowSettings FROM enemySettings WHERE Name = \'Enemy{i}\'').fetchone()[0].split(', ')
        settingEnemy = list(map(int, settingEnemy[:-1])) + [settingEnemy[-1]]
        settingEnemy = [settingEnemy[0] * (1 + 0.2 * complexity)] + [settingEnemy[1] * (1 + 0.2 * complexity)] + settingEnemy[2:]
        settingsEnemy.append(settingEnemy)
    return settingsEnemy


def terminate():  # Экстренное завершение
    pygame.quit()
    connection.close()
    sys.exit()


def draw_text(screen, text, size, x, y, color):  # Нарисовать текст
    font = pygame.font.Font(None, size)
    string_rendered = font.render(text, 1, color)
    intro_rect = string_rendered.get_rect()
    intro_rect.midtop = (x, y)
    screen.blit(string_rendered, intro_rect)


def screenIntro():  # Окно заставки
    color = pygame.Color('White')
    hsv = color.hsva
    color.hsva = (hsv[0], hsv[1], 0, hsv[3])
    valuechanging = 1

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYUP or event.type == pygame.MOUSEBUTTONUP:
                return 'Exit2'

        screen.fill(pygame.Color('Black'))
        draw_text(screen, 'GK', 50, WIDTH // 2, HEIGHT // 2 - 100, color)
        draw_text(screen, 'Production', 50, WIDTH // 2, HEIGHT // 2 - 50,
                  color)
        draw_text(screen, 'Present', 50, WIDTH // 2, HEIGHT // 2, color)

        hsv = color.hsva

        if valuechanging == 1 and (hsv[2] + valuechanging) > 60:
            valuechanging = -1
        elif valuechanging == -1 and (hsv[2] + valuechanging) < 1:
            return 'Exit2'

        color.hsva = (hsv[0], hsv[1], hsv[2] + valuechanging, hsv[3])

        pygame.display.flip()

        clock.tick(20)


def screenEndGame(result, countWaves):  # Окно после окончания игры
    pygame.mixer.music.stop()
    color = pygame.Color('White')
    posY1 = -150
    posY2 = HEIGHT - 100
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYUP or event.type == pygame.MOUSEBUTTONUP:
                pygame.mouse.set_visible(1)
                return 'Exit4'

        screen.fill(pygame.Color('Black'))
        draw_text(screen, 'Уровень', 50, WIDTH // 2, posY1, color)
        draw_text(screen, result, 50, WIDTH // 2, posY2, color)

        if posY2 - posY1 > 50:
            posY1 += 10
            posY2 -= 10
        else:
            draw_text(screen, 'Пройдено волн:', 50, WIDTH // 2, posY1 + 120, color)
            draw_text(screen, countWaves, 50, WIDTH // 2, posY2 + 120, color)

        pygame.display.flip()

        clock.tick(FPS)


def screenMainmenu():  # Окно главного меню
    all_sprites = pygame.sprite.Group()
    buttonChooseLevel = ButtonWithText(all_sprites, (pygame.Color('Deepskyblue3'), pygame.Color('Deepskyblue4')), (200, 75), (300, 300), ('Выбрать уровень', 30, pygame.Color('White')))
    buttonSettings = ButtonWithText(all_sprites, (pygame.Color('Deepskyblue3'), pygame.Color('Deepskyblue4')), (200, 75), (300, 400), ('Настройки', 30, pygame.Color('White')))
    buttonRestart = ButtonWithText(all_sprites, (
    pygame.Color('Deepskyblue3'), pygame.Color('Deepskyblue4')), (200, 75),
                                         (300, 500), ('Перезапустить', 30,
                                                      pygame.Color('White')))
    buttonExit = ButtonWithText(all_sprites, (
    pygame.Color('Deepskyblue3'), pygame.Color('Deepskyblue4')), (200, 75),
                                         (300, 600), ('Выйти', 30,
                                                      pygame.Color('White')))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONUP:
                if buttonChooseLevel.isPressed():
                    clickButton.play()
                    return 'Exit4'
                elif buttonSettings.isPressed():
                    clickButton.play()
                    return 'Exit3'
                elif buttonRestart.isPressed():
                    clickButton.play()
                    return 'Exit1'
                elif buttonExit.isPressed():
                    clickButton.play()
                    terminate()

        screen.blit(BackgroundMenu1, (0, 0))

        all_sprites.draw(screen)
        all_sprites.update()

        pygame.display.flip()

        clock.tick(FPS)


def screenChooseLevel():  # Окно выбора уровня
    colors = []
    for level in ['Level1', 'Level2', 'Level3', 'Level4', 'Level5', 'Level6', 'Level7', 'Level8']:
        if int(cursor.execute(f'SELECT Value FROM UserData WHERE Information = \'{level}\'').fetchone()[0]):
            colors.append([pygame.Color('Limegreen'), pygame.Color('Forestgreen')])
        else:
            colors.append([pygame.Color('Red'), pygame.Color('Red4')])

    all_sprites = pygame.sprite.Group()
    buttonLevel1 = ButtonWithText(all_sprites, (colors[0][0], colors[0][1]), (200, 50), (195, 350), ('Уровень 1', 30, pygame.Color('White')))
    buttonLevel2 = ButtonWithText(all_sprites, (colors[1][0], colors[1][1]), (200, 50), (195, 410), ('Уровень 2', 30, pygame.Color('White')))
    buttonLevel3 = ButtonWithText(all_sprites, (colors[2][0], colors[2][1]), (200, 50), (195, 470), ('Уровень 3', 30, pygame.Color('White')))
    buttonLevel4 = ButtonWithText(all_sprites, (colors[3][0], colors[3][1]), (200, 50), (195, 530), ('Уровень 4', 30, pygame.Color('White')))
    buttonLevel5 = ButtonWithText(all_sprites, (colors[4][0], colors[4][1]), (200, 50), (405, 350),
                                  ('Уровень 5', 30, pygame.Color('White')))
    buttonLevel6 = ButtonWithText(all_sprites, (colors[5][0], colors[5][1]), (200, 50), (405, 410),
                                  ('Уровень 6', 30, pygame.Color('White')))
    buttonLevel7 = ButtonWithText(all_sprites, (colors[6][0], colors[6][1]), (200, 50), (405, 470),
                                  ('Уровень 7', 30, pygame.Color('White')))
    buttonLevel8 = ButtonWithText(all_sprites, (colors[7][0], colors[7][1]), (200, 50), (405, 530),
                                  ('Уровень 8', 30, pygame.Color('White')))
    buttonLevelCustom = ButtonWithText(all_sprites, (pygame.Color('Deepskyblue3'), pygame.Color('Deepskyblue4')), (200, 50), (195, 590), ('Свой уровень', 30, pygame.Color('White')))
    buttonInfinity = ButtonWithText(all_sprites, (
    pygame.Color('Deepskyblue3'), pygame.Color('Deepskyblue4')), (200, 50),
                                       (405, 590), ('Бесконечность', 30,
                                                    pygame.Color('White')))
    buttonReturn = ButtonWithArrow(all_sprites, (pygame.Color('Red4'), pygame.Color('Red')), (100, 100), (540, 740), (((90, 10), (10, 50), (90, 90)), 0), None)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONUP:
                if buttonLevel1.isPressed():
                    clickButton.play()
                    return ('Exit5', (Level1, ))
                elif buttonLevel2.isPressed():
                    clickButton.play()
                    return ('Exit5', (Level2, ))
                elif buttonLevel3.isPressed():
                    clickButton.play()
                    return ('Exit5', (Level3, ))
                elif buttonLevel4.isPressed():
                    clickButton.play()
                    return ('Exit5', (Level4, ))
                elif buttonLevel5.isPressed():
                    clickButton.play()
                    return ('Exit5', (Level5, ))
                elif buttonLevel6.isPressed():
                    clickButton.play()
                    return ('Exit5', (Level6, ))
                elif buttonLevel7.isPressed():
                    clickButton.play()
                    return ('Exit5', (Level7, ))
                elif buttonLevel8.isPressed():
                    clickButton.play()
                    return ('Exit5', (Level8, ))
                elif buttonLevelCustom.isPressed():
                    clickButton.play()
                    return ('Exit5', (LevelCustom, ))
                elif buttonInfinity.isPressed():
                    level = [[randint(1, 6) for i in range(randint(1, 5))] for j in range(1000)]
                    level = ['Infinity'] + level
                    clickButton.play()
                    return ('Exit5', (level, ))
                elif buttonReturn.isPressed():
                    clickButton.play()
                    return 'Exit2'

        screen.blit(BackgroundMenu2, (0, 0))

        draw_text(screen, 'Выберите уровень', 50, 300, 200, pygame.Color('White'))

        all_sprites.draw(screen)
        all_sprites.update()

        pygame.display.flip()

        clock.tick(FPS)

def screenGame(level):  # Окно игры
    pygame.mouse.set_visible(0)
    pygame.mixer.music.play(-1)
    settingsEnemy1, settingsEnemy2, settingsEnemy3, settingsEnemy4, settingsEnemy5, settingsEnemy6 = load_enemySettings()
    Ship = load_ship()[0]

    camera = Camera()
    all_sprites = pygame.sprite.Group()
    background1_sprites = pygame.sprite.Group()
    background2_sprites = pygame.sprite.Group()
    projectile_sprites = pygame.sprite.Group()
    bonuses_sprites = pygame.sprite.Group()
    explosion_sprites = pygame.sprite.Group()
    game_sprites = pygame.sprite.Group()
    player_sprite = pygame.sprite.Group()
    Background((all_sprites, background1_sprites), True)
    Background((all_sprites, background1_sprites))
    player = Player((player_sprite, game_sprites), (all_sprites, projectile_sprites), (WIDTH // 2, 700), Ship, ShieldPic, 10, 1000, 3, 10, 1, 250, 0, 0, 2000, 2000, 3000)
    eventStatus = EventStatus([player.hideTime, player.spawnTime, player.waitTime, 0], 1)

    numberOfWave = 0
    lastBonus = 0
    lastMeteor = 0
    running = True
    while running:
        eventStatus.update()
        if player.lives == 0 and eventStatus.isSpawning():  # Проверка на конец игры
            return ('Exit6', ('не пройден', f'{numberOfWave}/{len(level) - 1}'))
        elif player.lives != 0 and numberOfWave != len(level) - 1 and len(game_sprites) == 1 and eventStatus.isPlaying():  # Проверка на смерть всех врагов
            for pos, enemy in enumerate(level[1:][numberOfWave]):
                dataEnemy = {1: (settingsEnemy1, enemys[0]), 2: (settingsEnemy2, enemys[1]), 3: (settingsEnemy3, enemys[2]), 4: (settingsEnemy4, enemys[3]), 5: (settingsEnemy5, enemys[4]), 6: (settingsEnemy6, enemys[5])}[enemy]
                Enemy((all_sprites, game_sprites), (all_sprites, projectile_sprites), dataEnemy[0], (100 * (pos + 1), -HEIGHT + 100 * (pos + 1)), dataEnemy[1])
                pygame.mixer.stop()
                spawnEnemy.play()
            lastBonus = pygame.time.get_ticks()
            numberOfWave += 1
        elif player.lives != 0 and numberOfWave == len(level) - 1 and eventStatus.isSpawning():  # Проверка на конец игры
            cursor.execute(f'UPDATE UserData SET Value = 1 WHERE Information = \'{level[0]}\'')
            connection.commit()
            return ('Exit6', ('пройден', f'{numberOfWave}/{len(level) - 1}'))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)

        background1_sprites.draw(screen)
        background2_sprites.draw(screen)
        bonuses_sprites.draw(screen)
        projectile_sprites.draw(screen)
        explosion_sprites.draw(screen)
        game_sprites.draw(screen)
        for i in range(1, player.lives + 1):  # Отрисовка полоски жизни
            screen.blit(Heart, (WIDTH - (50 * i + Heart.get_rect().w // 2), 50 - Heart.get_rect().h // 2))
        if player.lives:  # Отрисовка сердец
            pygame.draw.rect(screen, pygame.Color('Red'), (30, 30, round(player.hpnow * 0.25), 30))


        for sprite in game_sprites:
            if pygame.sprite.collide_mask(player, sprite) and type(sprite) != Player:  # Проверка на столкновение
                player.hitting(500)
                sprite.hitting(500)

            for explosionSettings in sprite.checkDamage(projectile_sprites):  # Проверка на попадание снаряда
                Explosion((all_sprites, explosion_sprites), (explosionSettings[0] - camera.dx, explosionSettings[1]), explosionSettings[2], sonicExplosionList)
                explosionSonic.play()

        for sprite in bonuses_sprites:  # Проверка на столкновение с бонусом
            if pygame.sprite.collide_mask(player, sprite):
                pygame.mixer.stop()
                pickupBonus.play()
                lastBonus = pygame.time.get_ticks()
                player.startBonus = pygame.time.get_ticks()
                if sprite.image == bonuses[0]:
                    player.shield()
                elif sprite.image == bonuses[1]:
                    player.speed = int(player.speed * 1.5)
                elif sprite.image == bonuses[2]:
                    player.countGuns = 2
                else:
                    player.speedShooting = int(player.speedShooting / 1.5)
                sprite.kill()



        all_sprites.update()
        player_sprite.update()

        if len(game_sprites) == 1 and eventStatus.isPlaying():  # Проверка на смерть всех врагов
            eventStatus.changeEvent()

        for sprite in game_sprites:
            if type(sprite) == Player and sprite.isDied:  # Проверка на смерть игрока
                sprite.isDied = False
                Explosion((all_sprites, explosion_sprites), (sprite.rect.centerx - camera.dx, sprite.rect.centery), round(max(sprite.rect.size) * 1.5), regularExplosionList)
                numberOfWave -= 1
                for sprite in game_sprites:
                    if type(sprite) != Player:
                        sprite.kill()
                projectile_sprites.empty()
                bonuses_sprites.empty()
                eventStatus.changeEvent()
                pygame.mixer.stop()
                playerDie.play()
            elif sprite.lives == 0:  # Проверка на смерть врага
                Explosion((all_sprites, explosion_sprites), (sprite.rect.centerx - camera.dx, sprite.rect.centery), round(max(sprite.rect.size) * 1.5), regularExplosionList)
                sprite.kill()
                pygame.mixer.stop()
                enemyDie.play()


        if pygame.time.get_ticks() - lastBonus > 15000 and eventStatus.isPlaying():  # Каждые 15 секунд появляется бонус
            lastBonus = pygame.time.get_ticks()
            Bonus((all_sprites, bonuses_sprites), randint(-200 + 50, 800 - 50))

        if pygame.time.get_ticks() - lastMeteor > 5000:  # Каждые 5 секунд появляется объект заднего фона
            lastMeteor = pygame.time.get_ticks()
            if random() * 100 > 50:
                MeteorWithAstronaut((all_sprites, background2_sprites), randint(-150, 750))
            else:
                Satellite((all_sprites, background2_sprites), randint(-150, 750))

        if len(background1_sprites) == 1:  # Обновление заднего фона
            Background((all_sprites, background1_sprites))

        pygame.display.flip()

        clock.tick(FPS)


class Bonus(pygame.sprite.Sprite):  # Спрайт бонуса игры
    def __init__(self, spriteGroups, posCenterX):
        super().__init__(*spriteGroups)
        self.image = choice(bonuses)
        self.rect = self.image.get_rect()
        self.posCenterX = posCenterX
        self.rect.centerx = self.posCenterX
        self.movingX = 0
        self.sign = 1
        self.lastUpdate = pygame.time.get_ticks()

    def update(self):
        self.rect.y += 1
        if pygame.time.get_ticks() - self.lastUpdate > 1000 / FPS2:
            self.lastUpdate = pygame.time.get_ticks()
            self.movingX += self.sign
            if abs(self.movingX) > 5:
                self.sign = - self.sign
            self.posCenterX += self.movingX
            if self.rect.top >= HEIGHT:
                self.kill()


class EventStatus():  # Мониторит текущее событие в игре
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


class GameObject(pygame.sprite.Sprite):  # Игровой спрайт
    def __init__(self, spriteGroups, projectileGroups, posCenter, image, hp, lives, damage, countGuns, speedShooting, movingX, movingY):
        super().__init__(*spriteGroups)
        self.projectileGroups = projectileGroups
        self.hp = hp
        self.hpnow = self.hp
        self.lives = lives
        self.damage = damage
        self.countGuns = countGuns
        self.speedShooting = speedShooting
        self.movingX = movingX
        self.movingY = movingY
        self.lastProjectile = pygame.time.get_ticks()

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = posCenter
        self.mask = pygame.mask.from_surface(self.image)
        self.posCenterX = self.rect.centerx

    def checkDamage(self, projectileSprites):
        result = []
        for sprite in projectileSprites:
            if pygame.sprite.collide_mask(self,
                                          sprite) and sprite.type != type(
                    self):
                result.append(sprite.damageSprite(self))
        return result

    def tryShoot(self, movingY, posCenterY):
        if pygame.time.get_ticks() - self.lastProjectile > self.speedShooting:
            self.lastProjectile = pygame.time.get_ticks()
            if self.countGuns == 1:
                Projectile(self, self.rect.w // 2, movingY, posCenterY)
            else:
                Projectile(self, self.rect.w // 3, movingY, posCenterY)
                Projectile(self, self.rect.w // 3 * 2, movingY, posCenterY)


class Player(GameObject):  # Спрайт игрока
    def __init__(self, spriteGroups, projectileGroups, posCenter, image, imageShield, speed, hp, lives, damage, countGuns, speedShooting, movingX, movingY, hideTime, spawnTime, waitTime):
        super().__init__(spriteGroups, projectileGroups, posCenter, image, hp, lives, damage, countGuns, speedShooting, movingX, movingY)
        imageWithShield = imageShield
        rect = self.image.get_rect()
        rect.center = imageShield.get_rect().center
        imageWithShield.blit(self.image, rect)
        self.speed = speed
        self.default = [speed, countGuns, speedShooting]
        self.images = (self.image, pygame.Surface(self.image.get_size(), pygame.SRCALPHA), imageWithShield)
        self.numberImage = 0
        self.hideTime = hideTime
        self.spawnTime = spawnTime
        self.waitTime = waitTime
        self.imageProjectile = choice(spaceMissileList)
        self.died = pygame.time.get_ticks() - self.hideTime
        self.lastChangeImage = pygame.time.get_ticks()
        self.isDied = False
        self.isShield = False
        self.startBonus = 0
        self.timeBonus = 5000
        self.hpShield = 300
        self.hpShieldnow = self.hpShield

    def hitting(self, damage):  # Нанести урон
        if self.isShield:
            self.hpShieldnow -= damage
        else:
            self.hpnow -= damage


    def shield(self):  # Включить щит
        self.image = self.images[2]
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)
        self.isShield = True
        pygame.mixer.stop()
        shieldUp.play()

    def unshield(self):  # Отключить щит
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)
        self.isShield = False
        pygame.mixer.stop()
        shieldDown.play()

    def update(self):
        if self.hpnow <= 0:
            self.lives -= 1
            self.hpnow = self.hp
            self.died = pygame.time.get_ticks()
            self.isDied = True
        if self.hpShieldnow <= 0:
            self.hpShieldnow = self.hpShield
            self.unshield()
        if pygame.time.get_ticks() - self.startBonus > self.timeBonus:
            if self.isShield:
                self.unshield()
            self.speed = self.default[0]
            self.countGuns = self.default[1]
            self.speedShooting = self.default[2]
        self.movingX = 0
        self.movingY = 0
        if pygame.time.get_ticks() - self.died <= self.hideTime:
            self.image = self.images[1]
        else:
            if pygame.time.get_ticks() - self.lastChangeImage > 1000 / FPSSpawnPlayer:
                if pygame.time.get_ticks() - self.died <= self.hideTime + self.spawnTime:  # При спавне картинка мигает
                    self.lastChangeImage = pygame.time.get_ticks()
                    self.image = self.images[self.numberImage]
                    self.numberImage = (self.numberImage + 1) % 2
                elif self.isShield:
                    self.image = self.images[2]
                else:
                    self.image = self.images[0]
            keystate = pygame.key.get_pressed()
            if keystate[pygame.K_a]:
                self.movingX += -self.speed
            if keystate[pygame.K_d]:
                self.movingX += self.speed
            if keystate[pygame.K_w]:
                self.movingY += -self.speed
            if keystate[pygame.K_s]:
                self.movingY += self.speed
            if pygame.time.get_ticks() - self.died > self.hideTime + self.spawnTime:
                self.tryShoot(-5, self.rect.top)


class Enemy(GameObject):  # Класс врага
    def __init__(self, spriteGroups, projectileGroups, settings, posCenter, image):
        super().__init__(spriteGroups, projectileGroups, posCenter, image, settings[0], 1, settings[1], settings[2], settings[3], settings[4], settings[5])

        if settings[6] == 'small':
            self.imageProjectile = choice(lasers[2::3])
        elif settings[6] == 'medium':
            self.imageProjectile = choice(lasers[1::3])
        else:
            self.imageProjectile = choice(lasers[::3])

    def hitting(self, damage):  # Нанести урон
        self.hpnow -= damage

    def update(self):
        if self.hpnow <= 0:
            self.lives -= 1
            self.hpnow = self.hp
        if (self.movingY < 0 and self.rect.centery + self.movingY < 50) or (self.movingY > 0 and self.rect.centery + self.movingY > HEIGHT // 2):
            self.movingY = -self.movingY
        self.rect.y += self.movingY
        if (self.posCenterX + self.movingX < WIDTH // 2 - BackgroundGame.get_rect().w // 2 + 50) or (self.posCenterX + self.movingX > WIDTH + BackgroundGame.get_rect().w // 2 - WIDTH // 2 - 50):
            self.movingX = -self.movingX
        self.posCenterX += self.movingX
        self.tryShoot(5, self.rect.bottom)


class Explosion(pygame.sprite.Sprite):  # Спрайт взрыва
    def __init__(self, spriteGroups, posCenter, size, ExplosionList):
        super().__init__(*spriteGroups)

        self.ExplosionList = [pygame.transform.scale(explosion, (size, size),) for explosion in ExplosionList]
        self.posCenter = posCenter
        self.imageNumber = 1
        self.image = self.ExplosionList[self.imageNumber - 1]
        self.rect = self.image.get_rect()
        self.rect.center = self.posCenter
        self.posCenterX = self.rect.centerx
        self.lastUpdate = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self.lastUpdate > 1000 / FPS2:
            self.lastUpdate = pygame.time.get_ticks()
            self.imageNumber += 1
            if self.imageNumber == len(self.ExplosionList):
                self.kill()
            else:
                self.image = self.ExplosionList[self.imageNumber - 1]
                self.rect = self.image.get_rect()
                self.rect.center = self.posCenter
                self.posCenterX = self.rect.centerx


class Projectile(pygame.sprite.Sprite):  # Класс снаряда
    def __init__(self, target, posShiftX, movingY, posCenterY):
        super().__init__(target.projectileGroups)

        self.type = type(target)
        if self.type == Player:
            rocketShoot.play()
        else:
            laserShoot.play()
        self.damage = target.damage
        self.movingY = movingY
        self.create = pygame.time.get_ticks()
        self.image = target.imageProjectile
        self.rect = self.image.get_rect()
        self.rect.centerx = target.posCenterX - target.rect.w // 2 + posShiftX
        self.rect.centery = posCenterY
        self.mask = pygame.mask.from_surface(self.image)
        self.posCenterX = self.rect.centerx

    def damageSprite(self, sprite):  # Нанести урон объекту
        sprite.hitting(self.damage)
        self.kill()
        return self.rect.center + (round(max(self.rect.size) * 1.5), regularExplosionList if self.type == Player else sonicExplosionList)


    def update(self):
        self.rect.y += self.movingY
        if self.rect.top >= HEIGHT or self.rect.bottom <= 0:
            self.kill()


class Background(pygame.sprite.Sprite):  # Спрайт заднего фона
    def __init__(self, spriteGroups, isFirst=False):
        super().__init__(spriteGroups)
        self.image = BackgroundGame
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.posCenterX = self.rect.centerx
        if isFirst:
            self.rect.bottom = HEIGHT
        else:
            self.rect.bottom = HEIGHT - self.image.get_rect().height

    def update(self):
        self.rect.y += 2
        if self.rect.top >= HEIGHT:
            self.kill()


class Camera:  # Меняет положение всех спрайтов относительно игрока
    def __init__(self):
        self.dx = 0

    def apply(self, object):  # Сменить позицию относительно игрока
        object.rect.centerx = object.posCenterX + self.dx

    def isCameraMoving(self, target):  # Проверка на движение камеры за игроком
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


    def tryCameraMoving(self, target):  # Попробовать двигаться за камерой камере
        if self.isCameraMoving(target):
            self.dx -= target.movingX
            return True
        else:
            return False

    def update(self, target):
        if not self.tryCameraMoving(target):
            target.rect.x += target.movingX
        target.posCenterX = target.rect.centerx - self.dx
        target.rect.y += target.movingY
        target.rect.centerx = max(50, target.rect.centerx)
        target.rect.centerx = min(WIDTH - 50, target.rect.centerx)
        target.rect.centery = max(200, target.rect.centery)
        target.rect.centery = min(HEIGHT - 50, target.rect.centery)


class MeteorWithAstronaut(pygame.sprite.Sprite):  # Спрайт заднего фона
    def __init__(self, spriteGroups, posCenterX):
        super().__init__(spriteGroups)

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
        self.posCenterX = self.rect.centerx
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

    def changeImage(self):  # Менять картинку каждую секунду
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

    def update(self):
        self.rect.y += 2
        if self.rect.y > HEIGHT:
            self.kill()
        else:
            self.changeImage()


class Satellite(pygame.sprite.Sprite):  # Спрайт заднего фона
    def __init__(self, spriteGroups, posCenterX):
        super().__init__(spriteGroups)

        self.image = choice((spaceSatellite1, spaceSatellite2))
        self.rect = self.image.get_rect().move(0, 100)
        self.posCenterX = posCenterX
        self.rect.centerx = self.posCenterX

    def update(self):
        self.rect.y += 2
        if self.rect.y > HEIGHT:
            self.kill()


def screenSettings():  # Окно настроек
    bigShip = load_ship()[1]
    complexity = int(cursor.execute('SELECT Value FROM UserData WHERE Information = \'complexity\'').fetchone()[0])

    all_sprites = pygame.sprite.Group()
    buttonLeft1 = ButtonWithArrow(all_sprites, (
    pygame.Color('Forestgreen'), pygame.Color('Limegreen')), (100, 100),
                                  (100, 250),
                                  (((90, 10), (10, 50), (90, 90)), 0),
                                  None)
    buttonRight1 = ButtonWithArrow(all_sprites, (
    pygame.Color('Forestgreen'), pygame.Color('Limegreen')), (100, 100),
                                   (500, 250),
                                   (((10, 10), (90, 50), (10, 90)), 0),
                                   None)
    buttonLeft2 = ButtonWithArrow(all_sprites, (pygame.Color('Forestgreen'), pygame.Color('Limegreen')), (200, 100), (180, 550), (((90, 10), (10, 50), (90, 90)), 0), ((90, 35, 80, 30), 0))
    buttonRight2 = ButtonWithArrow(all_sprites, (pygame.Color('Forestgreen'), pygame.Color('Limegreen')), (200, 100), (420, 550), (((110, 10), (190, 50), (110, 90)), 0), ((30, 35, 80, 30), 0))
    buttonReturn = ButtonWithArrow(all_sprites, (pygame.Color('Red4'), pygame.Color('Red')), (100, 100), (540, 740), (((90, 10), (10, 50), (90, 90)), 0), None)
    bigShipRect = bigShip.get_rect(center=(300, 700))
    complexitys = {-1: ('ЛЕГКО', pygame.Color('Green')), 0: ('НОРМАЛЬНО', pygame.Color('White')), 1: ('СЛОЖНО', pygame.Color('Red')), 2: ('ХАРДКОР', pygame.Color('Red4'))}

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONUP:
                changeShip = False
                changeComplexity = False
                numberOfShip = cursor.execute('SELECT Value FROM UserData WHERE Information = \'numberOfShip\'').fetchone()[0]
                if buttonLeft2.isPressed():
                    clickButton.play()
                    numberOfShip = (numberOfShip + 12 - 1 - 1) % 12 + 1
                    changeShip = True
                elif buttonRight2.isPressed():
                    clickButton.play()
                    numberOfShip = (numberOfShip + 12 - 1 + 1) % 12 + 1
                    changeShip = True
                elif buttonLeft1.isPressed():
                    clickButton.play()
                    complexity = max([complexity - 1, -1])
                    changeComplexity = True
                elif buttonRight1.isPressed():
                    clickButton.play()
                    complexity = min([complexity + 1, 2])
                    changeComplexity = True
                elif buttonReturn.isPressed():
                    clickButton.play()
                    return 'Exit2'
                if changeShip:
                    cursor.execute(f'UPDATE UserData SET Value = {numberOfShip} WHERE Information = \'numberOfShip\'')
                    connection.commit()
                    bigShip = load_ship()[1]
                if changeComplexity:
                    cursor.execute(f'UPDATE UserData SET Value = {complexity} WHERE Information = \'complexity\'')
                    connection.commit()
        screen.blit(BackgroundMenu2, (0, 0))
        screen.blit(bigShip, bigShipRect)

        draw_text(screen, 'Выберите уровень сложности', 50, 300, 100, pygame.Color('White'))
        draw_text(screen, complexitys[complexity][0], 50, 300, 250, complexitys[complexity][1])
        draw_text(screen, 'Выберите звездолёт', 50, 300, 400, pygame.Color('White'))

        all_sprites.draw(screen)
        all_sprites.update()

        pygame.display.flip()

        clock.tick(FPS)


class Button(pygame.sprite.Sprite):  # Спрайт кнопки
    def __init__(self, spriteGroups, colors, size, posCenter):
        super().__init__(spriteGroups)
        self.colors = colors
        self.size = size
        self.posCenter = posCenter

        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.posCenter[0]
        self.rect.centery = self.posCenter[1]

    def isPressed(self):  # Наведена ли мышь
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def update(self):
        self.draw()


class ButtonWithText(Button):  # Спрайт кнопки с текстом
    def __init__(self, spriteGroups, colors, size, posCenter, textInfo):
        super().__init__(spriteGroups, colors, size, posCenter)
        self.textInfo = textInfo

        self.draw()

    def draw(self):
        if self.isPressed():
            self.image.fill(self.colors[1])
        else:
            self.image.fill(self.colors[0])
        draw_text(self.image, self.textInfo[0], self.textInfo[1], self.rect.width // 2, self.rect.height // 2 - self.textInfo[1] // 4, self.textInfo[2])

class ButtonWithArrow(Button):  # Спрайт кнопки со стрелкой
    def __init__(self, spriteGroups, colors, size, posCenter, polygonInfo, rectInfo):
        super().__init__(spriteGroups, colors, size, posCenter)
        self.polygonInfo = polygonInfo
        self.rectInfo = rectInfo

        self.draw()

    def draw(self):
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        if self.isPressed():
            color = 0
        else:
            color = 1
        if self.polygonInfo:
            pygame.draw.polygon(self.image, self.colors[color], *self.polygonInfo)
        if self.rectInfo:
            pygame.draw.rect(self.image, self.colors[color],  *self.rectInfo)


if __name__ == '__main__':
    Level1, Level2, Level3, Level4, Level5, Level6, Level7, Level8, LevelCustom = load_levels()
    BackgroundMenu1, BackgroundMenu2, BackgroundGame, Meteor1, Meteor2, spaceAstronaut1_1, spaceAstronaut1_2, spaceAstronaut2_1, spaceAstronaut2_2, spaceSatellite1, spaceSatellite2, ShieldPic, Heart, enemys, lasers, regularExplosionList, sonicExplosionList, spaceMissileList, bonuses = load_graphics()
    spawnEnemy, spawnPlayer, shieldDown, shieldUp, shieldUp, rocketShoot, playerDie, pickupBonus, laserShoot, explosionSonic, explosionRegular, enemyDie, clickButton = load_sounds()
    rocketShoot.set_volume(0.1)
    laserShoot.set_volume(0.2)
    explosionRegular.set_volume(0.2)
    enemyDie.set_volume(0.1)
    playerDie.set_volume(0.1)
    pygame.mixer.music.set_volume(0.05)

    resultDict = {'Exit1': screenIntro, 'Exit2': screenMainmenu, 'Exit3': screenSettings, 'Exit4': screenChooseLevel, 'Exit5': screenGame, 'Exit6': screenEndGame}
    result = 'Exit1'  #('Exit5', Level1)
    while result:
        if type(result) == tuple:
            result = resultDict[result[0]](*result[1])
        else:
            result = resultDict[result]()
    connection.close()