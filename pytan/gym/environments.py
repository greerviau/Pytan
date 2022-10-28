import random
from itertools import combinations
import gym

from pytan.core.game import Game
from pytan.core.cards import ResourceCards
from pytan.core.state import GameStates
from pytan.core.ports import PortTypes
from pytan.log.logging import Logger
from pytan.gym.agents import Agent, Human, BotAgent, RandomAgent, GreedyAgent
from pytan.gym import GameEncoder

class CatanEnv(gym.Env):
    def __init__(self, players):
        super().__init__(players=players, logger=logger)

        GameEncoder.init_encoder(self)

        GameEncoder.visualize_tiles()

    @property
    def encoded(self):
        return GameEncoder.encoding()

    def reset(self, randomize: bool = False):
        super().reset(randomize=randomize)
        GameEncoder.init_encoder(self)

    def get_valid_actions(self):
        actions = []
        if self.state.can_roll():
            actions.append(('roll', []))
        if self.state == GameStates.DISCARDING:
            actions.extend(self.get_discard_options())
        if self.state == GameStates.MOVING_ROBBER:
            actions.extend(self.get_valid_robber())
        if self.state == GameStates.STEALING:
            actions.extend(self.get_valid_steals())
        if self.state == GameStates.ACCEPTING_TRADE:
            actions.append(('accept_trade', []))
            actions.append(('decline_trade', []))
        if self.state.can_buy_dev_card():
            actions.append(('buy_dev_card', []))
        if self.state.can_play_knight():
            actions.append(('play_knight', []))
        if self.state.can_play_monopoly():
            actions.extend(self.get_valid_monopolies())
        if self.state.can_play_year_plenty():
            actions.extend(self.get_valid_year_plenty())
        if self.state.can_play_road_builder():
            actions.append(('play_road_builder', []))
        if self.state.can_trade():
            actions.extend(self.get_valid_trades())

        actions.extend(self.get_valid_build_actions())

        if self.state.can_pass_turn() and not actions:
            actions.append(('pass_turn', []))
        #print(actions)
        return actions

    def get_discard_options(self):
        actions = []
        n = self.current_player.n_resource_cards // 2
        discards = set(combinations(self.current_player.resource_cards_list, n))
        for discard in discards:
            unique = set(discard)
            actions.append(('discard', [[(card, discard.count(card)) for card in unique]]))
        return actions

    def get_valid_robber(self):
        return [('move_robber', [coord]) for coord in self.board.legal_robber_placements() if self.board.is_player_on_tile(coord, self.current_player.id)]

    def get_valid_steals(self):
        return [('steal', [p.id]) for p in self.players_to_steal_from]

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
        if self.state.can_build_road() or self.state == GameStates.STARTING_ROAD:
            for coord in self.legal_road_placements():
                actions.append(('build_road', [coord]))
        if self.state.can_build_settlement() or self.state == GameStates.STARTING_SETTLEMENT:
            for coord in self.legal_settlement_placements():
                actions.append(('build_settlement', [coord]))
        if self.state.can_build_city():
            for coord in self.legal_city_placements():
                actions.append(('build_city', [coord]))
        return actions

    def get_valid_trades(self):
        trades = []
        for g_card in ResourceCards:
            e = 4
            if self._board.is_player_on_port(self.current_player.id, PortTypes(g_card.value)):
                e = 2
            elif self._board.is_player_on_port(self.current_player.id, PortTypes.ANY):
                e = 3
            n = self.current_player.count_resource_cards(g_card)
            if n >= e:
                for w_card in [c for c in ResourceCards if c != g_card]:
                    trades.append(('offer_trade', [[(g_card, e)], [(w_card, 1)], []]))
        return trades

    def step(self):
        actions = self.get_valid_actions()
        if self.current_player.agent:
            function, args = '', []
            if type(self.current_player.agent) == RandomAgent:
                function, args = self.current_player.agent.choose_action(actions)
            if type(self.current_player.agent) == GreedyAgent:
                function, args = self.current_player.agent.choose_action(actions, self)
            getattr(self, function)(*args)
        