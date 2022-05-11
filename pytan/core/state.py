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
        if self._state == GameStates.STARTING_ROAD:
            return True
        elif self._state == GameStates.INGAME:
            if self.game.current_player.can_buy_road():
                return True
        return False

    def can_build_settlement(self):
        if self._state == GameStates.STARTING_SETTLEMENT:
            return True
        elif self._state == GameStates.INGAME:
            if self.game.current_player.can_buy_settlement():
                return True
        return False

    def can_build_city(self):
        if self._state == GameStates.INGAME:
            if self.game.current_player.can_buy_city():
                return True
        return False

    def can_roll(self):
        return True

    def can_pass_turn(self):
        return False

    def can_trade(self):
        return False

    def can_buy_dev_card(self):
        return False

    def can_move_robber(self):
        return False
