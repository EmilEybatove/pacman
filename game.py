from functions import *

events_sequence, counter, number = ['up'], 1, 0
pause = False


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
        self.pacman, self.x, self.y, self.pacman_pos = generate_level(grid)
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
    global events_sequence, counter, number
    result = game.pacman.update(number, side)
    if game.mode == 1:
        if result == 1:
            for hunter in hunter_group:
                hunter.new()
                game.pacman.new()
                events_sequence, counter, number = ['up'], 1, 0
        elif result == 2:
            for hunter in hunter_group:
                hunter.setAttacked(True)
                timers[i].cancel()
                game.mode = 2
    if game.mode == 3:
        if result == 1:
            for hunter in hunter_group:
                if pygame.sprite.spritecollideany(hunter, player_group) is not None:
                    if not hunter.dead:
                        hunter.setDead(True)
                        hunter.setAttacked(False)
                        pygame.time.delay(pygame.time.delay(500))


if __name__ == "__main__":
    pygame.init()
    size = width, height = 500, 500
    screen = pygame.display.set_mode(size)
    game = Game('default_level.txt')
    i = 0


    def revival():
        global i
        for hunter in hunter_group:
            hunter.attacked = False
        game.mode = 1
        i += 1


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
    FPS = 60

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
        if counter == 0:
            game.pacman_pos = [int(game.pacman.x / 18), int(game.pacman.y / 18)]
            events_sequence = [events_sequence[1]] if len(events_sequence) > 1 else events_sequence
        if not pause:
            if game.mode in [1, 3, 5]:
                react(game, events_sequence[0], timers)
            if len(events_sequence) > 0:
                counter = (counter + 1) % 18
                number = (number + 1) % 9
            for hunter in hunter_group:
                hunter.move((game.pacman_pos[0], game.pacman_pos[1]))
        all_sprites.draw(screen)
        tiles_group.draw(screen)
        base_group.draw(screen)
        player_group.draw(screen)
        hunter_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

        if game.mode in [2]:
            pygame.time.delay(pygame.time.delay(500))
            game.mode = 3
            timers[i].start()
    terminate()
