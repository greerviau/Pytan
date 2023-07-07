import random
import os
import torch
from torch.nn import functional as F
from torch import nn
import numpy as np
from pytan.core.game import Game
from pytan.core.player import Player
from pytan.ai.env import CatanEnv
from pytan.ai.agents import DNNAgent
from pytan.ai.agents.dnnagent import Policy
from pytan.log.logging import Logger

agents = [
    DNNAgent(Player('P1', 0, 'red')),
    DNNAgent(Player('P2', 1, 'blue')),
    DNNAgent(Player('P3', 2, 'white')),
    DNNAgent(Player('P4', 3, 'orange'))
]

env = CatanEnv(agents, logger=Logger(log_file=None, console_log=False))

policy = Policy()

opt = torch.optim.Adam(policy.parameters(), lr=1e-3)

ITTERATIONS = 10000
GAMES = 100
TIMESTEPS = 190000

reward_sum_running_avg = None
first_spot_wins, second_spot_wins, third_spot_wins, fourth_spot_wins = 0,0,0,0
running_turn_avg = None
for it in range(ITTERATIONS):
    d_obs_history, value_history, reward_history, = [], [], []
    turns = []
    for g in range(GAMES):
        obs, prev_obs = env.reset(), None
        for t in range(TIMESTEPS):
            #env.render()
            current_player_id = env.game.current_player.id
            agent = env.agents[current_player_id]
            legal_actions = env.legal_actions
            if len(legal_actions) == 0:
                print(env.game.state)
                raise RuntimeError('No actions')
            
            game = Game.create_from_state(env.game.get_state())

            values = []
            for function, args in legal_actions:
                getattr(game, function)(*args)

                i_obs = env.get_state_vector(game)

                d_obs = policy.pre_process(i_obs, prev_obs)

                with torch.no_grad():
                    action_prob = policy(d_obs)
                    values.append(action_prob)
                    
                game.undo()
            final_value = max(values)
            c = values.count(final_value)
            if c > 1:
                action_i = random.choice([i for i, s in enumerate(values) if s == final_value])
            else:
                action_i = values.index(final_value)

            action = legal_actions[action_i]

            prev_obs = obs
            obs, reward, done, info = env.step(action)

            d_obs_history.append(policy.pre_process(obs, prev_obs))
            value_history.append(final_value)
            reward_history.append(reward)

            if done or env.game.turn > 500:
                turns.append(env.game.turn)
                avg_turns = sum(turns) / len(turns)

                reward_sum = sum(reward_history[-t:])
                reward_sum_running_avg = 0.99*reward_sum_running_avg + 0.01*reward_sum if reward_sum_running_avg else reward_sum
                print('\rIteration %d, Game %d (%d timesteps) - reward_sum: %.2f, running_avg: %.2f, avg turns: %d   ' % (it, g, t, reward_sum, reward_sum_running_avg, avg_turns), end='')

                scoreboard = env.game.scoreboard
                vps = list(scoreboard.values())
                ind = vps.index(max(vps))
                if ind == 0:
                    first_spot_wins += 1
                elif ind == 1:
                    second_spot_wins += 1
                elif ind == 2:
                    third_spot_wins += 1
                elif ind == 3:
                    fourth_spot_wins += 1
                break
                
    print()

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
        try:
            idxs = random.sample(range(len(value_history)), n_batch)
        except:
            idxs = range(len(value_history))
        d_obs_batch = torch.cat([d_obs_history[idx] for idx in idxs], 0)
        value_batch = torch.FloatTensor(np.array([value_history[idx] for idx in idxs]))
        advantage_batch = torch.FloatTensor([discounted_rewards[idx] for idx in idxs])

        opt.zero_grad()
        loss = policy(d_obs_batch, value_batch, advantage_batch)
        loss.backward()
        opt.step()

    if it % 5 == 0:
        avg_turns = sum(turns) / len(turns)
        running_turn_avg = 0.99*running_turn_avg + 0.01*avg_turns if running_turn_avg else avg_turns
        os.makedirs('ppo_models', exist_ok=True)
        torch.save(policy.state_dict(), f'ppo_models/model_itter_{it}.ckpt')
        print('Model Saved')
        print('Stats:')
        print('Average Turns: ', running_turn_avg)
        print('Starting Place Wins:')
        print('\tFirst: ', first_spot_wins)
        print('\tSecond: ', second_spot_wins)
        print('\tThird: ', third_spot_wins)
        print('\tFourth: ', fourth_spot_wins)