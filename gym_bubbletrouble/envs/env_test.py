import gym
import random
import cv2 as cv
import time

import sys
sys.path.append('../../bubbletrouble')


def test_step(env):
    env.reset()
    for _ in range(100):
        state, reward, done, _ = env.step(random.randint(0, 2))
        if done:
            env.reset()


def test_rendering(env):
    cv.namedWindow('Rendering test')
    env.reset()
    for _ in range(100):
        _, reward, done, _ = env.step(random.randint(0, 2))
        if done:
            env.reset()
        else:
            img = env.render()
            cv.imshow('Rendering test', img)
            if reward != 0:
                print(reward, done)
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
