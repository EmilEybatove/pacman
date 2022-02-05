import pygame
import functions

button_group = pygame.sprite.Group()


class Button(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, text, func):
        super().__init__(button_group)
        self.image = pygame.Surface((300, 50))
        self.rect = pygame.Rect(pos_x, pos_y, 300, 50)
        self.image.fill((35, 35, 35))
        self.down = False
        self.text = text
        self.func = func
        self.pos = (pos_x + 150 - len(text) * 6.75, pos_y + 10)

    def down_event(self):
        self.image.fill((80, 80, 80))
        self.down = True

    def up_event(self):
        self.image.fill((35, 35, 35))
        self.down = False

    def draw_text(self):
        font = pygame.font.Font(None, 40)
        text = font.render(self.text, True, (255, 255, 0))
        screen.blit(text, self.pos)

def play():
    pass


def multiplayer():
    pass


def create_level():
    pass


def exit():
    pass


commands = [play, multiplayer, create_level, exit]
texts = ['play', 'multiplayer', 'create level', 'exit']

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((700, 650))

    picture = pygame.transform.scale(functions.load_image('intro_picture.jpg'), (450, 100))
    screen.blit(picture, (150, 100))

    for i in range(4):
        button = Button(225, 250 + i * 80, texts[i], commands[i])

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in button_group:
                    if button.rect.collidepoint(pygame.mouse.get_pos()):
                        button.down_event()
            elif event.type == pygame.MOUSEBUTTONUP:
                for button in button_group:
                    if button.rect.collidepoint(pygame.mouse.get_pos()) and button.down:
                        button.func()
                    button.up_event()
        button_group.draw(screen)
        for button in button_group:
            button.draw_text()
        pygame.display.flip()
    pygame.quit()
