from enum import Enum

class GameStates(Enum):
    UNDEFINED = 'UNDEFINED'
    STARTING_SETTLEMENT = 'STARTING_SETTLEMENT'
    STARTING_ROAD = 'STARTING_ROAD'
    INGAME = 'INGAME'
    BUILDING_ROAD = 'BUILDING_ROAD'
    BUILDING_SETTLEMENT = 'BUILDING_SETTLEMENT'
    BUILDING_CITY = 'BUILDING_CITY'
    TRADING = 'TRADING'
    MOVING_ROBBER = 'PLACING_ROBBER'

class CatanGameState(object):
    def __init__(self, game):
        self._state = GameStates.UNDEFINED
        self._game = game

    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, s: GameStates):
        self._state = s

    def __eq__(self, other):
        return self._state == other

    def can_build_road(self):
        return self._state == GameStates.INGAME \
                and not self.can_roll() \
                and self._game.current_player.can_buy_road() \
                and self._game.current_player.roads_left > 0 \
                and any(self._game.legal_road_placements())

    def can_build_settlement(self):
        return self._state == GameStates.INGAME \
                and not self.can_roll() \
                and self._game.current_player.can_buy_settlement() \
                and self._game.current_player.settlements_left > 0 \
                and any(self._game.legal_settlement_placements())

    def can_build_city(self):
        return self._state == GameStates.INGAME  \
                and not self.can_roll() \
                and self._game.current_player.can_buy_city() \
                and self._game.current_player.cities_left > 0 \
                and self._game.current_player.settlements > 0 \
                and any(self._game.legal_city_placements())
    
    def is_building_road(self):
        return self._state in [GameStates.STARTING_ROAD, GameStates.BUILDING_ROAD]

    def is_building_settlement(self):
        return self._state in [GameStates.STARTING_SETTLEMENT, GameStates.BUILDING_SETTLEMENT]
    
    def is_building_city(self):
        return self._state == GameStates.BUILDING_CITY

    def can_roll(self):
        return self._state == GameStates.INGAME and not self._game.has_rolled

    def can_pass_turn(self):
        return self._state == GameStates.INGAME and self._game.has_rolled

    def can_trade(self):
        return False

    def can_buy_dev_card(self):
        return False

    def is_moving_robber(self):
        return False
