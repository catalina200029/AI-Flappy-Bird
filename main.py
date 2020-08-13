import pygame
#import neat
import time
from PIL import Image
import os
import math
import random

pygame.init()
pygame.font.init()

SCALE_AMOUNT = 1.75

WIN_WIDTH = int(288 * 1.75) #288
WIN_HEIGHT = int(512 * 1.75) #512
BORDER = 3

BACKGROUND = pygame.transform.rotozoom(pygame.image.load(os.path.join("imgs", "bg.png")), 0, SCALE_AMOUNT)
FLOOR = pygame.transform.rotozoom(pygame.image.load(os.path.join("imgs", "base.png")), 0, SCALE_AMOUNT)
BIRDS = [pygame.transform.rotozoom(pygame.image.load(os.path.join("imgs", "bird1.png")), 0, SCALE_AMOUNT), pygame.transform.rotozoom(pygame.image.load(os.path.join("imgs", "bird2.png")), 0, SCALE_AMOUNT), pygame.transform.rotozoom(pygame.image.load(os.path.join("imgs", "bird3.png")), 0, SCALE_AMOUNT)]
PIPE = pygame.transform.rotozoom(pygame.image.load(os.path.join("imgs", "pipe.png")), 0, SCALE_AMOUNT)

pygame.display.set_caption('AI Flappy Bird')


class Object:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.w = img.get_width()
        self.h = img.get_height()
        self.img = img

    def display(self, win):
        win.blit(self.img, (self.x, self.y))


class Background(Object):
    pass


class Floor(Object):
    VEL = 5

    def move(self):
        if self.x + self.w <= WIN_WIDTH:
            self.x = 0
        else:
            self.x -= self.VEL


class Bird():
    ROT_VEL = 20

    def __init__(self, x, y, imgs):
        self.x = x
        self.y = y
        self.imgs = imgs
        self.img_count = 0
        self.vel = 0
        self.tick_count = 0
        self.h = self.y
        self.angle = 0
        self.score = 0

    def display(self, win):
        new_image = pygame.transform.rotate(self.imgs[self.img_count], self.angle)
        win.blit(new_image, (self.x, self.y))

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.h = self.y
        self.img_count = 0

    def move(self):
        self.tick_count += 1
        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2
        if d >= 16:
            d = 16

        if d < 0:
            d -= 2

        self.y += d

        if d < 0 or self.y < self.y < self.h + 50:
            if self.angle < 25:
                self.angle = 25
        else:
            if self.angle > -90:
                self.angle -= self.ROT_VEL

        if d > 0:
            self.img_count = 2

    def get_mask(self):
        return pygame.mask.from_surface(self.imgs[self.img_count])


class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x, img):
        self.x = x

        self.top_h = random.randrange(WIN_HEIGHT - img.get_height() - self.GAP, WIN_HEIGHT - self.GAP - FLOOR.get_height())
        self.bottom_h = WIN_HEIGHT - self.top_h - self.GAP

        self.top_y = self.top_h - img.get_height()
        self.bottom_y = self.GAP + self.top_h

        self.top_img = pygame.transform.flip(img, False, True)
        self.bottom_img = img

        self.passed = False

    def move(self):
        self.x -= self.VEL

    def check_has_passed(self, bird):
        if not self.passed and self.x + self.bottom_img.get_width() < bird.x:
            self.passed = True
            bird.score += 1

    def display(self, win):
        win.blit(self.bottom_img, (self.x, self.bottom_y))
        win.blit(self.top_img, (self.x, self.top_y))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.top_img)
        bottom_mask = pygame.mask.from_surface(self.bottom_img)

        top_offset = (round(self.x - bird.x), self.top_y - round(bird.y))
        bottom_offset = (round(self.x - bird.x), self.bottom_y - round(bird.y))

        top_point = bird_mask.overlap(top_mask, top_offset)
        bottom_point = bird_mask.overlap(bottom_mask, bottom_offset)

        if top_point or bottom_point:
            return True

        return False


def display_win(bird, background, floor, pipes, win):
    background.display(win)
    floor.display(win)
    bird.display(win)

    for i in range(0, 5):
        pipes[i].display(win)


def main():
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    run = True
    game_over = False

    background = Background(0, 0, BACKGROUND)
    floor = Floor(0, WIN_HEIGHT - FLOOR.get_height(), FLOOR)
    clock = pygame.time.Clock()
    bird = Bird(WIN_WIDTH / 2.2, WIN_HEIGHT / 2, BIRDS)

    pipes = [Pipe(WIN_WIDTH, PIPE)]

    for i in range(1, 5):
        pipes.append(Pipe(pipes[i - 1].x + 250, PIPE))

    font = pygame.font.SysFont('Times New Roman', 32)
    game_over_text = font.render('Game Over', False, (0, 0, 0))
    score_text = font.render('Score: ' + str(bird.score), False, (0, 0, 0))
    game_over_rect = game_over_text.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT / 2))

    while run:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                run = False

        if not run:
            break

        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE] and not game_over:
            bird.jump()

        floor.move()

        bird.move()

        for i in range(0, 5):
            pipes[i].move()
            if not game_over:
                pipes[i].check_has_passed(bird)

        for i in range(0, 5):
            if not pipes[i].passed and pipes[i].collide(bird):
                game_over = True

        score_text = font.render('Score: ' + str(bird.score), False, (0, 0, 0))

        if pipes[0].x + pipes[0].top_img.get_width() <= 0:
            pipes.pop(0)
            pipes.append(Pipe(pipes[3].x + Pipe.GAP, PIPE))

        display_win(bird, background, floor, pipes, win)

        win.blit(score_text, (20, 20))

        if game_over:
            win.blit(game_over_text, game_over_rect)

        pygame.display.update()


main()

pygame.quit()