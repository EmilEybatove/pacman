import sys

import pygame
import functions
import os

level_group = pygame.sprite.Group()
flip_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()


exit_game = pygame.sprite.Sprite()
exit_game.image = pygame.Surface((125, 40))
exit_game.rect = pygame.Rect(640, 430, 125, 40)
exit_game.image.fill((200, 0, 0))
exit_group.add(exit_game)




load_image = functions.load_image


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

def draw_exit_text(screen):
    font = pygame.font.Font(None, 40)
    string_rendered = font.render('E X I T', True, (255, 255, 255))
    screen.blit(string_rendered, (exit_game.rect.x + 20, exit_game.rect.y + 7))


class Level(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, name):
        super().__init__(level_group)
        self.image = pygame.Surface((150, 30))
        self.rect = pygame.Rect(pos_x, pos_y, 150, 30)
        self.image.fill((35, 35, 35))
        self.down = False
        self.name = name[:-4]
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.pos = (pos_x, pos_y + 10)

    def down_event(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.image.fill((80, 80, 80))
            self.down = True

    def up_event(self):
        self.image.fill((35, 35, 35))
        self.down = False

    def draw_name(self, screen):
        font = pygame.font.Font(None, 20)
        text = font.render(self.name, True, (255, 255, 0))
        screen.blit(text, self.pos)

    def draw_level(self, screen):
        width = height = 10
        file = open(f'levels/{self.name}.txt', 'r').readlines()
        level_data = [elem.strip('\n') for elem in file]
        for i in range(len(level_data)):
            for j in range(len(level_data[0])):
                image = tile_images[values[level_data[i][j]]]
                image = pygame.transform.scale(image, (width, height))
                step = len(level_data[0]) - 15
                screen.blit(image, (self.pos_x + j * width - width // 2 * step, self.pos_y + 40 + i * height))

    def start(self, game):
        if not game.print_game(self.name + '.txt'):
            return False

        return True


class Flip(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, side):
        super().__init__(flip_group)
        self.image = load_image('on.png')
        if side == 'left':
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = pygame.Rect(pos_x, pos_y, 35, 35)
        self.side = side





def print_intro(game):
    page = 0
    exit_down = False
    levels = os.listdir('levels')

    if len(levels) > 0:
        level1 = Level(150, 50, levels[0])
    else:
        level1 = False
    if len(levels) > 1:
        level2 = Level(475, 50, levels[1])
    else:
        level2 = False
    left = Flip(20, 208, 'left')
    right = Flip(745, 208, 'right')

    pygame.init()
    screen = pygame.display.set_mode((800, 500))
    running = True
    if level1:
        level1.draw_level(screen)
    if level2:
        level2.draw_level(screen)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if exit_game.rect.collidepoint(pygame.mouse.get_pos()):
                    exit_game.image.fill((150, 0, 0))
                    exit_down = True

                if left.rect.collidepoint(pygame.mouse.get_pos()) and page > 0:
                    screen.fill((0, 0, 0))
                    page -= 1
                    level_group.empty()
                    level1 = Level(150, 50, levels[2 * page])
                    level2 = Level(475, 50, levels[2 * page + 1])
                    level1.draw_level(screen)
                    level2.draw_level(screen)
                elif right.rect.collidepoint(pygame.mouse.get_pos()) and page + 1 < len(levels) // 2:
                    screen.fill((0, 0, 0))
                    page += 1
                    level_group.empty()
                    level1 = Level(150, 50, levels[2 * page])
                    level2 = Level(475, 50, levels[2 * page + 1]) if len(levels) >= 2 * page + 1 else False
                    level1.draw_level(screen)
                    if level2:
                        level2.draw_level(screen)
                else:
                    for level in level_group:
                        level.down_event()
            elif event.type == pygame.MOUSEBUTTONUP:
                if exit_game.rect.collidepoint(pygame.mouse.get_pos()) and exit_down:
                    exit_down = False
                    exit_game.image.fill((200, 0, 0))
                    return True

                for level in level_group:
                    if level.rect.collidepoint(pygame.mouse.get_pos()) and level.down:
                        if not level.start(game):
                            return False
                        else:
                            screen = pygame.display.set_mode((800, 500))
                            level1.draw_level(screen)
                            if level2:
                                level2.draw_level(screen)
                        level.up_event()


        level_group.draw(screen)
        flip_group.draw(screen)
        for level in level_group:
            level.draw_name(screen)
        exit_group.draw(screen)
        draw_exit_text(screen)
        pygame.display.flip()
    return False