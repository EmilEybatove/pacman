import os
import pygame as pg
import sys
from random import random
from collections import deque
from time import sleep


def get_rect(x, y):
    return x * TILE + 1, y * TILE + 1, TILE - 2, TILE - 2


def get_click_mouse_pos():
    x, y = pg.mouse.get_pos()
    grid_x, grid_y = x // TILE, y // TILE
    click = pg.mouse.get_pressed()
    return (grid_x, grid_y) if click[0] else False


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pg.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Hunter(pg.sprite.Sprite):
    def __init__(self, sprite_group, start_pos, grid, pic=None):
        super().__init__(sprite_group)
        if pic:
            self.image = load_image(pic)
            self.rect = self.image.get_rect()
        else:
            self.image = pg.Surface((TILE, TILE))
            self.image.fill(pg.Color("green"))
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y, *_ = get_rect(*start_pos)
        # Usual code
        self.restricted = ["|", "-", "1", "2", "3", "4", 1, 2, 3, 4]
        self.allowed = ["0", 0, "."]

        self.graph = {}
        for y, row in enumerate(grid):
            for x, col in enumerate(row):
                if col in self.allowed:
                    self.graph[(x, y)] = self.graph.get((x, y), []) + self.get_next_nodes(x, y)

    def move(self, mouse_pos):
        if grid[mouse_pos[1]][mouse_pos[0]] in self.allowed:
            path = self.bfs(mouse_pos)
            if not path:
                return None
            self.rect.x, self.rect.y, *_ = get_rect(*path[-1])
            return path


    def get_next_nodes(self, x, y):
        check_next_node = lambda x, y: True if (0 <= x < cols) and (0 <= y < rows) and \
                                               (grid[y][x] in self.allowed) else False
        ways = [0, -1], [0, 1], [1, 0], [-1, 0]
        return [(x + dx, y + dy) for dx, dy in ways if check_next_node(x + dx, y + dy)]

    def bfs(self, end_point):
        start_point = self.rect.x // TILE, self.rect.y // TILE
        self.parent, self.queue = {start_point: None}, deque([start_point])

        if start_point not in self.graph:
            raise ValueError("Start point is not in graph")
        if end_point not in self.graph:
            raise ValueError("End point is not in graph")
        while self.queue:
            node = self.queue.popleft()
            for neighbour in self.graph[node]:
                if node == end_point:
                    path = [node]
                    n = self.parent.get(node)
                    while n is not None:
                        path.append(n)
                        n = self.parent.get(n)
                    return path[::-1]
                if neighbour not in self.parent:
                    self.queue.append(neighbour)
                    self.parent[neighbour] = node
        return None


if __name__ == '__main__':
    pg.init()
    SIZE = cols, rows = 25, 15
    TILE = 20
    sc = pg.display.set_mode([cols * TILE, rows * TILE])
    clock = pg.time.Clock()
    all_sprites = pg.sprite.Group()

    grid = [[1 if random() < 0.2 else 0 for col in range(cols)] for row in range(rows)]

    start_pos = (24, 14)
    hunter = Hunter(all_sprites, start_pos, grid)
    all_sprites.add(hunter)
    sc.fill(pg.Color('black'))

    while True:
        # draw cells
        [[pg.draw.rect(sc, pg.Color("darkorange"), get_rect(x, y), border_radius=TILE // 5)
          for x, col in enumerate(row) if col] for y, row in enumerate(grid)]
        # Where did we click - path to mouse position
        mouse_pos = get_click_mouse_pos()
        if mouse_pos:
            path = hunter.move(mouse_pos)
            if path:
                print("PATH!")
                for path_segment in path:
                    pg.draw.rect(sc, pg.Color("magenta"), get_rect(*path_segment), border_radius=TILE // 3)

        # Just some pygame stuff
        [sys.exit() for event in pg.event.get() if event.type == pg.QUIT]
        all_sprites.draw(sc)
        all_sprites.update()
        pg.display.flip()
        pg.display.set_caption(str(clock.get_fps()))
        sc.fill(pg.Color('black'))
