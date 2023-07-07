import random
import torch
import torch.nn as nn
import torch.optim as optim
from torch.nn import functional as F
import numpy as np
from pytan.core.game import Game
from pytan.core.player import Player
from .greedyagent import BotAgent

class Policy(nn.Module):
    def __init__(self):
        super(Policy, self).__init__()

        self.gamma = 0.99
        self.eps_clip = 0.1

        self.model = nn.Sequential(
            nn.Linear(15, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1)
        )

    def state_to_tensor(self, I):
        return torch.from_numpy(I.astype(np.float32).ravel()).unsqueeze(0)
    
    def pre_process(self, x, prev_x):
        return self.state_to_tensor(np.array(x)) - self.state_to_tensor(np.array(prev_x))

    def forward(self, d_obs, value=None, advantage=None, deterministic=False):
        if value is None:
            with torch.no_grad():
                logits = self.model(d_obs)
                value = logits[0].detach().cpu().numpy()
                return value
    
        # PPO
        ts = torch.FloatTensor(value.cpu().numpy())

        logits = self.model(d_obs)
        r = torch.sum(F.softmax(logits, dim=1) * ts, dim=1) / value
        loss1 = r * advantage
        loss2 = torch.clamp(value, 1-self.eps_clip, 1+self.eps_clip) * advantage
        loss = -torch.min(loss1, loss2)
        loss = torch.mean(loss)

        return loss
                
class DNNAgent(BotAgent):
    def __init__(self, player: Player):
        super().__init__(player)
        self.policy = Policy()

    def choose_action(self, env: 'CatanEnv'):
        actions = env.legal_actions
        if len(actions) == 0:
            raise RuntimeError('No actions')

        #print(game.get_state())

        game = Game.create_from_state(env.game.get_state())

        scores = []
        for function, args in actions:
            getattr(game, function)(*args)
            scores.append(self.score_state(env.get_state_vector(game)))
            game.undo()
        m = max(scores)
        c = scores.count(m)
        if c > 1:
            i = random.choice([i for i, s in enumerate(scores) if s == m])
        else:
            i = scores.index(m)
        action = actions[i]
        return action

    def score_state(self, state):

        score = self.forward_pass(state)

        return score
    
    def forward_pass(self, vector: list):
        return 0
    
    