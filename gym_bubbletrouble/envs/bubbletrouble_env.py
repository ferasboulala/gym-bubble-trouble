import gym
import BubbleTrouble
from settings import *
import numpy as np
import cv2 as cv

import random
import time


ACTION_LEFT = 0
ACTION_RIGHT = 1
ACTION_FIRE = 2
ACTION_IDLE = 3

T_LIMIT = 45
MAX_N_STEPS = FPS * T_LIMIT


class BubbleTroubleEnv(gym.Env):
    metadata = {'render.modes': ['rgb_array']}

    def __init__(self, K=5, rewards=None, rand=True, timed=False):
        self.rewards = rewards
        if self.rewards is None:
            self.rewards = {'moving': 0, 'fire': 0, 'score': 1, 'death': -1, 'win': 1, 'step': 0}
        self.action_space = gym.spaces.Discrete(4)
        self.state = None
        self.reward = None
        self.previous_score = None
        self.rand = rand
        self.timed = timed
        self.K = K
        self.n_steps = 0
        self.seed()

    def step(self, action):
        assert self.action_space.contains(action), '%r (%s) invalid' % (action, type(action))

        key = BubbleTrouble.key_map[action]
        BubbleTrouble.handle_key(key, True)
        BubbleTrouble.game_update(restart=False)

        self.state = self.extract_state()

        win = BubbleTrouble.is_completed()
        destroyed_object = self.previous_score != BubbleTrouble.score()
        self.previous_score = BubbleTrouble.score()

        self.n_steps += 1
        done = BubbleTrouble.is_over() or (self.n_steps >= MAX_N_STEPS and self.timed) or win

        self.reward = self._f(action, done, win, destroyed_object)

        return self.state, self.reward, done, {}

    def reset(self):
        self.n_steps = 0
        BubbleTrouble.game_start(self.rand, False)
        BubbleTrouble.game_update(restart=False)
        self.previous_score = BubbleTrouble.score()

    def render(self, mode='rgb_array', *args, **kwargs):
        assert mode == 'rgb_array'
        image = BubbleTrouble.surface_image()
        return image.swapaxes(1, 2).transpose((2, 0, 1))

    def seed(self, seed=time.time()):
        random.seed(seed)

    def close(self):
        BubbleTrouble.quit_game()

    def _f(self, action, dead, win, score_change):
        fitness = self.rewards['step']
        if action == ACTION_FIRE:
            fitness += self.rewards['fire']
        elif action != ACTION_IDLE:
            fitness += self.rewards['moving']
        if dead:
            fitness += self.rewards['death']
        if win:
            fitness += self.rewards['win']
        if score_change:
            fitness += self.rewards['score']

        return fitness

    def extract_state(self):
        game = BubbleTrouble.game
        player = game.player
        c_x = player.position() / WINDOWWIDTH
        t = self.n_steps / MAX_N_STEPS
        shoot = player.can_shoot()

        objects_states = [0, 0, 0, 0, 0] * self.K
        objects = game.balls + game.hexagons
        objects.sort(key=lambda obj: self.euclidean_distance_squared(obj.position(),
                                                                     (player.position(), WINDOWHEIGHT)))
        n = len(objects) / MAX_BALLS_AT_ALL_TIME

        for i, obj in enumerate(objects):
            if i == self.K:
                break
            objects_states[i*5:i*5+5] = [
                obj.size / MAX_BALL_SIZE,
                obj.position()[0] / WINDOWWIDTH,
                obj.position()[1] / WINDOWHEIGHT,
                obj.speed[0] / WINDOWWIDTH,
                obj.speed[1] / WINDOWHEIGHT
            ]

        return np.array([n, t, c_x, shoot] + objects_states)

    @staticmethod
    def euclidean_distance_squared(p1, p2):
        return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2

    def render_with_states(self):
        img = np.ascontiguousarray(self.render(), dtype=np.uint8)
        _, _, c_x, _, *balls = self.extract_state()

        for i in range(self.K):
            size, x, y, _, _ = balls[i*5:i*5+5]
            x, y = x * WINDOWWIDTH, y * WINDOWHEIGHT
            if size == 0:
                break
            d = size * MAX_BALL_SIZE * SIZE_TO_PIXELS
            p1, p2 = (int(x - d/2), int(y - d/2)), (int(x + d/2), int(y + d/2))
            img = cv.rectangle(img, p1, p2, GREEN, 2)
            img = cv.line(img, (int(x), int(y)), (int(c_x * WINDOWWIDTH), WINDOWHEIGHT), GREEN, 2)

        return img
