import board
import player as pl
import random
from datetime import datetime
import copy
import os
from cards import *

class Game(object):
    def __init__(self, players = [], board = board.Board()):
        # Init
        if players:
            self._players = players
        else:
            self._players = [
                pl.Player('Player 1', 0, 'red'),
                pl.Player('Player 2', 1, 'blue'),
                pl.Player('Player 3', 2, 'green'),
                pl.Player('Player 4', 3, 'orange')
            ]
    
        self._board = board

        self.reset()
        
    def reset(self):
        # Reset the game state
        self._players = [pl.Player.clone_player(p) for p in self._players]

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

        self._board.reset()

    def init_log_file(self):
        timestamp = datetime.now()
        players_string = '-'.join([str(p) for p in self._players])
        log_file = f'./game_logs/{timestamp}-{players_string}.log'
        log_file = log_file.replace(' ', '-')
        if not os.path.exists('./game_logs'):
            os.makedirs('./game_logs')
        self._log_file = open(log_file, 'w')

        self.log('=== CATAN ===\n')
        self.log(f'Game Started: {timestamp}')
        player_string = '\n'.join([f'{p.identifier} {str(p)}' for p in self._players])
        self.log(player_string)
        self.log(f'{self._current_player} starts')


    def log(self, text, end='\n'):
        print(text, end=end)
        if self._log_file:
            self._log_file.write(text+end)

    @property
    def players(self):
        return self._players
    
    @property
    def board(self):
        return self._board
    
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
    
    def start_game(self):
        self.reset()
        self.init_log_file()

    def end_game(self):
        self.log('Ending Game')
        self._log_file.close()
        self._log_file = None

    def get_player_by_id(self, player_id):
        for player in self._players:
            if player.identifier == player_id:
                return player

    def roll(self):
        # Roll a random dice roll
        dice_1 = random.choice([1,2,3,4,5,6])
        dice_2 = random.choice([1,2,3,4,5,6])
        dice_roll = dice_1 + dice_2
        self.roll(dice_roll)

    def roll(self, dice_roll):
        # Roll a determined dice roll
        self._last_roll = self._current_roll
        self._current_roll = dice_roll
        self.log(f'{self._current_player} rolled a {dice_roll}')
        tiles = self._board.find_tiles_with_prob(dice_roll)
        for tile in tiles:
            settlements = self._board.find_settlements_on_tile(tile)
            for settlement in settlements:
                player = self.get_player_by_id(settlement.player_id)
                tile_id = tile.data.identifier
                self.log(f'{player} picked up a {RESOURCE_CARDS[tile_id]}')
                player.collect_resource_card(tile_id)

    def pass_turn(self):
        self._current_player_idx += 1
        if self._current_player_idx >= len(self._players):
            self._current_player_idx = 0
        self.current_player = self._players[self._current_player_idx]
        self.log(f'It is now {self._current_player}\'s turn')
        self._turns += 1
    
    def build_legal_road(self, coord):
        legal_road_placements = self._board.find_legal_road_placements(self._current_player.identifier)
        if coord in [e.hex_code for e in legal_road_placements]:
            self.log(f'{self._current_player} built road at {hex(coord)}')
            self._board.build_road(coord, self._current_player)
            self._moves_made += 1
        else:
            self.log(f'{self._current_player} cannot build road at {hex(coord)}')
    
    def build_road(self, coord):
        if self._current_player.roads_left > 0:
            if self._current_player.can_buy_road():
                self.build_legal_road(coord)
            else:
                self.log(f'{self._current_player} cannot afford road')
        else:
            self.log(f'{self._current_player} has no roads left')
    
    def build_legal_settlement(self, coord):
        legal_settlement_placements = self._board.find_legal_settlement_placements(self._current_player.identifier)
        if coord in [n.hex_code for n in legal_settlement_placements]:
            self.log(f'{self._current_player} built settlement at {hex(coord)}')
            settlement = self._board.build_settlement(coord, self._current_player)
            self._moves_made += 1
        else:
            self.log(f'{self._current_player} cannot build settlement at {hex(coord)}')
    
    def build_settlement(self, coord):
        if self._current_player.settlements_left > 0:
            if self._current_player.can_buy_settlement():
                self.build_legal_settlement(coord)
            else:
                self.log(f'{self._current_player} cannot afford settlement')
        else:
            self.log(f'{self._current_player} has no settlements left')

        
    def build_first_settlement(self, coord):
        empty_nodes = self._board.find_empty_nodes()
        if coord in [n.hex_code for n in empty_nodes]:
            self.log(f'{self._current_player} built their first settlement at {hex(coord)}')
            settlement = self._board.build_settlement(coord, self._current_player)
            self._moves_made += 1
        else:
            self.log(f'{self._current_player} could not build first settlement at {hex(coord)}')

    def upgrade_to_city(self, coord):
        if self._current_player.cities_left > 0:
            if self._current_player.can_buy_city():
                existing_settlements = self._board.find_settlement_nodes(self._current_player.identifier)
                if coord in [n.hex_code for n in existing_settlements]:
                    self.log(f'{self._current_player} upgraded to city at {hex(coord)}')
                    city = self._board.upgrade_to_city(coord, self._current_player)
                    self._moves_made += 1
                else:
                    self.log(f'{self._current_player} cannot upgrade city at {hex(coord)}')
            else:
                self.log(f'{self._current_player} cannot afford city')
        else:
            self.log(f'{self._current_player} has no cities left')
                
if __name__ == '__main__':
    game = Game()
    print(game.players)
    game.start_game()