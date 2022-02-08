import os
from random import choice
import pygame
import functions
import os
from pygame import Color
import pygame.gfxdraw

level_group = pygame.sprite.Group()
flip_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
delete_group = pygame.sprite.Group()

exit_game = pygame.sprite.Sprite()
exit_game.image = pygame.Surface((125, 40))
exit_game.rect = pygame.Rect(640, 430, 125, 40)
exit_game.image.fill((200, 0, 0))
exit_group.add(exit_game)




load_image = functions.load_image

default = ['Level_1', 'Level_2', 'Level_3']




class Delete(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, level):
        super().__init__(delete_group)
        self.image = pygame.transform.scale(load_image('delete.png'), (35, 35))
        self.rect = pygame.Rect(pos_x, pos_y - 5, 35, 35)
        self.level = level
        self.pos_x = pos_x
        self.pos_y = pos_y - 5
        self.down = False


    def update(self):
        os.remove(f'levels/{self.level}')


    def down_event(self, screen):
        rect = pygame.Rect(self.pos_x, self.pos_y, 35, 35)
        pygame.gfxdraw.box(screen, rect, (0, 0, 0, 100))



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
        self.pos = (pos_x + 75 - len(name) * 2, pos_y + 10)
        if self.name not in default:
            self.delete = Delete(pos_x + 170, pos_y, name)

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
        colors = [None, pygame.Color('chartreuse2'), pygame.Color('cyan'), pygame.Color('darkcyan'),
                  pygame.Color('darkgoldenrod1'), pygame.Color('darkorchid1'), pygame.Color('darkturquoise'),
                  pygame.Color('gold'), pygame.Color('gray74'), pygame.Color('lightslateblue'),
                  pygame.Color('violet'), pygame.Color("green")]
        res = game.print_game(self.name + '.txt', choice(colors))
        if not res:
            return False
        else:
            if res == "Next_level":
                pass # What to do???
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
    levels = sorted(os.listdir(os.path.join(functions.SCRIPT_PATH, 'levels')))

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

                for delete in delete_group:
                    if delete.rect.collidepoint(pygame.mouse.get_pos()):
                        delete.down = True

                if left.rect.collidepoint(pygame.mouse.get_pos()) and page > 0:
                    screen.fill((0, 0, 0))
                    page -= 1
                    level_group.empty()
                    level1 = Level(150, 50, levels[2 * page])
                    level2 = Level(475, 50, levels[2 * page + 1])
                    level1.draw_level(screen)
                    level2.draw_level(screen)
                elif right.rect.collidepoint(pygame.mouse.get_pos()) and (page + 1) * 2 < len(levels):
                    screen.fill((0, 0, 0))
                    page += 1
                    level_group.empty()
                    delete_group.empty()
                    level1 = Level(150, 50, levels[2 * page])
                    level2 = Level(475, 50, levels[2 * page + 1]) if len(levels) > 2 * page + 1 else False
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
                    delete_group.empty()
                    level_group.empty()
                    return True

                for delete in delete_group:
                    if delete.rect.collidepoint(pygame.mouse.get_pos()) and delete.down:
                        delete.update()
                        screen.fill((0, 0, 0))
                        levels = os.listdir('levels')
                        level_group.empty()
                        delete_group.empty()
                        if 2 * page < len(levels):
                            level1 = Level(150, 50, levels[2 * page])
                        else:
                            level1 = False
                        if len(levels) > 2 * page + 1:
                            level2 = Level(475, 50, levels[2 * page + 1])
                        else:
                            level2 = False
                        print(level1, level2)
                        if not level1 and not level2:
                            page -= 1
                            level1 = Level(150, 50, levels[2 * page])
                            level2 = Level(475, 50, levels[2 * page + 1])
                            level1.draw_level(screen)
                            level2.draw_level(screen)
                        elif not level2:
                            level1.draw_level(screen)
                        else:
                            level1.draw_level(screen)
                            level2.draw_level(screen)



                    delete.down = False

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
        delete_group.draw(screen)
        draw_exit_text(screen)
        for delete in delete_group:
            if delete.down:
                delete.down_event(screen)
        pygame.display.flip()

    return False
