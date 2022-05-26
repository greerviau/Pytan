from pytan.core.cards import ResourceCards, DevCards, ROAD, SETTLEMENT, CITY, DEV_CARD

class Player(object):
    def __init__(self, name: str, identifier: int, color: str):
        # Init
        self._name = name
        self._identifier = identifier
        self._color = color
        self._resource_cards = []
        self._dev_cards = []
        self._roads = 0
        self._settlements = 0
        self._cities = 0

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
    def identifier(self) -> int:
        return self._identifier

    @property
    def color(self) -> str:
        return self._color

    @property
    def resource_cards(self) -> list[ResourceCards]:
        return self._resource_cards

    @property
    def n_resource_cards(self) -> int:
        return len(self._resource_cards)

    @property
    def dev_cards(self) -> list[DevCards]:
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
    def victory_points(self) -> int:
        return self.settlements + (self._cities * 2) + (self._largest_army * 2) + (self._longest_road * 2)

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

    def count_resource_cards(self, card: ResourceCards) -> int:
        return self._resource_cards.count(card)

    def add_resource_card(self, card: ResourceCards):
        self._resource_cards.append(card)

    def add_resource_cards(self, cards: list[tuple[ResourceCards, int]]):
        for card, n in cards:
            for _ in range(n):
                self._resource_cards.append(card)

    def remove_resource_card(self, card: ResourceCards):
        try:
            self._resource_cards.remove(card)
        except ValueError:
            pass

    def remove_all_resource_card(self, card: ResourceCards) -> int:
        og_len = len(self._resource_cards)
        self._resource_cards = [c for c in self._resource_cards if c != card]
        return og_len - len(self._resource_cards)

    def remove_resource_cards(self, cards: list[tuple[ResourceCards, int]]):
        for card, n in cards:
            for _ in range(n):
                self.remove_resource_card(card)

    def are_cards_in_hand(self, cards_needed: tuple[ResourceCards, int]) -> bool:
        card, n = cards_needed
        if self._resource_cards.count(card) < n:
            return False
        return True

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
        return self.are_multiple_cards_in_hand(DEV_CARD)

    def buy_dev_card(self, dev_card: DevCards, turn_bought: int):
        if self.can_buy_dev_card():
            self.remove_resource_cards(DEV_CARD)
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
        return self.are_multiple_cards_in_hand(ROAD)

    def add_road(self, coord: int):
        self._last_road_built = coord
        self._roads += 1

    def can_buy_settlement(self) -> bool:
        return self.are_multiple_cards_in_hand(SETTLEMENT)

    def add_settlement(self, coord: int):
        self._last_settlement_built = coord
        self._settlements += 1

    def can_buy_city(self) -> bool:
        return self.are_multiple_cards_in_hand(CITY)

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
                return True
        return False

    def can_play_plenty(self, turn: int) -> bool:
        for card, t in self._dev_cards:
            if card == DevCards.YEAR_PLENTY and t < turn:
                return True
        return False

    def clone_player(self) -> 'Player':
        return Player(self._name, self._identifier, self._color)

    def __repr__(self):
        return f'{self._name} ({self._color})'