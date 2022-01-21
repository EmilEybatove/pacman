import os
import sys
from collections import deque
from pprint import pprint
from random import sample, choice
import pygame
from pygame import Color
from math import sqrt

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
base_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
hunter_group = pygame.sprite.Group()
TILE = tile_width = tile_height = 18

if os.name == "nt":
    SCRIPT_PATH = os.getcwd()
else:
    SCRIPT_PATH = sys.path[0]

ghostGate = [(10, 12), (11, 12), (12, 12), (13, 12), (14, 12), (15, 12),
             (10, 13), (11, 13), (12, 13), (13, 13), (14, 13), (15, 13)]
# GONNA WORK ONLY FOR DEFAULT MAP!!
ghost_color = [Color(255, 0, 0, 255),  # Red
               Color(255, 128, 255, 255),  # pink
               Color(128, 255, 255, 255),  # light blue
               Color(255, 128, 0, 255),  # orange
               Color(50, 50, 255, 255),  # blue vulnerable
               Color(255, 255, 255, 255)]  # white

SIZE = cols, rows = 26, 26


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


tile_images = {
    'vertical': load_image('vertical.png'),
    'horisontal': load_image('horisontal.png'),
    '1': load_image('1.png'),
    '2': load_image('2.png'),
    '3': load_image('4.png'),
    '4': load_image('3.png'),
    'empty': load_image('empty.png'),
    'point': load_image('point.png'),
    'energo': load_image('energo.png'),
    'gate': load_image('gate.png')
}

values = {
    '|': 'vertical',
    '-': 'horisontal',
    '1': '1',
    '2': '2',
    '3': '3',
    '4': '4',
    '.': 'empty',
    '@': 'pacman',
    '*': 'energo',
    '0': 'point',
    '?': 'gate'
}


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, groups=(tiles_group, all_sprites)):
        super().__init__(*groups)
        self.cords = [pos_x, pos_y]
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


def get_rect(x, y):
    return x * TILE + 1, y * TILE + 1, TILE - 2, TILE - 2


def load_image(name, colorkey=None):
    if SCRIPT_PATH:
        fullname = os.path.join(SCRIPT_PATH, 'data', name)
    else:
        fullname = os.path.join('data', name)

    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


class Hunter(pygame.sprite.Sprite):
    def __init__(self, sprite_group, row, col, grid, color_ind):
        super().__init__(sprite_group)
        self.grid = grid
        self.row = row
        self.col = col
        self.attacked = False
        self.color = color_ind
        self.dead = False
        self.attackedTimer = 240
        self.deathTimer = 120
        self.counter = 0
        self.path = []
        try:
            self.frame = 0
            self.anim = {}
            for i in range(6):
                self.anim[i] = load_image(os.path.join("ghost_sprites", "ghost_" + str(i) + ".gif"))
            self.color_frames(ghost_color[0], ghost_color[self.color])
            self.image = self.anim[0]
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y, *_ = get_rect(self.row, self.col)
        except FileNotFoundError:
            self.image = pygame.Surface((TILE, TILE))
            self.image.fill(pygame.Color("green"))
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y, *_ = get_rect(self.row, self.col)
        # Usual code
        self.restricted = ["|", "-", "1", "2", "3", "4", 1, 2, 3, 4]
        self.allowed = ["0", 0, ".", "*", "?"]
        self.graph = {}
        for y, row in enumerate(grid):
            for x, col in enumerate(row):
                if col in self.allowed:
                    self.graph[(x, y)] = self.graph.get((x, y), []) + self.get_next_nodes(x, y)
                else:
                    self.graph[(x, y)] = []

    def color_frames(self, from_color: Color, to_color: Color):
        for i in range(6):
            palette = list(self.anim[i].get_palette())
            for j, c in enumerate(palette):
                if c == from_color:
                    palette[j] = to_color
            self.anim[i].set_palette(palette)

    def move(self, goal, pacman_pos):
        if goal and self.graph[goal]:
            if not self.attacked and not self.dead:
                real_goal = goal
            elif self.attacked and not self.dead:
                self.color_frames(ghost_color[self.color], ghost_color[4])
                distances = {}
                for node in self.get_next_nodes(self.row, self.col):
                    distances[node] = sqrt((pacman_pos[0] - node[0]) ** 2 + (pacman_pos[1] - node[1]) ** 2)
                for el in distances.keys():
                    if distances[el] == max(distances.values()):
                        real_goal = el
            elif self.dead:
                self.color_frames(ghost_color[self.color], Color(0, 0, 0, 255))
                real_goal = choice(ghostGate)

            if self.counter == 0:
                self.path = self.find_path((self.row, self.col), real_goal)
            self.counter = (self.counter + 1) % 18
            self.frame = (self.frame + 1) % 6
            self.image = self.anim[self.frame]
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y, *_ = get_rect(self.row, self.col)
            if self.path and len(self.path) > 1:
                self.move_to_one_node((self.row, self.col), self.path[1])
        return None

    def move_to_one_node(self, from_node, to_node):
        if from_node[0] < to_node[0]:
            self.rect = self.rect.move(1, 0)
        elif from_node[0] > to_node[0]:
            self.rect = self.rect.move(-1, 0)
        elif from_node[1] < to_node[1]:
            self.rect = self.rect.move(0, 1)
        elif from_node[1] > to_node[1]:
            self.rect = self.rect.move(0, -1)
        else:
            if self.attacked:
                self.setDead(True)
            else:
                return ValueError("YOUR STUPID PACMAN DEAD")

    def get_next_nodes(self, x, y):
        check_node = lambda x, y: True if (0 <= x < cols) and (0 <= y < rows) and \
                                          (self.grid[y][x] in self.allowed) else False
        ways = [0, -1], [0, 1], [1, 0], [-1, 0]
        return [(x + dx, y + dy) for dx, dy in ways if check_node(x + dx, y + dy)]

    def cleanup(self):
        self.parent = dict()
        self.queue = ""
        self.node = ""
        self.path = []

    def find_path(self, start_point, end_point):
        self.cleanup()
        self.parent, self.queue = {start_point: None}, deque([start_point])

        if start_point not in self.graph:
            raise ValueError("Start point is not in graph")
        if end_point not in self.graph:
            raise ValueError("End point is not in graph")
        while self.queue:
            self.node = self.queue.popleft()
            for neighbour in self.graph[self.node]:
                if self.node == end_point:
                    self.path = [self.node]
                    n = self.parent.get(self.node)
                    while n is not None:
                        self.path.append(n)
                        n = self.parent.get(n)
                    return self.path[::-1]
                if neighbour not in self.parent:
                    self.queue.append(neighbour)
                    self.parent[neighbour] = self.node
        return None

    def setAttacked(self, isAttacked):
        self.attacked = isAttacked

    def isAttacked(self):
        return self.attacked

    def setDead(self, isDead):
        self.dead = isDead

    def isDead(self):
        return self.dead


def load_image_pacman(name, colorkey=None):
    fullname = os.path.join('data/pacman_sprites', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


def load_level(filename):
    filename = "levels/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    global base_group
    new_player, x, y, pacman_pos = None, None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
                pacman_pos = [x, y]
            elif level[y][x] in list(values.keys()):
                Tile(values[level[y][x]], x, y)
    return new_player, x, y, pacman_pos


def terminate():
    pygame.quit()
    sys.exit()


def print_intro():
    screen.fill('black')
    pygame.display.set_caption('play pacman')
    pygame.draw.rect(screen, 'yellow', (100, 300, 300, 50), 1)
    pygame.display.flip()
    intro_text = ["Welcome to", "PACMAN",
                  "Введите название своего уровня", "или", "сразу нажмите Enter для начала игры"]
    font = pygame.font.Font(None, 40)
    string_rendered = font.render(intro_text[0], 1, pygame.Color('yellow'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top = 50
    intro_rect.x = 250 - intro_rect.width // 2
    screen.blit(string_rendered, intro_rect)
    font = pygame.font.Font(None, 80)
    string_rendered = font.render(intro_text[1], 3, pygame.Color('yellow'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top = 80
    intro_rect.x = 250 - intro_rect.width // 2
    screen.blit(string_rendered, intro_rect)
    font = pygame.font.Font(None, 20)
    for i in range(2, 5):
        string_rendered = font.render(intro_text[i], 1, pygame.Color('yellow'))
        intro_rect = string_rendered.get_rect()
        intro_rect.top = 250 + 15 * (i - 2)
        intro_rect.x = 250 - intro_rect.width // 2
        screen.blit(string_rendered, intro_rect)
    picture = pygame.transform.scale(load_image('intro_picture.jpg'), (300, 70))
    screen.blit(picture, (100, 400))


def print_text(text):
    font = pygame.font.Font(None, 40)
    text_coord = 310
    pygame.draw.rect(screen, 'black', (105, 305, 290, 40), 0)
    string_rendered = font.render(text, 20, pygame.Color('yellow'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top = text_coord
    intro_rect.x = 110
    screen.blit(string_rendered, intro_rect)
    pygame.display.flip()


def start_screen():
    need_input = False
    input_text = ''
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif need_input is False and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return 'default_level'
            elif need_input and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return input_text
                elif event.key == pygame.K_BACKSPACE:
                    if len(input_text) > 0:
                        input_text = input_text[:-1]
                else:
                    if len(input_text) <= 20:
                        input_text += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.pos[0] > 100 and event.pos[0] < 400 and \
                        event.pos[1] > 300 and event.pos[1] < 350:
                    need_input = True
        print_text(input_text)
        pygame.display.flip()


def show_level(level, count1, count2):
    pygame.init()
    size = count1 * 18 + 100, count2 * 18 + 100
    screen = pygame.display.set_mode(size)
    screen.fill('black')
    pygame.display.set_caption('play pacman')
    try:
        player, level_x, level_y, _ = generate_level(load_level(level))
    except FileNotFoundError:
        player, level_x, level_y, _ = generate_level(load_level('default_level.txt'))
    all_sprites.draw(screen)
    pygame.display.flip()
    return player, level_x, level_y


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = load_image_pacman('pacman.gif')
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.x = tile_width * pos_x
        self.y = tile_height * pos_y
        self.score = 0

    def pacman_location(self):
        return (self.x, self.y)

    # проверяет все столкновения
    def collides(self):
        lst = ['vertical', 'horisontal', '1', '2', '3', '4', 'gate']
        if pygame.sprite.spritecollideany(self, tiles_group) is None or \
                pygame.sprite.spritecollideany(self, tiles_group).image in [tile_images[_] for _ in lst]:
            return False
        else:
            if pygame.sprite.spritecollideany(self, tiles_group).image is tile_images['point']:
                self.score += 10
                tile = pygame.sprite.spritecollideany(self, tiles_group)
                tile.image = tile_images['empty']
            elif pygame.sprite.spritecollideany(self, tiles_group).image is tile_images['energo']:
                self.score += 50
                tile = pygame.sprite.spritecollideany(self, tiles_group)
                tile.image = tile_images['empty']
            # СЮДА ДОПИСАТЬ ОБРАБОТКУ СТОЛКНОВЕНИЙ С ПРИЗРАКАМИ
            return True

    # обрабатывает движение пакмена влево
    def update_left(self, number):
        self.rect = self.rect.move(-1, 0)
        fl = self.collides()
        self.rect = self.rect.move(1, 0)
        if fl:
            self.rect = self.rect.move(-1, 0)
            self.x -= 1
        lst_picture = ['l_0', 'l_1', 'l_2', 'l_3', 'l_4', 'l_5', 'l_6', 'l_7', 'l_0']
        self.image = load_image_pacman(lst_picture[number] + '.gif')

    # обрабатыает движения пакмена вправо
    def update_right(self, number):
        self.rect = self.rect.move(18, 0)
        fl = self.collides()
        self.rect = self.rect.move(-18, 0)
        if fl:
            self.x += 1
            self.rect = self.rect.move(1, 0)
        lst_picture = ['r_0', 'r_1', 'r_2', 'r_3', 'r_4', 'r_5', 'r_6', 'r_7', 'r_0']
        self.image = load_image_pacman(lst_picture[number] + '.gif')

    # обрабатывает движения пакмена вверх
    def update_up(self, number):
        self.rect = self.rect.move(0, -1)
        fl = self.collides()
        self.rect = self.rect.move(0, 1)
        if fl:
            self.rect = self.rect.move(0, -1)
            self.y -= 1
        lst_picture = ['u_0', 'u_1', 'u_2', 'u_3', 'u_4', 'u_5', 'u_6', 'u_7', 'u_0']
        self.image = load_image_pacman(lst_picture[number] + '.gif')

    # обрабатывает движения пакмена вниз
    def update_down(self, number):
        self.rect = self.rect.move(0, 18)
        fl = self.collides()
        self.rect = self.rect.move(0, -18)
        if fl:
            self.y += 1
            self.rect = self.rect.move(0, 1)
        lst_picture = ['d_0', 'd_1', 'd_2', 'd_3', 'd_4', 'd_5', 'd_6', 'd_7', 'd_0']
        self.image = load_image_pacman(lst_picture[number] + '.gif')