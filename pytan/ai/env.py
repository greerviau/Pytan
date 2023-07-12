import random
from itertools import combinations
import gym

from pytan.core.game import Game
from pytan.core.cards import ResourceCards
from pytan.core.state import GameStates
from pytan.core.ports import PortTypes
from pytan.log.logging import Logger
from pytan.ai.agents import Agent

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
        self.game.start_game(randomize=True)
        return self.get_state_vector(self.game)

    def step(self, action):
        if self.is_legal(action):
            function, args = action
            getattr(self.game, function)(*args)
        done = self.game.state == GameStates.GAME_OVER
        current_player = self.game.current_player
        if not self.game.has_rolled:
            current_player = self.game.players[self.game.current_player_idx-1]
        reward = current_player.total_victory_points
        return self.get_state_vector(self.game), reward, done, None
    
    def unstep(self):
        success = self.game.undo()
        if not success:
            raise RuntimeError("Failed to undo")
    
    def get_state_vector(self, game: Game = None):
        if not game:
            game = self.game
        curr_player = game.current_player
        state_vector = []
        state_vector.append(curr_player.total_victory_points)
        state_vector.append(curr_player.victory_points)
        state_vector.append(game.turn)
        state_vector.append(self.calculate_exploration_score(curr_player.id))
        state_vector.append(curr_player.longest_road)
        state_vector.append(curr_player.roads)
        state_vector.append(curr_player.settlements)
        state_vector.append(curr_player.cities)
        state_vector.append(curr_player.production_points)
        state_vector.append(curr_player.diversity_score)
        state_vector.append(len(curr_player.dev_cards))
        state_vector.append(curr_player.largest_army)
        state_vector.append(curr_player.can_buy_city())
        state_vector.append(curr_player.can_buy_settlement())
        state_vector.append(curr_player.can_buy_road())
        state_vector.append(curr_player.can_buy_dev_card())
        state_vector.append(self.robber_score(curr_player.id))
        return state_vector
    
    def robber_score(self, player_id):
        # Robber placement
        robber = self.game.board.robber.coord
        tile = self.game.board.tiles[robber]
        prod = tile.prod_points
        n_settlements = len(self.game.board.settlements_on_tile(robber))
        n_cities = len(self.game.board.cities_on_tile(robber))
        players = set(self.game.board.players_on_tile(robber))
        vps = sum([self.game.get_player_by_id(p).victory_points for p in players])
        l = len(players) if len(players) > 0 else 1
        score = 0
        if not self.game.board.is_player_on_tile(robber, player_id):
            score = prod * (n_settlements + (n_cities*2)) * (vps/l)
        else:
            score = -100

        return score

    def calculate_exploration_score(self, player_id: int) -> int:
        try:
            starting_road = list(self.game.board.friendly_roads(player_id).keys())[0]
        except IndexError:
            return 0
        explored = set()
        explored.add(starting_road)
        score = self.explore_road(starting_road, explored) / 250
        return score

    def explore_road(self, road_coord: int, explored: set):
        neighbors = [coord for coord, road in self.game.board.edge_neighboring_edges(road_coord).items() if road == None]
        unexplored_neighbors = list(set(neighbors) - explored)
        for neighbor in unexplored_neighbors:
            explored.add(neighbor)
        score = sum([t.prod_points for t in self.game.board.edge_neighboring_tiles(road_coord).values()])
        for neighbor in unexplored_neighbors:
                score += self.explore_road(neighbor, explored)
        return score 
        