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

    def choose_action(self, env: 'CatanEnv'):
        actions = env.legal_actions
        if len(actions) == 0:
            raise RuntimeError('No actions')
        return random.choice(actions)

class GreedyAgent(BotAgent):
    def __init__(self, player: Player):
        super().__init__(player)

    def choose_action(self, env: 'CatanEnv'):
        actions = env.legal_actions
        if len(actions) == 0:
            raise RuntimeError('No actions')

        #print(game.get_state())

        self.game = Game.create_from_state(env.game.get_state())

        scores = []
        for function, args in actions:
            getattr(self.game, function)(*args)
            scores.append(self.score_state())
            self.game.undo()
        m = max(scores)
        c = scores.count(m)
        if c > 1:
            i = random.choice([i for i, s in enumerate(scores) if s == m])
        else:
            i = scores.index(m)
        action = actions[i]
        return action

    def score_state(self):
        curr_player = self.game.current_player if self.game.state != GameStates.STARTING_SETTLEMENT else self.game.players[self.game.current_player_idx-1]
        score = curr_player.victory_points * 100
        score = curr_player.longest_road_chain / 15
        score += self.calculate_exploration_score(curr_player.id)
        score += curr_player.longest_road
        score += curr_player.settlements
        score += (curr_player.cities * 2) * (1 + self.game.turn // 50)
        score += curr_player.pp_score
        score += curr_player.diversity_score
        score += len(curr_player.dev_cards) * 0.2
        score += curr_player.largest_army
        score += (curr_player.can_buy_city() * 2) * (1 + self.game.turn // 30)
        score += curr_player.can_buy_settlement()
        score += curr_player.can_buy_road() * 0.25
        score += curr_player.can_buy_dev_card() * 0.2

        score += self.robber_score(curr_player.id)

        return score
    
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
            score += prod * (n_settlements + (n_cities*2)) * (vps/l)
        else:
            score -= 100

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
