from pytan.core.cards import ResourceCards, DevCards, ROAD_COST, SETTLEMENT_COST, CITY_COST, DEV_CARD_COST
from pytan.core.tiles import CatanTile, TileTypes
from collections import defaultdict
import copy

class Player(object):
    def __init__(self, name: str, id: int, color: str):
        # Init
        self._name = name
        self._id = id
        self._color = color
        self._resource_cards = defaultdict(int)
        self._dev_cards = []
        self._roads = 0
        self._settlements = 0
        self._cities = 0

        self._resource_production = defaultdict(int)

        self._diversity = defaultdict(int)

        self._vps = 0

        self._knights_played = 0
        self._longest_road_chain = 0

        self._largest_army = False
        self._longest_road = False

        self._last_road_built = 0x00
        self._last_settlement_built = 0x00
        self._last_city_built = 0x00

    @property
    def name(self) -> str:
        return self._name

    @property
    def id(self) -> int:
        return self._id

    @property
    def color(self) -> str:
        return self._color

    @property
    def resource_cards(self) -> dict[ResourceCards, int]:
        return self._resource_cards

    @property
    def resource_cards_list(self) -> list[ResourceCards]:
        l = []
        for card, count in self._resource_cards.items():
            l.extend([card for _ in range(count)])
        return l

    @property
    def n_resource_cards(self) -> int:
        return sum(self._resource_cards.values())

    @property
    def dev_cards(self) -> dict[DevCards, int]:
        return self._dev_cards

    @property
    def n_dev_cards(self) -> int:
        return len(self._dev_cards)

    @property
    def roads(self) -> int:
        return self._roads

    @property
    def roads_left(self) -> int:
        return 12 - self._roads

    @property
    def settlements(self) -> int:
        return self._settlements

    @property
    def settlements_left(self) -> int:
        return 5 - self._settlements

    @property
    def cities(self) -> int:
        return self._cities

    @property
    def cities_left(self) -> int:
        return 4 - self._cities

    @property
    def resource_production(self) -> dict:
        return self._resource_production

    @property
    def production_points(self) -> int:
        return sum(list(self._resource_production.values()))

    @property
    def pp_score(self) -> float:
        s = self._settlements if self._settlements > 0 else 1
        return self.production_points / s

    @property
    def diversity(self) -> dict:
        return self._diversity
    
    @property
    def diversity_score(self) -> float:
        m = max(self._diversity.values()) if sum(self._diversity.values()) > 0 else 1
        return sum([d / m for d in self._diversity.values()])

    @property
    def victory_points(self) -> int:
        return self._settlements + (self._cities * 2) + (self._largest_army * 2) + (self._longest_road * 2)

    @property
    def total_victory_points(self) -> int:
        return self.victory_points + self._vps

    @property
    def knights_played(self) -> int:
        return self._knights_played

    @property
    def longest_road_chain(self) -> int:
        return self._longest_road_chain

    @property
    def largest_army(self) -> bool:
        return self._largest_army

    @property
    def longest_road(self) -> bool:
        return self._longest_road
        
    @property
    def last_road_built(self) -> int:
        return self._last_road_built

    @property
    def last_settlement_built(self) -> int:
        return self._last_settlement_built
    
    @property
    def last_city_built(self) -> int:
        return self._last_city_built

    @largest_army.setter
    def largest_army(self, b: bool):
        self._largest_army = b

    @longest_road_chain.setter
    def longest_road_chain(self, c: int):
        self._longest_road_chain = c

    @longest_road.setter
    def longest_road(self, b: bool):
        self._longest_road = b

    def add_tile(self, tile: CatanTile):
        tile_type = tile.tile_type
        prod = tile.prod_points
        if tile_type != TileTypes.DESERT:
            self._diversity[tile_type] += 1
            self._resource_production[tile_type] += prod
        else:
            self._diversity[tile_type] -= 1

    def count_resource_cards(self, card: ResourceCards) -> int:
        if card in self._resource_cards.keys():
            return self._resource_cards[card]
        return 0

    def add_resource_card(self, card: ResourceCards):
        self._resource_cards[card] += 1

    def add_resource_cards(self, cards: list[tuple[ResourceCards, int]]):
        for card, n in cards:
            self._resource_cards[card] += n

    def remove_resource_card(self, card: ResourceCards):
        self._resource_cards[card] -= 1

    def remove_all_resource_card(self, card: ResourceCards) -> int:
        og_len = self.n_resource_cards
        self._resource_cards[card] = 0
        return og_len - self.n_resource_cards

    def remove_resource_cards(self, cards: list[tuple[ResourceCards, int]]):
        for card, n in cards:
            self._resource_cards[card] -= n

    def are_cards_in_hand(self, cards_needed: tuple[ResourceCards, int]) -> bool:
        card, n = cards_needed
        return self.count_resource_cards(card) >= n

    def are_multiple_cards_in_hand(self, cards_needed: list[tuple[ResourceCards, int]]) -> bool:
        for c in cards_needed:
            if not self.are_cards_in_hand(c):
                return False
        return True

    def count_dev_cards(self, card: DevCards) -> int:
        count = 0
        for c, _ in self._dev_cards:
            if c == card:
                count += 1
        return count

    def can_buy_dev_card(self) -> bool:
        return self.are_multiple_cards_in_hand(DEV_CARD_COST)

    def add_dev_card(self, dev_card: DevCards, turn_bought: int):
        if self.can_buy_dev_card():
            self._dev_cards.append((dev_card, turn_bought))
            if dev_card == DevCards.VICTORY_POINT:
                self._vps += 1

    def remove_dev_card(self, dev_card: DevCards):
        for card, turn in self._dev_cards:
            if card == dev_card:
                self._dev_cards.remove((card,turn))
                break
        if dev_card == DevCards.KNIGHT:
            self._knights_played += 1

    def can_buy_road(self) -> bool:
        return self.are_multiple_cards_in_hand(ROAD_COST)

    def add_road(self, coord: int):
        self._last_road_built = coord
        self._roads += 1

    def can_buy_settlement(self) -> bool:
        return self.are_multiple_cards_in_hand(SETTLEMENT_COST)

    def add_settlement(self, coord: int):
        self._last_settlement_built = coord
        self._settlements += 1

    def can_buy_city(self) -> bool:
        return self.are_multiple_cards_in_hand(CITY_COST)

    def add_city(self, coord: int):
        self._last_city_built = coord
        self._settlements -= 1
        self._cities += 1

    def can_play_knight(self, turn: int) -> bool:
        for card, t in self._dev_cards:
            if card == DevCards.KNIGHT and t < turn:
                return True
        return False

    def can_play_monopoly(self, turn: int) -> bool:
        for card, t in self._dev_cards:
            if card == DevCards.MONOPOLY and t < turn:
                return True
        return False

    def can_play_road_builder(self, turn: int) -> bool:
        for card, t in self._dev_cards:
            if card == DevCards.ROADBUILDER and t < turn:
                if self.roads_left >= 2:
                    return True
        return False

    def can_play_plenty(self, turn: int) -> bool:
        for card, t in self._dev_cards:
            if card == DevCards.YEAR_PLENTY and t < turn:
                return True
        return False

    def clone_player(self) -> 'Player':
        return Player(self._name, self._id, self._color)

    def get_state(self) -> dict:
        return {
            'name': self._name,
            'id': self._id,
            'color': self._color,
            'resource_cards': self._resource_cards.copy(),
            'dev_cards': self._dev_cards.copy(),
            'roads': self._roads,
            'settlements': self._settlements,
            'cities': self._cities,
            'resource_production': self._resource_production.copy(),
            'diversity': self._diversity.copy(),
            'vps': self._vps,
            'knights_played': self._knights_played,
            'longest_road_chain': self._longest_road_chain,
            'largest_army': self._largest_army,
            'longest_road': self._longest_road,
            'last_road_built': self._last_road_built,
            'last_settlement_built': self._last_settlement_built,
            'last_city_built': self._last_city_built
        }

    def restore(self, state: dict):
        self._name = state['name']
        self._id = state['id']
        self._color = state['color']
        self._resource_cards = state['resource_cards'].copy()
        self._dev_cards = state['dev_cards'].copy()
        self._roads = state['roads']
        self._settlements = state['settlements']
        self._cities = state['cities']
        self._resource_production = state['resource_production'].copy()
        self._diversity = state['diversity'].copy()
        self._vps = state['vps']
        self._knights_played = state['knights_played']
        self._longest_road_chain = state['longest_road_chain']
        self._largest_army = state['largest_army']
        self._longest_road = state['longest_road']
        self._last_road_built = state['last_road_built']
        self._last_settlement_built = state['last_settlement_built']
        self._last_city_built = state['last_city_built']
    
    @staticmethod
    def create_from_state(state: dict) -> 'Player':
        player = Player('', '', 0)
        player.restore(state)
        return player

    def __repr__(self):
        return f'{self._name} ({self._color})'