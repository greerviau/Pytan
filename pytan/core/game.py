from pytan.core.board import Board, CatanTile, TileTypes
from pytan.core.piece import Piece, PieceTypes
from pytan.core.player import Player
from pytan.core.cards import *
from pytan.core.state import GameStates, CatanGameState
import random
from datetime import datetime
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
                Player('P1', 0, 'red'),
                Player('P2', 1, 'blue'),
                Player('P3', 2, 'white'),
                Player('P4', 3, 'orange')
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

        self._resource_card_counts = RESOURCE_CARD_COUNTS.copy()
        self._dev_cards = []
        for card in DEV_CARD_COUNTS:
            for _ in range(DEV_CARD_COUNTS[card]):
                self._dev_cards.append(card)
        random.shuffle(self._dev_cards)

        self._current_player_idx = random.randint(0,len(self._players)-1)
        self._current_player = self._players[self._current_player_idx]
        self._discarding_players = []
        self._players_to_steal_from = []
        
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

    def log(self, text: str, end='\n'):
        print(text, end=end)
        self._logs.append(text)
    
    def log_dump(self) -> str:
        return '\n'.join(self._logs)

    def add_observer(self, observable: object):
        self._observers.add(observable)

    def notify(self):
        for obs in self._observers:
            try:
                obs.notify(self)
            except:
                pass

    @property
    def players(self) -> list[Player]:
        return self._players
    
    @property
    def board(self) -> Board:
        return self._board

    @property
    def state(self) -> CatanGameState:
        return self._game_state
    
    @property
    def current_state(self) -> GameStates:
        return self._game_state.state
    
    @property
    def resource_card_counts(self) -> dict[ResourceCards, int]:
        return self._resource_card_counts

    @property
    def dev_cards(self) -> list[DevCards]:
        return self._dev_cards

    @property
    def n_dev_cards(self) -> int:
        return len(self._dev_cards)

    @property
    def current_player(self) -> Player:
        return self._current_player if not any(self._discarding_players) else self._discarding_players[0]

    @property
    def discarding_players(self) -> list[Player]:
        return self._discarding_players

    @property
    def players_to_steal_from(self) -> list[Player]:
        return self._players_to_steal_from

    @property
    def current_rol(self) -> int:
        return self._current_roll
    
    @property
    def last_roll(self) -> int:
        return self._last_roll

    @property
    def has_rolled(self) -> bool:
        return self._has_rolled

    @property
    def longest_road(self) -> Player:
        return self._longest_road

    @property
    def largest_army(self) -> Player:
        return self._largest_army

    @property
    def moves_made(self) -> int:
        return self._moves_made

    @property
    def turns(self) -> int:
        return self._turns

    @state.setter
    def state(self, s: GameStates):
        self._game_state.set_state(s)

    def get_player_by_id(self, player_id) -> Player:
        for player in self._players:
            if player.identifier == player_id:
                return player
    
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
            player.add_resource_cards(pickup_list)
            self._remove_resources(pickup_list)

    def discard(self, resource_list: list[tuple[str, int]]):
        new_resource_list = []
        for card, n in resource_list:
            new_resource_list.append((ResourceCards(card), n))
        self.discard(new_resource_list)

    def discard(self, resource_list: list[tuple[ResourceCards, int]]):
        if self._game_state.can_discard(log=True):
            player = self._discarding_players[0]
            d = player.n_resource_cards // 2
            if len(resource_list) > d:
                self.log(f'Too many resource cards to discard, discard {d} cards')
            else:
                self._discarding_players.pop(0)
                player.remove_cards(resource_list)
                self._add_resources(resource_list)
                s = f'{player} discarded '
                for card, n in resource_list:
                    s += f'{n}x{card.value} '
                self.log(s)
                if len(self._discarding_players) == 0:
                    self._game_state.set_state(GameStates.MOVING_ROBBER)
                else:
                    p = self._discarding_players[0]
                    d = p.n_resource_cards // 2
                    self.log(f'{p} must discard {d} cards')
        else:
            self.log('No players need to discard')
        self.notify()

    def roll(self, dice_roll=0):
        if self._game_state.can_roll(log=True):
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
                for player in self._players:
                    if player.n_resource_cards > 7:
                        self._discarding_players.append(player)
                if any(self._discarding_players):
                    p = self._discarding_players[0]
                    d = p.n_resource_cards // 2
                    self.log(f'{p} must discard {d} cards')
                    self._game_state.set_state(GameStates.DISCARDING)
                else:
                    self.log(f'{self._current_player} is moving the robber')
                    self._game_state.set_state(GameStates.MOVING_ROBBER)
            else:
                tiles = self._board.tiles_with_prob(dice_roll)
                self._collect_resources(tiles)
                
        self.notify()

    def _pass_turn(self):
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

    def pass_turn(self):
        if self._game_state.can_pass_turn(log=True):
            self._pass_turn()

    def start_building(self, piece_type: PieceTypes):
        if piece_type == PieceTypes.ROAD:
            self._game_state.set_state(GameStates.BUILDING_ROAD)
        elif piece_type == PieceTypes.SETTLEMENT:
            self._game_state.set_state(GameStates.BUILDING_SETTLEMENT)
        elif piece_type == PieceTypes.CITY:
            self._game_state.set_state(GameStates.BUILDING_CITY)
        self.notify()

    def legal_road_placements(self) -> list[int]:
        if self._game_state == GameStates.STARTING_ROAD:
            return self._board.node_neighboring_edges(self._current_player.last_settlement_built)
        else:
            return self._board.legal_road_placements(self._current_player.identifier)
    
    def _build_road(self, coord: int):
        road = None
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
        return road

    def build_road(self, coord: int):
        if self._game_state == GameStates.STARTING_ROAD:
            road = self._build_road(coord)
            if road is not None:
                self._game_state.set_state(GameStates.STARTING_SETTLEMENT)
                self._pass_turn()
        elif self._game_state.can_build_road(log=True):
            road = self._build_road(coord)
            if road is not None:
                self._current_player.remove_resource_cards(ROAD)
                self._add_resources(ROAD)
            self._game_state.set_state(GameStates.INGAME)
                        
        self.notify()

    def legal_settlement_placements(self) -> list[int]:
        if self._game_state == GameStates.STARTING_SETTLEMENT:
            return self._board.legal_starting_settlement_placements(self._current_player.identifier)
        else:
            return self._board.legal_settlement_placements(self._current_player.identifier)

    def _build_settlement(self, coord: int) -> Piece:
        settlement = None
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
        return settlement

    def build_settlement(self, coord: int):
        if self._game_state == GameStates.STARTING_SETTLEMENT:
            settlement = self._build_settlement(coord)
            if settlement is not None:
                if self._current_player.settlements == 2:
                    tiles = self._board.node_neighboring_tiles(self._current_player.last_settlement_built)
                    self._collect_resources(tiles, coord)
                    self._remove_resources(SETTLEMENT)
                self._game_state.set_state(GameStates.STARTING_ROAD)
        elif self._game_state.can_build_settlement(log=True):
            settlement = self._build_settlement(coord)
            if settlement is not None:
                self._current_player.remove_resource_cards(SETTLEMENT)
                self._add_resources(SETTLEMENT)
            self._game_state.set_state(GameStates.INGAME)
        self.notify()

    def legal_city_placements(self) -> list[int]:
        return self._board.legal_city_placements(self._current_player.identifier)

    def _build_city(self, coord: int) -> Piece:
        city = None
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
        return city

    def build_city(self, coord: int):
        if self._game_state.can_build_city(log=True):
            city = self._build_city(coord)
            if city is not None:
                self._current_player.remove_resource_cards(CITY)
                self._add_resources(CITY)
            self._game_state.set_state(GameStates.INGAME)
                        
        self.notify()

    def buy_dev_card(self):
        if self._game_state.can_buy_dev_card(log=True):
            card = self._dev_cards.pop(0)
            self._current_player.buy_dev_card(card)
            self.log(f'{self._current_player} bought a {card.value} Dev Card')
                        
        self.notify()

    def move_robber(self, tile_coord: int):
        if self._game_state.is_moving_robber(log=True):
            self._board.move_robber(tile_coord)
            players = self._board.players_on_tile(tile_coord)
            if any(players):
                self._game_state.set_state(GameStates.STEALING)
                self.log(f'{self._current_player} is stealing')
                self._players_to_steal_from = players
            else:
                self._game_state.set_state(GameStates.INGAME)

        self.notify()

    def steal(self, player_id: int):
        if self._game_state.can_steal(log=True):
            player_to_steal = self.get_player_by_id(player_id)
            if player_to_steal in players_to_steal_from:
                card = random.choice(player_to_steal.resource_cards)
                player_to_steal.remove_resource_card(card)
                self._current_player.add_resource_card(card)
                self.log(f'{self._current_player} stole a {card.value} from {player_to_steal}')
            else:
                self.log(f'Cant steal from {player_to_steal}')

        self.notify()

    #def trade(self, giving: list[tuple[ResourceCards, int]], wanting: list[tuple[ResourceCards, int]], players: list[Player]):
    #    if self._game_state.can_trade():


                
if __name__ == '__main__':
    game = Game()
    print(game.players)
    game.start_game(log=False)
    game.build_first_settlement(0x67)