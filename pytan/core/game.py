from pytan.core.board import Board, TILE_TYPES
from pytan.core.player import Player
from pytan.core.cards import *
from pytan.core.state import GameStates, CatanGameState
import random
from datetime import datetime
import copy
import os

TILE_TYPES_TO_RESOURCE = {  
    TILE_TYPES.WHEAT: RESOURCE_CARDS.WHEAT,
    TILE_TYPES.WOOD: RESOURCE_CARDS.WOOD,
    TILE_TYPES.SHEEP: RESOURCE_CARDS.SHEEP,
    TILE_TYPES.ORE: RESOURCE_CARDS.ORE,
    TILE_TYPES.BRICK: RESOURCE_CARDS.BRICK
}

class Game(object):
    def __init__(self, players = [], board = Board()):
        # Init
        if players:
            self._players = players
        else:
            self._players = [
                Player('Player 1', 0, 'red'),
                Player('Player 2', 1, 'blue'),
                Player('Player 3', 2, 'white'),
                Player('Player 4', 3, 'orange')
            ]
    
        self._board = board

        self.reset()
        
    def reset(self):
        # Reset the game state
        self._players = [p.clone_player() for p in self._players]

        self._game_state = CatanGameState(self)

        self._resource_card_counts = copy.copy(RESOURCE_CARD_COUNTS)
        self._dev_card_counts = copy.copy(DEV_CARD_COUNTS)

        self._current_player_idx = random.randint(0,len(self._players)-1)
        self._current_player = self._players[self._current_player_idx]
        
        self._current_roll = 0
        self._last_roll = 0

        self._longest_road = None
        self._largest_army = None

        self._moves_made = 0
        self._turns = 0

        self._game_start = datetime.now()
        self._logs = []
        self.log('=== CATAN ===\n')
        self.log(f'Game Started: {self._game_start}')
        player_string = '\n'.join([f'{p.identifier} {str(p)}' for p in self._players])
        self.log(player_string)
        self.log(f'{self._current_player} starts')

        self._board.reset()

    def save_to_log_file(self):
        players_string = '-'.join([str(p) for p in self._players])
        log_filename = f'./game_logs/{self._game_start}-{players_string}.log'
        log_filename = log_filename.replace(' ', '-')
        if not os.path.exists('./game_logs'):
            os.makedirs('./game_logs')
        log_file = open(log_filename, 'w')

        for log in self._logs:
            log_file.write(log+'\n')
        
        log_file.close()
        log_file = None

    def log(self, text, end='\n'):
        print(text, end=end)
        self._logs.append(text)

    @property
    def players(self):
        return self._players
    
    @property
    def board(self):
        return self._board

    @property
    def state(self):
        return self._game_state
    
    @property
    def resource_card_counts(self):
        return self._resource_card_counts

    @property
    def dev_card_counts(self):
        return self._dev_card_counts

    @property
    def current_player(self):
        return self._current_player

    @property
    def current_rol(self):
        return self._current_roll
    
    @property
    def last_roll(self):
        return self._last_roll

    @property
    def longest_road(self):
        return self._longest_road

    @property
    def largest_army(self):
        return self._largest_army

    @property
    def moves_made(self):
        return self._moves_made

    @property
    def turns(self):
        return self._turns

    @state.setter
    def state(self, s):
        self._game_state = s
    
    def start_game(self):
        self.reset()
        self._game_state = GameStates.STARTING_SETTLEMENT

    def end_game(self, log=True):
        self.log('Ending Game')
        if log:
            self.save_to_log_file()

    def get_player_by_id(self, player_id):
        for player in self._players:
            if player.identifier == player_id:
                return player

    def roll(self, dice_roll=0):
        if dice_roll == 0:
            # Roll a random dice roll
            dice_1 = random.choice([1,2,3,4,5,6])
            dice_2 = random.choice([1,2,3,4,5,6])
            dice_roll = dice_1 + dice_2
        # Roll a determined dice roll
        self._last_roll = self._current_roll
        self._current_roll = dice_roll
        self.log(f'{self._current_player} rolled a {dice_roll}')
        tiles = self._board.tiles_with_prob(dice_roll)
        for tile_coord, tile in tiles.items():
            settlements = self._board.settlements_on_tile(tile_coord)
            card = TILE_TYPES_TO_RESOURCE[tile.tile_type]
            for settlement_coord, settlement in settlements.items():
                player = self.get_player_by_id(settlement.owner_id)
                self.log(f'{player} picked up a {card.value}')
                player.collect_resource_card(card)

    def pass_turn(self):
        self._current_player_idx += 1
        if self._current_player_idx >= len(self._players):
            self._current_player_idx = 0
        self.current_player = self._players[self._current_player_idx]
        self.log(f'It is now {self._current_player}\'s turn')
        self._turns += 1

    def legal_road_placements(self):
        if self._game_state == GameStates.STARTING_ROAD:
            return self._board.legal_starting_road_placements(self._current_player.identifier)
        else:
            return self._board.legal_road_placements(self._current_player.identifier)

    def build_road(self, coord: int):
        road = self._board.build_road(coord, self._current_player)
        if road is not None:
            self.log(f'{self._current_player} built road at {hex(coord)}')
            self._moves_made += 1
            self._current_player.add_road()
            return True
        else:
            self.log(f'{self._current_player} faild to build road at {hex(coord)}')
        return False
    
    def build_legal_road(self, coord: int):
        if self._current_player.roads_left > 0:
            if self._current_player.can_buy_road():
                if coord in self._board.legal_road_placements(self._current_player.identifier):
                    self.build_road(coord)
                else:
                    self.log(f'{self._current_player} cannot build road at {hex(coord)}')
            else:
                self.log(f'{self._current_player} cannot afford road')
        else:
            self.log(f'{self._current_player} has no roads left')

    def build_starting_road(self, coord: int):
        n_settlements = self._current_player.settlements
        if coord in self._board.legal_starting_road_placements(self._current_player.identifier):
            valid = False
            if n_settlements == 1 and self._current_player.first_settlement in self._board.edge_neighboring_nodes(coord):
                valid = True
            if n_settlements == 2 and self._current_player.second_settlement in self._board.edge_neighboring_nodes(coord):
                value = True
            if valid:
                self.build_road(coord)
            else:
                self.log(f'{self._current_player} failed to build road at {hex(coord)}')
        else:
            self.log(f'{self._current_player} cannot build road at {hex(coord)}')

    def legal_settlement_placements(self):
        if self._game_state == GameStates.STARTING_SETTLEMENT:
            return self._board.legal_starting_settlement_placements(self._current_player.identifier)
        else:
            return self._board.legal_settlement_placements(self._current_player.identifier)

    def build_settlement(self, coord: int):
        self.log(f'{self._current_player} built settlement at {hex(coord)}')
        settlement = self._board.build_settlement(coord, self._current_player)
        if settlement is not None:
            self._moves_made += 1
            self._current_player.add_settlement()
            return True
        else:
            self.log(f'{self._current_player} failed to build settlement at {hex(coord)}')
        return False

    def build_legal_settlement(self, coord: int):
        if self._current_player.settlements_left > 0:
            if self._current_player.can_buy_settlement():
                if coord in self._board.legal_settlement_placements(self._current_player.identifier):
                    self.build_settlement(coord)
                else:
                    self.log(f'{self._current_player} cannot build settlement at {hex(coord)}')
            else:
                self.log(f'{self._current_player} cannot afford settlement')
        else:
            self.log(f'{self._current_player} has no settlements left')

    def build_starting_settlement(self, coord: int):
        if coord in self._board.legal_starting_settlement_placements(self._current_player.identifier):
            success = self.build_settlement(coord)
            if success:
                if self._current_player.first_settlement == 0:
                    self._current_player.first_settlement = coord 
                else:
                    self._current_player.second_settlement == coord
        else:
            self.log(f'{self._current_player} cannot build settlement at {hex(coord)}')

    def legal_city_placements(self):
        return self._board.legal_city_placements(self._current_player.identifier)

    def build_city(self, coord: int):
        self.log(f'{self._current_player} upgraded to city at {hex(coord)}')
        city = self._board.upgrade_to_city(coord, self._current_player)
        if city is not None:
            self._moves_made += 1
            self._current_player.add_city()
            return True
        else:
            self.log(f'{self._current_player} failed to upgrade city at {hex(coord)}')
        return False

    def upgrade_to_city(self, coord: int):
        if self._current_player.cities_left > 0:
            if self._current_player.can_buy_city():
                existing_settlements = self._board.settlement_nodes(self._current_player.identifier)
                if coord in [n.hex_code for n in existing_settlements]:
                    self.build_city(coord)
                else:
                    self.log(f'{self._current_player} cannot upgrade city at {hex(coord)}')
            else:
                self.log(f'{self._current_player} cannot afford city')
        else:
            self.log(f'{self._current_player} has no cities left')

    def buy_dev_card(self):
        if self._current_player.can_buy_dev_card():
            self._current_player.buy_dev_card()
            self.log(f'{self._current_player.buy_dev_card} bought a dev card')
        else:
            self.log(f'{self._current_player.buy_dev_card} could not afford a dev card')
                
if __name__ == '__main__':
    game = Game()
    print(game.players)
    game.start_game(log=False)
    game.build_first_settlement(0x67)