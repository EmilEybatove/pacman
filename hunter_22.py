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
    pg.draw.rect(sc, pg.Color('red'), get_rect(grid_x, grid_y))
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
        # Usual code
        self.rect.x, self.rect.y = start_pos
        self.graph = {}
        for y, row in enumerate(grid):
            for x, col in enumerate(row):
                if not col:
                    self.graph[(x, y)] = self.graph.get((x, y), []) + self.get_next_nodes(x, y)
        self.graph[(0, 0)] = (0, 1)
        self.queue = deque([(self.rect.x, self.rect.y)])
        self.visited = {(self.rect.x, self.rect.y): None}
        print(self.graph.keys(), flush=True)

    def move(self, mouse_pos):
        if not grid[mouse_pos[1]][mouse_pos[0]]:
            self.bfs(mouse_pos)
        # К этому моменту у нас есть self.queue и self.visited, оформленные правильно
        print(f"\nself.visited: {self.visited}", flush=True)
        print(f"\nself.queue: {self.queue}", flush=True)
        # Она же измениться должна
        path_head, path_segment = mouse_pos, mouse_pos
        while path_segment and path_segment in self.visited:
            self.rect.x, self.rect.y = get_rect(*path_segment)[:2]
            sleep(0.1)
            path_segment = self.visited[path_segment]
        pg.draw.rect(sc, pg.Color("magenta"), get_rect(*path_head), border_radius=TILE // 3)

    def get_next_nodes(self, x, y):
        check_next_node = lambda x, y: True if 0 <= x < cols and 0 <= y < rows and not grid[y][x] else False
        ways = [0, -1], [0, 1], [1, 0], [-1, 0]
        return [(x + dx, y + dy) for dx, dy in ways if check_next_node(x + dx, y + dy)]

    def bfs(self, goal):
        self.queue = deque([(self.rect.x, self.rect.y)])
        self.visited = {(self.rect.x, self.rect.y): None}

        while len(self.queue) >= 2:
            cur_node = self.queue.popleft()
            print(cur_node, flush=True)
            if cur_node == goal:
                break
            next_nodes = self.graph[cur_node]
            for next_node in next_nodes:
                if next_node not in self.visited:
                    self.queue.append(next_node)
                    self.visited[next_node] = cur_node
            print("The end!", len(self.queue))


if __name__ == '__main__':
    pg.init()
    SIZE = cols, rows = 25, 15
    TILE = 20
    sc = pg.display.set_mode([cols * TILE, rows * TILE])
    clock = pg.time.Clock()
    all_sprites = pg.sprite.Group()

    grid = [[1 if random() < 0.2 else 0 for col in range(cols)] for row in range(rows)]

    real_start_pos = (0, 0)
    hunter = Hunter(all_sprites, real_start_pos, grid)
    all_sprites.add(hunter)
    sc.fill(pg.Color('black'))

    while True:
        # draw cells
        [[pg.draw.rect(sc, pg.Color("darkorange"), get_rect(x, y), border_radius=TILE // 5)
          for x, col in enumerate(row) if col] for y, row in enumerate(grid)]
        # Where did we click - path to mouse position
        mouse_pos = get_click_mouse_pos()
        if mouse_pos:
            hunter.move(mouse_pos)

        # Just some pygame stuff
        [sys.exit() for event in pg.event.get() if event.type == pg.QUIT]
        all_sprites.draw(sc)
        all_sprites.update()
        pg.display.flip()
        pg.display.set_caption(str(clock.get_fps()))