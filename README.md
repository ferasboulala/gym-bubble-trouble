# gym-bubble-trouble
A gym environment for RL of the bubble trouble game. `bubbletrouble` contains the pygame implementation of Bubble Trouble made by [stonayeft](https://github.com/stoyaneft/bubble-trouble). The `gym` wrapper is in the `gym_bubbletrouble` directory. To use the environment, you must add the directory to your `PYTHONPATH` or start your python script within that directory.

## Installation
1. `$ cd gym-bubble-trouble`
2. `$ pip install -e .`

## To play
3. `$ cd bubbletrouble`
4. `$ python BubbleTrouble.py`

## Levels
Levels can be edited from the `levels.json` description file. The game will start with the specified amount of objects
it will randomize their positions when starting.
