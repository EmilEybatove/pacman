from functios import *

events_sequence, counter, number = ['up'], 1, 0

class Game:
    def __init__(self, level, score=0, mode=1):
        """значения mode:
        0 - пауза
        1 - основная игра
        2 - съел точку (пауза)
        3 - съел точку процесс
        4 - съел призрака (пауза)
        5 - уход призрака
        6 - призрак съел пакмена
        """
        self.lives = 3
        self.score = score
        self.mode = mode
        grid = load_level(level)
        self.pacman, self.x, self.y, self.pacman_pos = generate_level(grid)



        self.ghosts = []
        temp = sample(ghostGate, k=4)
        for col in range(1):
            start_pos = x, y = temp[col]
            hunter = Hunter(hunter_group, x, y, grid, col)
            self.ghosts.append(hunter)
            all_sprites.add(hunter)


if __name__ == "__main__":
    pygame.init()
    size = width, height = 500, 500
    screen = pygame.display.set_mode(size)
    game = Game('default_level.txt')
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
                if event.key in change_values.keys() and len(events_sequence) <= 1:
                    events_sequence.append(change_values[event.key])
        if counter == 0:
            game.pacman_pos = [int(game.pacman.x / 18), int(game.pacman.y / 18)]
            events_sequence = [events_sequence[1]] if len(events_sequence) > 1 else events_sequence
        if game.mode in [1, 3, 5]:
            if events_sequence[0] == 'left':
                game.pacman.update_left(number)
            elif events_sequence[0] == 'right':
                game.pacman.update_right(number)
            elif events_sequence[0] == 'up':
                game.pacman.update_up(number)
            elif events_sequence[0] == 'down':
                game.pacman.update_down(number)
        if len(events_sequence) > 0:
            counter = (counter + 1) % 18
            number = (number + 1) % 9
        for hunter in hunter_group:
            if (hunter.row, hunter.col) != game.pacman_pos:
                hunter.move(choice(hunter.get_next_nodes(game.pacman_pos[0], game.pacman_pos[1])))
        all_sprites.draw(screen)
        all_sprites.update()
        tiles_group.draw(screen)
        base_group.draw(screen)
        player_group.draw(screen)
        hunter_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
    terminate()