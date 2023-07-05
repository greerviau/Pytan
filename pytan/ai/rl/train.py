import random
import numpy as np
from PIL import Image
import torch
from torch.nn import functional as F
from torch import nn
from pytan.core.player import Player
from pytan.ai.env import CatanEnv
from pytan.ai.agents import DNNAgent

agents = [
    DNNAgent(Player('Net1', 0, 'red')),
    DNNAgent(Player('Net2', 1, 'blue')),
    DNNAgent(Player('Net3', 2, 'white')),
    DNNAgent(Player('Net4', 3, 'orange'))
]

env = CatanEnv(agents)
env.reset()

opt = torch.optim.Adam(policy.parameters(), lr=1e-3)

reward_sum_running_avg = None
for it in range(100000):
    d_obs_history, action_history, action_prob_history, reward_history = [], [], [], []
    for ep in range(10):
        obs, prev_obs = env.reset(), None
        for t in range(190000):
            #env.render()

            d_obs = policy.pre_process(obs, prev_obs)
            with torch.no_grad():
                action, action_prob = policy(d_obs)

            prev_obs = obs
            obs, reward, done, info = env.step(policy.convert_action(action))

            d_obs_history.append(d_obs)
            action_history.append(action)
            action_prob_history.append(action_prob)
            reward_history.append(reward)

            if done:
                reward_sum = sum(reward_history[-t:])
                reward_sum_running_avg = 0.99*reward_sum_running_avg + 0.01*reward_sum if reward_sum_running_avg else reward_sum
                print('Iteration %d, Episode %d (%d timesteps) - last_action: %d, last_action_prob: %.2f, reward_sum: %.2f, running_avg: %.2f' % (it, ep, t, action, action_prob, reward_sum, reward_sum_running_avg))
                break

    # compute advantage
    R = 0
    discounted_rewards = []

    for r in reward_history[::-1]:
        if r != 0: R = 0 # scored/lost a point in pong, so reset reward sum
        R = r + policy.gamma * R
        discounted_rewards.insert(0, R)

    discounted_rewards = torch.FloatTensor(discounted_rewards)
    discounted_rewards = (discounted_rewards - discounted_rewards.mean()) / discounted_rewards.std()

    # update policy
    for _ in range(5):
        n_batch = 24576
        idxs = random.sample(range(len(action_history)), n_batch)
        d_obs_batch = torch.cat([d_obs_history[idx] for idx in idxs], 0)
        action_batch = torch.LongTensor([action_history[idx] for idx in idxs])
        action_prob_batch = torch.FloatTensor([action_prob_history[idx] for idx in idxs])
        advantage_batch = torch.FloatTensor([discounted_rewards[idx] for idx in idxs])

        opt.zero_grad()
        loss = policy(d_obs_batch, action_batch, action_prob_batch, advantage_batch)
        loss.backward()
        opt.step()

    if it % 5 == 0:
        torch.save(policy.state_dict(), 'params.ckpt')

env.close()