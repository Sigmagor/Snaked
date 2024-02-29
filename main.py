import os
import random
import sys

import pygame


def opposite(direction):
    return {
        "right": "left",
        "left": "right",
        "up": "down",
        "down": "up"
    }.get(direction)


def draw_board(screen):
    global color
    for i in range(20):
        color = (214, 252, 0) if color == (173, 255, 47) else (173, 255, 47)
        for j in range(20):
            pygame.draw.rect(screen, color, (i * 32, j * 32, 32, 32))
            color = (214, 252, 0) if color == (173, 255, 47) else (173, 255, 47)


def load_image(name, colorkey=None):
    fullname = os.path.join("data", name)
    if not os.path.isfile(fullname):
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def mod_menu(is_opened, mods):
    if is_opened:
        for i in mod_buttons:
            i.kill()
    else:
        Button(mod_buttons, 40, 320, "Apple Fly", "button5.png" if "Apple Fly" in mods else "button6.png", (150, 75))
        Button(mod_buttons, 40, 420, "More Apple", "button5.png" if "More Apple" in mods else "button6.png", (150, 75))
        Button(mod_buttons, 40, 520, "Toxic Apple", "button5.png" if "Toxic Apple" in mods else "button6.png",
               (150, 75))


def speed_menu(is_opened, speed):
    if is_opened:
        for i in speed_buttons:
            i.kill()
    else:
        Button(speed_buttons, 450, 320, "Slow", "button3.png" if speed == 12 else "button2.png", (150, 75))
        Button(speed_buttons, 450, 420, "Normal", "button3.png" if speed == 8 else "button2.png", (150, 75))
        Button(speed_buttons, 450, 520, "Fast", "button3.png" if speed == 5 else "button2.png", (150, 75))


def extend():
    global snake_list
    previous = snake_list[-2]
    if previous.rotated:
        if previous.rect.x > snake_list[-3].rect.x:
            snake_list.insert(-1, Body(snake, previous.rect.x + 32, previous.rect.y))
            snake_list[-1].rect.x += 32
        else:
            snake_list.insert(-1, Body(snake, previous.rect.x - 32, previous.rect.y))
            snake_list[-1].rect.x -= 32
    else:
        if previous.rect.y > snake_list[-3].rect.y:
            snake_list.insert(-1, Body(snake, previous.rect.x, previous.rect.y + + 32, rotated=False))
            snake_list[-1].rect.y += 32
        else:
            snake_list.insert(-1, Body(snake, previous.rect.x, previous.rect.y - 32, rotated=False))
            snake_list[-1].rect.y -= 32


def create_apple(toxic=False):
    if toxic:
        apl = Apple(toxic_apples, random.choice(range(0, 640, 32)), random.choice(range(0, 640, 32)), True)
        while pygame.sprite.spritecollideany(apl, snake) or pygame.sprite.spritecollideany(apl, apples):
            apl.kill()
            apl = Apple(toxic_apples, random.choice(range(0, 640, 32)), random.choice(range(0, 640, 32)), True)
    else:
        apl = Apple(apples, random.choice(range(0, 640, 32)), random.choice(range(0, 640, 32)))
        while pygame.sprite.spritecollideany(apl, snake) or pygame.sprite.spritecollideany(apl, toxic_apples):
            apl.kill()
            apl = Apple(apples, random.choice(range(0, 640, 32)), random.choice(range(0, 640, 32)))


class Head(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.image = img(load_image("head.png"), 90)
        self.rect = self.image.get_rect()
        self.rect.x = 160
        self.rect.y = 32
        self.direction = "right"
        self.paused = False

    def update(self):
        if not self.paused:
            if self.direction == "right":
                self.image = img(load_image("head.png"), 90)
            elif self.direction == "left":
                self.image = img(load_image("head.png"), -90)
            elif self.direction == "up":
                self.image = img(load_image("head.png"), 180)
            elif self.direction == "down":
                self.image = load_image("head.png")

    def move(self):
        global prev_pos
        if not self.paused:
            prev_pos = self.rect[:2].copy()
            if self.direction == "right":
                self.rect.x += 32
            elif self.direction == "left":
                self.rect.x -= 32
            elif self.direction == "up":
                self.rect.y -= 32
            elif self.direction == "down":
                self.rect.y += 32

    def change_direction(self, dir):
        if dir:
            if dir[0] != opposite(self.direction):
                self.direction = dir[0]
            del dir[0]

    def check_collision(self):
        if not (0 <= self.rect.x < 640 and 0 <= self.rect.y < 640):
            return True
        for i in snake_list[1:]:
            if pygame.sprite.collide_rect(i, self):
                return True
        return False

    def check_apple(self):
        for i in apples:
            if pygame.sprite.collide_rect(self, i):
                return True, i
        return False, False

    def check_toxic_apple(self):
        for i in toxic_apples:
            if pygame.sprite.collide_rect(self, i):
                return True, i
        return False, False


class Body(pygame.sprite.Sprite):
    def __init__(self, group, x, y, rotated=True):
        super().__init__(group)
        self.image = img(load_image("body.png"), 90) if rotated else load_image("body.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.paused = False
        self.direction = "right"
        self.rotated = rotated

    def update(self):
        if not self.paused:
            index = snake_list.index(self)
            tail = snake_list[index + 1]
            head = snake_list[index - 1]
            if head.rect.y == tail.rect.y:
                self.image = img(load_image("body.png"), 90)
                self.rotated = True
            elif head.rect.x == tail.rect.x:
                self.image = load_image("body.png")
                self.rotated = False
            self.turn(head, tail)

    def move(self):
        global prev_pos
        if not self.paused:
            prev_pos_copy = prev_pos.copy()
            prev_pos = self.rect[:2]
            self.rect.x, self.rect.y = prev_pos_copy

    def turn(self, head, tail):
        if (
                head.rect.y > tail.rect.y and head.rect.x < self.rect.x
        ) or (
                head.rect.y < tail.rect.y and tail.rect.x < self.rect.x
        ):
            self.image = img(load_image("turn.png"), -90)

        if (
                head.rect.y < tail.rect.y and head.rect.x < self.rect.x
        ) or (
                head.rect.y > tail.rect.y and tail.rect.x < self.rect.x
        ):
            self.image = load_image("turn.png")

        if (
                head.rect.y > tail.rect.y and head.rect.x > self.rect.x
        ) or (
                head.rect.y < tail.rect.y and tail.rect.x > self.rect.x
        ):
            self.image = img(load_image("turn.png"), 180)

        if (
                head.rect.y < tail.rect.y and head.rect.x > self.rect.x
        ) or (
                head.rect.y > tail.rect.y and tail.rect.x > self.rect.x
        ):
            self.image = img(load_image("turn.png"), 90)

    def set_direction(self, index):
        self.direction = snake_list[index - 1].direction


class Tail(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.image = img(load_image("tail.png"), 90)
        self.rect = self.image.get_rect()
        self.rect.x = 32
        self.rect.y = 32
        self.direction = "right"
        self.paused = False

    def move(self):
        if not self.paused:
            self.rect.x, self.rect.y = prev_pos

    def update(self):
        if not self.paused:
            if snake_list[-2].rect.y == self.rect.y:
                if snake_list[-2].rect.x > self.rect.x:
                    self.image = img(load_image("tail.png"), 90)
                else:
                    self.image = img(load_image("tail.png"), -90)
            else:
                if snake_list[-2].rect.y > self.rect.y:
                    self.image = load_image("tail.png")
                else:
                    self.image = img(load_image("tail.png"), 180)


class Button(pygame.sprite.Sprite):
    def __init__(self, group, x, y, txt, filename, size):
        super().__init__(group)
        self.image = pygame.transform.scale(load_image(filename), size)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.txt = txt
        self.size = size

    def check_click(self, x, y):
        return self.rect.left <= x <= self.rect.right and self.rect.top <= y <= self.rect.bottom

    def set_txt(self, font):
        f = pygame.font.SysFont('comicsansms', font)
        text = f.render(self.txt, False, (0, 0, 0))
        width, height = text.get_size()
        y = self.rect.y + (self.rect.height - height) // 2
        x = self.rect.x + (self.rect.width - width) // 2
        outline_positions = [
            (-2, -2), (-2, 2), (2, -2), (2, 2)
        ]
        for pos in outline_positions:
            screen.blit(text, (x + pos[0], y + pos[1]))
        text = f.render(self.txt, False, (255, 255, 255))
        screen.blit(text, (x, y))

    def set_img(self, filename):
        self.image = pygame.transform.scale(load_image(filename), self.size)


class Apple(pygame.sprite.Sprite):
    def __init__(self, group, x, y, toxic=False):
        super().__init__(group)
        self.image = load_image("toxic_apple.png") if toxic else load_image("apple.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = [random.choice((2, 1, -1, -2)), random.choice((2, 1, -1, -2))]

    def fly(self):
        self.rect.x += self.direction[0]
        self.rect.y += self.direction[1]
        if not (0 <= self.rect.x <= 608):
            self.direction[0] *= -1
        if not (0 <= self.rect.y <= 608):
            self.direction[1] *= -1


img = pygame.transform.rotate
prev_pos = []
buttons = pygame.sprite.Group()
snake = pygame.sprite.Group()
apples = pygame.sprite.Group()
toxic_apples = pygame.sprite.Group()
speed_buttons = pygame.sprite.Group()
mod_buttons = pygame.sprite.Group()

pygame.init()
color = (255, 255, 255)
screen = pygame.display.set_mode((640, 640))
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()
head = Head(snake)
snake_list = [head, Body(snake, 128, 32), Body(snake, 96, 32), Body(snake, 64, 32), Tail(snake)]


def pause_menu():
    for i in snake_list:
        i.paused = not i.paused
    pressed = False
    resume_button = Button(buttons, 170, 200, "Resume", "button1.png", (300, 150))
    main_menu_button = Button(buttons, 220, 380, "Main Menu", "button2.png", (200, 100))
    Button(buttons, 142, 50, "", "pause.png", (356, 100))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE]:
                    pressed = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if resume_button.check_click(*event.pos):
                    pressed = True
                if main_menu_button.check_click(*event.pos):
                    main_menu()

        if pressed:
            break
        draw_board(screen)
        snake.draw(screen)
        surface = pygame.Surface((640, 640), pygame.SRCALPHA)
        pygame.draw.rect(surface, (0, 0, 0, 150), (0, 0, 640, 640))
        screen.blit(surface, (0, 0))
        buttons.draw(screen)
        resume_button.set_txt(50)
        main_menu_button.set_txt(40)
        pygame.display.flip()
    for i in snake_list:
        i.paused = not i.paused


def main_menu(speed=8, mods=[], score=0):
    global color, screen, buttons, snake, clock, head, snake_list
    for i in buttons:
        i.kill()
    for i in speed_buttons:
        i.kill()
    for i in mod_buttons:
        i.kill()
    play_button = Button(buttons, 220, 250, "Play", "button1.png", (200, 100))
    speed_button = Button(buttons, 450, 225, "Speed", "button1.png", (150, 75))
    mod_button = Button(buttons, 40, 225, "Modifiers", "button1.png", (150, 75))
    if score:
        score_button = Button(buttons, 232, 520, "", "score_button.png", (175, 87))
        Button(buttons, 210, 420, "", "score.png", (220, 87))
    Button(buttons, 95, 85, "", "label.png", (450, 100))
    running = True
    speed_menu_is_opened = False
    mod_menu_is_opened = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.check_click(*event.pos):
                    play(speed, mods)
                if speed_button.check_click(*event.pos):
                    speed_menu(speed_menu_is_opened, speed)
                    speed_menu_is_opened = not speed_menu_is_opened
                    if speed_menu_is_opened:
                        speed_button.set_img("button4.png")
                    else:
                        speed_button.set_img("button1.png")

                if mod_button.check_click(*event.pos):
                    mod_menu(mod_menu_is_opened, mods)
                    mod_menu_is_opened = not mod_menu_is_opened
                    if mod_menu_is_opened:
                        mod_button.set_img("button4.png")
                    else:
                        mod_button.set_img("button1.png")

                if speed_menu_is_opened:
                    for i in speed_buttons:
                        if i.check_click(*event.pos):
                            if i.txt == "Slow":
                                speed = 12
                            elif i.txt == "Normal":
                                speed = 8
                            elif i.txt == "Fast":
                                speed = 5
                            for j in speed_buttons:
                                j.set_img("button2.png")
                            i.set_img("button3.png")

                if mod_menu_is_opened:
                    for i in mod_buttons:
                        if i.check_click(*event.pos):
                            if i.txt in mods:
                                i.image = pygame.transform.scale(load_image("button6.png"), (150, 75))
                            else:
                                i.image = pygame.transform.scale(load_image("button5.png"), (150, 75))
                            mods.remove(i.txt) if i.txt in mods else mods.append(i.txt)
                    print(mods)

        draw_board(screen)
        snake.draw(screen)
        surface = pygame.Surface((640, 640), pygame.SRCALPHA)
        pygame.draw.rect(surface, (0, 0, 0, 150), (0, 0, 640, 640))
        screen.blit(surface, (0, 0))
        buttons.draw(screen)
        speed_buttons.draw(screen)
        mod_buttons.draw(screen)
        play_button.set_txt(60)
        speed_button.set_txt(45)
        mod_button.set_txt(29)
        for i in speed_buttons:
            i.set_txt(40)
        for i in mod_buttons:
            if i.txt == "Apple Fly":
                i.set_txt(30)
            else:
                i.set_txt(24)
        if score:
            score_button.txt = str(len(snake_list) - 5)
            score_button.set_txt(30)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


def play(speed, mods):
    global color, screen, buttons, snake, clock, head, snake_list
    for i in buttons:
        i.kill()
    for i in snake_list:
        i.kill()
    for i in apples:
        i.kill()
    for i in toxic_apples:
        i.kill()
    head = Head(snake)
    snake_list = [head, Body(snake, 128, 32), Body(snake, 96, 32), Body(snake, 64, 32), Tail(snake)]
    score_label = Button(snake, 576, 0, "", "invisibility.png", (64, 64))
    if "More Apple" in mods:
        n = 5
    else:
        n = 1
    for _ in range(n):
        create_apple()
        if "Toxic Apple" in mods:
            create_apple(toxic=True)
    running = True
    count = 0
    direction = []
    for i in snake_list:
        i.paused = not i.paused
    start = True
    while running:
        if head.check_collision():
            main_menu(speed, mods, len(snake_list) - 5)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_a]:
                    direction.append("left")
                elif keys[pygame.K_d]:
                    direction.append("right")
                    if start:
                        for i in snake_list:
                            i.paused = not i.paused
                        start = False
                elif keys[pygame.K_w]:
                    direction.append("up")
                    if start:
                        for i in snake_list:
                            i.paused = not i.paused
                        start = False
                elif keys[pygame.K_s]:
                    direction.append("down")
                    if start:
                        for i in snake_list:
                            i.paused = not i.paused
                        start = False
                if keys[pygame.K_ESCAPE]:
                    pause_menu()
        if count % speed == 0:
            head.change_direction(direction)
            for i in snake_list:
                i.move()
            for i in snake_list:
                i.update()
        count += 1
        if head.check_apple()[0]:
            print(apples.__len__())
            spr = head.check_apple()[1]
            print(apples.__len__())
            spr.kill() if spr else None
            print(apples.__len__())
            create_apple()
            print(apples.__len__())
            print(apples.__len__())
            extend()
            print(apples.__len__())
            print("-" * 20)
        if "Toxic Apple" in mods:
            if head.check_toxic_apple()[0]:
                spr = head.check_toxic_apple()[1]
                spr.kill() if spr else None

                create_apple(toxic=True)
                direction = []
                for _ in range(5):
                    direction.append(random.choice(["up", "down", "right", "left"]))
                    try:
                        while direction[-1] in [direction[-2], opposite(direction[-2])]:
                            del direction[-1]
                            direction.append(random.choice(["up", "down", "right", "left"]))
                    except IndexError:
                        pass
        if "Apple Fly" in mods:
            if not snake_list[0].paused:
                for i in apples:
                    i.fly()
                for i in toxic_apples:
                    i.fly()
        draw_board(screen)
        snake.draw(screen)
        score_label.txt = str(len(snake_list) - 5)
        score_label.set_txt(30)
        apples.draw(screen)
        toxic_apples.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


main_menu()
