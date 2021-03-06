import os
import sys

import pygame
from copy import deepcopy

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
images_group = pygame.sprite.Group()
base_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

exit_game = pygame.sprite.Sprite()
exit_game.image = pygame.Surface((125, 40))
exit_game.rect = pygame.Rect(600, 570, 125, 40)
exit_game.image.fill((200, 0, 0))
exit_group.add(exit_game)
save_text = 'Не сохранено'


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
    'vertical': load_image('walls/rose/vertical.png'),
    'horizontal': load_image('walls/rose/horizontal.png'),
    '1': load_image('walls/rose/1.png'),
    '2': load_image('walls/rose/2.png'),
    '3': load_image('walls/rose/4.png'),
    '4': load_image('walls/rose/3.png'),
    'empty': load_image('walls/rose/empty.png'),
    'pacman': load_image('pacman.png'),
    'energo': load_image('walls/rose/energo.png'),
    'point': load_image('walls/rose/point.png'),
    'end-top': load_image('walls/rose/end_t.png'),
    'end-bottom': load_image('walls/rose/end_b.png'),
    'end-left': load_image('walls/rose/end_l.png'),
    'end-right': load_image('walls/rose/end_r.png'),
    'gate': load_image('walls/rose/gate.png')
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
    't': 'end-top',
    'b': 'end-bottom',
    'l': 'end-left',
    'r': 'end-right',
    '?': 'gate'
}

dct = {v: k for k, v in values.items()}

tile_width = tile_height = 18


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, groups=(tiles_group, all_sprites)):
        super().__init__(*groups)
        self.cords = [pos_x, pos_y]
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 50, tile_height * pos_y + 50)


def draw_exit_text(screen):
    font = pygame.font.Font(None, 40)
    string_rendered = font.render('E X I T', True, (255, 255, 255))
    screen.blit(string_rendered, (exit_game.rect.x + 20, exit_game.rect.y + 7))


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
        self.wall()
        self.way = []
        self.mandatory_cell = []
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
        global saved

        if arr == '@' and sum(map(lambda x: x.count('@'), self.board)) == 1:
            return None
        if arr == '*' and sum(map(lambda x: x.count('*'), self.board)) == 4:
            return None
        cell = self.get_cell(mouse_pos)
        if cell is not None:
            if self.width // 2 - 4 <= cell[0] <= self.width // 2 + 3:
                if self.height // 2 - 2 <= cell[1] <= self.height // 2 + 1:
                    return None
        if cell is None or cell[0] in [0, self.width - 1] or cell[1] in [0, self.height - 1]:
            return None
        if arr == '.':
            for elem in tiles_group:
                if elem.cords == list(cell):
                    tiles_group.remove(elem)
                self.board[cell[1]][cell[0]] = ' '
            return True
        self.on_click(cell, arr)
        saved = False
        return True

    def get_cell(self, mouse_pos):
        if mouse_pos[0] >= self.cell_size * self.width + self.left:
            return None
        if mouse_pos[1] >= self.cell_size * self.height + self.top:
            return None
        if mouse_pos[0] <= self.left or mouse_pos[1] <= self.top:
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
                if j in [-1, 0] and i == -2:
                    Tile(values['?'], a, b, (base_group,))
                elif i == -2 and j == -4:
                    Tile(values['1'], a, b, (base_group,))
                elif i == -2 and j == 3:
                    Tile(values['2'], a, b, (base_group,))
                elif i == 1 and j == 3:
                    Tile(values['4'], a, b, (base_group,))
                elif i == 1 and j == -4:
                    Tile(values['3'], a, b, (base_group,))
                elif i in [-2, 1]:
                    Tile(values['-'], a, b, (base_group,))
                elif j in [-4, 3]:
                    Tile(values['|'], a, b, (base_group,))
                else:
                    Tile(values['.'], a, b, (base_group,))

    def wall(self):
        for i in range(self.height):
            Tile(values['|'], 0, i, (base_group,))
            Tile(values['|'], self.width - 1, i, (base_group,))

        for i in range(self.width):
            if i == 0:
                Tile(values['1'], i, 0, (base_group,))
                Tile(values['3'], i, self.height - 1, (base_group,))
            elif i == self.width - 1:
                Tile(values['2'], i, 0, (base_group,))
                Tile(values['4'], i, self.height - 1, (base_group,))
            else:
                Tile(values['-'], i, 0, (base_group,))
                Tile(values['-'], i, self.height - 1, (base_group,))

    def voln(self, pos, board):
        self.way.append(pos)
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                a, b = pos[0] + i, pos[1] + j
                if [a, b] not in self.way and board[a][b] not in ['1', '2', '3', '4', '|', '-', 't', 'b', 'l', 'r']:
                    self.voln([a, b], board)

    def make_way(self, board):
        player_pos = None
        self.way = []
        self.mandatory_cell = []
        for i in range(self.height):
            for j in range(self.width):
                if board[i][j] in ['0', '*', '?']:
                    self.mandatory_cell.append([i, j])
                if board[i][j] == '@':
                    player_pos = [i, j]
        if player_pos is None:
            return False
        self.voln(player_pos, board)
        for elem in self.mandatory_cell:
            if elem not in self.way:
                return False
        return True

    def size_event(self, event_num):
        if event_num == 0:
            if self.width % 2 == 1:
                for i in [-2, -1, 0, 1]:
                    self.board[self.height // 2 + i][self.width // 2 - 4] = ' '
            self.width += 1
            self.board = [elem + [' '] for elem in self.board]
        elif event_num == 2:
            self.width -= 1
            for elem in tiles_group:
                if elem.cords[0] == self.width:
                    tiles_group.remove(elem)
            self.board = [elem[:-1] for elem in self.board]

        elif event_num == 1:
            self.height += 1
            self.board.append([' '] * self.width)
        elif event_num == 3:
            self.height -= 1
            for elem in tiles_group:
                if elem.cords[1] == self.height:
                    tiles_group.remove(elem)
            self.board = self.board[:-1]
        self.center()
        self.wall()

    def save_file(self, filename):
        global save_text
        if filename + '.txt' not in os.listdir('levels') or not len(filename) == 0:

            board = deepcopy(self.board)
            pacman = False
            energo = 0

            for i in [-2, -1, 0, 1]:
                for j in [-4, -3, -2, -1, 0, 1, 2, 3]:
                    b, a = self.height // 2 + i, self.width // 2 + j
                    if j in [-1, 0] and i == -2:
                        board[b][a] = '?'
                    elif i == -2 and j == -4:
                        board[b][a] = '1'
                    elif i == -2 and j == 3:
                        board[b][a] = '2'
                    elif i == 1 and j == 3:
                        board[b][a] = '4'
                    elif i == 1 and j == -4:
                        board[b][a] = '3'
                    elif i in [-2, 1]:
                        board[b][a] = '-'
                    elif j in [-4, 3]:
                        board[b][a] = '|'
                    else:
                        board[b][a] = '.'

            for i in range(self.height):
                board[i][0] = '|'
                board[i][self.width - 1] = '|'

            for i in range(self.width):
                if i == 0:
                    board[0][i] = '1'
                    board[self.height - 1][i] = '3'
                elif i == self.width - 1:
                    board[0][i] = '2'
                    board[self.height - 1][i] = '4'
                else:
                    board[0][i] = '-'
                    board[self.height - 1][i] = '-'

            if not self.make_way(board):
                save_text = 'Пакмен не может дойти до всех обязательных полей'
                return None

            for elem in board:
                if '@' in elem:
                    pacman = True
                energo += elem.count('*')

            if not pacman or energo < 4:
                save_text = 'Нужен ровно один пакмен и 4 большие точки'
                return None

            file = open(f'levels/{filename}.txt', mode='w', encoding='utf-8')

            for elem in board:
                print(''.join(list(map(lambda x: '.' if x == ' ' else x, elem))), file=file)
            file.close()
            save_text = 'Сохранено'
            return True
        else:
            save_text = 'Имя файла не доступно'
            return False


class Images(pygame.sprite.Sprite):
    def __init__(self, tile_type, number, a):
        super().__init__(images_group)
        self.image = tile_images[tile_type]
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect().move(835 if a == 0 else 895, number * 80 + 50)


def complate(result, screen, text='Не сохранено'):
    color = (0, 150, 00) if result else (150, 0, 00)
    text_x = 620
    if result or text == 'Не сохранено':
        pygame.draw.rect(screen, color, (600, 400, 120, 40), width=0)
    if text == 'Сохранено':
        text_x = 620
    elif text == 'Не сохранено':
        text_x = 610
    elif text == 'Имя файла не доступно':
        pygame.draw.rect(screen, color, (550, 400, 220, 40), width=0)
        text_x = 570
    elif text == 'Нужен ровно один пакмен и 4 большие точки':
        text1 = 'Нужен ровно один пакмен'
        text2 = 'и 4 большие точки'
        pygame.draw.rect(screen, color, (550, 400, 220, 60), width=0)
        text_x_1 = 563
        text_x_2 = 585
        text_y_1 = 413
        text_y_2 = 435
        font = pygame.font.Font(None, 20)
        font.bold = True
        text_for_print_1 = font.render(text1, True, (255, 255, 255))
        text_for_print_2 = font.render(text2, True, (255, 255, 255))
        screen.blit(text_for_print_1, (text_x_1, text_y_1))
        screen.blit(text_for_print_2, (text_x_2, text_y_2))
        return None

    elif text == 'Пакмен не может дойти до всех обязательных полей':
        text1 = 'Пакмен не может дойти до'
        text2 = 'всех обязательных полей'
        pygame.draw.rect(screen, color, (550, 400, 220, 60), width=0)
        text_x_1 = 563
        text_x_2 = 563
        text_y_1 = 413
        text_y_2 = 435
        font = pygame.font.Font(None, 20)
        font.bold = True
        text_for_print_1 = font.render(text1, True, (255, 255, 255))
        text_for_print_2 = font.render(text2, True, (255, 255, 255))
        screen.blit(text_for_print_1, (text_x_1, text_y_1))
        screen.blit(text_for_print_2, (text_x_2, text_y_2))
        return None

    font = pygame.font.Font(None, 20)
    font.bold = True
    text = "Сохранено" if result else text
    text_for_print = font.render(text, True, (255, 255, 255))

    text_y = 413
    screen.blit(text_for_print, (text_x, text_y))


def cords(mouse_pos):
    a, b = -1, -1
    if mouse_pos[0] in range(835, 885):
        a = 0
    elif mouse_pos[0] in range(895, 945):
        a = 1

    for i in range(7):
        if mouse_pos[1] in range(50 + i * 80, 100 + i * 80):
            b = i
            break

    if a >= 0 and b >= 0:
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

input_box = pygame.Rect(560, 250, 200, 50)
button = pygame.Rect(600, 330, 120, 40)


def save_file(text, screen):
    pygame.draw.rect(screen, (50, 50, 50), input_box, width=0)
    pygame.draw.rect(screen, (25, 25, 25), button, width=0)

    font = pygame.font.Font(None, 30)

    text1 = font.render('Назовите карту', True, (255, 255, 0))
    text_x = 580
    text_y = 220
    screen.blit(text1, (text_x, text_y))

    font = pygame.font.Font(None, 25)
    text = font.render(text, True, (255, 255, 0))
    text_x = 570
    text_y = 265
    screen.blit(text, (text_x, text_y))

    text = font.render('Сохранить', True, (255, 255, 0))
    text_x = 615
    text_y = 340
    screen.blit(text, (text_x, text_y))


def arrows(pos_x, pos_y):
    a = 0 if pos_x in range(560, 595) else 1 if pos_x in range(725, 760) else -1
    b = 0 if pos_y in range(55, 90) else 1 if pos_y in range(90, 125) else -1
    return b * 2 + a if a >= 0 and b >= 0 else None


def print_create():
    global save_text, exit_game

    all_sprites.empty()
    tiles_group.empty()
    images_group.empty()
    base_group.empty()
    exit_group.empty()

    exit_game = pygame.sprite.Sprite()
    exit_game.image = pygame.Surface((125, 40))
    exit_game.rect = pygame.Rect(600, 570, 125, 40)
    exit_game.image.fill((200, 0, 0))
    exit_group.add(exit_game)
    save_text = 'Не сохранено'

    current = False
    saved = False
    exit_down = False

    pygame.init()
    pygame.display.set_caption('Создание поля')
    size = width, height = 1000, 650
    screen = pygame.display.set_mode(size)
    number1, number2 = 25, 25
    board = Board(number1, number2)
    running = True
    player, level_x, level_y = generate_level([''.join(elem) for elem in board.board])
    a = 0
    down = 0

    for elem in tile_images:
        if elem != 'gate':
            Images(elem, a // 2, a % 2)
            a += 1
    click, text, position = False, '', -1

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if exit_game.rect.collidepoint(pygame.mouse.get_pos()):
                    exit_game.image.fill((150, 0, 0))
                    exit_down = True
                if current and board.get_click(event.pos, current):
                    down = 1
                click = input_box.collidepoint(event.pos)

                if button.collidepoint(event.pos):
                    saved = board.save_file(text)

                if cords(event.pos) is not None:
                    current = dct[list(tile_images.keys())[cords(event.pos)]]
                if current:
                    board.get_click(event.pos, current)

                if arrows(event.pos[0], event.pos[1]) is not None:
                    a = arrows(event.pos[0], event.pos[1])
                    bool1 = a == 0 and number1 == 27
                    bool2 = a == 1 and number2 == 31
                    bool3 = a == 2 and number1 == 10
                    bool4 = a == 3 and number2 == 6
                    if not bool1 and not bool2 and not bool3 and not bool4:
                        board.size_event(a)
                        saved = False
                        save_text = 'Не сохранено'

                        number1 = number1 + 1 if a == 0 else number1 - 1 if a == 2 else number1
                        number2 = number2 + 1 if a == 1 else number2 - 1 if a == 3 else number2

                player, level_x, level_y = generate_level([''.join(elem) for elem in board.board])
                a = 0
                for elem in tile_images:
                    if elem != 'gate':
                        Images(elem, a // 2, a % 2)
                        a += 1

            elif event.type == pygame.MOUSEBUTTONUP:
                if exit_game.rect.collidepoint(pygame.mouse.get_pos()) and exit_down:
                    exit_down = False
                    exit_game.image.fill((200, 0, 0))

                    return True

                exit_game.image.fill((200, 0, 0))

            if event.type == pygame.KEYDOWN:
                if click:
                    if event.key == pygame.K_RETURN:
                        text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode if len(text) <= 15 else ''

            if event.type == pygame.MOUSEMOTION:
                if down:
                    board.get_click(event.pos, current)
                    generate_level([''.join(elem) for elem in board.board])

            if event.type == pygame.MOUSEBUTTONUP:
                down = 0

        screen.fill((0, 0, 0))
        board.render(screen)
        pygame.draw.rect(screen, (50, 50, 50), (800, 20, 180, 610))
        tiles_group.draw(screen)
        images_group.draw(screen)
        draw(screen, number1, number2)
        arrows_group.draw(screen)
        base_group.draw(screen)
        exit_group.draw(screen)
        draw_exit_text(screen)
        current_image = list(values.keys()).index(current) if current else -1
        if current_image >= 0:
            a = 833 if current_image % 2 == 0 else 893
            b = current_image // 2 * 80 + 50 - 2
            pygame.draw.rect(screen, (255, 255, 0), (a, b, 54, 54), width=2)
        save_file(text + '|' if click else text, screen)
        complate(saved, screen, save_text)

        pygame.display.flip()
    return False
