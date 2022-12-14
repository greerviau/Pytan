import random
from pytan.core.state import GameStates
from pytan.core.player import Player
from pytan.core.game import Game

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

class RandomAgent(BotAgent):
    def __init__(self, player: Player):
        super().__init__(player)

    def choose_action(self, actions: list[tuple[str, None]], game_state: dict):
        if len(actions) == 0:
            raise RuntimeError('No actions')
        return random.choice(actions)

class GreedyAgent(BotAgent):
    def __init__(self, player: Player):
        super().__init__(player)

    def choose_action(self, actions: list[tuple[str, None]], game_state: dict):
        if len(actions) == 0:
            raise RuntimeError('No actions')

        self.game = Game.create_from_state(game_state)
        scores = []
        for function, args in actions:
            getattr(self.game, function)(*args)
            scores.append(self.score_state(function))
            self.game.undo()
        m = max(scores)
        c = scores.count(max)
        action = actions[scores.index(m)]
        if c > 1:
            action = random.choice([a for a in actions if a == m])
        return action

    def score_state(self, function: str):
        curr_player = self.game.current_player if self.game.state != GameStates.STARTING_SETTLEMENT else self.game.players[self.game.current_player_idx-1]
        score = curr_player.total_victory_points
        road_score = ((curr_player.longest_road_chain / 12) * (self.calculate_exploration_score(curr_player.id) * 0.01)) + curr_player.longest_road * 2
        score += road_score
        score += curr_player.settlements
        score += curr_player.cities * 2
        score += curr_player.pp_score
        score += curr_player.diversity_score
        score += len(curr_player.dev_cards) * 0.4
        score += curr_player.largest_army * 2
        score += curr_player.can_buy_city()
        score += curr_player.can_buy_settlement() * 0.5
        score += curr_player.can_buy_road() * 0.25
        score += curr_player.can_buy_dev_card() * 0.2

        # Robber placement
        robber = self.game.board.robber.coord
        tile = self.game.board.tiles[robber]
        prod = tile.prod_points
        n_settlements = len(self.game.board.settlements_on_tile(robber))
        n_cities = len(self.game.board.cities_on_tile(robber))
        players = set(self.game.board.players_on_tile(robber))
        vps = sum([self.game.get_player_by_id(p).victory_points for p in players])
        l = len(players) if len(players) > 0 else 1
        score += prod * (n_settlements + (n_cities*2)) * (vps/l)
        if self.game.board.is_player_on_tile(robber, curr_player.id):
            score -= 100

        return score

    def calculate_exploration_score(self, player_id: int) -> int:
        roads = list(self.game.board.friendly_roads(player_id).keys())
        score = [0.0]
        explored = set()
        while roads:
            depth = [1]
            self.explore_road(roads[0], explored, depth, score)
            roads = [r for r in roads if r not in explored]
        return score[0]

    def explore_road(self, road_coord: int, explored: set, depth: list[int], score: list[float], parent_neighbors=[]):
        explored.add(road_coord)
        if not [s for s in self.game.board.edge_neighboring_nodes(road_coord).values() if s]:
            neighbors = [coord for coord, road in self.game.board.edge_neighboring_edges(road_coord).items() if road == None]
            if depth[0] == 1:
                parent_neighbors = neighbors.copy()
            elif depth[0] == 2 and [n for n in parent_neighbors if n not in neighbors and road_coord != n]:
                depth[0] += 1
            else:
                parent_neighbors = []
            neighbors = [n for n in neighbors if n not in explored]
            prod_points = sum([t.prod_points for t in self.game.board.edge_neighboring_tiles(road_coord).values()])
            score[0] += (len(neighbors) / depth[0]) + (prod_points / depth[0])
            explored.update(neighbors)
            if neighbors:
                depth[0] += 1
                for neighbor in neighbors:
                    self.explore_road(neighbor, explored, depth, score, parent_neighbors=parent_neighbors)    
