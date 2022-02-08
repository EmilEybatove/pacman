import os
import sys
from collections import deque
from pprint import pprint
from random import sample, choice, random
import pygame
from pygame import Color
from math import sqrt
import threading

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
hunter_group = pygame.sprite.Group()
pause_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, color=None, groups=(tiles_group, all_sprites)):
        super().__init__(*groups)
        self.cords = [pos_x, pos_y]
        self.image = tile_images[tile_type]
        self.color = color
        if self.color:
            self.coloring()
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

    def coloring(self):
        for x in range(18):
            for y in range(18):
                real_color = self.image.get_at((x, y))
                if  real_color == pygame.Color((132, 0, 132, 255)):
                    self.image.set_at((x, y), self.color)
                elif real_color == pygame.Color((255, 0, 255, 255)):
                    self.image.set_at((x, y), pygame.Color((255, 206, 255, 255)))


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
        self.color = color_ind
        self.attacked = False
        self.dead = False
        self.counter = 0
        self.start_pos = [row, col]
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
        if color_ind == 0:  # Потому что надо вызвать только один раз
            get_available_nodes((self.row, self.col))
            # print(available_nodes)

    def new(self):
        self.row = self.start_pos[0]
        self.col = self.start_pos[1]
        self.rect.x = self.start_pos[0] * TILE
        self.rect.y = self.start_pos[1] * TILE
        self.counter = 0
        self.setDead(False)
        self.setAttacked(False)

    def color_frames(self, from_color: Color, to_color: Color):
        for i in range(6):
            palette = list(self.anim[i].get_palette())
            for j, c in enumerate(palette):
                if c == from_color:
                    palette[j] = to_color
            self.anim[i].set_palette(palette)

    def move(self, goal, grid):
        real_goal = ""
        if goal and graph[goal]:
            if self.attacked:
                self.color_frames(ghost_color[self.color], ghost_color[4])
                distances = {}
                for node in self.get_next_nodes(self.row, self.col, grid):
                    distances[node] = sqrt((node[0] - goal[0]) ** 2 + (node[1] - goal[1]) ** 2)
                for el in distances.keys():
                    if distances[el] == max(distances.values()):
                        real_goal = el
            if self.dead:
                self.color_frames(ghost_color[4], Color(0, 0, 0, 255))
                if (self.row, self.col) in ghostGate:
                    self.setDead(False)
                real_goal = choice(ghostGate)
            if not self.attacked and not self.dead:
                self.color_frames(Color(0, 0, 0, 255), ghost_color[self.color])
                self.color_frames(ghost_color[4], ghost_color[self.color])
                real_goal = goal
            if self.counter == 0:
                self.row, self.col = int(self.rect.x / 18), int(self.rect.y / 18)
                self.path = find_path((self.row, self.col), real_goal)
            self.counter = (self.counter + 1) % 18
            self.frame = (self.frame + 1) % 6
            self.image = self.anim[self.frame]
            # print(f"We are now at position {self.row, self.col} and gonna go to {real_goal}")
            # print(f"Our path is {self.path}")
            if self.path and len(self.path) > 1:
                final_goal = self.path[1]
                if self.row < final_goal[0]:
                    self.rect.x += 1
                elif self.row > final_goal[0]:
                    self.rect.x -= 1
                elif self.col < final_goal[1]:
                    self.rect.y += 1
                elif self.col > final_goal[1]:
                    self.rect.y -= 1

    def get_next_nodes(self, x, y, grid):
        check_node = lambda x, y: True if (0 <= x < cols) and (0 <= y < rows) and \
                                          (grid[y][x] in allowed) else False
        ways = [0, -1], [0, 1], [1, 0], [-1, 0]
        return [(x + dx, y + dy) for dx, dy in ways if check_node(x + dx, y + dy)]

    def closest_available_node(self, search_node):
        distances = {}
        for node in available_nodes:
            if node != (self.row, self.col):
                distances[node] = sqrt((node[0] - search_node[0]) ** 2 + (node[1] - search_node[1]) ** 2)
        for el in distances.keys():
            if distances[el] == min(distances.values()):
                return el

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


def generate_level(level, color):
    global cols, rows, ghostGate
    points = 0
    rows = len(level)
    cols = len(level[0])
    new_player, x, y, pacman_pos = None, None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '@':
                Tile('empty', x, y, color)
                new_player = Player(x, y)
                pacman_pos = [x, y]
            elif level[y][x] in list(values.keys()):
                if level[y][x] in ['0', '*']:
                    points += 1
                Tile(values[level[y][x]], x, y, color)
    for i in [-3, -2, -1, 0, 1, 2]:
        for j in [-1, 0]:
            ghostGate.append((cols // 2 + i, rows // 2 + j))
    return new_player, x, y, pacman_pos, points, ghostGate


def terminate():
    pygame.quit()
    sys.exit()


def return_path(game, num, event, hunter):
    x, y = game.pacman_pos
    side = {
        'left': (-1, 0),
        'right': (1, 0),
        'up': (0, -1),
        'down': (0, 1)
    }
    if num == 0:
        return hunter.closest_available_node((x, y))

    if num == 1:
        return hunter.closest_available_node((x + side[event][0] * 2, y + side[event][1] * 2))

    if num == 2:
        return hunter.closest_available_node((x - side[event][0] * 2, y - side[event][1] * 2))

    if num == 3:
        if (x - hunter.row) ** 2 + (y - hunter.col) ** 2 <= 64:
            return hunter.closest_available_node((0, rows))
        return hunter.closest_available_node((x, y))


class PauseImage(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(pause_group)
        self.n = 0
        self.image = load_image('pause.png')
        self.rect = self.image.get_rect().move(pos_x, pos_y)

    def update(self):
        self.n += 1
        self.image = load_image('on.png' if self.n % 2 == 1 else 'pause.png')


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = load_image_pacman('pacman.gif')
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.x = tile_width * pos_x
        self.y = tile_height * pos_y
        self.score = 0
        self.start_pos = [pos_x, pos_y]
        self.counter = 1
        self.side_tuples = {
            'left': (-1, 0),
            'right': (1, 0),
            'up': (0, -1),
            'down': (0, 1)
        }

        self.check_tuple = {
            'left': (-1, 0),
            'right': (18, 0),
            'up': (0, -1),
            'down': (0, 18)
        }

        self.image_list = {
            'left': ['l_0', 'l_1', 'l_2', 'l_3', 'l_4', 'l_5', 'l_6', 'l_7', 'l_0'],
            'right': ['r_0', 'r_1', 'r_2', 'r_3', 'r_4', 'r_5', 'r_6', 'r_7', 'r_0'],
            'up': ['u_0', 'u_1', 'u_2', 'u_3', 'u_4', 'u_5', 'u_6', 'u_7', 'u_0'],
            'down': ['d_0', 'd_1', 'd_2', 'd_3', 'd_4', 'd_5', 'd_6', 'd_7', 'd_0']
        }

    def new(self):
        self.x = tile_width * self.start_pos[0]
        self.y = tile_height * self.start_pos[1]
        self.rect.x = self.x
        self.rect.y = self.y

    # проверяет все столкновения
    def collides(self):
        restricted = ['vertical', 'horizontal', '1', '2', '3', '4', 'gate', 'end-top', 'end-left', 'end-right', 'end-bottom']
        collide_list = pygame.sprite.spritecollideany(self, tiles_group)
        if collide_list is None or collide_list.image in [tile_images[_] for _ in restricted]:
            return False
        else:
            if collide_list.image is tile_images['point']:
                self.score += 10
                tile = pygame.sprite.spritecollideany(self, tiles_group)
                tile.image = tile_images['empty']
                return 'point'
            elif collide_list.image is tile_images['energo']:
                self.score += 50
                tile = pygame.sprite.spritecollideany(self, tiles_group)
                tile.image = tile_images['empty']
                return 'energo'
            return True

    # обрабатывает движение пакмена
    def update(self, number, side):
        self.rect = self.rect.move(self.check_tuple[side][0], self.check_tuple[side][1])
        fl = self.collides()
        self.rect = self.rect.move(-self.check_tuple[side][0], -self.check_tuple[side][1])
        if fl and fl != 'energo':
            self.rect = self.rect.move(self.side_tuples[side])
            self.x += self.side_tuples[side][0]
            self.y += self.side_tuples[side][1]
        lst_picture = self.image_list[side]
        self.image = load_image_pacman(lst_picture[number] + '.gif')
        if fl in ['point', 'energo']:
            return fl

class Player_hunter(pygame.sprite.Sprite):
    def __init__(self, sprite_group, row, col, color):
        """Color must be in pygame.Color() format!"""
        super().__init__(sprite_group)
        self.row = row
        self.col = col
        self.color = color
        self.attacked = False
        self.dead = False
        self.start_pos = [row, col]
        self.check_tuple = {
            'left': (-1, 0),
            'right': (18, 0),
            'up': (0, -1),
            'down': (0, 18)
        }
        self.side_tuples = {
            'left': (-1, 0),
            'right': (1, 0),
            'up': (0, -1),
            'down': (0, 1)
        }
        self.frame = 0
        self.anim = {}
        for i in range(6):
            self.anim[i] = load_image(os.path.join("ghost_sprites", "ghost_" + str(i) + ".gif"))
        self.color_frames(ghost_color[0], self.color)
        self.image = self.anim[0]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y, *_ = get_rect(self.row, self.col)
        # Usual code
        self.restricted = ["|", "-", "1", "2", "3", "4", 1, 2, 3, 4]
        self.allowed = ["0", 0, ".", "*", "?"]

    def new(self):
        self.row = self.start_pos[0]
        self.col = self.start_pos[1]
        self.rect.x = self.start_pos[0] * TILE
        self.rect.y = self.start_pos[1] * TILE
        self.setDead(False)
        self.setAttacked(False)

    def color_frames(self, from_color: Color, to_color: Color):
        for i in range(6):
            palette = list(self.anim[i].get_palette())
            for j, c in enumerate(palette):
                if c == from_color:
                    palette[j] = to_color
            self.anim[i].set_palette(palette)

    def move(self, side):
        if self.attacked:
            self.color_frames(self.color, ghost_color[4])
        elif self.dead:
            self.color_frames(self.color, Color(0, 0, 0, 255))

        self.rect = self.rect.move(self.check_tuple[side][0], self.check_tuple[side][1])
        if self.collides():
            self.rect = self.rect.move(-self.check_tuple[side][0], -self.check_tuple[side][1])
        self.row += self.side_tuples[side][0] // TILE
        self.col += self.side_tuples[side][1] // TILE

        # Update self.image
        self.frame = (self.frame + 1) % 6
        self.image = self.anim[self.frame]


    def collides(self):
        if pygame.sprite.spritecollideany(self, tiles_group) is not None:
            return True
        return False

    def setAttacked(self, isAttacked):
        self.attacked = isAttacked

    def isAttacked(self):
        return self.attacked

    def setDead(self, isDead):
        self.dead = isDead

    def isDead(self):
        return self.dead

def get_available_nodes(start_node):
    if graph.get(start_node):
        for node in graph.get(start_node):
            if node not in available_nodes:
                available_nodes.append(node)
                get_available_nodes(node)


def get_next_nodes(x, y, grid):
    check_node = lambda x, y: True if (0 <= x < len(grid[0])) and (0 <= y < len(grid)) and \
                                      (grid[y][x] in allowed) else False
    ways = [0, -1], [0, 1], [1, 0], [-1, 0]
    return [(x + dx, y + dy) for dx, dy in ways if check_node(x + dx, y + dy)]


def find_path(start_point, end_point):
    parent, queue = {start_point: None}, deque([start_point])
    if start_point not in graph:
        raise ValueError("Start point is not in graph")
    if end_point not in graph:
        raise ValueError("End point is not in graph")
    while queue:
        node = queue.popleft()
        for neighbour in graph[node]:
            if node == end_point:
                path = [node]
                n = parent.get(node)
                while n is not None:
                    path.append(n)
                    n = parent.get(n)
                # print(self.path[::-1])
                return path[::-1]
            if neighbour not in parent:
                queue.append(neighbour)
                parent[neighbour] = node
    return None



restricted = ["|", "-", "1", "2", "3", "4", 1, 2, 3, 4, "b", "l", "r", "t"]
allowed = ["0", 0, ".", "*", "?"]

graph = {}


def make_graph(grid):
    for y, row in enumerate(grid):
        for x, col in enumerate(row):
            if col in allowed:
                graph[(x, y)] = graph.get((x, y), []) + get_next_nodes(x, y, grid)
            else:
                # graph[(x, y)] = graph.get((x, y), ["unavailable"]) + get_next_nodes(x, y)
                graph[(x, y)] = []


TILE = tile_width = tile_height = 18

SCRIPT_PATH = None
if os.name == "nt":
    SCRIPT_PATH = os.getcwd()
else:
    SCRIPT_PATH = sys.path[0]

tile_images = {
    'vertical': load_image('walls/rose/vertical.png'),
    'horizontal': load_image('walls/rose/horizontal.png'),
    '1': load_image('walls/rose/1.png'),
    '2': load_image('walls/rose/2.png'),
    '3': load_image('walls/rose/4.png'),
    '4': load_image('walls/rose/3.png'),
    'empty': load_image('walls/rose/empty.png'),
    'point': load_image('walls/rose/point.png'),
    'energo': load_image('walls/rose/energo.png'),
    'gate': load_image('walls/rose/gate.png'),
    'end-top': load_image('walls/rose/end_t.png'),
    'end-bottom': load_image('walls/rose/end_b.png'),
    'end-left': load_image('walls/rose/end_l.png'),
    'end-right': load_image('walls/rose/end_r.png'),
    'pacman': load_image('pacman.png')
    }
values = {
    '|': 'vertical',
    '-': 'horizontal',
    '1': '1',
    '2': '2',
    '3': '3',
    '4': '4',
    '.': 'empty',
    '@': 'pacman',
    '*': 'energo',
    '0': 'point',
    '?': 'gate',
    't': 'end-top',
    'b': 'end-bottom',
    'l': 'end-left',
    'r': 'end-right'
}

# Must come before pygame.init()
pygame.mixer.pre_init(22050, -16, 1, 1024)
pygame.mixer.init()
pygame.mixer.set_num_channels(3)
channel_backgound = pygame.mixer.Channel(1)
main_channel = pygame.mixer.Channel(2)


snd_big_dot = pygame.mixer.Sound(os.path.join(SCRIPT_PATH, "data", "sounds", "ate_big_dot.wav"))
snd_small_dot = pygame.mixer.Sound(os.path.join(SCRIPT_PATH, "data", "sounds", "ate_small_dot.wav"))
snd_chase = pygame.mixer.Sound(os.path.join(SCRIPT_PATH, "data", "sounds", "chase.wav"))
snd_death = pygame.mixer.Sound(os.path.join(SCRIPT_PATH, "data", "sounds", "death.wav"))
snd_default = pygame.mixer.Sound(os.path.join(SCRIPT_PATH, "data", "sounds", "default.wav"))

songs = [pygame.mixer.Sound(os.path.join(SCRIPT_PATH, "data", "sounds", "songs", "Pensilvania polka.mp3")),
         pygame.mixer.Sound(os.path.join(SCRIPT_PATH, "data", "sounds", "songs", "Can't Smile Without You.mp3")),
         pygame.mixer.Sound(os.path.join(SCRIPT_PATH, "data", "sounds", "songs", "Clouds.mp3")),
         pygame.mixer.Sound(os.path.join(SCRIPT_PATH, "data", "sounds", "songs", "I got you babe.mp3")),
         pygame.mixer.Sound(os.path.join(SCRIPT_PATH, "data", "sounds", "songs", "Phil steals the money.mp3")),
         pygame.mixer.Sound(os.path.join(SCRIPT_PATH, "data", "sounds", "songs", "Take me round again.mp3")),
         pygame.mixer.Sound(os.path.join(SCRIPT_PATH, "data", "sounds", "songs", "The ice sculpture.mp3")),
         pygame.mixer.Sound(os.path.join(SCRIPT_PATH, "data", "sounds", "songs", "Weatherman.mp3"))]


available_nodes = []
ghostGate = []
ghost_color = [Color(255, 0, 0, 255),  # Red
               Color(255, 128, 255, 255),  # pink
               Color(128, 255, 255, 255),  # light blue
               Color(255, 128, 0, 255),  # orange
               Color(50, 50, 255, 255),  # blue vulnerable
               Color(255, 255, 255, 255)]  # white
cols, rows = 26, 26