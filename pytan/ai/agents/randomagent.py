import random
import pytan
from pytan.core.player import Player
from . import BotAgent

class RandomAgent(BotAgent):
    def __init__(self, player: Player):
        super().__init__(player)

    def choose_action(self, env: 'CatanEnv'):
        actions = env.legal_actions
        if len(actions) == 0:
            raise RuntimeError('No actions')
        return random.choice(actions)
