import torch
import torch.nn as nn
import torch.optim as optim
from pytan.core.player import Player
from .greedyagent import GreedyAgent

class Policy(nn.Module):
        def __init__(self):
            super(Policy, self).__init__()

            self.gamma = 0.99
            self.eps_clip = 0.1

            self.layers = nn.Sequential(
                nn.Linear(6000, 512), nn.ReLU(),
                nn.Linear(512, 2),
            )

        def state_to_tensor(self, I):
            """ prepro 210x160x3 uint8 frame into 6000 (75x80) 1D float vector. See Karpathy's post: http://karpathy.github.io/2016/05/31/rl/ """
            if I is None:
                return torch.zeros(1, 6000)
            I = I[35:185] # crop - remove 35px from start & 25px from end of image in x, to reduce redundant parts of image (i.e. after ball passes paddle)
            I = I[::2,::2,0] # downsample by factor of 2.
            I[I == 144] = 0 # erase background (background type 1)
            I[I == 109] = 0 # erase background (background type 2)
            I[I != 0] = 1 # everything else (paddles, ball) just set to 1. this makes the image grayscale effectively
            return torch.from_numpy(I.astype(np.float32).ravel()).unsqueeze(0)

        def pre_process(self, x, prev_x):
            return self.state_to_tensor(x) - self.state_to_tensor(prev_x)

        def convert_action(self, action):
            return action + 2

        def forward(self, d_obs, action=None, action_prob=None, advantage=None, deterministic=False):
            if action is None:
                with torch.no_grad():
                    logits = self.layers(d_obs)
                    if deterministic:
                        action = int(torch.argmax(logits[0]).detach().cpu().numpy())
                        action_prob = 1.0
                    else:
                        c = torch.distributions.Categorical(logits=logits)
                        action = int(c.sample().cpu().numpy()[0])
                        action_prob = float(c.probs[0, action].detach().cpu().numpy())
                    return action, action_prob
                
class DNNAgent(GreedyAgent):
    def __init__(self, player: Player):
        super().__init__(player)
        self.model = self.StateScoreModel()

    def score_state(self):
        curr_player = self.game.get_player_by_id(self.player.id)
        state_vector = []
        state_vector.append(curr_player.victory_points * 100)
        state_vector.append(self.game.turn)
        state_vector.append(self.calculate_exploration_score(curr_player.id))
        state_vector.append(curr_player.longest_road)
        state_vector.append(curr_player.settlements)
        state_vector.append(curr_player.cities)
        state_vector.append(curr_player.pp_score)
        state_vector.append(curr_player.diversity_score)
        state_vector.append(len(curr_player.dev_cards))
        state_vector.append(curr_player.largest_army)
        state_vector.append(curr_player.can_buy_city())
        state_vector.append(curr_player.can_buy_settlement())
        state_vector.append(curr_player.can_buy_road())
        state_vector.append(curr_player.can_buy_dev_card())
        state_vector.append(self.robber_score(curr_player.id))

        score = self.forward_pass(state_vector)

        return score
    
    def forward_pass(self, vector: list):
        return 0
    
    