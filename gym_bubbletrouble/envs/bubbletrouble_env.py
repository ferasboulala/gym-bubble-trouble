import gym
import BubbleTrouble
import random
import time


REWARD_MOVING = 0
REWARD_FIRE = 0
REWARD_SCORE = 1
REWARD_DEATH = -1
REWARD_WIN = 1


ACTION_LEFT = 0
ACTION_RIGHT = 1
ACTION_FIRE = 2


class BubbleTroubleEnv(gym.Env):
    metadata = {'render.modes': ['rgb_array']}

    def __init__(self, rand=False):
        self.action_space = gym.spaces.Discrete(3)
        self.state = None
        self.reward = None
        self.previous_score = BubbleTrouble.score()
        self.rand = rand
        self.seed()

    def step(self, action):
        assert self.action_space.contains(action), '%r (%s) invalid' % (action, type(action))

        key = BubbleTrouble.key_map[action]
        BubbleTrouble.handle_key(key, True)
        BubbleTrouble.game_update(restart=False)
        BubbleTrouble.handle_key(key, False)
        BubbleTrouble.game_update(restart=False)

        self.state = None   # TODO : Add hand-picked states

        win = BubbleTrouble.is_completed()
        destroyed_object = self.previous_score != BubbleTrouble.score()
        self.previous_score = BubbleTrouble.score()

        done = BubbleTrouble.is_over()

        self.reward = self._f(action, done, win, destroyed_object)

        return self.state, self.reward, done, {}

    def reset(self):
        BubbleTrouble.game_start(self.rand)
        BubbleTrouble.game_update(restart=False)

    def render(self, mode='rgb_array', *args, **kwargs):
        assert mode == 'rgb_array'
        image = BubbleTrouble.surface_image()
        return image.swapaxes(1, 2)

    def seed(self, seed=time.time()):
        random.seed(seed)

    def close(self):
        BubbleTrouble.quit_game()

    @staticmethod
    def _f(action, dead, win, score_change):
        fitness = 0
        if action != ACTION_FIRE:
            fitness += REWARD_MOVING
        else:
            fitness += REWARD_FIRE
        if dead:
            fitness += REWARD_DEATH
        if win:
            fitness += REWARD_WIN
        if score_change:
            fitness += REWARD_SCORE

        return fitness
