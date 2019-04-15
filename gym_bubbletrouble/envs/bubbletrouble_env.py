import gym
import BubbleTrouble
import random
import time


ACTION_LEFT = 0
ACTION_RIGHT = 1
ACTION_FIRE = 2

# Limiting through steps instead of time
T_LIMIT = 45
FPS = 30
MAX_N_STEPS = FPS * T_LIMIT


class BubbleTroubleEnv(gym.Env):
    metadata = {'render.modes': ['rgb_array']}

    def __init__(self, rewards=None, rand=True, timed=False):
        self.rewards = rewards
        if self.rewards is None:
            self.rewards = {'moving': 0, 'fire': 0, 'score': 1, 'death': -1, 'win': 1, 'step': 0}
        self.action_space = gym.spaces.Discrete(3)
        self.state = None
        self.reward = None
        self.previous_score = None
        self.rand = rand
        self.timed = timed
        self.n_steps = 0
        self.seed()

    def step(self, action):
        assert self.action_space.contains(action), '%r (%s) invalid' % (action, type(action))

        key = BubbleTrouble.key_map[action]
        BubbleTrouble.handle_key(key, True)
        BubbleTrouble.game_update(restart=False)

        self.state = None   # TODO : Add hand-picked states

        win = BubbleTrouble.is_completed()
        destroyed_object = self.previous_score != BubbleTrouble.score()
        self.previous_score = BubbleTrouble.score()

        self.n_steps += 1
        done = BubbleTrouble.is_over() or (self.n_steps >= MAX_N_STEPS and self.timed)

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
        else:
            fitness += self.rewards['moving']
        if dead:
            fitness += self.rewards['death']
        if win:
            fitness += self.rewards['win']
        if score_change:
            fitness += self.rewards['score']

        return fitness
