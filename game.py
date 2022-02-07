from functions import *

events_sequence, number = ['up'], 0
i = -1
mult = 0


class Game:
    def __init__(self, level, grid, lives=3):
        self.lives = lives
        self.pacman, self.x, self.y, self.pacman_pos, self.points, self.ghostGate = generate_level(grid)
        global ghostGate
        ghostGate = self.ghostGate

        self.start_pacman_pos = self.pacman_pos.copy()
        self.hunter_start_pos = []
        self.ghosts = []
        temp = sample(self.ghostGate, k=4)
        for col in range(4):
            start_pos = x, y = temp[col]
            self.hunter_start_pos.append(start_pos)
            hunter = Hunter(hunter_group, x, y, grid, col)
            self.ghosts.append(hunter)
            all_sprites.add(hunter)

    @staticmethod
    def PlayBackgoundSound(snd, SOUND):
        channel_backgound.stop()
        if SOUND:
            channel_backgound.play(snd, loops=-1)


def revival():
    global mult
    for hunter in hunter_group:
        hunter.setAttacked(False)
    mult = 0


def react(game, side, timers, screen, count_columns, count_rows):
    global events_sequence, number, i, mult
    result = game.pacman.update(number, side)
    if result:
        game.points -= 1
        screen.fill((0, 0, 0))
        draw(screen, game, count_columns, count_rows)

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

        mult = 0
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
                draw(screen, game, count_columns, count_rows)
                break
            elif hunter.isAttacked():
                mult += 1
                game.pacman.score += 2 ** mult * 100
                hunter.setAttacked(False)
                hunter.setDead(True)
                pygame.time.delay(500)
                screen.fill((0, 0, 0))
                draw(screen, game, count_columns, count_rows)


def open_result_window(result, level, grid):
    # открываем окно
    pygame.init()
    size = 500, 500
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('result')
    screen.fill('black')
    running = True
    # выбор надписи и картинки в зависимости от результата
    if not result:
        intro_text = ["GAME OVER", "Try again!!"]
    else:
        intro_text = ["YOU WIN", "Congratulations!!"]
        picture = pygame.transform.scale(load_image('ballons.jpg'), (400, 220))
        screen.blit(picture, (50, 0))
    # отрисовываем надписи
    font = pygame.font.Font(None, 80)
    string_rendered = font.render(intro_text[0], 3, pygame.Color('yellow'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top = 220
    intro_rect.x = 250 - intro_rect.width // 2
    screen.blit(string_rendered, intro_rect)
    font = pygame.font.Font(None, 40)
    string_rendered = font.render(intro_text[1], 1, pygame.Color('yellow'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top = 300
    intro_rect.x = 250 - intro_rect.width // 2
    screen.blit(string_rendered, intro_rect)
    # отрисовываем кнопки
    pygame.draw.rect(screen, 'yellow', (100, 370, 100, 50), 2)
    pygame.draw.rect(screen, 'yellow', (300, 370, 100, 50), 2)
    font = pygame.font.Font(None, 25)
    string_rendered = font.render('choise map', 1, pygame.Color('yellow'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top = 395 - intro_rect.height // 2
    intro_rect.x = 150 - intro_rect.width // 2
    screen.blit(string_rendered, intro_rect)
    font = pygame.font.Font(None, 25)
    string_rendered = font.render('play', 1, pygame.Color('yellow'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top = 395 - intro_rect.height // 2
    intro_rect.x = 350 - intro_rect.width // 2
    screen.blit(string_rendered, intro_rect)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if 100 <= event.pos[0] <= 200 and 370 <= event.pos[1] <= 420:
                    terminate()
                    #переход к выбору карты
                elif 300 <= event.pos[0] <= 400 and 370 <= event.pos[1] <= 420:
                    #играем на той же карте заново
                    game = Game(level, grid, 3)
                    terminate()
        pygame.display.flip()


def change_image_volume(game, SOUND, screen, count_columns, count_rows):
    if SOUND:
        game.PlayBackgoundSound(snd_love, SOUND)
        image_volume = pygame.transform.scale(load_image('volume.png'), (40, 40))
    else:
        game.PlayBackgoundSound(snd_love, SOUND)
        image_volume = pygame.transform.scale(load_image('mute.png'), (40, 40))
    screen.blit(image_volume, (count_columns * 18 + 55, count_rows * 18 - 170))


def draw(screen, game, count_columns, count_rows):
    # отрисовка кнопок плей/пауза
    image_pause = pygame.transform.scale(load_image('pause.png'), (30, 30))
    image_play = pygame.transform.scale(load_image('on.png'), (30, 30))
    screen.blit(image_pause, (count_columns * 18 + 80, count_rows * 18 - 100))
    screen.blit(image_play, (count_columns * 18 + 40, count_rows * 18 - 100))
    # отрисовка кнопки volume
    image_volume = pygame.transform.scale(load_image('volume.png'), (40, 40))
    screen.blit(image_volume, (count_columns * 18 + 55, count_rows * 18 - 170))
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
    # отрисовка количества очков
    font = pygame.font.Font(None, 40)
    string_rendered = font.render(str(game.pacman.score), True, pygame.Color('yellow'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top = 60
    intro_rect.x = count_columns * 18 + (75 - intro_rect.width // 2)
    screen.blit(string_rendered, intro_rect)


def draw_exit_text(screen, count_columns, count_rows):
    font = pygame.font.Font(None, 40)
    string_rendered = font.render('E X I T', True, (255, 255, 255))
    screen.blit(string_rendered, (count_columns * 18 + 28, count_rows * 18 - 43))


def print_game(level):
    global events_sequence, number

    grid = load_level(level)

    make_graph(grid)

    pause, stop = False, False

    exit_down = False
    SOUND = True

    pygame.init()
    # вычисление размеров поля для загруженного уровня
    count_columns = len(load_level(level)[0])
    count_rows = len(load_level(level))

    exit_game = pygame.sprite.Sprite()
    exit_game.image = pygame.Surface((125, 40))
    exit_game.rect = pygame.Rect(count_columns * 18 + 10, count_rows * 18 - 50, 125, 40)
    exit_game.image.fill((200, 0, 0))
    exit_group.add(exit_game)

    width = count_columns * 18 + 150
    height = count_rows * 18
    size = width, height

    screen = pygame.display.set_mode(size)
    game = Game(level, grid)
    draw(screen, game, count_columns, count_rows)
    game.PlayBackgoundSound(snd_love, SOUND)

    timer1 = threading.Timer(10, revival)
    timer2 = threading.Timer(10, revival)
    timer3 = threading.Timer(10, revival)
    timer4 = threading.Timer(10, revival)
    timers = [timer1, timer2, timer3, timer4]

    running = True
    player = None
    count1 = count2 = 26
    clock = pygame.time.Clock()
    FPS = 80
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
                if event.key == pygame.K_m:
                    SOUND = not SOUND
                    change_image_volume(game, SOUND, screen, count_columns, count_rows)
            if event.type == pygame.MOUSEBUTTONDOWN:
                x = event.pos[0]
                y = event.pos[1]
                if count_rows * 18 - 100 <= y <= count_rows * 18 - 70:
                    if count_columns * 18 + 80 <= x <= count_columns * 18 + 110:
                        pause = True
                    elif count_columns * 18 + 40 <= x <= count_columns * 18 + 70:
                        pause = False
                elif count_columns * 18 + 55 <= x <= count_columns * 18 + 95 and \
                        count_rows * 18 - 170 <= y <= count_rows * 18 - 130:
                    SOUND = not SOUND
                    change_image_volume(game, SOUND, screen, count_columns, count_rows)
                if exit_game.rect.collidepoint(pygame.mouse.get_pos()):
                    exit_game.image.fill((150, 0, 0))
                    exit_down = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if exit_game.rect.collidepoint(pygame.mouse.get_pos()) and exit_down:
                    print('rthsetg')
                    return True
                exit_down = False
                exit_game.image.fill((200, 0, 0))

        if game.pacman.counter == 0:
            game.pacman_pos = [int(game.pacman.x / 18), int(game.pacman.y / 18)]
            events_sequence = [events_sequence[1]] if len(events_sequence) > 1 else events_sequence
        if not pause:
            react(game, events_sequence[0], timers, screen, count_columns, count_rows)
            game.pacman.counter = (game.pacman.counter + 1) % 18
            number = (number + 1) % 9
            num = 0
            for hunter in hunter_group:
                hunter.move(return_path(game, num, events_sequence[0], hunter), grid)
                num += 1
        all_sprites.draw(screen)
        tiles_group.draw(screen)
        player_group.draw(screen)
        hunter_group.draw(screen)
        exit_group.draw(screen)
        draw_exit_text(screen, count_columns, count_rows)
        pygame.display.flip()
        clock.tick(FPS)
        if game.points == 0:
            open_result_window(True, level, grid)
        if game.lives == 0:
            open_result_window(False, level, grid)
    return False