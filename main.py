import pygame
import os
import random
import csv
import math
from pygame.rect import Rect

NUM_MONSTERS = 20

WIDTH = 800
HEIGHT = 600

background_colour = (234, 212, 252)

pygame.init()
font = pygame.font.SysFont("sans-serif", 20)
screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption('Dig Dug')
clock = pygame.time.Clock()

TILE_SIZE = 32

MONSTER = pygame.transform.scale(pygame.image.load("images/monster_standing.png"),
                                 (TILE_SIZE, TILE_SIZE)).convert_alpha()
PLAYER = pygame.transform.scale(pygame.image.load("images/playerDigging1.png"), (TILE_SIZE, TILE_SIZE)).convert_alpha()
PLAYER_LIVES = pygame.transform.scale(PLAYER, (PLAYER.get_width() / 1.0, PLAYER.get_height() / 1.0))

coin_sound = pygame.mixer.Sound("sounds/166184__drminky__retro-coin-collect.wav")


class Character(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()
        self.walk_animation = [
            pygame.image.load(os.path.join("images", f"{type}_standing.png")).convert_alpha(),
        ]
        self.walk_animation[0].set_colorkey((20, 20, 20))
        self.image = self.walk_animation[0]


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.walk_animation = [
            [
                pygame.transform.scale(pygame.image.load(os.path.join("images", f"playerDigging1.png")),
                                       (TILE_SIZE, TILE_SIZE)).convert_alpha(),
                pygame.transform.scale(pygame.image.load(os.path.join("images", f"playerDigging2.png")),
                                       (TILE_SIZE, TILE_SIZE)).convert_alpha()
            ],
            [
                pygame.transform.scale(pygame.image.load(os.path.join("images", f"playerDigging1Rotated.png")),
                                       (TILE_SIZE, TILE_SIZE)).convert_alpha(),
                pygame.transform.scale(pygame.image.load(os.path.join("images", f"playerDigging2Rotated.png")),
                                       (TILE_SIZE, TILE_SIZE)).convert_alpha()
            ]
        ]
        # self.hurt = pygame.image.load(os.path.join("Assets", "Hero", "digdug_still.png")).convert_alpha()

        self.speed = 1
        #
        self.current_img = 0
        self.current = 0
        self.image = self.walk_animation[self.current][self.current_img]
        self.flipx = False
        self.flipy = False
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 1

        self.attacking = False
        self.attackingTime = 120
        self.cooldownTime = 120
        self.direction = 1

    def update(self, level):
        global score
        keys = pygame.key.get_pressed()
        input_x = 0
        input_y = 0
        moving = False
        if keys[pygame.K_UP]:
            self.current = 1
            self.flipy = False
            self.flipx = False
            input_y = -self.speed

            moving = True

        if keys[pygame.K_DOWN]:
            self.current = 1
            self.flipx = False
            self.flipy = True
            input_y = self.speed

            moving = True

        if keys[pygame.K_LEFT]:
            input_x = -self.speed
            self.current = 0
            self.flipy = False
            self.flipx = True

            moving = True

        if keys[pygame.K_RIGHT]:
            input_x = self.speed
            self.current = 0
            self.flipy = False
            self.flipx = False

            moving = True

        new_rect = self.rect.copy()

        # check if we are aligned with a column
        if new_rect.x % TILE_SIZE == 0:
            # vertical movement
            new_rect.y += input_y * self.speed

        # check if we are aligned with a row
        if new_rect.y % TILE_SIZE == 0:
            # horizontal movement
            new_rect.x += input_x * self.speed

        for row in level:
            for row_i in range(len(row)):
                tile = row[row_i]
                if tile is not None and new_rect.colliderect(tile):
                    if tile.is_obstacle:
                        new_rect = self.rect.copy()
                    elif tile.is_dirt:
                        row[row_i] = None
                        score += 0

        self.rect = new_rect

        if moving:
            self.current_img += 0.1
            if self.current_img >= len(self.walk_animation):
                self.current_img = 0
        self.image = pygame.transform.flip(self.walk_animation[self.current][int(self.current_img)], self.flipx,
                                           self.flipy)

        super().update()
        self.rect.clamp_ip(screen.get_rect())

    def attack(self):
        self.cooldown()
        if self.cooldown == 0 and not self.attacking:
            self.attacking = True
            self.cooldown = 1
        elif self.attacking:
            self.attackingTime -= 1
            if self.attackingTime <= 0:
                self.attackingTime = 120
                self.attacking = False

    def cooldown(self):
        if self.cooldownTime > 0:
            self.cooldownTime += 1
            if self.cooldownTime >= 120:
                self.cooldownTime = 0


class Coin(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        self.image = pygame.image.load("images/coin_1.gif")
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.topleft = pos


def get_random_available_tile(distances = None, distance_tiles = 0):
    BAD_TILES = [(16, 8), (17, 8), (16, 9), (17, 9)]
    for j in range(20):
        x = random.randrange(0, WIDTH - 1, TILE_SIZE)
        y = random.randrange(0, HEIGHT - 180, TILE_SIZE)

        tile = (x // 32, y // 32)
        if tile in BAD_TILES:
            print("dodge the rock")
            continue

        if distances:
            ok = True
            # if difference between two points is less than 80 pixels, place coin
            for dist in distances:
                if math.dist((x, y), dist) < distance_tiles * 32:
                    ok = False
                    break
            if not ok:
                continue

        return x, y

def add_coins(n):
    # put coins in list, return
    coins = []
    distances = []
    for i in range(n):
        # multiple coins
        x, y = get_random_available_tile(distances, 3)
        coins.append(Coin((x, y)))
        distances.append((x, y))


    return coins


class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y, movementx, movementy, img=MONSTER):
        super().__init__()
        self.direction = None
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.ix = x
        self.iy = y
        self.movementx = movementx
        self.movementy = movementy

    def draw(self):
        screen.blit(self.image, self.rect)

    def move(self, level):
        self.rect.x += self.movementx
        self.rect.y += self.movementy

        # change direction if we hit a tile
        for row in level:
            for tile in row:
                if tile != None:
                    if self.rect.colliderect(tile.rect):
                        self.movementx = -self.movementx
                        self.movementy = -self.movementy

        if self.rect.x >= WIDTH - self.rect.width and self.movementx > 0 or self.rect.x <= 0 and self.movementx < 0:
            self.movementx = - self.movementx

        if self.rect.y >= HEIGHT - self.rect.height and self.movementy > 0 or self.rect.y <= 0 and self.movementy < 0:
            self.movementy = - self.movementy

        # are we aligned with grid position
        if self.rect.x % TILE_SIZE == 0 and self.rect.y % TILE_SIZE == 0:
            self.choose_direction(level)

    def choose_direction(self, level):
        valid_exits = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        # index
        for i in range(len(valid_exits)-1, -1, -1):
            # find tile coordinates to see if this tile is a valid exit
            tile_x = self.rect.x + TILE_SIZE * valid_exits[i][0]
            tile_y = self.rect.y + TILE_SIZE * valid_exits[i][1]
            # see if there is a tile at tilex and tiley
            grid_x = tile_x // TILE_SIZE
            grid_y = tile_y // TILE_SIZE
            if level[grid_y][grid_x] is not None:
                del valid_exits[i]

        if len(valid_exits) == 0:
            return
        # if there is 1 available exit, don't go back on yourself
        elif len(valid_exits) > 1:
            for i in range(len(valid_exits) - 1, -1, -1):
                if valid_exits[i] == (-self.movementx, -self.movementy):
                    del valid_exits[i]

        chosen_exit = random.choice(valid_exits)
        self.movementx = chosen_exit[0]
        self.movementy = chosen_exit[1]

    # def offset(self, target):
    #     offsetx = self.ix - target.rect.x
    #     offsety = self.iy - target.rect.y
    #     if offsetx <= TILE_SIZE * 4 and offsetx > 0 and offsety <= TILE_SIZE * 3 and offsety > -TILE_SIZE * 4:
    #         if offsety > 0:
    #             multi = -offsety
    #         else:
    #             multi = offsety
    #         if self.rect.x >= self.ix + TILE_SIZE * 1.5 + ((offsetx - TILE_SIZE * 4) // 2) - (
    #                 (multi - TILE_SIZE * 4) // 10) and self.movementx > 0:
    #             self.movementx = -self.movementx
    #     if offsetx >= -TILE_SIZE * 4 and offsetx < 0 and offsety <= TILE_SIZE * 3 and offsety > -TILE_SIZE * 4:
    #         if self.rect.x <= self.ix + TILE_SIZE and self.movementx < 0:
    #             self.movementx = -self.movementx
    #
    #     return offsetx, offsety

    def player_collision(self, player):
        if self.rect.colliderect(player.rect):
            return True

        return False


# implementing tiles
class Tile():
    def __init__(self, image, x, y, is_obstacle, is_dirt):
        self.image = image
        # manual load in: self.image = pygame.image.Load(image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.is_obstacle = is_obstacle
        self.is_dirt = is_dirt

    # helper function: draw the tile
    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))


class TileMap():
    def __init__(self, filename):
        # self.map_w, self.map_h = x * self.tile_size, y * self.tile_size
        self.start_x, self.start_y = 0, 0
        self.tile_img = pygame.image.load("images/tile.png")
        self.filename = filename
        self.map = self.load(self.filename)

    # display all tiles for each row
    def draw(self):
        for row in self.map:
            for tile in row:
                if tile is not None:
                    tile.draw(screen)

    def load(self, filename):  # this should probably be rewritten
        tile_size_original = 16
        map = []
        with open(os.path.join(filename)) as file:
            data = csv.reader(file, delimiter=',')
            screen_y = self.start_y
            for row in data:
                screen_x = self.start_x
                tile_row = []
                for number in row:
                    number = int(number)
                    if number >= 0:
                        # get image corresponding from tile
                        x = tile_size_original * (
                                number % 6)  # this is rather not efficient i think but it is run only once
                        y = tile_size_original * (number // 6)
                        tile_surface_original = pygame.surface.Surface((tile_size_original, tile_size_original))
                        tile_surface_scaled = pygame.surface.Surface((TILE_SIZE, TILE_SIZE))
                        tile_surface_original.blit(self.tile_img, (0, 0),
                                                   Rect(x, y, tile_size_original, tile_size_original))
                        pygame.transform.scale(tile_surface_original, (TILE_SIZE, TILE_SIZE),
                                               tile_surface_scaled)
                        is_obstacle = number == 21 or 24 <= number <= 45
                        is_dirt = not is_obstacle
                        tile_row.append(Tile(tile_surface_scaled, screen_x, screen_y, is_obstacle, is_dirt))
                    else:
                        tile_row.append(None)
                    screen_x += TILE_SIZE
                map.append(tile_row)
                screen_y += TILE_SIZE
        return map


# button
class Button(pygame.Rect):
    def __init__(self, x, y, width, height, color, text, outline=None, outline_width=3):
        super().__init__(x, y, width, height)
        self.color = color
        self.text = text
        self.outline = outline
        self.outline_width = outline_width
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.text_surf = font.render(self.text, 1, (0, 0, 0))

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.text_surf, (self.x + self.width / 2 - self.text_surf.get_width() / 2,
                                     self.y + self.height / 2 - self.text_surf.get_height() / 2))
        if self.outline:
            pygame.draw.rect(screen, self.outline, self.rect, self.outline_width)

    def click(self):
        m = pygame.mouse.get_pos()
        if self.rect.collidepoint(m):
            return True
        return False


livesText = font.render("Lives: ", 1, (255, 255, 255))
scoreText = font.render("SCORE", 1, (255, 255, 255))


def draw(all_sprites, monsters, score, lives, level):
    screen.fill((0, 0, 0))
    # screen.fill(background_colour)
    # screen.blit(background, (0,0))
    level.draw()
    all_sprites.draw(screen)

    # draw lives
    screen.blit(livesText, (0, HEIGHT - livesText.get_height()))
    for i in range(lives):
        screen.blit(PLAYER_LIVES,
                    (PLAYER_LIVES.get_height() * 1.1 * i + livesText.get_width(), HEIGHT - PLAYER_LIVES.get_height()))

    # score
    scoreSurf = font.render(str(score), 1, (255, 255, 255))
    screen.blit(scoreText, (WIDTH / 2 - scoreText.get_width() / 2, 0))
    screen.blit(scoreSurf, (WIDTH / 2 - scoreSurf.get_width() / 2, scoreText.get_height()))

    #for x in range(25):
    #    for y in range(18):
    #        pygame.draw.rect(screen, (0, 0, 255), (x*32, y*32, 30, 30))
    #        surf = font.render(str(x)+","+str(y), 1, (255, 255, 255))
    #        screen.blit(surf, (x*32, y*32))
    pygame.display.flip()


# main menu
def main_menu():
    global clock

    DigDug = font.render("Dig Dug", 1, (0, 0, 0))
    playButton = Button(WIDTH / 2 - 100, HEIGHT / 2 - 90, 200, 50, (0, 255, 0), "Play", (0, 0, 0))
    exitButton = Button(WIDTH / 2 - 100, HEIGHT / 2 + 40, 200, 50, (255, 0, 0), "Exit", (0, 0, 0))
    while True:
        clock.tick(30)

        screen.fill((150, 150, 150))

        screen.blit(DigDug, (WIDTH / 2 - DigDug.get_width() / 2, 100))
        playButton.draw()
        exitButton.draw()

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if playButton.click():
                    game()
                elif exitButton.click():
                    quit()


# main game

score = 0
lives = 3
sides = []

running = True


def game():
    global running, score, lives, clock
    next_obstacle = HEIGHT

    level = TileMap("map.csv")

    for row in level.map:
        for tile in row:
            if tile != None:
                if tile.is_obstacle:
                    next_obstacle = tile.rect.y
                    break

    all_sprites = pygame.sprite.Group()

    monsters = []
    monster_positions = []
    blocked_pos = []
    for _ in range(NUM_MONSTERS):
        monsterx = random.randrange(0, WIDTH - TILE_SIZE * 3, TILE_SIZE)
        monstery = random.randrange(0, next_obstacle - TILE_SIZE * 3, TILE_SIZE)
        monster_positions.append((monsterx, monstery))
        while (monsterx / TILE_SIZE, monstery) in blocked_pos:
            monsterx = random.randrange(0, WIDTH - TILE_SIZE * 3, TILE_SIZE)
            monstery = random.randrange(0, next_obstacle - TILE_SIZE * 3, TILE_SIZE)
        monster = Monster(monsterx, monstery, 1, 0)
        blocked_pos.append((monsterx / TILE_SIZE, monstery))
        monsters.append(monster)
        all_sprites.add(monster)

    px, py = get_random_available_tile(monster_positions, distance_tiles=4)
    player = Player(px, py)

    all_sprites.add(player)

    coins = add_coins(10)
    all_sprites.add(coins)

    level.map[0][0] = None
    for x, row in enumerate(level.map):
        for y, tile in enumerate(row):
            if tile != None:
                for monster in monsters:
                    if tile.rect.x == monster.rect.x and tile.rect.y == monster.rect.y:
                        level.map[x][y] = None
                        if monster.movementy != 0:
                            level.map[x + 1][y] = level.map[x + 2][y] = None
                        elif monster.movementx != 0:
                            level.map[x][y + 1] = level.map[x][y + 2] = None

    # game loop / keep live
    while running:
        clock.tick(60)

        player.attack()
        player.update(level.map)

        # loop through monsters
        for monster in monsters:
            monster.move(level.map)
            # monster.offset(player)
            col = monster.player_collision(player)
            if col and not player.attacking:
                lives -= 1
                score -= score
                if lives == 0:
                    lives = 3
                    score = 0
                    return
                pygame.time.delay(2000)
                return game()
            elif col and player.attacking:
                monsters.remove(monster)
                score += 600

        # loop through coins
        for coin in coins[:]:
            if player.rect.colliderect(coin.rect):
                coins.remove(coin)
                all_sprites.remove(coin)
                score += 1
                coin_sound.play()

        # loop through event queue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                player.attacking = True

        #for i in all_sprites:
        #    print(i)
        draw(all_sprites, monsters, score, lives, level)


main_menu()
