import pygame
import functions
import os

level_group = pygame.sprite.Group()
flip_group = pygame.sprite.Group()

page = 0

load_image = functions.load_image

tile_images = {
    'vertical': load_image('vertical.png'),
    'horizontal': load_image('horizontal.png'),
    '1': load_image('1.png'),
    '2': load_image('2.png'),
    '3': load_image('4.png'),
    '4': load_image('3.png'),
    'empty': load_image('empty.png'),
    'point': load_image('point.png'),
    'energo': load_image('energo.png'),
    'pacman': load_image('pacman.png'),
    'gate': load_image('gate.png')}

values = {
    '|': 'vertical',
    '-': 'horizontal',
    '1': '1',
    '2': '2',
    '3': '3',
    '4': '4',
    '.': 'empty',
    '0': 'point',
    '*': 'energo',
    '@': 'pacman',
    '?': 'gate'
}


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

    def draw_name(self):
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

    def start(self):
        pass


class Flip(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, side):
        super().__init__(flip_group)
        self.image = load_image('on.png')
        if side == 'left':
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = pygame.Rect(pos_x, pos_y, 35, 35)
        self.side = side


levels = os.listdir('levels')
print(levels)

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

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 450))
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
                for level in level_group:
                    if level.rect.collidepoint(pygame.mouse.get_pos()) and level.down:
                        level.start()
                    level.up_event()


        level_group.draw(screen)
        flip_group.draw(screen)
        for level in level_group:
            level.draw_name()
        pygame.display.flip()
    pygame.quit()
