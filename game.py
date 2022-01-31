from functions import *

events_sequence, number = ['up'], 0
pause, stop = False, False
i = -1
mult = 0


class Game:
    def __init__(self, level, mode=1, lives=3):
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
        self.mode = mode
        self.pacman, self.x, self.y, self.pacman_pos, self.points, self.ghostGate = generate_level(grid)
        global ghostGate
        ghostGate = self.ghostGate

        self.start_pacman_pos = self.pacman_pos.copy()
        self.hunter_start_pos = []
        self.ghosts = []
        temp = sample(self.ghostGate, k=4)
        print(f"\n\ntemp: {temp} \nghostGate: {ghostGate}\n\n")
        for col in range(4):
            start_pos = x, y = temp[col]
            self.hunter_start_pos.append(start_pos)
            hunter = Hunter(hunter_group, x, y, grid, col)
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
    # отрисовка кнопок плей/пауза
    image_pause = pygame.transform.scale(load_image('pause.png'), (30, 30))
    image_play = pygame.transform.scale(load_image('on.png'), (30, 30))
    screen.blit(image_pause, (count_columns * 18 + 80, count_rows * 18 - 40))
    screen.blit(image_play, (count_columns * 18 + 40, count_rows * 18 - 40))
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


if __name__ == "__main__":
    pygame.init()
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
            if event.type == pygame.MOUSEBUTTONDOWN:
                x = event.pos[0]
                y = event.pos[1]
                if count_rows * 18 - 40 <= y <= count_rows * 18 - 10:
                    if count_columns * 18 + 80 <= x <= count_columns * 18 + 110:
                        pause = True
                    elif count_columns * 18 + 40 <= x <= count_columns * 18 + 70:
                        pause = False


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
        player_group.draw(screen)
        hunter_group.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)
        if game.points == 0:
            print('you win!!!')
    terminate()
