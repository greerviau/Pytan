from pytan.core.player import Player

class Agent:
    def __init__(self, bot: bool, player: Player):
        self.__bot = bot
        self.__player = player

    @property
    def bot(self) -> bool:
        return self.__bot

    @property
    def player(self) -> Player:
        return self.__player

    @property
    def player_id(self) -> int:
        return self.__player.id

class Human(Agent):
    def __init__(self, player: Player):
        super().__init__(False, player)

class BotAgent(Agent):
    def __init__(self, player: Player):
        super().__init__(True, player)

from .randomagent import RandomAgent
from .greedyagent import GreedyAgent
from .dnnagent import DNNAgent