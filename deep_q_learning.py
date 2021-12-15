'''
   This code was written by following the following PyTorch tutorial
   Tutorial Title: TRAIN A MARIO-PLAYING RL AGENT
   Project Title: MadMario
   Author: Yuansong Feng, Suraj Subramanian, Howard Wang, Steven Guo
   Date: June 2020
   Code version: 2.0
   Availability: https://pytorch.org/tutorials/intermediate/mario_rl_tutorial.html#train-a-mario-playing-rl-agent
                 https://github.com/YuansongFeng/MadMario
'''

import torch
from pathlib import Path
import random, datetime, numpy as np, cv2
from gym.wrappers import FrameStack, GrayScaleObservation, TransformObservation
from agents.deep_q_learning_agent import DeepQLearningMario

from nes_py.wrappers import JoypadSpace

import gym_super_mario_bros

from util.deep_q_logging import MetricLogger
from util.wrappers import SkipFrame, ResizeObservation

env = gym_super_mario_bros.make('SuperMarioBros-1-1-v0')

env = JoypadSpace(
    env,
    [['right'],
    ['right', 'A']]
)
env = SkipFrame(env, skip=4)
env = GrayScaleObservation(env, keep_dim=False)
env = ResizeObservation(env, shape=84)
env = TransformObservation(env, f=lambda x: x / 255.)
env = FrameStack(env, num_stack=4)

save_dir = Path('./data/checkpoints')

mario = DeepQLearningMario(state_dim=(4, 84, 84), action_dim=env.action_space.n, save_dir=save_dir)

logger = MetricLogger(save_dir)

episodes = 40000

for e in range(episodes):

    state = env.reset()

    while True:

        action = mario.act(state)

        next_state, reward, done, info = env.step(action)

        mario.cache(state, next_state, action, reward, done)

        q, loss = mario.learn()

        logger.log_step(reward, loss, q)

        state = next_state

        if done or info['flag_get']:
            break

    logger.log_episode()

    if e % 20 == 0:
        logger.record(
            episode=e,
            epsilon=mario.exploration_rate,
            step=mario.curr_step
        )
