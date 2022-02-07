import asyncio
import socketio
from functions import *

events_sequence, number = ['up'], 0
i = -1
mult = 0


class Game:
    def __init__(self, level, mode=1, lives=3):
        self.lives = lives
        self.mode = mode
        grid = load_level(level)
        self.pacman, self.x, self.y, self.pacman_pos, self.points = generate_level(grid)
        self.start_pacman_pos = self.pacman_pos.copy()
        self.hunter_start_pos = []
        self.ghosts = []
        temp = sample(ghostGate, k=4)
        for col in range(1):
            start_pos = x, y = temp[col]
            self.hunter_start_pos.append(start_pos)
            hunter = PlayerHunter(hunter_group, x, y, col)
            self.ghosts.append(hunter)
            all_sprites.add(hunter)


def revival():
    global mult
    for hunter in hunter_group:
        hunter.setAttacked(False)
    mult = 0


def react(game, side, timers):
    global events_sequence, number, i, mult
    result = game.pacman.update(number, side)
    if result:
        game.points -= 1
        screen.fill((0, 0, 0))
        draw(screen, game)

    if result == 'energo':
        if events_sequence[0] in ['right', 'down']:
            game.pacman.update(number, side)
        if i != -1:
            timers[i].cancel()
        for hunter in hunter_group:
            if not hunter.isDead():
                hunter.setAttacked(True)

        pygame.time.delay(500)
        i += 1

        timers[i].start()

    for hunter in hunter_group:
        if pygame.sprite.spritecollideany(hunter, player_group):
            if not hunter.isAttacked() and not hunter.isDead():
                for hunter in hunter_group:
                    hunter.new()
                game.pacman.new()
                events_sequence, game.pacman.counter, number = ['up'], 1, 0
                game.lives -= 1
                screen.fill((0, 0, 0))
                draw(screen, game)
                break
            elif hunter.isAttacked():
                mult += 1
                game.pacman.score += 2 ** mult * 100
                hunter.setAttacked(False)
                hunter.setDead(True)
                pygame.time.delay(500)
                screen.fill((0, 0, 0))
                draw(screen, game)


def draw(screen, game):
    # отрисовка жизней
    image_pacman = pygame.transform.scale(load_image('pacman_sprites/r_1.gif'), (25, 25))
    if game.lives > 2:
        screen.blit(image_pacman, (count_columns * 18 + 40, count_rows * 9 - 20))
    if game.lives > 1:
        screen.blit(image_pacman, (count_columns * 18 + 80, count_rows * 9 - 20))
    # отрисовка надписи "SCORE"
    font = pygame.font.Font(None, 35)
    string_rendered = font.render('S C O R E', True, pygame.Color('yellow'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top = 20
    intro_rect.x = count_columns * 18 + 15
    screen.blit(string_rendered, intro_rect)
    # отрисовка количество очков
    font = pygame.font.Font(None, 40)
    string_rendered = font.render(str(game.pacman.score), True, pygame.Color('yellow'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top = 60
    intro_rect.x = count_columns * 18 + (75 - intro_rect.width // 2)
    screen.blit(string_rendered, intro_rect)


sio = socketio.AsyncClient()

pygame.init()
level = 'Level_1.txt'
# вычисление размеров поля для загруженного уровня
count_columns = len(load_level(level)[0])
count_rows = len(load_level(level))
width = count_columns * 18 + 150
height = count_rows * 18
size = width, height

screen = pygame.display.set_mode(size)
game = Game(level)

draw(screen, game)

timer1 = threading.Timer(10, revival)
timer2 = threading.Timer(10, revival)
timer3 = threading.Timer(10, revival)
timer4 = threading.Timer(10, revival)
timers = [timer1, timer2, timer3, timer4]

running = True
player = None
count1 = count2 = 26
clock = pygame.time.Clock()
FPS = 40
change_values = {
    pygame.K_LEFT: 'left',
    pygame.K_RIGHT: 'right',
    pygame.K_UP: 'up',
    pygame.K_DOWN: 'down'
}


async def send_ping():
    await sio.emit('Hello world')


@sio.on('*')
async def catch_all(event, data):
    global events_sequence, number
    data = [data[elem] for elem in data]
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
            break
        if event.type == pygame.KEYDOWN:
            if event.key in change_values.keys() and len(events_sequence) <= 1:
                events_sequence.append(change_values[event.key])

    if game.pacman.counter == 0:
        events_sequence = [events_sequence[1]] if len(events_sequence) > 1 else events_sequence
    react(game, data[0][0], timers)
    for hunter in hunter_group:
        if len(data) > 1:
            hunter.move(data[1][0])

    game.pacman.counter = (game.pacman.counter + 1) % 18
    number = (number + 1) % 9

    all_sprites.draw(screen)
    tiles_group.draw(screen)
    player_group.draw(screen)
    hunter_group.draw(screen)

    pygame.display.flip()

    await sio.emit('my event', events_sequence)
    clock.tick(FPS)

@sio.event
async def connect():
    await sio.emit('my message', ['up'])
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
    await sio.connect('http://localhost:8080')
    await sio.wait()


if __name__ == "__main__":
    asyncio.run(start_server())