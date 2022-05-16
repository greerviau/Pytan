from pytan.core.board import Board, CatanTile, TileTypes
from pytan.core.piece import PieceTypes
from pytan.core.player import Player
from pytan.core.cards import *
from pytan.core.state import GameStates, CatanGameState
import random
from datetime import datetime
import copy
import os

TILE_TYPES_TO_RESOURCE = {  
    TileTypes.WHEAT: ResourceCards.WHEAT,
    TileTypes.WOOD: ResourceCards.WOOD,
    TileTypes.SHEEP: ResourceCards.SHEEP,
    TileTypes.ORE: ResourceCards.ORE,
    TileTypes.BRICK: ResourceCards.BRICK,
    TileTypes.DESERT: None
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

        self._observers = set()
    
        self.reset()
        
    def reset(self):
        # Reset the game state
        self._observers = self._observers.copy()
        self._players = [p.clone_player() for p in self._players]

        self._game_state = CatanGameState(self)
        self._game_state.set_state(GameStates.UNDEFINED)

        self._resource_card_counts = copy.copy(RESOURCE_CARD_COUNTS)
        self._dev_cards = []
        for card in DEV_CARD_COUNTS:
            for _ in range(DEV_CARD_COUNTS[card]):
                self._dev_cards.append(card)
        random.shuffle(self._dev_cards)

        self._current_player_idx = random.randint(0,len(self._players)-1)
        self._current_player = self._players[self._current_player_idx]
        
        self._current_roll = 0
        self._last_roll = 0
        self._has_rolled = False

        self._longest_road = None
        self._largest_army = None

        self._moves_made = 0
        self._turns = 0

        self._game_start = datetime.now()
        self._logs = []

        self._board.reset()

    def save_to_log_file(self):
        players_string = '-'.join([str(p) for p in self._players])
        log_filename = f'./game_logs/{self._game_start}-{players_string}.log'
        log_filename = log_filename.replace(' ', '-')
        if not os.path.exists('./game_logs'):
            os.makedirs('./game_logs')
        log_file = open(log_filename, 'w')

        log_file.write(self.log_dump())
        
        log_file.close()
        log_file = None

    def log(self, text, end='\n'):
        print(text, end=end)
        self._logs.append(text)
    
    def log_dump(self):
        return '\n'.join(self._logs)

    def add_observer(self, observable):
        self._observers.add(observable)

    def notify(self):
        for obs in self._observers:
            obs.notify(self)

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
    def current_state(self):
        return self._game_state.state
    
    @property
    def resource_card_counts(self):
        return self._resource_card_counts

    @property
    def dev_cards(self):
        return self._dev_cards

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
    def has_rolled(self):
        return self._has_rolled

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
    def state(self, s: GameStates):
        self._game_state.set_state(s)
    
    def start_game(self):
        self.reset()

        self.log('=== CATAN ===\n')
        self.log(f'Game Started: {self._game_start}')
        player_string = '\n'.join([f'{p.identifier} {str(p)}' for p in self._players])
        self.log(player_string)
        self.log(f'{self._current_player} starts')

        self.state = GameStates.STARTING_SETTLEMENT
        self.notify()

    def end_game(self, log=False):
        self.log('Ending Game')
        if log:
            self.save_to_log_file()
        self.notify()

    def get_player_by_id(self, player_id):
        for player in self._players:
            if player.identifier == player_id:
                return player

    def _remove_resources(self, resource_list: list[tuple[ResourceCards, int]]):
        for card, n in resource_list:
            self._resource_card_counts[card] -= n

    def _add_resources(self, resource_list: list[tuple[ResourceCards, int]]):
        for card, n in resource_list:
            self._resource_card_counts[card] += n

    def _collect_resources(self, tiles: dict[int, CatanTile], node_coord=0x00):
        pickups = {}
        for tile_coord, tile in tiles.items():
            if tile_coord != self._board.robber.coord:
                card = TILE_TYPES_TO_RESOURCE[tile.tile_type]
                if card is not None:
                    for s_coord, settlement in self._board.settlements_on_tile(tile_coord).items():
                        if node_coord == 0 or node_coord == s_coord:
                            p_id = settlement.owner_id
                            if p_id not in pickups.keys():
                                pickups[p_id] = {}
                            if card not in pickups[p_id].keys():
                                pickups[p_id][card] = 0
                            pickups[p_id][card] += 1
                    
                    for c_coord, city in self._board.cities_on_tile(tile_coord).items():
                        if node_coord == 0 or node_coord == s_coord:
                            p_id = city.owner_id
                            if p_id not in pickups.keys():
                                pickups[p_id] = {}
                            if card not in pickups[p_id].keys():
                                pickups[p_id][card] = 0
                            pickups[p_id][card] += 2

            for p_id, cards in pickups.items():
                pickup_list = []
                player = self.get_player_by_id(p_id)
                for card, count in cards.items():
                    self.log(f'{player} picked up {count} {card.value}')
                    pickup_list.append((card,count))
                player.collect_resource_cards(pickup_list)
                self._remove_resources(pickup_list)
`
    def roll(self, dice_roll=0):
        self._has_rolled = True
        if dice_roll == 0:
            # Roll a random dice roll
            dice_1 = random.choice([1,2,3,4,5,6])
            dice_2 = random.choice([1,2,3,4,5,6])
            dice_roll = dice_1 + dice_2
        # Roll a determined dice roll
        self._last_roll = self._current_roll
        self._current_roll = dice_roll
        self.log(f'{self._current_player} rolled a {dice_roll}')
        if dice_roll == 7:
            self._game_state.set_state(GameStates.MOVING_ROBBER)
        else:
            tiles = self._board.tiles_with_prob(dice_roll)
            self._collect_resources(tiles)
                
        self.notify()

    def pass_turn(self):
        self._has_rolled = False
        self._turns += 1
        d = 1
        if self._turns == 4 or self._turns == 8:
            d = 0
        elif self._turns >= 5 and self._turns < 8:
            d = -1
        if self._turns >= 8:
            self._game_state.set_state(GameStates.INGAME)
        self._current_player_idx += d
        if self._current_player_idx >= len(self._players):
            self._current_player_idx = 0
        elif self._current_player_idx < 0:
            self._current_player_idx = len(self._players)-1
        self._current_player = self._players[self._current_player_idx]
        self.log(f'It is now {self._current_player}\'s turn')
        self.notify()

    def start_building(self, piece_type: PieceTypes):
        if piece_type == PieceTypes.ROAD:
            self._game_state.set_state(GameStates.BUILDING_ROAD)
        elif piece_type == PieceTypes.SETTLEMENT:
            self._game_state.set_state(GameStates.BUILDING_SETTLEMENT)
        elif piece_type == PieceTypes.CITY:
            self._game_state.set_state(GameStates.BUILDING_CITY)
        self.notify()

    def legal_road_placements(self):
        if self._game_state == GameStates.STARTING_ROAD:
            return self._board.node_neighboring_edges(self._current_player.last_settlement_built)
        else:
            return self._board.legal_road_placements(self._current_player.identifier)
    
    def _build_road(self, coord: int):
        if coord in self.legal_road_placements():
            road = self._board.build_road(coord, self._current_player)
            if road is not None:
                self.log(f'{self._current_player} built road at {hex(coord)}')
                self._moves_made += 1
                self._current_player.add_road(coord)
            else:
                self.log(f'{self._current_player} failed to build road at {hex(coord)}')
        else:
            self.log(f'{self._current_player} cannot build road at {hex(coord)}')

    def build_road(self, coord: int):
        if self._game_state == GameStates.STARTING_ROAD:
            self._build_road(coord)
            self._game_state.set_state(GameStates.STARTING_SETTLEMENT)
            self.pass_turn()
        elif self._game_state != GameStates.UNDEFINED:
            if self._game_state.state in [GameStates.INGAME, GameStates.BUILDING_ROAD]:
                if self._current_player.roads_left > 0:
                    if self._current_player.can_buy_road():
                        self._build_road(coord)
                        self._game_state.set_state(GameStates.INGAME)
                        self._current_player.remove_resource_cards(ROAD)
                        self._add_resources(ROAD)
                    else:
                        self.log(f'{self._current_player} cant afford road')
                else:
                    self.log(f'{self._current_player} has no roads left')
            else:
                self.log(f'Cant build road, current state {self._game_state}')
        else:
            self.log('Game has not started')
        self.notify()

    def legal_settlement_placements(self):
        if self._game_state == GameStates.STARTING_SETTLEMENT:
            return self._board.legal_starting_settlement_placements(self._current_player.identifier)
        else:
            return self._board.legal_settlement_placements(self._current_player.identifier)

    def _build_settlement(self, coord: int):
        if coord in self.legal_settlement_placements():
            settlement = self._board.build_settlement(coord, self._current_player)
            if settlement is not None:
                self.log(f'{self._current_player} built settlement at {hex(coord)}')
                self._moves_made += 1
                self._current_player.add_settlement(coord)
            else:
                self.log(f'{self._current_player} failed to build settlement at {hex(coord)}')
        else:
            self.log(f'{self._current_player} cannot build settlement at {hex(coord)}')

    def build_settlement(self, coord: int):
        if self._game_state == GameStates.STARTING_SETTLEMENT:
            self._build_settlement(coord)
            if self._current_player.settlements == 2:
                tiles = self._board.node_neighboring_tiles(self._current_player.last_settlement_built)
                self._collect_resources(tiles, coord)
                self._remove_resources(SETTLEMENT)
            self._game_state.set_state(GameStates.STARTING_ROAD)
        elif self._game_state != GameStates.UNDEFINED:
            if self._game_state.state in [GameStates.INGAME, GameStates.BUILDING_SETTLEMENT]:
                if self._current_player.settlements_left > 0:
                    if self._current_player.can_buy_settlement():
                        self._build_settlement(coord)
                        self._game_state.set_state(GameStates.INGAME)
                        self._current_player.remove_resource_cards(SETTLEMENT)
                        self._add_resources(SETTLEMENT)
                    else:
                        self.log(f'{self._current_player} cannot afford settlement')
                else:
                    self.log(f'{self._current_player} has no settlements left')
            else:
                self.log(f'Cant build settlement, current state {self._game_state}')
        else:
            self.log('Game has not started')
        self.notify()

    def legal_city_placements(self):
        return self._board.legal_city_placements(self._current_player.identifier)

    def _build_city(self, coord: int):
        if coord in self.legal_city_placements():
            city = self._board.build_city(coord, self._current_player)
            if city is not None:
                self.log(f'{self._current_player} upgraded to city at {hex(coord)}')
                self._moves_made += 1
                self._current_player.add_city(coord)
            else:
                self.log(f'{self._current_player} failed to upgrade city at {hex(coord)}')
        else:
            self.log(f'{self._current_player} cannot upgrade city at {hex(coord)}')

    def build_city(self, coord: int):
        if self._game_state != GameStates.UNDEFINED:
            if self._game_state.state in [GameStates.INGAME, GameStates.BUILDING_CITY]:
                if self._current_player.cities_left > 0:
                    if self._current_player.can_buy_city():
                        self._build_city(coord)
                        self._game_state.set_state(GameStates.INGAME)
                        self._current_player.remove_resource_cards(CITY)
                        self._add_resources(CITY)
                    else:
                        self.log(f'{self._current_player} cannot afford city')
                else:
                    self.log(f'{self._current_player} has no cities left')
            else:
                self.log(f'Cant build city, current state {self._game_state}')
        else:
            self.log('Game has not started')
        self.notify()

    def buy_dev_card(self):
        if self._game_state != GameStates.UNDEFINED:
            if self._game.state.can_buy_dev_card():
                if self._current_player.can_buy_dev_card():
                    if len(self._dev_cards) > 0:
                        card = self._dev_cards.pop(0)
                        self._current_player.buy_dev_card(card)
                        self.log(f'{self._current_player.buy_dev_card} bought a {card.value} Dev Card')
                    else:
                        self.log('No Dev Cards left')
                else:
                    self.log(f'{self._current_player.buy_dev_card} could not afford a Dev Card')
            else:
                self.log(f'Cant buy dev card, current state {self._game_state}')
        else:
            self.log('Game has not started')
        self.notify()

    def move_robber(self, tile_coord: int):
        self._board.move_robber(tile_coord)
        self._game_state.set_state(GameStates.STEALING)
    

                
if __name__ == '__main__':
    game = Game()
    print(game.players)
    game.start_game(log=False)
    game.build_first_settlement(0x67)