import asyncio
import socketio
import pygame
import functions



sio = socketio.AsyncClient()

pygame.init()
# вычисление размеров поля для загруженного уровня
width = 550
height = 300
size = width, height

server_group = pygame.sprite.Group()
level_group = pygame.sprite.Group()
flip_group = pygame.sprite.Group()

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

screen = pygame.display.set_mode(size)

default = ['Level_1', 'Level_2', 'Level_3']

class Server(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, num):
        super().__init__(server_group)
        self.players = 0
        self.server_num = num
        self.image = pygame.Surface((500, 30))
        self.rect = pygame.Rect(pos_x, pos_y, 500, 30)
        self.image.fill((50, 50, 50))
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.down = False

    def draw_text(self):
        font = pygame.font.Font(None, 20)
        string_rendered = font.render(f'Server {str(self.server_num)}', True, (255, 255, 255))
        screen.blit(string_rendered, (self.pos_x + 20, self.pos_y + 7))

    def draw_count(self):
        font = pygame.font.Font(None, 20)
        string_rendered = font.render(str(self.players), True, (255, 255, 255))
        screen.blit(string_rendered, (self.pos_x + 470, self.pos_y + 7))

    def down_event(self):
        self.image.fill((80, 80, 80))
        self.down = True

    def up_event(self, event):
        self.image.fill((50, 50, 50))
        if event and self.down:
            return True
        self.down = False


class Level(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, name):
        super().__init__(level_group)
        self.image = pygame.Surface((150, 30))
        self.rect = pygame.Rect(pos_x, pos_y, 150, 30)
        self.image.fill((35, 35, 35))
        self.down = False
        self.name = name
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.pos = (pos_x + 75 - len(name) * 2, pos_y + 10)

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


class Flip(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, side):
        super().__init__(flip_group)
        self.image = load_image('on.png')
        if side == 'left':
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = pygame.Rect(pos_x, pos_y, 35, 35)
        self.side = side


@sio.event
async def not_on_server(data):

    players = [len(elem.keys()) for elem in data]

    number = 0
    for server in server_group:
        server.players = players[number]
        number += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return None
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for server in server_group:
                if server.rect.collidepoint(pygame.mouse.get_pos()):
                    server.down_event()
        elif event.type == pygame.MOUSEBUTTONUP:
            for server in server_group:
                if server.up_event(server.rect.collidepoint(pygame.mouse.get_pos())):
                    server_group.empty()
                    await sio.emit('now_on_server', server.server_num)
    server_group.draw(screen)
    for server in server_group:
        server.draw_text()
        server.draw_count()
    pygame.display.flip()
    await sio.emit('not_on_server', '')


@sio.event
async def on_server(data):
    width = 700
    height = 500
    size = width, height
    screen = pygame.display.set_mode(size)
    screen.fill((0, 0, 0))

    if data[1] == 1:
        left = Flip(110, 20, 'left')
        right = Flip(200, 50, 'right')

    level = Level(150, 30, data[2])
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return None
    level_group.draw(screen)
    level.draw_level(screen)
    level.draw_name(screen)
    flip_group.draw(screen)
    pygame.display.flip()

    await sio.emit('on_server', '')


@sio.event
async def start_game(data):

    events_sequence, number = ['up'], 0
    i = -1
    mult = 0


    width = 550
    height = 300
    size = width, height

    server_group.empty()
    level_group.empty()
    flip_group.empty()

    screen.fill((0, 0, 0))


# @sio.on('*')
# async def catch_all(event, data):
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             break
#
#     pygame.display.flip()
#
#     await sio.emit('not on server', '')

@sio.event
async def connect():
    await sio.emit('not_on_server', '')
    print("I'm connected!")


@sio.event
def connect_error(data):
    print("The connection failed!")


@sio.event
def disconnect():
    print("I'm disconnected!")


@sio.event
async def onAny(listener):
    print('efrgrgawrg')


async def start_server():
    for i in range(3):
        server = Server(20, 20 + i * 40, i)
    await sio.connect('http://localhost:8080')
    await sio.wait()


if __name__ == "__main__":
    asyncio.run(start_server())
