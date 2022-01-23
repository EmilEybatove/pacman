from functions import *

events_sequence, counter, number = ['up'], 1, 0
pause, stop = False, False
i = -1

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
    global events_sequence, counter, number, i
    result = game.pacman.update(number, side)

    if result:
        game.points -= 1
    
    if result == 'energo':
        if i != -1:
            timers[i].cancel()
        for hunter in hunter_group:
            if not hunter.isDead():
                hunter.setAttacked(True)

        pygame.time.delay(500)

        counter -= 1
        i += 1

        timers[i].start()

    for hunter in hunter_group:
        if pygame.sprite.spritecollideany(hunter, player_group):
            if not hunter.isAttacked() and not hunter.isDead():
                for hunter in hunter_group:
                    hunter.new()
                game.pacman.new()
                events_sequence, counter, number = ['up'], 1, 0
                break
            elif hunter.isAttacked():
                hunter.setAttacked(False)
                hunter.setDead(True)
                pygame.time.delay(500)
                counter -= 1



if __name__ == "__main__":
    pygame.init()
    size = width, height = 500, 500
    screen = pygame.display.set_mode(size)
    game = Game('default_level.txt')



    def revival():
        for hunter in hunter_group:
            hunter.setAttacked(False)


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
            react(game, events_sequence[0], timers)
            counter = (counter + 1) % 18
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
        pygame.display.flip()
        clock.tick(FPS)
    terminate()
