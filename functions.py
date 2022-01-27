import os
import sys
from collections import deque
from pprint import pprint
from random import sample, choice, random
import pygame
from pygame import Color
import threading
from math import sqrt

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
hunter_group = pygame.sprite.Group()
pause_group = pygame.sprite.Group()
TILE = tile_width = tile_height = 18
SCRIPT_PATH = None
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

cols, rows = 26, 26


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
    'gate': load_image('gate.png')}

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
        self.color = color_ind
        self.attacked = False
        self.dead = False
        self.counter = 0
        self.path = []
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
        # Usual code
        self.restricted = ["|", "-", "1", "2", "3", "4", 1, 2, 3, 4]
        self.allowed = ["0", 0, ".", "*", "?"]
        self.graph = {}
        for y, row in enumerate(grid):
            for x, col in enumerate(row):
                if col in self.allowed:
                    self.graph[(x, y)] = self.graph.get((x, y), []) + self.get_next_nodes(x, y)
                else:
                    self.graph[(x, y)] = self.graph.get((x, y), ["unavailable"]) + self.get_next_nodes(x, y)
        self.available_nodes = self.get_available_nodes()

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

    def move(self, goal):
        if goal and self.graph[goal]:
            if self.attacked:
                self.color_frames(ghost_color[self.color], ghost_color[4])
                distances = {}
                for node in self.get_next_nodes(self.row, self.col):
                    distances[node] = sqrt((node[0] - goal[0]) ** 2 + (node[1] - goal[1]) ** 2)
                for el in distances.keys():
                    if distances[el] == max(distances.values()):
                        real_goal = el
                        # real_goal = choice([el for el in self.graph if self.graph[el]])
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
                self.path = self.find_path((self.row, self.col), real_goal)
            self.counter = (self.counter + 1) % 18
            self.frame = (self.frame + 1) % 6
            self.image = self.anim[self.frame]
            # print(f"We are now at position {self.row, self.col} and gonna go to {goal}")
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

    def get_next_nodes(self, x, y):
        check_node = lambda x, y: True if (0 <= x < cols) and (0 <= y < rows) and \
                                          (self.grid[y][x] in self.allowed) else False
        ways = [0, -1], [0, 1], [1, 0], [-1, 0]
        return [(x + dx, y + dy) for dx, dy in ways if check_node(x + dx, y + dy)]

    def get_available_nodes(self):
        check_node = lambda x, y: True if (0 <= x < cols) and (0 <= y < rows) and \
                                          (self.grid[y][x] in self.allowed) else False
        return [(x, y) for x in range(cols + 1) for y in range(rows + 1) if check_node(x, y)]

    def closest_available_node(self, search_node):
        distances = {}
        for node in self.available_nodes:
            distances[node] = sqrt((node[0] - search_node[0]) ** 2 + (node[1] - search_node[1]) ** 2)
        for el in distances.keys():
            if distances[el] == min(distances.values()):
                return el

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
                    # print(self.path[::-1])
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


# преобразование текстового файла в список спрайтов
def load_level(filename):
    filename = "levels/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


# создание уровня
def generate_level(level):
    global cols, rows
    points = 0
    rows = len(level)
    cols = len(level[0])
    new_player, x, y, pacman_pos = None, None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
                pacman_pos = [x, y]
            elif level[y][x] in list(values.keys()):
                if level[y][x] in ['0', '*']:
                    points += 1
                Tile(values[level[y][x]], x, y)

    return new_player, x, y, pacman_pos, points


def terminate():
    pygame.quit()
    sys.exit()


# оформление стартового окна
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


# отображение ввода текста пользователем в окне
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


# обработка ввода
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
                if 100 < event.pos[0] < 400 and 300 < event.pos[1] < 350:
                    need_input = True
        print_text(input_text)
        pygame.display.flip()



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




# класс пакмена
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
        lst = ['vertical', 'horisontal', '1', '2', '3', '4', 'gate']
        collid_lst = pygame.sprite.spritecollideany(self, tiles_group)
        if collid_lst is None or collid_lst.image in [tile_images[_] for _ in lst]:
            return False
        else:
            if collid_lst.image is tile_images['point']:
                self.score += 10
                tile = pygame.sprite.spritecollideany(self, tiles_group)
                tile.image = tile_images['empty']
                return 'point'
            elif collid_lst.image is tile_images['energo']:
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
