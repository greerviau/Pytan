from pytan.core.game import Game
from pytan.core.state import GameStates

def get_valid_build_actions(self, game: Game):
    actions = []
    if game.state.can_build_road() or game.state == GameStates.STARTING_ROAD:
        for coord in game.legal_road_placements():
            actions.append(f'build_road={hex(coord)}')
    if game.state.can_build_settlement() or game.state == GameStates.STARTING_SETTLEMENT:
        for coord in game.legal_settlement_placements():
            actions.append(f'build_settlement={hex(coord)}')
    if game.state.can_build_city():
        for coord in game.legal_city_placements():
            actions.append(f'build_city={hex(coord)}')
    return actions

def get_valid_trades(self, game: Game):
    pass
    player_resource_cards = game.current_turn_player.resource_cards
    for card, num in player_resource_cards.items():
        for n in range(num):


if __name__ == '__main__':
    from pytan.log.logging import Logger
    logger = Logger(console_log=False)
    game = Game(logger=logger)
    game.start_game()
    print(get_valid_actions(game))