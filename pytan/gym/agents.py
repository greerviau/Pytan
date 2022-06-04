import random

class BotAgent(object):
    def __init__(self):
        self._bot = True

class RandomAgent(object):
    def __init__(self):
        super().__init__()

    def choose_action(self, actions: list[tuple[str, None]]):
        return random.choice(actions)

class GreedyAgent(object):
    def __init__(self):
        super().__init__()

    def choose_action(self, actions: list[tuple[str, None]], game: 'Game'):
        scores = []
        for function, args in actions:
            getattr(game, function)(*args)
            scores.append(self.score_state(game))
            game.undo()
        m = max(scores)
        c = scores.count(max)
        action = actions[scores.index(m)]
        if c > 1:
            action = random.choice([a for a in actions if a == m])
        return action

    def score_state(self, game: 'Game'):
        score = game.current_player.total_victory_points
        score += game.current_player.roads * 0.5
        score += game.current_player.settlements
        score += game.current_player.cities * 2
        score += len(game.current_player.dev_cards) * 0.5
        score += game.current_player.longest_road_chain
        score += game.current_player.longest_road * 2
        score += game.current_player.largest_army * 2
        score += game.current_player.pp_score
        score += game.current_player.diversity_score
        score += game.current_player.can_buy_city() * 2
        score += game.current_player.can_buy_settlement()
        score += game.current_player.can_buy_road() * 0.5
        score += game.current_player.can_buy_dev_card() * 0.5

        # Robber placement
        other_players = game.other_players
        robber = game.board.robber.coord
        tile = game.board.tiles[robber]
        prod = tile.prod_points
        n_settlements = len(game.board.settlements_on_tile(robber))
        n_cities = len(game.board.cities_on_tile(robber))
        players = set(game.board.players_on_tile(robber))
        vps = sum([game.get_player_by_id(p).victory_points for p in players])
        l = len(players) if len(players) > 0 else 1
        score += prod * (n_settlements + (n_cities*2)) * (vps/l)
        return score