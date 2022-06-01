import random

class BotAgent(object):
    def __init__(self):
        self._bot = True

class RandomAgent(object):
    def __init__(self):
        super().__init__()

    def choose_action(self, actions: list[tuple[str, None]], game: 'Game'):
        return random.choice(actions)

class GreedyAgent(object):
    def __init__(self):
        super().__init__()

    def choose_action(self, actions: list[tuple[str, None]], game: 'Game'):
        scores = []
        for function, args in actions:
            #print('test action')
            #print(len(game.legal_settlement_placements()))
            getattr(game, function)(*args)
            score = self.score_state(game)
            #print(score)
            scores.append(score)
            game.undo()
        m = max(scores)
        c = scores.count(max)
        action = actions[scores.index(m)]
        if c > 1:
            action = random.choice([a for a in actions if a == m])
        #print(action)
        return action

    def score_state(self, game: 'Game'):
        score = game.current_turn_player.total_victory_points
        score += game.current_turn_player.roads * 0.5
        score += game.current_turn_player.settlements
        score += game.current_turn_player.cities * 2
        score += len(game.current_turn_player.dev_cards) * 0.5
        score += game.current_turn_player.longest_road_chain
        score += game.current_turn_player.longest_road * 2
        score += game.current_turn_player.largest_army * 2
        score += game.current_turn_player.production_points
        score += game.current_turn_player.diversity * 2
        score += game.current_turn_player.can_buy_city() * 2
        score += game.current_turn_player.can_buy_settlement()
        score += game.current_turn_player.can_buy_road() * 0.5
        score += game.current_turn_player.can_buy_dev_card() * 0.5
        return score