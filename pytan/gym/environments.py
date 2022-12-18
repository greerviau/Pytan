import random
from itertools import combinations
import gym

from pytan.core.game import Game
from pytan.core.cards import ResourceCards
from pytan.core.state import GameStates
from pytan.core.ports import PortTypes
from pytan.log.logging import Logger
from pytan.gym.agents import Agent, RandomAgent, GreedyAgent

class CatanEnv(gym.Env):
    def __init__(self, agents: list[Agent], logger = None, verbose = False, manual = False):
        super(CatanEnv, self).__init__()
        self.name = 'catan'
        self.manual = manual

        self.agents = dict(zip([agent.player_id for agent in agents], agents))

        self.game = Game(players=[agent.player for agent in agents], logger=logger)

        #self.valid_actions = []

        #self.action_space = gym.spaces.Discrete()
        #self.observation_space = gym.spaces.Box(0, 1, (self.total_cards * self.total_positions + self.n_players + self.action_space.n ,))

        self.verbose = verbose

    @property
    def current_player(self):
        return self.agents[self.game.current_player.id]

    @property
    def legal_actions(self):
        actions = []
        if self.game.state.can_roll():
            actions.append(('roll', []))
        if self.game.state == GameStates.DISCARDING:
            actions.extend(self.get_discard_options())
        if self.game.state == GameStates.MOVING_ROBBER:
            actions.extend(self.get_valid_robber())
        if self.game.state == GameStates.STEALING:
            actions.extend(self.get_valid_steals())
        if self.game.state == GameStates.ACCEPTING_TRADE:
            actions.append(('accept_trade', []))
            actions.append(('decline_trade', []))
        if self.game.state.can_buy_dev_card():
            actions.append(('buy_dev_card', []))
        if self.game.state.can_play_knight():
            actions.append(('play_knight', []))
        if self.game.state.can_play_monopoly():
            actions.extend(self.get_valid_monopolies())
        if self.game.state.can_play_year_plenty():
            actions.extend(self.get_valid_year_plenty())
        if self.game.state.can_play_road_builder():
            actions.append(('play_road_builder', []))
        if self.game.state.can_trade():
            actions.extend(self.get_valid_trades())

        actions.extend(self.get_valid_build_actions())

        if self.game.state.can_pass_turn() and not actions:
            actions.append(('pass_turn', []))

        return actions

    def is_legal(self, action):
        return action in self.legal_actions

    def get_discard_options(self):
        actions = []
        n = self.game.current_player.n_resource_cards // 2
        discards = set(combinations(self.game.current_player.resource_cards_list, n))
        for discard in discards:
            unique = set(discard)
            actions.append(('discard', [[(card, discard.count(card)) for card in unique]]))
        return actions

    def get_valid_robber(self):
        return [('move_robber', [coord]) for coord in self.game.board.legal_robber_placements()]

    def get_valid_steals(self):
        return [('steal', [p.id]) for p in self.game.players_to_steal_from]

    def get_valid_monopolies(self):
        return [('play_monopoly', [card]) for card in ResourceCards]

    def get_valid_year_plenty(self):
        actions = set()
        for card1 in ResourceCards:
            for card2 in ResourceCards:
                actions.add(('play_year_plenty', (card1, card2)))
        return list(actions)

    def get_valid_build_actions(self):
        actions = []
        if self.game.state.can_build_road() or self.game.state == GameStates.STARTING_ROAD:
            for coord in self.game.legal_road_placements():
                actions.append(('build_road', [coord]))
        if self.game.state.can_build_settlement() or self.game.state == GameStates.STARTING_SETTLEMENT:
            for coord in self.game.legal_settlement_placements():
                actions.append(('build_settlement', [coord]))
        if self.game.state.can_build_city():
            for coord in self.game.legal_city_placements():
                actions.append(('build_city', [coord]))
        return actions

    def get_valid_trades(self):
        trades = []
        for g_card in ResourceCards:
            e = 4
            if self.game.board.is_player_on_port(self.game.current_player.id, PortTypes(g_card.value)):
                e = 2
            elif self.game.board.is_player_on_port(self.game.current_player.id, PortTypes.ANY):
                e = 3
            n = self.game.current_player.count_resource_cards(g_card)
            if n >= e:
                for w_card in [c for c in ResourceCards if c != g_card]:
                    trades.append(('offer_trade', [[(g_card, e)], [(w_card, 1)], []]))
        return trades
    
    def reset(self):
        self.game.reset(randomize=True)

    def step(self, action):
        if self.is_legal(action):
            function, args = action
            getattr(self.game, function)(*args)
        