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
    DISCARDING = 'DISCARDING'
    MOVING_ROBBER = 'MOVING_ROBBER'
    STEALING = 'STEALING'

class CatanGameState(object):
    def __init__(self, game):
        self._state = GameStates.UNDEFINED
        self._game = game

    @property
    def state(self):
        return self._state

    def __eq__(self, other):
        return self._state == other

    def set_state(self, s: GameStates):
        self._state = s

    def log(self, text, end='\n'):
        self._game.log(text, end=end)

    def can_build_road(self, log=False):
        if self._state != GameStates.UNDEFINED:
            if self._state in [GameStates.INGAME, GameStates.BUILDING_ROAD]:
                if not self.can_roll():
                    if self._game.current_player.can_buy_road():
                        if self._game.current_player.roads_left > 0:
                            if any(self._game.legal_road_placements()):
                                return True
                            elif log:
                                self.log('No legal road placements')
                        elif log:
                            self.log(f'{self._game.current_player} has no roads left')
                    elif log:
                        self.log(f'{self._game.current_player} cant afford road')
                elif log:
                    self.log('Roll first')
            elif log:
                self.log(f'Cant build road, current state {self._state}')
        elif log:
            self.log('Game has not started')
        return False

    def can_build_settlement(self, log=False):
        if self._state != GameStates.UNDEFINED:
            if self._state in [GameStates.INGAME, GameStates.BUILDING_SETTLEMENT]:
                if not self.can_roll():
                    if self._game.current_player.can_buy_settlement():
                        if self._game.current_player.settlements_left > 0:
                            if any(self._game.legal_settlement_placements()):
                                return True
                            elif log:
                                self.log('No legal settlement placements')
                        elif log:
                            self.log(f'{self._game.current_player} has no settlements left')
                    elif log:
                        self.log(f'{self._game.current_player} cannot afford settlement')
                elif log:
                    self.log('Roll first')
            elif log:
                self.log(f'Cant build settlement, current state {self._state}')
        elif log:
            self.log('Game has not started')
        return False

    def can_build_city(self, log=False):
        if self._state != GameStates.UNDEFINED:
            if self._state in [GameStates.INGAME, GameStates.BUILDING_CITY]:
                if not self.can_roll():
                    if self._game.current_player.can_buy_city():
                        if self._game.current_player.cities_left > 0:
                            if self._game.current_player.settlements > 0:
                                if any(self._game.legal_city_placements()):
                                    return True
                                elif log:
                                    self.log('No legal city placements')
                            elif log:
                                self.log(f'{self._game.current_player} has no settlements to upgrade')
                        elif log:
                            self.log(f'{self._game.current_player} has no cities left')
                    elif log:
                        self.log(f'{self._game.current_player} cannot afford city')
                elif log:
                    self.log('Roll first')
            elif log:
                self.log(f'Cant build city, current state {self._state}')
        elif log:
            self.log('Game has not started')
        return False
    
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

    def can_buy_dev_card(self, log=False):
        if self._state != GameStates.UNDEFINED:
            if self._state == GameStates.INGAME:
                if self._game.current_player.can_buy_dev_card():
                    if not self.can_roll():
                        if self._game.n_dev_cards > 0:
                            return True
                        elif log:
                            self.log('No Dev Cards left')
                    elif log:
                        self.log('Roll first')
                elif log:
                    self.log(f'{self._game.current_player} could not afford a Dev Card')
            elif log:
                self.log(f'Cant buy dev card, current state {self._state}')
        elif log:
            self.log('Game has not started')
        return False

    def is_moving_robber(self):
        return self._state == GameStates.MOVING_ROBBER

    def __repr__(self):
        return self._state.value
