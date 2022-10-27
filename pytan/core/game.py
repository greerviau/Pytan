from pytan.core.board import Board
from pytan.core.tiles import TILE_TYPES_TO_RESOURCE
from pytan.core.player import Player
from pytan.core.cards import *
from pytan.core.state import GameStates, CatanGameState
from pytan.core.ports import PortTypes
from pytan.core.tiles import CatanTile
from pytan.log.logging import Logger
from collections import defaultdict
import numpy as np
import random

class Game(object):

    def __init__(self, players: list[Player] = [], logger: Logger = Logger(console_log=True), seed: float = random.random()):
        # Init
        self._logger = logger

        self._prng = random.Random()

        self.set_seed(seed)

        self.init_game_vars()

        self._game_state = CatanGameState(self)

        self._stored_states = []
        self._state_idx = -1

        self._observers = set()

        self._board = Board(seed=seed)

        self.clear_players()
        if players:
            for player in players:
                self.add_player(player)
        else:
            self.add_player(Player('P1', 0, 'red'))
            self.add_player(Player('P2', 1, 'blue'))
            self.add_player(Player('P3', 2, 'white'))
            self.add_player(Player('P4', 3, 'orange'))
        player_ids = set([p.id for p in self._players])
        assert len(player_ids) == len(self._players)
        
        self.set_starting_player(self._prng.randint(0,len(self._players)-1))

        self.shuffle_dev_cards()
    
    @property
    def logger(self) -> Logger:
        return self._logger

    @property
    def observers(self) -> set:
        return self._observers

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
    def last_state(self) -> dict:
        return self._last_state
    
    @property
    def next_state(self) -> dict:
        return self._next_state
    
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
    def current_player_idx(self) -> int:
        return self._current_player_idx

    @property
    def current_turn_player(self) -> Player:
        return self._players[self._current_player_idx]

    @property
    def current_player(self) -> Player:
        return self.discarding_player if self._discarding_players \
                else self.player_accepting_trade if self._players_accepting_trade \
                else self._players[self._current_player_idx]

    @property
    def other_players(self) -> list[Player]:
        return [player for player in self._players if player.id != self.current_turn_player.id]

    @property
    def discarding_players(self) -> list[Player]:
        return [self.get_player_by_id(i) for i in self._discarding_players]

    @property
    def discarding_player(self) -> Player:
        return self.get_player_by_id(self._discarding_players[0])

    @property
    def players_to_steal_from(self) -> list[Player]:
        return [self.get_player_by_id(i) for i in self._players_to_steal_from]

    @property
    def player_accepting_trade(self) -> Player:
        return self.get_player_by_id(self._players_accepting_trade[0])

    @property
    def players_accepted_trade(self) -> list[Player]:
        return [self.get_player_by_id(i) for i in self._players_accepted_trade]

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
    def knight_played_this_turn(self) -> bool:
        return self._knight_played_this_turn

    @property
    def free_roads(self) -> int:
        return self._free_roads

    @property
    def longest_road(self) -> Player:
        return self.get_player_by_id(self._longest_road) if self._longest_road > -1 else None

    @property
    def largest_army(self) -> Player:
        return self.get_player_by_id(self._largest_army) if self._largest_army > -1 else None

    @property
    def moves_made(self) -> int:
        return self._moves_made

    @property
    def turn(self) -> int:
        return self._turn

    @property
    def state_idx(self) -> int:
        return self._state_idx
    
    @property
    def stored_states(self) -> list[dict]:
        return self._stored_states

    @property
    def can_undo(self) -> bool:
        return self._state_idx > 0

    @property
    def can_redo(self) -> bool:
        return self._state_idx < len(self._stored_states) - 1

    @state.setter
    def state(self, s: GameStates):
        self._game_state.set_state(s)

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

        self._knight_played_this_turn = False

        self._free_roads = 0

        self._longest_road = -1
        self._largest_army = -1

        self._moves_made = 0
        self._turn = 0
        
    def reset(self, randomize: bool = False):
        # Reset the game state
        self.init_game_vars()
        self._observers = self._observers.copy()
        self._players = [p.clone_player() for p in self._players]
        self._current_player_idx = self._starting_player_idx

        self._stored_states = []
        self._state_idx = -1

        if randomize:
            self.set_seed(random.random(), log=False)
        else:
            self.set_seed(self._seed, log=False)

        self._board.set_seed(self._seed)
        self._board.reset()

        self.shuffle_dev_cards()

        self._game_state.set_state(GameStates.UNDEFINED)

    def set_seed(self, seed: float, log: bool = True):
        if log:
            self._logger.log_action('set_seed', seed)
        self._seed = seed
        self._prng.seed(self._seed)

    def clear_observers(self):
        self._observers = set()

    def add_observer(self, observable: object):
        self._observers.add(observable)

    def notify(self, new:bool = True, update:bool = True):
        if new:
            if self._state_idx < len(self._stored_states)-1:
                self._stored_states[self._state_idx+1] = self.get_state()
            else:
                self._stored_states.append(self.get_state())
            self._state_idx += 1
        for player in self._players:
            if player.total_victory_points >= 10:
                self._logger.log(f'GAME OVER {self.current_turn_player} wins!')
                self._game_state.set_state(GameStates.GAME_OVER)
        if update:
            for obs in self._observers:
                try:
                    obs.notify(self)
                except:
                    pass

    def shuffle_dev_cards(self):
        self._dev_cards = []
        for card in DEV_CARD_COUNTS:
            for _ in range(DEV_CARD_COUNTS[card]):
                self._dev_cards.append(card)
        self._prng.shuffle(self._dev_cards)

    def set_starting_player(self, player_idx: int):
        self._logger.log_action('set_starting_player', player_idx)
        self._starting_player_idx = player_idx
        self._current_player_idx = self._starting_player_idx

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
            if player.id == player_id:
                return player
    
    def start_game(self, randomize: bool = False):
        self.reset(randomize)

        self._logger.log('=== CATAN ===\n')
        self._logger.log(f'Game Started: {self._logger.start}')
        player_string = '\n'.join([f'{p.id} {str(p)}' for p in self._players])
        self._logger.log(player_string)
        self._logger.log(f'{self.current_turn_player} starts')
        self._logger.log_action('start_game')

        self.state = GameStates.STARTING_SETTLEMENT
        self.notify()

    def end_game(self, log: bool = False):
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

    def _collect_resources(self, tiles: dict[int, CatanTile], node_coord: int = 0x00):
        pickups = defaultdict(lambda: defaultdict(int))
        quantity = defaultdict(int)
        for tile_coord, tile in tiles.items():
            if tile_coord != self._board.robber.coord:
                card = TILE_TYPES_TO_RESOURCE[tile.tile_type]
                if card is not None:
                    for s_coord, settlement in self._board.settlements_on_tile(tile_coord).items():
                        if node_coord == 0 or node_coord == s_coord:
                            p_id = settlement.owner_id
                            pickups[p_id][card] += 1
                            quantity[card] += 1
                    
                    for c_coord, city in self._board.cities_on_tile(tile_coord).items():
                        if node_coord == 0 or node_coord == s_coord:
                            p_id = city.owner_id
                            pickups[p_id][card] += 2
                            quantity[card] += 2

        for p_id, cards in pickups.items():
            pickup_list = []
            player = self.get_player_by_id(p_id)
            p_l = []
            for card, count in cards.items():
                if quantity[card] < self._resource_card_counts[card]:
                    p_l.append(f'{count} {card.value}')
                    pickup_list.append((card,count))
            if pickup_list:
                s = ', '.join(p_l)
                self._logger.log(f'{player} picked up {s}')
                player.add_resource_cards(pickup_list)
                self._remove_resources(pickup_list)

    def discard(self, resource_list: list[tuple[ResourceCards, int]]):
        if self._game_state.can_discard(log=True):
            player = self.discarding_player
            d = player.n_resource_cards // 2
            d_sum = sum([n for card, n in resource_list])
            if d_sum > d:
                self._logger.log(f'Too many resource cards to discard, discard {d} cards')
            else:
                self._discarding_players.pop(0)
                player.remove_resource_cards(resource_list)
                self._add_resources(resource_list)
                d_l = []
                for card, n in resource_list:
                    d_l.append(f'{n} {card.value}')
                s = ', '.join(d_l)
                self._logger.log(f'{player} discarded {s}')
                self._logger.log_action('discard', resource_list)
                if len(self._discarding_players) == 0:
                    self._logger.log(f'{self.current_player} is moving the robber')
                    self._game_state.set_state(GameStates.MOVING_ROBBER)
                else:
                    p = self.discarding_player
                    d = p.n_resource_cards // 2
                    self._logger.log(f'{p} must discard {d} cards')
                self.notify()
        else:
            self._logger.log('No players need to discard')

    def roll(self, dice_roll: int = 0):
        if self._game_state.can_roll(log=True):
            self._has_rolled = True
            # Roll a random dice roll
            dice_1 = self._prng.choice([1,2,3,4,5,6])
            dice_2 = self._prng.choice([1,2,3,4,5,6])
            d_roll = dice_1 + dice_2
            if dice_roll == 0:
                dice_roll = d_roll
            # Roll a determined dice roll
            self._last_roll = self._current_roll
            self._current_roll = dice_roll
            self._logger.log(f'{self.current_turn_player} rolled a {dice_roll}')
            self._logger.log_action('roll', dice_roll)
            if dice_roll == 7:
                for player in self._players:
                    if player.n_resource_cards > 7:
                        self._discarding_players.append(player.id)
                if self._discarding_players:
                    p = self.discarding_player
                    d = p.n_resource_cards // 2
                    self._logger.log(f'{p} must discard {d} cards')
                    self._game_state.set_state(GameStates.DISCARDING)
                else:
                    self._logger.log(f'{self.current_turn_player} is moving the robber')
                    self._game_state.set_state(GameStates.MOVING_ROBBER)
            else:
                tiles = self._board.tiles_with_prob(dice_roll)
                self._collect_resources(tiles)   
            self.notify()

    def _pass_turn(self):
        self._has_rolled = False
        self._knight_played_this_turn = False
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
        self._logger.log(f'It is now {self.current_turn_player}\'s turn')

    def pass_turn(self):
        if self._game_state.can_pass_turn(log=True):
            self._logger.log_action('pass_turn')
            self._pass_turn()
            self.notify()

    def legal_road_placements(self) -> list[int]:
        if self._game_state == GameStates.STARTING_ROAD:
            return self._board.node_neighboring_edges(self.current_turn_player.last_settlement_built)
        else:
            return self._board.legal_road_placements(self.current_turn_player.id)
    
    def _build_road(self, coord: int) -> bool:
        if coord in self.legal_road_placements():
            if self._board.build_road(coord, self.current_turn_player):
                self._logger.log(f'{self.current_turn_player} built road at {hex(coord)}')
                self._logger.log_action('build_road', hex(coord))
                self._moves_made += 1
                self.current_turn_player.add_road(coord)
                chain = self._board.find_longest_road_chain(self.current_turn_player.id)
                self.current_turn_player.longest_road_chain = chain
                if chain >= 5:
                    if not self.longest_road or (self.longest_road and chain > self.longest_road.longest_road_chain):
                        if self.longest_road:
                            self.longest_road.longest_road = False
                        self._longest_road = self.current_turn_player.id
                        self.current_turn_player.longest_road = True
                return True
            else:
                self._logger.log(f'{self.current_turn_player} failed to build road at {hex(coord)}')
        else:
            self._logger.log(f'{self.current_turn_player} cannot build road at {hex(coord)}')
        return False

    def build_road(self, coord: int):
        if self._game_state == GameStates.STARTING_ROAD:
            if self._build_road(coord):
                self._game_state.set_state(GameStates.STARTING_SETTLEMENT)
                self._pass_turn()
                self.notify()
        elif self._game_state.can_build_road(log=True):
            if self._build_road(coord):
                if self._free_roads == 0:
                    self.current_turn_player.remove_resource_cards(ROAD_COST)
                    self._add_resources(ROAD_COST)
                else:
                    self._free_roads -= 1
                if self._free_roads == 0:
                    self._game_state.set_state(GameStates.INGAME)       
                self.notify()

    def legal_settlement_placements(self) -> list[int]:
        if self._game_state == GameStates.STARTING_SETTLEMENT:
            return self._board.legal_starting_settlement_placements(self.current_turn_player.id)
        else:
            return self._board.legal_settlement_placements(self.current_turn_player.id)

    def _build_settlement(self, coord: int) -> bool:
        if coord in self.legal_settlement_placements():
            if self._board.build_settlement(coord, self.current_turn_player):
                self._logger.log(f'{self.current_turn_player} built settlement at {hex(coord)}')
                self._logger.log_action('build_settlement', hex(coord))
                self._moves_made += 1
                self.current_turn_player.add_settlement(coord)
                return True
            else:
                self._logger.log(f'{self.current_turn_player} failed to build settlement at {hex(coord)}')
        else:
            self._logger.log(f'{self.current_turn_player} cannot build settlement at {hex(coord)}')
        return False

    def build_settlement(self, coord: int):
        if self._game_state == GameStates.STARTING_SETTLEMENT:
            if self._build_settlement(coord):
                tiles = self._board.node_neighboring_tiles(self.current_turn_player.last_settlement_built)
                for t in tiles:
                    self.current_turn_player.add_tile(self._board.tiles[t])
                if self.current_turn_player.settlements == 2:
                    self._collect_resources(tiles, coord)
                self._game_state.set_state(GameStates.STARTING_ROAD)
                self.notify()
        elif self._game_state.can_build_settlement(log=True):
            if self._build_settlement(coord):
                self.current_turn_player.remove_resource_cards(SETTLEMENT_COST)
                self._add_resources(SETTLEMENT_COST)
                tiles = self._board.node_neighboring_tiles(self.current_turn_player.last_settlement_built)
                for t in tiles:
                    self.current_turn_player.add_tile(self._board.tiles[t])
                self._game_state.set_state(GameStates.INGAME)
                self.notify()

    def legal_city_placements(self) -> list[int]:
        return self._board.legal_city_placements(self.current_turn_player.id)

    def _build_city(self, coord: int) -> bool:
        if coord in self.legal_city_placements():
            if self._board.build_city(coord, self.current_turn_player):
                self._logger.log(f'{self.current_turn_player} upgraded to city at {hex(coord)}')
                self._logger.log_action('build_city', hex(coord))
                self._moves_made += 1
                self.current_turn_player.add_city(coord)
                return True
            else:
                self._logger.log(f'{self.current_turn_player} failed to upgrade city at {hex(coord)}')
        else:
            self._logger.log(f'{self.current_turn_player} cannot upgrade city at {hex(coord)}')
        return False

    def build_city(self, coord: int):
        if self._game_state.can_build_city(log=True):
            if self._build_city(coord):
                self.current_turn_player.remove_resource_cards(CITY_COST)
                self._add_resources(CITY_COST)
                self._game_state.set_state(GameStates.INGAME)               
                self.notify()

    def buy_dev_card(self, dev_card:DevCards = None):
        if self._game_state.can_buy_dev_card(log=True):
            if not dev_card:
                dev_card = self._dev_cards.pop(0)
            self.current_turn_player.add_dev_card(dev_card, self._turn)
            self.current_turn_player.remove_resource_cards(DEV_CARD_COST)
            self._add_resources(DEV_CARD_COST)
            self._logger.log(f'{self.current_turn_player} bought a {dev_card.value} Dev Card')
            self._logger.log_action('buy_dev_card', dev_card)         
            self.notify()

    def move_robber(self, tile_coord: int, auto_steal: bool = False):
        if self._game_state.is_moving_robber(log=True):
            if tile_coord != self.board.robber.coord:
                self._board.move_robber(tile_coord)
                self._logger.log(f'{self.current_player} moved the robber to {hex(tile_coord)}')
                self._logger.log_action('move_robber', hex(tile_coord))
                player_ids = [p_id for p_id in self._board.players_on_tile(tile_coord) if self.get_player_by_id(p_id).n_resource_cards > 0 and p_id != self.current_player.id]
                if len(player_ids) == 1:
                    self._game_state.set_state(GameStates.STEALING)
                    self._players_to_steal_from = player_ids
                    if auto_steal:
                        self._steal(player_ids[0])
                elif player_ids:
                    self._game_state.set_state(GameStates.STEALING)
                    self._logger.log(f'{self.current_turn_player} is stealing')
                    self._players_to_steal_from = player_ids
                else:
                    self._game_state.set_state(GameStates.INGAME)
                self.notify()
            else:
                self._logger.log('Robber is already at that location')
    
    def _steal(self, player_id: int):
        player_to_steal = self.get_player_by_id(player_id)
        if player_id in self._players_to_steal_from:
            if player_to_steal.n_resource_cards > 0:
                card = self._prng.choice(player_to_steal.resource_cards_list)
                player_to_steal.remove_resource_card(card)
                self.current_turn_player.add_resource_card(card)
                self._logger.log(f'{self.current_turn_player} stole a {card.value} from {player_to_steal}')
                self._players_to_steal_from = []
                self._game_state.set_state(GameStates.INGAME)
                return True
            else:
                self._logger.log(f'{player_to_steal} has no cards to steal')
        else:
            self._logger.log(f'Cant steal from {player_to_steal}')
        return False

    def steal(self, player_id: int):
        if self._game_state.can_steal(log=True):
            if self._steal(player_id):
                self._logger.log_action('steal', player_id)
                self.notify()

    def offer_trade(self, giving: list[tuple[ResourceCards, int]], wanting: list[tuple[ResourceCards, int]], players: list[int]):
        if self._game_state.can_trade(log=True):
            if self.current_turn_player.are_multiple_cards_in_hand(giving):
                if wanting:
                    if len(giving) == 1 and len(wanting) == 1 and not players:
                        give_card, give_n = giving[0]
                        want_card, want_n = wanting[0]
                        if self._resource_card_counts[want_card] >= 1:
                            if give_n == 4 and want_n == 1:
                                self.current_turn_player.remove_resource_cards(giving)
                                self.current_turn_player.add_resource_card(want_card)
                                self._add_resources(giving)
                                self._remove_resources(wanting)
                                self._logger.log(f'{self.current_turn_player} traded 4 {give_card.value} for a {want_card.value}')
                                self._logger.log_action('offer_trade', giving, wanting, players)
                                self.notify()
                                return
                            if self.board.is_player_on_port(self.current_turn_player.id, PortTypes(give_card.value)) and give_n == 2 and want_n == 1:
                                self.current_turn_player.remove_resource_cards(giving)
                                self.current_turn_player.add_resource_card(want_card)
                                self._add_resources(giving)
                                self._remove_resources(wanting)
                                self._logger.log(f'{self.current_turn_player} traded 2 {give_card.value} for a {want_card.value}')
                                self._logger.log_action('offer_trade', giving, wanting, players)
                                self.notify()
                                return
                            elif self.board.is_player_on_port(self.current_turn_player.id, PortTypes.ANY) and give_n == 3 and want_n == 1:
                                self.current_turn_player.remove_resource_cards(giving)
                                self.current_turn_player.add_resource_card(want_card)
                                self._add_resources(giving)
                                self._remove_resources(wanting)
                                self._logger.log(f'{self.current_turn_player} traded 3 {give_card.value} for a {want_card.value}')
                                self._logger.log_action('offer_trade', giving, wanting, players)
                                self.notify()
                                return
                        else:
                            self._logger.log(f'The bank does not have any {want_card.value} left')
                    if players:
                        s = f'{self.current_turn_player} wants to trade '
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
                                self._players_accepting_trade.append(player.id)
                            else:
                                self._logger.log(f'{player} does not have the cards to trade')
                        if self._players_accepting_trade:
                            self._logger.log(f'{self.player_accepting_trade} accept or decline trade?')
                            self._give_trade = giving
                            self._want_trade = wanting
                            self._game_state.set_state(GameStates.ACCEPTING_TRADE)
                            self.notify()
                        else:
                            self._logger.log('No players have the requested card')
                    else:
                        self._logger.log('Specify players to trade with')
                else:
                    self._logger.log('Specify cards to trade for')
            else:
                self._logger.log(f'{self.current_turn_player} does not have specified cards to trade')

    def accept_trade(self):
        if self._game_state.can_accept_decline_trade(log=True):
            self._logger.log(f'{self.current_player} accepted trade')
            self._logger.log_action('accept_trade')
            p = self._players_accepting_trade.pop(0)
            self._players_accepted_trade.append(p)
            if not self._players_accepting_trade:
                if self._players_accepted_trade:
                    self._game_state.set_state(GameStates.CONFIRMING_TRADE)
                else:
                    self._game_state.set_state(GameStates.INGAME)
            else:
                self._logger.log(f'{self.player_accepting_trade} accept or decline trade?')   
            self.notify()

    def decline_trade(self):
        if self._game_state.can_accept_decline_trade(log=True):
            self._logger.log(f'{self.current_player} declined trade')
            self._logger.log_action('decline_trade')
            p = self._players_accepting_trade.pop(0)
            if not self._players_accepting_trade:
                if self._players_accepted_trade:
                    self._game_state.set_state(GameStates.CONFIRMING_TRADE)
                else:
                    self._game_state.set_state(GameStates.INGAME)
            else:
                self._logger.log(f'{self.player_accepting_trade} accept or decline trade?')
            self.notify()

    def confirm_trade(self, player_id: int):
        if self._game_state.can_confirm_trade(log=True):
            player = self.get_player_by_id(player_id)
            if player_id in self._players_accepted_trade:
                self.current_turn_player.remove_resource_cards(self._give_trade)
                self.current_turn_player.add_resource_cards(self._want_trade)
                player.remove_resource_cards(self._want_trade)
                player.add_resource_cards(self._give_trade)

                s = f'{self.current_turn_player} traded '
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
                self.notify()
            else:
                self._logger.log(f'Cannot trade with {player}')

    def play_knight(self):
        if self._game_state.can_play_knight(log=True):
            self._logger.log(f'{self.current_turn_player} played a Knight')
            self._logger.log_action('play_knight')
            self._game_state.set_state(GameStates.MOVING_ROBBER)
            self.current_turn_player.remove_dev_card(DevCards.KNIGHT)
            self._knight_played_this_turn = True
            army = self.current_turn_player.knights_played
            if army >= 3:
                if not self.largest_army or (self.largest_army and army > self.largest_army.knights_played):
                    self._largest_army = self.current_turn_player.id
                    self.current_turn_player.largest_army = True
                    self._logger.log(f'{self.current_turn_player} has the Largest Army')
            self.notify()

    def play_monopoly(self, resource_card: ResourceCards):
        if self._game_state.can_play_monopoly(log=True):
            self._logger.log(f'{self.current_turn_player} played Monopoly on {resource_card.value}')
            self._logger.log_action('play_monopoly', resource_card)
            self.current_turn_player.remove_dev_card(DevCards.MONOPOLY)
            removed = 0
            for player in self.other_players:
                removed += player.remove_all_resource_card(resource_card)
                if not removed:
                    self._logger.log(f'{player} payed {self.current_turn_player} {removed} {resource_card.value} due to Monopoly')
            self.current_turn_player.add_resource_cards([(resource_card, removed)])
            self.notify()

    def play_road_builder(self):
        if self._game_state.can_play_road_builder(log=True):
            self._game_state.set_state(GameStates.ROADBUILDER)
            self._free_roads = 2
            self._logger.log(f'{self.current_turn_player} played Road Builder, build 2 roads for free')
            self._logger.log_action('play_road_builder')
            self.current_turn_player.remove_dev_card(DevCards.ROADBUILDER)
            self.notify()

    def play_year_plenty(self, card1: ResourceCards, card2: ResourceCards):
        if self._game_state.can_play_year_plenty(log=True):
            if card1 and card2:
                pickup_list = []
                if card1 == card2:
                    pickup_list = [(card1, 2)]
                    self._logger.log(f'{self.current_turn_player} played Year of Plenty, picked up 2 {card1.value}')
                else:
                    pickup_list = [(card1, 1), (card2, 1)]
                    self._logger.log(f'{self.current_turn_player} played Year of Plenty, picked up a {card1.value} and a {card2.value}')
                self.current_turn_player.add_resource_cards(pickup_list)
                self._remove_resources(pickup_list)
                self.current_turn_player.remove_dev_card(DevCards.YEAR_PLENTY)
                self._logger.log_action('play_year_plenty', card1, card2)
                self.notify()

    def get_state(self) -> dict:
        return {
            'board': self._board.get_state(),
            'players': [player.get_state() for player in self._players],
            'logger': self._logger.get_state(),
            'prng': self._prng.getstate(),
            'state': self._game_state.state,
            'resource_card_counts': self._resource_card_counts.copy(),
            'dev_cards': self._dev_cards.copy(),
            'current_player_idx': self._current_player_idx,
            'discarding_players': self._discarding_players.copy(),
            'players_to_steal_from': self._players_to_steal_from.copy(),
            'players_accepting_trade': self._players_accepting_trade.copy(),
            'players_accepted_trade': self._players_accepted_trade.copy(),
            'give_trade': self._give_trade.copy(),
            'want_trade': self._want_trade.copy(),
            'current_roll': self._current_roll,
            'last_roll': self._last_roll,
            'has_rolled': self._has_rolled,
            'knight_played_this_turn': self._knight_played_this_turn,
            'free_roads': self._free_roads,
            'longest_road': self._longest_road,
            'largest_army': self._largest_army,
            'moves_made': self._moves_made,
            'turn': self._turn
        }

    def restore(self, state: dict):
        self._board = Board.create_from_state(state['board'])
        self._players = [Player.create_from_state(s) for s in state['players']]
        self._logger = Logger.create_from_state(state['logger'])
        self._prng.setstate(state['prng'])
        self._game_state.set_state(state['state'])
        self._resource_card_counts = state['resource_card_counts'].copy()
        self._dev_cards = state['dev_cards'].copy()
        self._current_player_idx = state['current_player_idx']
        self._discarding_players = state['discarding_players'].copy()
        self._players_to_steal_from = state['players_to_steal_from'].copy()
        self._players_accepting_trade = state['players_accepting_trade'].copy()
        self._players_accepted_trade = state['players_accepted_trade'].copy()
        self._give_trade = state['give_trade'].copy()
        self._want_trade = state['want_trade'].copy()
        self._current_roll = state['current_roll']
        self._last_roll = state['last_roll']
        self._has_rolled = state['has_rolled']
        self._knight_played_this_turn = state['knight_played_this_turn']
        self._free_roads = state['free_roads']
        self._longest_road = state['longest_road']
        self._largest_army = state['largest_army']
        self._moves_made = state['moves_made']
        self._turn = state['turn']

    @staticmethod
    def create_from_state(state: dict) -> 'Game':
        game = Game()
        game.restore(state)
        return game
    
    def undo(self, update:bool = True):
        if len(self._stored_states) > 0 and self._state_idx > 0:
            self._state_idx -= 1
            self.restore(self._stored_states[self._state_idx])
            self.notify(new=False, update=update)
        else:
            print('Cant undo')
    
    def redo(self, update: bool = True):
        if self._state_idx < len(self._stored_states)-1:
            self._state_idx += 1
            self.restore(self._stored_states[self._state_idx])
            self.notify(new=False, update=update)
        else:
            print('Cant redo')