from pytan.core.cards import ResourceCards, DevCards, ROAD, SETTLEMENT, CITY, DEV_CARD

class Player(object):
    def __init__(self, name, identifier, color):
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

        self._last_road_built = 0x00
        self._last_settlement_built = 0x00
        self._last_city_built = 0x00

    @property
    def name(self):
        return self._name

    @property
    def identifier(self):
        return self._identifier

    @property
    def color(self):
        return self._color

    @property
    def resource_cards(self):
        return self._resource_cards

    @property
    def n_resource_cards(self):
        return len(self._resource_cards)

    @property
    def dev_cards(self):
        return self._dev_cards

    @property
    def n_dev_cards(self):
        return len(self._dev_cards)

    @property
    def roads(self):
        return self._roads

    @property
    def roads_left(self):
        return 12 - self._roads

    @property
    def settlements(self):
        return self._settlements

    @property
    def settlements_left(self):
        return 5 - self._settlements

    @property
    def cities(self):
        return self._cities

    @property
    def cities_left(self):
        return 4 - self._cities

    @property
    def victory_points(self):
        return self._vps

    @property
    def knights_played(self):
        return self._knights_played
        
    @property
    def last_road_built(self):
        return self._last_road_built

    @property
    def last_settlement_built(self):
        return self._last_settlement_built
    
    @property
    def last_city_built(self):
        return self._last_city_built

    def count_resource_cards(self, card: ResourceCards):
        return self._resource_cards.count(card)

    def collect_resource_cards(self, cards: list[tuple[ResourceCards, int]]):
        for card, n in cards:
            for _ in range(n):
                self._resource_cards.append(card)

    def remove_resource_card(self, card: ResourceCards):
        self._resource_cards.remove(card)

    def remove_resource_cards(self, cards: list[tuple[ResourceCards, int]]):
        for card, n in cards:
            for _ in range(n):
                self._resource_cards.remove(card)

    def are_cards_in_hand(self, cards_needed: tuple[ResourceCards, int]):
        for card, n in cards_needed:
            if self._resource_cards.count(card) < n:
                return False
        return True

    def count_dev_cards(self, card: DevCards):
        return self._dev_cards.count(card)

    def can_buy_dev_card(self):
        return self.are_cards_in_hand(DEV_CARD)

    def buy_dev_card(self):
        if self.can_buy_dev_card():
            self.remove_resource_cards(DEV_CARD)
            self._dev_cards.append(dev_card)

    def remove_dev_card(self, dev_card: DevCards):
        card = self.DevCards.remove(dev_card)
        if dev_card == DevCards.KNIGHT:
            self._knights_played += 1

    def can_buy_road(self):
        return self.are_cards_in_hand(ROAD)

    def add_road(self, coord: int):
        self._last_road_built = coord
        self._roads += 1

    def can_buy_settlement(self):
        return self.are_cards_in_hand(SETTLEMENT)

    def add_settlement(self, coord: int):
        self._last_settlement_built = coord
        self._settlements += 1

    def can_buy_city(self):
        return self.are_cards_in_hand(CITY)

    def add_city(self, coord: int):
        self._last_city_built = coord
        self._settlements -= 1
        self._cities += 1

    def clone_player(self):
        return Player(self._name, self._identifier, self._color)

    def __repr__(self):
        return f'{self._name} ({self._color})'