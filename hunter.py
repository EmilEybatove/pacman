import os
import sys
from collections import deque
from pprint import pprint
from random import choice

import pygame


def get_rect(x, y):
    return x * TILE + 1, y * TILE + 1, TILE - 2, TILE - 2


class Pacman:
    def packman_location(self):
        return (24, 24)
        # return self.get_click_mouse_pos()

    def get_click_mouse_pos(self):
        x, y = pygame.mouse.get_pos()
        grid_x, grid_y = x // TILE, y // TILE
        click = pygame.mouse.get_pressed()
        return (grid_x, grid_y) if click[0] else False


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
    else:
        image = image.convert_alpha()
    return image


class Hunter(pygame.sprite.Sprite):
    def __init__(self, sprite_group, row, col, grid, color_ind):
        super().__init__(sprite_group)
        self.row = row
        self.col = col
        self.attacked = False
        self.color = color_ind
        self.dead = False
        self.ghostSpeed = 1 / 4
        self.attackedTimer = 240
        self.deathTimer = 120
        try:
            self.frame = 0
            self.anim = {}
            for i in range(6):
                self.anim[i] = load_image(os.path.join("ghost_sprites", "ghost_" + str(i) + ".gif"))
            self.color_frames(ghost_color[0], ghost_color[self.color])
            self.image = self.anim[0]
            self.rect = self.image.get_rect()
            # print(f"row, col: {row, col}")
            # print(f"get_rect returns: {get_rect(row, col)}")
            # print(f"size of field: {cols, rows}, REALLY: {cols * TILE, rows * TILE}")
            self.rect.x, self.rect.y, *_ = get_rect(self.row, self.col)
        except FileNotFoundError:
            self.image = pygame.Surface((TILE, TILE))
            self.image.fill(pygame.Color("green"))
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y, *_ = get_rect(self.row, self.col)
        # Usual code
        self.restricted = ["|", "-", "1", "2", "3", "4", 1, 2, 3, 4]
        self.allowed = ["0", 0, ".", "*", "?"]
        # print(f"self.allowed: {self.allowed}")
        self.graph = {}
        for y, row in enumerate(grid):
            for x, col in enumerate(row):
                if col in self.allowed:
                    self.graph[(x, y)] = self.graph.get((x, y), []) + self.get_next_nodes(x, y)
                else:
                    self.graph[(x, y)] = []

        # print("And here is our graph: ")
        # pprint(self.graph)

    def update(self):  # Ghosts states: Alive, Attacked, Dead Attributes: Color, Direction, Location
        if not self.attacked and not self.dead:
            self.frame += 1
            if self.frame >= len(self.anim):
                self.frame = 0
        elif self.attacked:
            self.color_frames(ghost_color[self.color], ghost_color[4])
            self.frame += 1
            if self.frame >= len(self.anim):
                self.frame = 0
            # [Q timer works here than color sprite to blue/white and then recolor to define one]
        else:
            self.color_frames(ghost_color[self.color], (0, 0, 0, 0))
            self.move(choice(ghostGate))

        self.image = self.anim[self.frame]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y, *_ = get_rect(self.row, self.col)

    def color_frames(self, from_color, to_color):
        for i in range(6):
            for x in range(16):
                for y in range(16):
                    if self.anim[i].get_at((x, y)) == from_color:
                        self.anim[i].set_at((x, y), to_color)
                        # blue vulnerable

    def move(self, goal):
        if goal and self.graph[goal]:
            if not self.attacked and not self.dead:
                # print(f"We are now at position {self.row, self.col} and gonna go to {goal}")
                path = self.find_path((self.row, self.col), goal)
                # print(f"Our path is {path}")
                if path and len(path) > 1:
                    final = path[1]
                    # print(f"Finally go to {final}")
                    self.row, self.col = final
                return
            elif self.attacked:
                goal = choice([el for el in self.graph if self.graph[el]])
                path = self.find_path((self.row, self.col), goal)
                if path and len(path) > 1:
                    final = path[1]
                    self.row, self.col = final
                return
            else:
                goal = choice(ghostGate)
                path = self.find_path((self.row, self.col), goal)
                if path and len(path) > 1:
                    final = path[1]
                    self.row, self.col = final
                return
        return None

    def get_next_nodes(self, x, y):
        check_node = lambda x, y: True if (0 <= x < cols) and (0 <= y < rows) and \
                                               (grid[y][x] in self.allowed) else False
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



if __name__ == '__main__':
    pygame.init()
    SIZE = cols, rows = 26, 26
    TILE = 18
    sc = pygame.display.set_mode([cols * TILE, rows * TILE])
    clock = pygame.time.Clock()
    if os.name == "nt":
        SCRIPT_PATH = os.getcwd()
    else:
        SCRIPT_PATH = sys.path[0]
    all_sprites = pygame.sprite.Group()

    with open("levels/Level_1.txt", 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    grid = list(map(lambda x: x.ljust(max_width, '.'), level_map))
    # print("This is our grid: ")
    # pprint(grid)
    # grid = [[1 if random() < 0.01 else 0 for col in range(cols)] for row in range(rows)]
    restricted = ["|", "-", "1", "2", "3", "4", 1, 2, 3, 4]
    allowed = ["0", 0, ".", "*"]

    # REDACT!!!!!
    ghostGate = [(10, 12), (11, 12), (12, 12), (13, 12), (14, 12), (15, 12),
                 (10, 13), (11, 13), (12, 13), (13, 13), (14, 13), (15, 13)]
    # GONNA WORK ONLY FOR DEFAULT MAP!!
    ghost_color = [(255, 0, 0, 255), (255, 128, 255, 255), (128, 255, 255, 255),
                   (255, 128, 0, 255), (50, 50, 255, 255), (255, 255, 255, 255)]
    # Red, pink, blue, orange
    # blue vulnerable, white
    ghosts = []
    for col in range(4):
        start_pos = x, y = choice(ghostGate)
        # print(f"Start position of ghost {col}: {start_pos}, x: {x}, y: {y}")
        hunter: Hunter = Hunter(all_sprites, x, y, grid, col)
        ghosts.append(hunter)
        all_sprites.add(hunter)

    pacman = Pacman()

    while True:
        sc.fill(pygame.Color('black'))
        # draw cells
        [[pygame.draw.rect(sc, pygame.Color("darkorange"), get_rect(x, y), border_radius=TILE // 5)
          for x, col in enumerate(row) if col in restricted] for y, row in enumerate(grid)]
        # Where do we go - path to mouse position
        goal = pacman.get_click_mouse_pos()
        # ghosts[0].setAttacked(True)
        if goal and ghosts[0].graph[goal]:
            for hunter in ghosts:
                if (hunter.row, hunter.col) != goal:
                    hunter.move(choice(hunter.get_next_nodes(goal[0], goal[1])))
                    all_sprites.draw(sc)
                    all_sprites.update()
        # Just some pygame stuff
        [sys.exit() for event in pygame.event.get() if event.type == pygame.QUIT]
        all_sprites.draw(sc)
        all_sprites.update()
        pygame.display.flip()
        clock.tick(20)
        pygame.display.set_caption("Pacman")