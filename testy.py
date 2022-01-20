from create import *




def load_image_pacman(name, colorkey=None):
    fullname = os.path.join('data/pacman_sprites', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image

# преобразование текстового файла в список спрайтов
def load_level(filename):
    filename = "levels/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


# создание уровня
def generate_level(level):
    global base_group
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
            elif level[y][x] in list(values.keys()):
                Tile(values[level[y][x]], x, y)
    return new_player, x, y


def terminate():
    pygame.quit()
    sys.exit()


# оформление стартового окна
def print_intro():
    screen.fill('black')
    pygame.display.set_caption('play pacman')
    pygame.draw.rect(screen, 'yellow', (100, 300, 300, 50), 1)
    pygame.display.flip()
    intro_text = ["Welcome to", "PACMAN",
                  "Введите название своего уровня", "или", "сразу нажмите Enter для начала игры"]
    font = pygame.font.Font(None, 40)
    string_rendered = font.render(intro_text[0], 1, pygame.Color('yellow'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top = 50
    intro_rect.x = 250 - intro_rect.width // 2
    screen.blit(string_rendered, intro_rect)
    font = pygame.font.Font(None, 80)
    string_rendered = font.render(intro_text[1], 3, pygame.Color('yellow'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top = 80
    intro_rect.x = 250 - intro_rect.width // 2
    screen.blit(string_rendered, intro_rect)
    font = pygame.font.Font(None, 20)
    for i in range(2, 5):
        string_rendered = font.render(intro_text[i], 1, pygame.Color('yellow'))
        intro_rect = string_rendered.get_rect()
        intro_rect.top = 250 + 15 * (i - 2)
        intro_rect.x = 250 - intro_rect.width // 2
        screen.blit(string_rendered, intro_rect)
    picture = pygame.transform.scale(load_image('intro_picture.jpg'), (300, 70))
    screen.blit(picture, (100, 400))


# отображение ввода текста пользователем в окне
def print_text(text):
    font = pygame.font.Font(None, 40)
    text_coord = 310
    pygame.draw.rect(screen, 'black', (105, 305, 290, 40), 0)
    string_rendered = font.render(text, 20, pygame.Color('yellow'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top = text_coord
    intro_rect.x = 110
    screen.blit(string_rendered, intro_rect)
    pygame.display.flip()


# обработка ввода
def start_screen():
    need_input = False
    input_text = ''
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif need_input is False and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return 'default_level'
            elif need_input and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return input_text
                elif event.key == pygame.K_BACKSPACE:
                    if len(input_text) > 0:
                        input_text = input_text[:-1]
                else:
                    if len(input_text) <= 20:
                        input_text += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.pos[0] > 100 and event.pos[0] < 400 and \
                        event.pos[1] > 300 and event.pos[1] < 350:
                    need_input = True
        print_text(input_text)
        pygame.display.flip()


# отображение уровней (необходимо название уровня и количество
def show_level(level, count1, count2):
    pygame.init()
    size = count1 * 18 + 100, count2 * 18 + 100
    screen = pygame.display.set_mode(size)
    screen.fill('black')
    pygame.display.set_caption('play pacman')
    try:
        player, level_x, level_y = generate_level(load_level(level))
    except FileNotFoundError:
        player, level_x, level_y = generate_level(load_level('default_level.txt'))
    all_sprites.draw(screen)
    pygame.display.flip()
    return player, level_x, level_y


# класс пакмена
class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = load_image_pacman('pacman.gif')
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 50, tile_height * pos_y + 50)
        self.x = pos_x
        self.y = pos_y
        self.score = 0

    # проверяет все столкновения
    def collides(self):
        lst = ['vertical', 'horisontal', '1', '2', '3', '4']
        if pygame.sprite.spritecollideany(self, tiles_group) is None or \
            pygame.sprite.spritecollideany(self, tiles_group).image in [tile_images[_] for _ in lst]:
            return False
        else:
            if pygame.sprite.spritecollideany(self, tiles_group).image is tile_images['point']:
                self.score += 10
                tile = pygame.sprite.spritecollideany(self, tiles_group)
                tile.image = tile_images['empty']
            elif pygame.sprite.spritecollideany(self, tiles_group).image is tile_images['energo']:
                self.score += 50
                tile = pygame.sprite.spritecollideany(self, tiles_group)
                tile.image = tile_images['empty']
            # СЮДА ДОПИСАТЬ ОБРАБОТКУ СТОЛКНОВЕНИЙ С ПРИЗРАКАМИ
            return True

    # обрабатывает движение пакмена влево
    def update_left(self):
        self.rect = self.rect.move(-9, 0)
        fl = self.collides()
        self.rect = self.rect.move(9, 0)
        lst_picture = ['l_0', 'l_1', 'l_2', 'l_3', 'l_4', 'l_5', 'l_6', 'l_7', 'l_0']
        if fl:
            for _ in range(9):
                self.rect = self.rect.move(-1, 0)
                self.image = load_image_pacman(lst_picture[_] + '.gif')
                all_sprites.draw(screen)
                player_group.draw(screen)
                pygame.display.flip()
                clock.tick(FPS)

    # обрабатыает движения пакмена вправо
    def update_right(self):
        self.rect = self.rect.move(18, 0)
        fl = self.collides()
        self.rect = self.rect.move(-18, 0)
        lst_picture = ['r_0', 'r_1', 'r_2', 'r_3', 'r_4', 'r_5', 'r_6', 'r_7', 'r_0']
        if fl:
            for _ in range(9):
                self.rect = self.rect.move(1, 0)
                self.image = load_image_pacman(lst_picture[_] + '.gif')
                all_sprites.draw(screen)
                player_group.draw(screen)
                pygame.display.flip()
                clock.tick(FPS)

    # обрабатывает движения пакмена вверх
    def update_up(self):
        self.rect = self.rect.move(0, -9)
        fl = self.collides()
        self.rect = self.rect.move(0, 9)
        lst_picture = ['u_0', 'u_1', 'u_2', 'u_3', 'u_4', 'u_5', 'u_6', 'u_7', 'u_0']
        if fl:
            for _ in range(9):
                self.rect = self.rect.move(0, -1)
                self.image = load_image_pacman(lst_picture[_] + '.gif')
                all_sprites.draw(screen)
                player_group.draw(screen)
                pygame.display.flip()
                clock.tick(FPS)

    # обрабатывает движения пакмена вниз
    def update_down(self):
        self.rect = self.rect.move(0, 18)
        fl = self.collides()
        self.rect = self.rect.move(0, -18)
        lst_picture = ['d_0', 'd_1', 'd_2', 'd_3', 'd_4', 'd_5', 'd_6', 'd_7', 'd_0']
        if fl:
            for _ in range(9):
                self.rect = self.rect.move(0, 1)
                self.image = load_image_pacman(lst_picture[_] + '.gif')
                all_sprites.draw(screen)
                player_group.draw(screen)
                pygame.display.flip()
                clock.tick(FPS)


if __name__ == '__main__':
    pygame.init()
    size = width, height = 500, 500
    screen = pygame.display.set_mode(size)
    running = True
    player = None
    print_intro()
    level = start_screen()
    if '.txt' not in level:
        level += '.txt'
    try:
        load_level(level)
    except FileNotFoundError:
        level = 'default_level.txt'
    count2 = len(load_level(level))
    count1 = len(load_level(level)[0])
    player, level_x, level_y = show_level(level, count1, count2)
    clock = pygame.time.Clock()
    FPS = 60
    while running:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.update_left()
        elif keys[pygame.K_RIGHT]:
            player.update_right()
        elif keys[pygame.K_UP]:
            player.update_up()
        elif keys[pygame.K_DOWN]:
            player.update_down()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.update_left()
                elif event.key == pygame.K_RIGHT:
                    player.update_right()
                elif event.key == pygame.K_UP:
                    player.update_up()
                elif event.key == pygame.K_DOWN:
                    player.update_down()
        all_sprites.draw(screen)
        player_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)