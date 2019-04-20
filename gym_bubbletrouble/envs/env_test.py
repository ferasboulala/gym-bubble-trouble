import gym
import random
import cv2 as cv
import time

import sys
sys.path.append('../../bubbletrouble')


def test_step(env):
    env.reset()
    for i in range(100):
        state, reward, done, _ = env.step(random.randint(0, 2))
        if done:
            env.reset()
        if not i % 10:
            print('Step {}'.format(i))
            print(state, reward, done)


def test_rendering(env):
    cv.namedWindow('Rendering test')
    env.reset()
    for _ in range(300):
        state, reward, done, _ = env.step(random.randint(0, 3))
        if reward != 0:
            print(reward)
            print(state)
        if done:
            env.reset()
        else:
            img = env.render_with_states()
            cv.imshow('Rendering test', img)
            cv.waitKey(33)
    cv.destroyAllWindows()


def main():
    random.seed(time.time())
    env = gym.make('gym_bubbletrouble:BubbleTrouble-v0')
    print('Testing stepping function')
    test_step(env)
    print('Testing rendering function')
    test_rendering(env)
    env.close()


if __name__ == '__main__':
    main()
