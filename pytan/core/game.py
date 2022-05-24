from pytan.core.board import Board, CatanTile, TileTypes
from pytan.core.piece import Piece, PieceTypes
from pytan.core.player import Player
from pytan.core.cards import *
from pytan.core.state import GameStates, CatanGameState
from pytan.core.trading import PortTypes, PORT_TO_RESOURCE
from pytan.log.logging import Logger
import random
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

    def __init__(self, players = [], board = None, logger = Logger(), seed=random.random()):
        # Init
        self._logger = logger

        self.set_seed(seed)

        self.init_game_vars()

        self._game_state = CatanGameState(self)

        self._observers = set()

        self._board = Board(seed=seed)
        if board:
            self._board(board)

        self.clear_players()
        if players:
            self._players = players
        else:
            self.add_player(Player('P1', 0, 'red'))
            self.add_player(Player('P2', 1, 'blue'))
            self.add_player(Player('P3', 2, 'white'))
            self.add_player(Player('P4', 3, 'orange'))
        
        self.set_starting_player(random.randint(0,len(self._players)-1))

        self.shuffle_dev_cards()

    def init_game_vars(self):
        # Init game variables
        self._resource_card_counts = RESOURCE_CARD_COUNTS.copy()

        self._discarding_players = []
        self._players_to_steal_from = []
        self._players_accepting_trade = []
        self._players_accepted_trade = []

        self._give_trade = []
        self._want_trade = []
        
        self._current_roll = 0
        self._last_roll = 0
        self._has_rolled = False

        self._free_roads = 0

        self._longest_road = None
        self._largest_army = None

        self._moves_made = 0
        self._turn = 0
        
    def reset(self):
        # Reset the game state
        self._logger.log_action('reset')
        self.init_game_vars()
        self._observers = self._observers.copy()
        self._players = [p.clone_player() for p in self._players]
        self._current_player_idx = self._starting_player_idx
        self._current_player = self._players[self._current_player_idx]

        self._board.set_seed(self._seed)
        self._board.setup_tiles()
        self._board.setup_ports()

        self.shuffle_dev_cards()

        self._game_state.set_state(GameStates.UNDEFINED)
        self._board.reset()

    def set_seed(self, seed: float):
        self._logger.log_action('set_seed', seed)
        self._seed = seed
        random.seed(self._seed)

    def add_observer(self, observable: object):
        self._observers.add(observable)

    def notify(self):
        for obs in self._observers:
            try:
                obs.notify(self)
            except:
                pass

    @property
    def logger(self) -> Logger:
        return self._logger

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
        return self._discarding_players[0] if any(self._discarding_players) else self._players_accepting_trade[0] if any(self._players_accepting_trade) else self._current_player

    @property
    def other_players(self) -> list[Player]:
        return [player for player in self._players if player.identifier != self._current_player.identifier]

    @property
    def discarding_players(self) -> list[Player]:
        return self._discarding_players

    @property
    def players_to_steal_from(self) -> list[Player]:
        return self._players_to_steal_from

    @property
    def players_accepted_trade(self) -> list[Player]:
        return self._players_accepted_trade

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
    def free_roads(self) -> int:
        return self._free_roads

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
    def turn(self) -> int:
        return self._turn

    @state.setter
    def state(self, s: GameStates):
        self._game_state.set_state(s)

    def shuffle_dev_cards(self):
        self._dev_cards = []
        for card in DEV_CARD_COUNTS:
            for _ in range(DEV_CARD_COUNTS[card]):
                self._dev_cards.append(card)
        random.shuffle(self._dev_cards)

    def set_starting_player(self, player_idx: int):
        self._logger.log_action('set_starting_player', player_idx)
        self._starting_player_idx = player_idx
        self._current_player_idx = self._starting_player_idx
        self._current_player = self._players[self._current_player_idx]

    def clear_players(self):
        self._logger.log_action('clear_players')
        self._players = []

    def add_player(self, player: Player):
        if len(self._players) < 4:
            self._logger.log_action('add_player', player)
            self._players.append(player)
        else:
            self._logger.log('Max 4 players')

    def get_player_by_id(self, player_id: int) -> Player:
        for player in self._players:
            if player.identifier == player_id:
                return player
    
    def start_game(self):
        self.reset()

        self._logger.log('=== CATAN ===\n')
        self._logger.log(f'Game Started: {self._logger.start}')
        player_string = '\n'.join([f'{p.identifier} {str(p)}' for p in self._players])
        self._logger.log(player_string)
        self._logger.log(f'{self._current_player} starts')
        self._logger.log_action('start_game')

        self.state = GameStates.STARTING_SETTLEMENT
        self.notify()

    def end_game(self, log=False):
        self._logger.log('Ending Game')
        self._logger.log_action('end_game')
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
                self._logger.log(f'{player} picked up {count} {card.value}')
                pickup_list.append((card,count))
            player.add_resource_cards(pickup_list)
            self._remove_resources(pickup_list)

    def discard(self, resource_list: list[tuple[ResourceCards, int]]):
        if self._game_state.can_discard(log=True):
            player = self._discarding_players[0]
            d = player.n_resource_cards // 2
            d_sum = sum([n for card, n in resource_list])
            if d_sum > d:
                self._logger.log(f'Too many resource cards to discard, discard {d} cards')
            else:
                self._discarding_players.pop(0)
                player.remove_resource_cards(resource_list)
                self._add_resources(resource_list)
                s = f'{player} discarded '
                for card, n in resource_list:
                    s += f'{n} {card.value} '
                self._logger.log(s)
                self._logger.log_action('discard', resource_list)
                if len(self._discarding_players) == 0:
                    self._game_state.set_state(GameStates.MOVING_ROBBER)
                else:
                    p = self._discarding_players[0]
                    d = p.n_resource_cards // 2
                    self._logger.log(f'{p} must discard {d} cards')
        else:
            self._logger.log('No players need to discard')
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
            self._logger.log(f'{self._current_player} rolled a {dice_roll}')
            self._logger.log_action('roll', dice_roll)
            if dice_roll == 7:
                for player in self._players:
                    if player.n_resource_cards > 7:
                        self._discarding_players.append(player)
                if any(self._discarding_players):
                    p = self._discarding_players[0]
                    d = p.n_resource_cards // 2
                    self._logger.log(f'{p} must discard {d} cards')
                    self._game_state.set_state(GameStates.DISCARDING)
                else:
                    self._logger.log(f'{self._current_player} is moving the robber')
                    self._game_state.set_state(GameStates.MOVING_ROBBER)
            else:
                tiles = self._board.tiles_with_prob(dice_roll)
                self._collect_resources(tiles)
                
        self.notify()

    def _pass_turn(self):
        self._has_rolled = False
        self._turn += 1
        d = 1
        if self._turn == 4 or self._turn == 8:
            d = 0
        elif self._turn >= 5 and self._turn < 8:
            d = -1
        if self._turn >= 8:
            self._game_state.set_state(GameStates.INGAME)
        self._current_player_idx += d
        if self._current_player_idx >= len(self._players):
            self._current_player_idx = 0
        elif self._current_player_idx < 0:
            self._current_player_idx = len(self._players)-1
        self._current_player = self._players[self._current_player_idx]
        self._logger.log(f'It is now {self._current_player}\'s turn')
        self.notify()

    def pass_turn(self):
        if self._game_state.can_pass_turn(log=True):
            self._logger.log_action('pass_turn')
            self._pass_turn()

    def legal_road_placements(self) -> list[int]:
        if self._game_state == GameStates.STARTING_ROAD:
            return self._board.node_neighboring_edges(self._current_player.last_settlement_built)
        else:
            return self._board.legal_road_placements(self._current_player.identifier)
    
    def _build_road(self, coord: int) -> Piece:
        road = None
        if coord in self.legal_road_placements():
            road = self._board.build_road(coord, self._current_player)
            if road is not None:
                self._logger.log(f'{self._current_player} built road at {hex(coord)}')
                self._logger.log_action('build_road', hex(coord))
                self._moves_made += 1
                self._current_player.add_road(coord)
            else:
                self._logger.log(f'{self._current_player} failed to build road at {hex(coord)}')
        else:
            self._logger.log(f'{self._current_player} cannot build road at {hex(coord)}')
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
                if self._free_roads == 0:
                    self._current_player.remove_resource_cards(ROAD)
                    self._add_resources(ROAD)
                else:
                    self._free_roads -= 1
                if self._free_roads == 0:
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
                self._logger.log(f'{self._current_player} built settlement at {hex(coord)}')
                self._logger.log_action('build_settlement', hex(coord))
                self._moves_made += 1
                self._current_player.add_settlement(coord)
            else:
                self._logger.log(f'{self._current_player} failed to build settlement at {hex(coord)}')
        else:
            self._logger.log(f'{self._current_player} cannot build settlement at {hex(coord)}')
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
                self._logger.log(f'{self._current_player} upgraded to city at {hex(coord)}')
                self._logger.log_action('build_city', hex(coord))
                self._moves_made += 1
                self._current_player.add_city(coord)
            else:
                self._logger.log(f'{self._current_player} failed to upgrade city at {hex(coord)}')
        else:
            self._logger.log(f'{self._current_player} cannot upgrade city at {hex(coord)}')
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
            self._current_player.buy_dev_card(card, self._turn)
            self._logger.log(f'{self._current_player} bought a {card.value} Dev Card')
            self._logger.log_action('buy_dev_card')
                        
        self.notify()

    def move_robber(self, tile_coord: int):
        if self._game_state.is_moving_robber(log=True):
            self._board.move_robber(tile_coord)
            self._logger.log_action('move_robber', hex(tile_coord))
            players = [p for p in self._board.players_on_tile(tile_coord) if any(p.resource_cards) and p.identifier != self._current_player.identifier]
            if len(players) == 1:
                self._game_state.set_state(GameStates.STEALING)
                self._players_to_steal_from = players
                self.steal(players[0].identifier)
            elif any(players):
                self._game_state.set_state(GameStates.STEALING)
                self._logger.log(f'{self._current_player} is stealing')
                self._players_to_steal_from = players
            else:
                self._game_state.set_state(GameStates.INGAME)

        self.notify()

    def steal(self, player_id: int):
        if self._game_state.can_steal(log=True):
            player_to_steal = self.get_player_by_id(player_id)
            if player_to_steal in self._players_to_steal_from:
                if any(player_to_steal.resource_cards):
                    card = random.choice(player_to_steal.resource_cards)
                    player_to_steal.remove_resource_card(card)
                    self._current_player.add_resource_card(card)
                    self._logger.log(f'{self._current_player} stole a {card.value} from {player_to_steal}')
                    self._logger.log_action('steal', player_id)
                    self._players_to_steal_from = []
                    self._game_state.set_state(GameStates.INGAME)
                else:
                    self._logger.log(f'{player_to_steal} has no cards to steal')
            else:
                self._logger.log(f'Cant steal from {player_to_steal}')

        self.notify()
    '''
    def offer_trade(self, giving: list[tuple[str, int]], wanting: list[tuple[str, int]], players: list[int]):
        give_list = []
        for card, n in giving:
            give_list.append((ResourceCards(card), n))
        want_list = []
        for card, n in wanting:
            want_list.append((ResourceCards(card), n))
        self.offer_trade(give_list, want_list, players)
    '''
    def offer_trade(self, giving: list[tuple[ResourceCards, int]], wanting: list[tuple[ResourceCards, int]], players: list[int]):
        if self._game_state.can_trade(log=True):
            if self._current_player.are_multiple_cards_in_hand(giving):
                if any(wanting):
                    if len(giving) == 1 and len(wanting) == 1 and not any(players):
                        give_card, give_n = giving[0]
                        want_card, want_n = wanting[0]
                        if give_n == 4 and want_n == 1:
                            self._current_player.remove_resource_cards(giving)
                            self._current_player.add_resource_card(want_card)
                            self._add_resources(giving)
                            self._remove_resources(wanting)
                            self._logger.log(f'{self._current_player} traded 4 {give_card.value} for a {want_card.value}')
                            self._logger.log_action('offer_trade', giving, wanting, players)
                            self.notify()
                            return
                        if self.board.is_player_on_port(self._current_player.identifier, PortTypes(give_card.value)) and give_n == 2 and want_n == 1:
                            self._current_player.remove_resource_cards(giving)
                            self._current_player.add_resource_card(want_card)
                            self._add_resources(giving)
                            self._remove_resources(wanting)
                            self._logger.log(f'{self._current_player} traded 2 {give_card.value} for a {want_card.value}')
                            self._logger.log_action('offer_trade', giving, wanting, players)
                            self.notify()
                            return
                        elif self.board.is_player_on_port(self._current_player.identifier, PortTypes.ANY) and give_n == 3 and want_n == 1:
                            self._current_player.remove_resource_cards(giving)
                            self._current_player.add_resource_card(want_card)
                            self._add_resources(giving)
                            self._remove_resources(wanting)
                            self._logger.log(f'{self._current_player} traded 3 {give_card.value} for a {want_card.value}')
                            self._logger.log_action('offer_trade', giving, wanting, players)
                            self.notify()
                            return
                    
                    if any(players):
                        s = f'{self._current_player} wants to trade '
                        for c, n in giving:
                            s += f'{n} {c.value} '
                        s += 'for '
                        for c, n in wanting:
                            s += f'{n} {c.value} '
                        self._logger.log(s)
                        self._logger.log_action('offer_trade', giving, wanting, players)
                        
                        for p_id in players:
                            player = self.get_player_by_id(p_id)
                            if player.are_multiple_cards_in_hand(wanting):
                                self._players_accepting_trade.append(player)
                            else:
                                self._logger.log(f'{player} does not have the cards to trade')
                        if any(self._players_accepting_trade):
                            self._logger.log(f'{self._players_accepting_trade[0]} accept or decline trade?')
                            self._give_trade = giving
                            self._want_trade = wanting
                            self._game_state.set_state(GameStates.ACCEPTING_TRADE)
                        else:
                            self._logger.log('No players have the requested card')
                    else:
                        self._logger.log('Specify players to trade with')
                else:
                    self._logger.log('Specify cards to trade for')
            else:
                self._logger.log(f'{self._current_player} does not have specified cards to trade')
        self.notify()

    def accept_trade(self):
        if self._game_state.can_accept_decline_trade(log=True):
            self._logger.log(f'{self.current_player} accepted trade')
            self._logger.log_action('accept_trade')
            p = self._players_accepting_trade.pop(0)
            self._players_accepted_trade.append(p)
            if not any(self._players_accepting_trade):
                if any(self._players_accepted_trade):
                    self._game_state.set_state(GameStates.CONFIRMING_TRADE)
                else:
                    self._game_state.set_state(GameStates.INGAME)
            else:
                self._logger.log(f'{self._players_accepting_trade[0]} accept or decline trade?')
            
        self.notify()

    def decline_trade(self):
        if self._game_state.can_accept_decline_trade(log=True):
            self._logger.log(f'{self.current_player} declined trade')
            self._logger.log_action('decline_trade')
            p = self._players_accepting_trade.pop(0)
            if not any(self._players_accepting_trade):
                if any(self._players_accepted_trade):
                    self._game_state.set_state(GameStates.CONFIRMING_TRADE)
                else:
                    self._game_state.set_state(GameStates.INGAME)
            else:
                self._logger.log(f'{self._players_accepting_trade[0]} accept or decline trade?')
        self.notify()

    def confirm_trade(self, player_id: int):
        if self._game_state.can_confirm_trade(log=True):
            player = self.get_player_by_id(player_id)
            if player_id in [p.identifier for p in self._players_accepted_trade]:
                self._current_player.remove_resource_cards(self._give_trade)
                self._current_player.add_resource_cards(self._want_trade)
                player.remove_resource_cards(self._want_trade)
                player.add_resource_cards(self._give_trade)

                s = f'{self._current_player} traded '
                for c, n in self._want_trade:
                    s += f'{n} {c.value} '
                s += f'to {player} for '
                for c, n in self._give_trade:
                    s += f'{n} {c.value} '
                self._logger.log(s)
                self._logger.log_action('confirm_trade', player_id)

                self._game_state.set_state(GameStates.INGAME)
                self._want_trade = []
                self._give_trade = []
                self._players_accepted_trade = []
            else:
                self._logger.log(f'Cannot trade with {player}')
        self.notify()

    def play_knight(self):
        if self._game_state.can_play_knight(log=True):
            self._logger.log(f'{self._current_player} played a Knight')
            self._logger.log_action('play_knight')
            self._game_state.set_state(GameStates.MOVING_ROBBER)
            self._current_player.remove_dev_card(DevCards.KNIGHT)
            if self._largest_army is None and self._current_player.knights_played == 3:
                self._largest_army = self._current_player
                self._current_player.largest_army = True
                self._logger.log(f'{self._current_player} has the Largest Army')
        self.notify()

    def play_monopoly(self, resource_card: ResourceCards):
        if self._game_state.can_play_monopoly(log=True):
            self._logger.log(f'{self._current_player} played Monopoly on {resource_card.value}')
            self._logger.log_action('play_monopoly', resource_card)
            self._current_player.remove_dev_card(DevCards.MONOPOLY)
            removed = 0
            for player in self.other_players:
                removed += player.remove_all_resource_card(resource_card)
                if not removed:
                    self._logger.log(f'{player} payed {self._current_player} {removed} {resource_card.value} due to Monopoly')
            self._current_player.add_resource_cards([(resource_card, removed)])
        self.notify()

    def play_road_builder(self):
        if self._game_state.can_play_road_builder(log=True):
            self._game_state.set_state(GameStates.ROADBUILDER)
            self._free_roads = 2
            self._logger.log(f'{self._current_player} played Road Builder, build 2 roads for free')
            self._logger.log_action('play_road_builder')
            self._current_player.remove_dev_card(DevCards.ROADBUILDER)
        self.notify()

    def play_year_plenty(self, pickup_list: list[tuple[ResourceCards, int]]):
        if self._game_state.can_play_year_plenty(log=True):
            count = 0
            cards = []
            for card, n in pickup_list:
                cards.append(card)
                count += n
            if count > 2 or count < 2:
                self._logger.log(f'Cannot pickup {count} cards with Year of Plenty, choose 2')
            else:
                self._current_player.add_resource_cards(pickup_list)
                self._remove_resources(pickup_list)
                self._current_player.remove_dev_card(DevCards.YEAR_PLENTY)
                if len(cards) == 1:
                    self._logger.log(f'{self._current_player} played Year of Plenty, picked up 2 {cards[0].value}')
                else:
                    self._logger.log(f'{self._current_player} played Year of Plenty, picked up a {cards[0].value} and a {cards[1].value}')
                self._logger.log_action('play_year_plenty', pickup_list)

        self.notify()
                
if __name__ == '__main__':
    game = Game()
    print(game.players)
    game.start_game(log=False)
    game.build_first_settlement(0x67)