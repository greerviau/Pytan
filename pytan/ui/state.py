from enum import Enum
from pytan.core.state import GameStates

class UIStates(Enum):
    SETUP = 'SETUP'
    INGAME = 'INGAME'
    BUILDING_ROAD = 'BUILDING_ROAD'
    BUILDING_SETTLEMENT = 'BUILDING_SETTLEMENT'
    BUILDING_CITY = 'BUILDING_CITY'
    CREATING_TRADE = 'CREATING_TRADE'
    MONOPOLY = 'MONOPOLY'
    YEAR_PLENTY = 'YEAR_PLENTY'

class CatanUIState(object):
    def __init__(self, game):
        self.game = game

        self._state = UIStates.SETUP

    @property
    def state(self):
        return self._state

    def __eq__(self, other):
        return self._state == other

    def set_state(self, s: UIStates):
        self._state = s

    def is_in_setup(self) -> bool:
        return self._state == UIStates.SETUP
    
    def is_ingame(self) -> bool:
        return self._state == UIStates.INGAME

    def is_building_road(self) -> bool:
        return self._state == UIStates.BUILDING_ROAD or \
                self.game.state in [GameStates.STARTING_ROAD, GameStates.ROADBUILDER]

    def is_building_settlement(self) -> bool:
        return self._state == UIStates.BUILDING_SETTLEMENT \
                or self.game.state == GameStates.STARTING_SETTLEMENT
    
    def is_building_city(self) -> bool:
        return self._state == UIStates.BUILDING_CITY

    def is_creating_trading(self) -> bool:
        return self._state == UIStates.CREATING_TRADE

    def is_moving_robber(self) -> bool:
        return self.game.state == GameStates.MOVING_ROBBER

    def is_playing_monopoly(self) -> bool:
        return self._state == UIStates.MONOPOLY

    def is_playing_year_plenty(self) -> bool:
        return self._state == UIStates.YEAR_PLENTY

    def can_roll(self) -> bool:
        return self._state == UIStates.INGAME and self.game.state.can_roll()

    def can_pass_turn(self) -> bool:
        return self._state == UIStates.INGAME and self.game.state.can_pass_turn()

    def can_cancel(self) -> bool:
        return (self.is_building_road() and self.game.state != GameStates.STARTING_ROAD) \
                or (self.is_building_settlement() and self.game.state != GameStates.STARTING_SETTLEMENT) \
                or self.is_building_city() \
                or self._state in [UIStates.YEAR_PLENTY, UIStates.MONOPOLY]

    def can_build_road(self) -> bool:
        return not self.is_building_road() and self.game.state.can_build_road()

    def can_build_settlement(self) -> bool:
        return not self.is_building_settlement() and self.game.state.can_build_settlement()

    def can_build_city(self) -> bool:
        return not self.is_building_city() and self.game.state.can_build_city()

    def can_buy_dev_card(self) -> bool:
        return self._state == UIStates.INGAME and self.game.state.can_buy_dev_card()

    def can_play_knight(self) -> bool:
        return self._state == UIStates.INGAME and self.game.state.can_play_knight()
    
    def can_play_monopoly(self) -> bool:
        return self._state == UIStates.INGAME and self.game.state.can_play_monopoly()
    
    def can_play_road_builder(self) -> bool:
        return self._state == UIStates.INGAME and self.game.state.can_play_road_builder()
    
    def can_play_year_plenty(self) -> bool:
        return self._state == UIStates.INGAME and self.game.state.can_play_year_plenty()
    
    def can_trade(self) -> bool:
        return self._state == UIStates.INGAME and self.game.state.can_trade()