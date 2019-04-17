from threading import Timer
import json
import random

import pygame

from bubbles import Ball, Hexagon
from player import Player
from settings import *

RAND_SHIFT = 200


class BubbleTroubleGame:
    def __init__(self, level=1):
        self.balls = []
        self.hexagons = []
        self.player = Player()
        self.game_over = False
        self.level_completed = False
        self.time_left = 0
        self.timers = None
        self.level = level
        self.score = 0

    def load_level(self, level=1, rand=True, timed=True):
        self.__init__(level)
        self.player.set_position(WINDOWWIDTH / 2)
        self.player.is_alive = True

        with open(APP_PATH + 'levels.json', 'r') as levels_file:
            levels = json.load(levels_file)
            level = levels[str(self.level)]
            self.time_left = level['time']

            for ball in level['balls']:
                x, y = ball['x'], ball['y']
                if not self._valid_coordinates(x, y):
                    raise ValueError('Object coordinates should be set between 0 and 1')
                x, y = x * WINDOWWIDTH, y * WINDOWHEIGHT
                if rand:
                    x, y = x + random.randint(-RAND_SHIFT, RAND_SHIFT), y + random.randint(-RAND_SHIFT, RAND_SHIFT)
                size = ball['size']
                if size > MAX_BALL_SIZE:
                    raise ValueError('Ball cannot exceed {}'.format(MAX_BALL_SIZE))
                speed = ball['speed']
                for s in speed:
                    if s < 0:
                        raise ValueError('Object velocity must be non-negative')
                self.balls.append(Ball(x, y, size, speed))

            for hexagon in level['hexagons']:
                x, y = hexagon['x'], hexagon['y']
                if not self._valid_coordinates(x, y):
                    raise ValueError('Object coordinates should be set between 0 and 1')
                x, y = x * WINDOWWIDTH, y * WINDOWHEIGHT
                if rand:
                    x, y = x + random.randint(-RAND_SHIFT, RAND_SHIFT), y + random.randint(-RAND_SHIFT, RAND_SHIFT)
                size = hexagon['size']
                if size > MAX_BALL_SIZE:
                    raise ValueError('Ball cannot exceed {}'.format(MAX_BALL_SIZE))
                if size < 1:
                    raise ValueError('Object size must be a positive integer.')
                speed = hexagon['speed']
                for s in speed:
                    if s < 0:
                        raise ValueError('Object velocity must be non-negative')
                self.hexagons.append(Hexagon(x, y, size, speed))

        if timed:
            self._set_timers()

    def restart(self):
        self.exit_game()

    def update(self, restart=True):
        if restart:
            if self.level_completed or self.game_over:
                self.restart()
                self.load_level(self.level)
                return
        self._check_for_collisions()
        for ball in self.balls:
            ball.update()
        for hexagon in self.hexagons:
            hexagon.update()
        self.player.update()
        if not self.balls and not self.hexagons:
            self.level_completed = True

    def exit_game(self):
        self._stop_timers()

    def move_player(self, direction):
        self.player.moving_right = direction == -1
        self.player.moving_left = direction == 1

    def fire_player(self):
        self.move_player(0)
        self.player.shoot()

    def stop_player(self):
        self.player.stop_moving()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit_game()

    def _check_for_collisions(self):
        self._check_for_bubble_collision(self.balls, True)
        self._check_for_bubble_collision(self.hexagons, False)

    def _check_for_bubble_collision(self, bubbles, is_ball):
        for bubble_index, bubble in enumerate(bubbles):
            if pygame.sprite.collide_rect(bubble, self.player.weapon) \
                    and self.player.weapon.is_active:
                self.player.reload()
                self.score += 1
                if is_ball:
                    self._split_ball(bubble_index)
                else:
                    self._split_hexagon(bubble_index)
                return True
            if pygame.sprite.collide_mask(bubble, self.player):
                self.player.is_alive = False
                self._decrease_lives()
                return True
        return False

    def _decrease_lives(self):
        self.player.lives -= 1
        if self.player.lives:
            self.player.is_alive = False
        else:
            self.game_over = True

    def _split_ball(self, ball_index):
        ball = self.balls[ball_index]
        if ball.size > 1:
            self.balls.append(Ball(
                ball.rect.left - ball.size**2,
                ball.rect.top - 10, ball.size - 1, [-3, -5])
            )
            self.balls.append(
                Ball(ball.rect.left + ball.size**2,
                     ball.rect.top - 10, ball.size - 1, [3, -5])
            )
        del self.balls[ball_index]

    def _split_hexagon(self, hex_index):
        hexagon = self.hexagons[hex_index]
        if hexagon.size > 1:
            self.hexagons.append(
                Hexagon(hexagon.rect.left, hexagon.rect.centery,
                        hexagon.size - 1, [-3, -5]))
            self.hexagons.append(
                Hexagon(hexagon.rect.right, hexagon.rect.centery,
                        hexagon.size - 1, [3, -5]))
        del self.hexagons[hex_index]

    def _set_timers(self):
        self._stop_timers()
        self.timers = [Timer(t, self._tick, []) for t in range(0, self.time_left)]
        for timer in self.timers:
            timer.start()

    def _tick(self):
        self.time_left -= 1
        if self.time_left == 0:
            self._decrease_lives()

    def _stop_timers(self):
        if self.timers is not None:
            for timer in self.timers:
                if timer.is_alive():
                    timer.cancel()
        self.timers = None

    @staticmethod
    def _valid_coordinates(x, y):
        return 0 <= x <= 1 and 0 <= y <= 1
