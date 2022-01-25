from functions import *

events_sequence, number = ['up'], 0
pause, stop = False, False
i = -1


# sides = ['up', 'right', 'down', 'left', 'up', 'right']

def start():
    stop = False


class Game:
    def __init__(self, level, score=0, mode=1, lives=3):
        """значения mode:
        0 - пауза
        1 - основная игра
        2 - съел точку (пауза)
        3 - съел точку процесс
        4 - съел призрака (пауза)
        5 - уход призрака
        6 - призрак съел пакмена
        """
        self.lives = lives
        self.score = score
        self.mode = mode
        grid = load_level(level)
        self.pacman, self.x, self.y, self.pacman_pos, self.points = generate_level(grid)
        self.start_pacman_pos = self.pacman_pos.copy()
        self.hunter_start_pos = []
        self.ghosts = []
        temp = sample(ghostGate, k=4)
        for col in range(4):
            start_pos = x, y = temp[col]
            self.hunter_start_pos.append(start_pos)
            hunter = Hunter(hunter_group, x, y, grid, col)
            self.ghosts.append(hunter)
            all_sprites.add(hunter)


def react(game, side, timers):
    global events_sequence, number, i
    result = game.pacman.update(number, side)
    if result:
        game.points -= 1

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
                break
            elif hunter.isAttacked():
                # print('counter: ', game.pacman.counter)
                # game.pacman.counter -= 1
                # game.pacman.update(number, sides[(sides.index(events_sequence[0]) + 2)])
                hunter.setAttacked(False)
                hunter.setDead(True)
                pygame.time.delay(500)


def draw(screen, game):
    # отрисовка кнопок плей/пауза
    image_pause = pygame.transform.scale(load_image('pause.png'), (30, 30))
    image_play = pygame.transform.scale(load_image('on.png'), (30, 30))
    screen.blit(image_pause, (count_columns * 18 + 80, count_rows * 18 - 40))
    screen.blit(image_play, (count_columns * 18 + 40, count_rows * 18 - 40))
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


if __name__ == "__main__":
    pygame.init()
    level = 'default_level.txt'
    # вычисление размеров поля для загруженного уровня
    count_columns = len(load_level(level)[0])
    count_rows = len(load_level(level))
    width = count_columns * 18 + 150
    height = count_rows * 18
    size = width, height

    screen = pygame.display.set_mode(size)
    game = Game(level)



    timer1 = threading.Timer(10, revival)
    timer2 = threading.Timer(10, revival)
    timer3 = threading.Timer(10, revival)
    timer4 = threading.Timer(10, revival)
    timers = [timer1, timer2, timer3, timer4]

    running = True
    player = None
    level = 'default_level.txt'
    count1 = count2 = 26
    clock = pygame.time.Clock()
    FPS = 40
    change_values = {
        pygame.K_LEFT: 'left',
        pygame.K_RIGHT: 'right',
        pygame.K_UP: 'up',
        pygame.K_DOWN: 'down'
    }

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == 27:
                    pause = bool(1 - pause)
                if event.key in change_values.keys() and len(events_sequence) <= 1:
                    events_sequence.append(change_values[event.key])
            if event.type == pygame.MOUSEBUTTONDOWN:
                x = event.pos[0]
                y = event.pos[1]
                if count_rows * 18 - 40 <= y <= count_rows * 18 - 10:
                    if count_columns * 18 + 80 <= x <= count_columns * 18 + 110:
                        pause = True
                    elif count_columns * 18 + 40 <= x <= count_columns * 18 + 70:
                        pause = False

        screen.fill((0, 0, 0))

        if game.pacman.counter == 0:
            game.pacman_pos = [int(game.pacman.x / 18), int(game.pacman.y / 18)]
            events_sequence = [events_sequence[1]] if len(events_sequence) > 1 else events_sequence
        if not pause:
            react(game, events_sequence[0], timers)
            game.pacman.counter = (game.pacman.counter + 1) % 18
            number = (number + 1) % 9
            num = 0
            for hunter in hunter_group:
                hunter.move(return_path(game, num, events_sequence[0], hunter))
                num += 1
        all_sprites.draw(screen)
        tiles_group.draw(screen)
        base_group.draw(screen)
        player_group.draw(screen)
        hunter_group.draw(screen)
        draw(screen, game)
        pygame.display.flip()
        clock.tick(FPS)
        if game.points == 0:
            print('you win!!!')
    terminate()
