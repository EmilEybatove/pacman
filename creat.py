import os
import sys

import pygame

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
images_group = pygame.sprite.Group()
base_group = pygame.sprite.Group()
current = False


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
    'empty': load_image('empty.png')}

dct = {
    'vertical': '|',
    'horisontal': '-',
    '1': '1',
    '2': '2',
    '3': '3',
    '4': '4',
    'empty': '.'
}

tile_width = tile_height = 18


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, groups=(tiles_group, all_sprites)):
        super().__init__(*groups)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 50, tile_height * pos_y + 50)


values = {
    '.': 'empty',
    '|': 'vertical',
    '-': 'horisontal',
    '1': '1',
    '2': '2',
    '3': '3',
    '4': '4',
}


def generate_level(level):
    global base_group

    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] in list(values.keys()):
                Tile(values[level[y][x]], x, y)

    return new_player, x, y


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.number = 0
        self.board = [[' '] * width for _ in range(height)]
        self.center()

        self.left = 50
        self.top = 50
        self.cell_size = 18
        self.click = 0

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        for i in range(self.height):
            for j in range(self.width):
                b = i * self.cell_size + self.left
                a = j * self.cell_size + self.top
                pygame.draw.rect(screen, (255, 255, 255), (a, b, self.cell_size, self.cell_size), width=1)

    def get_click(self, mouse_pos, arr):
        cell = self.get_cell(mouse_pos)
        self.on_click(cell, arr)

    def get_cell(self, mouse_pos):
        if mouse_pos[0] > self.cell_size * self.width + self.left:
            return None
        if mouse_pos[1] > self.cell_size * self.height + self.top:
            return None
        return (mouse_pos[0] - self.left) // self.cell_size, (mouse_pos[1] - self.top) // self.cell_size

    def on_click(self, cell_coords, arr):
        if cell_coords is not None:
            self.board[cell_coords[1]][cell_coords[0]] = arr

    def center(self):
        global base_group
        base_group = pygame.sprite.Group()
        for i in [-2, -1, 0, 1]:
            for j in [-4, -3, -2, -1, 0, 1, 2, 3]:
                b, a = self.height // 2 + i, self.width // 2 + j
                if i == -2 and j == -4:
                    Tile(values['1'], a, b, (base_group,))
                    # self.board[self.height // 2 + i][self.width // 2 + j] = '1'
                elif i == -2 and j == 3:
                    Tile(values['2'], a, b, (base_group,))
                    # self.board[self.height // 2 + i][self.width // 2 + j] = '2'
                elif i == 1 and j == 3:
                    Tile(values['4'], a, b, (base_group,))
                    # self.board[self.height // 2 + i][self.width // 2 + j] = '4'
                elif i == 1 and j == -4:
                    Tile(values['3'], a, b, (base_group,))
                    # self.board[self.height // 2 + i][self.width // 2 + j] = '3'
                elif i in [-2, 1]:
                    Tile(values['-'], a, b, (base_group,))
                    # self.board[self.height // 2 + i][self.width // 2 + j] = '-'
                elif j in [-4, 3]:
                    Tile(values['|'], a, b, (base_group,))
                    # self.board[self.height // 2 + i][self.width // 2 + j] = '|'
                else:
                    Tile(values['.'], a, b, (base_group,))
                    # self.board[self.height // 2 + i][self.width // 2 + j] = '.'

    def size_event(self, event_num):
        if event_num == 0:
            if self.width % 2 == 1:
                for i in [-2, -1, 0, 1]:
                    self.board[self.height // 2 + i][self.width // 2 - 4] = ' '
            self.width += 1
            self.board = [elem + [' '] for elem in self.board]
        elif event_num == 2:
            self.width -= 1
            self.board = [elem[:-1] for elem in self.board]

        elif event_num == 1:
            self.height += 1
            self.board.append([' '] * self.width)
        elif event_num == 3:
            self.height -= 1
            self.board = self.board[:-1]
        self.center()


class Images(pygame.sprite.Sprite):
    def __init__(self, tile_type, number, a):
        super().__init__(images_group)
        self.image = tile_images[tile_type]
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect().move(835 if a == 0 else 895, number * 80 + 50)


def cords(mouse_pos):
    a, b = -1, -1
    if mouse_pos[0] in range(835, 885):
        a = 0
    elif mouse_pos[0] in range(895, 945):
        a = 1

    for i in range(4):
        if mouse_pos[1] in range(50 + i * 80, 100 + i * 80):
            b = i
            break

    if a >= 0 and b >= 0 and not (a == 1 and b == 3):
        return b * 2 + a
    return None


def draw(screen, x, y):
    pygame.draw.rect(screen, (50, 50, 50), (560, 55, 200, 70), width=0)
    font = pygame.font.Font(None, 50)
    text = font.render(f"{x}×{y}", True, (255, 255, 0))
    text_x = 610
    text_y = 70
    screen.blit(text, (text_x, text_y))


arrows_group = pygame.sprite.Group()


class Arrows(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(arrows_group)
        self.image = load_image(tile_type)
        self.rect = self.image.get_rect().move(pos_x, pos_y)


Arrows('up.png', 560, 55)
Arrows('down.png', 560, 90)
Arrows('up.png', 725, 55)
Arrows('down.png', 725, 90)


def arrows(pos_x, pos_y):
    a = 0 if pos_x in range(560, 595) else 1 if pos_x in range(725, 760) else -1
    b = 0 if pos_y in range(55, 90) else 1 if pos_y in range(90, 125) else -1
    return b * 2 + a if a >= 0 and b >= 0 else None


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Создание поля')
    size = width, height = 1000, 650
    screen = pygame.display.set_mode(size)
    number1, number2 = 25, 25
    board = Board(number1, number2)
    running = True
    player, level_x, level_y = generate_level([''.join(elem) for elem in board.board])
    a = 0

    for elem in tile_images:
        Images(elem, a // 2, a % 2)
        a += 1
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if cords(event.pos) is not None:
                    current = dct[list(tile_images.keys())[cords(event.pos)]]
                if current:
                    board.get_click(event.pos, current)

                if arrows(event.pos[0], event.pos[1]) is not None:
                    a = arrows(event.pos[0], event.pos[1])
                    board.size_event(a)
                    number1 = number1 + 1 if a == 0 else number1 - 1 if a == 2 else number1
                    number2 = number2 + 1 if a == 1 else number2 - 1 if a == 3 else number2

                player, level_x, level_y = generate_level([''.join(elem) for elem in board.board])
                a = 0
                for elem in tile_images:
                    Images(elem, a // 2, a % 2)
                    a += 1
        screen.fill((0, 0, 0))
        board.render(screen)
        pygame.draw.rect(screen, (50, 50, 50), (800, 20, 180, 610))
        all_sprites.draw(screen)
        tiles_group.draw(screen)
        player_group.draw(screen)
        images_group.draw(screen)
        draw(screen, number1, number2)
        arrows_group.draw(screen)
        base_group.draw(screen)

        pygame.display.flip()
    pygame.quit()
