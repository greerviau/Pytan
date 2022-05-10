from pytan.core.cards import RESOURCE_CARDS, DEV_CARDS

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
    def dev_cards(self):
        return self._dev_cards

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

    def collect_resource_card(self, card):
        self._resource_cards.append(card)

    def remove_resource_card(self, card):
        self._resource_cards.remove(card)

    def are_cards_in_hand(self, cards_needed):
        for card, num in cards_needed:
            if self._resource_cards.count(card) < num:
                return False
        return True

    def can_buy_dev_card(self):
        return self.are_cards_in_hand([(RESOURCE_CARDS.WHEAT, 1), (RESOURCE_CARDS.SHEEP, 1), (RESOURCE_CARDS.ORE, 1)])

    def collect_dev_card(self, dev_card):
        if self.can_buy_dev_card():
            self.remove_resource_card(RESOURCE_CARDS.WHEAT)
            self.remove_resource_card(RESOURCE_CARDS.SHEEP)
            self.remove_resource_card(RESOURCE_CARDS.ORE)
            self._dev_cards.append(dev_card)

    def remove_dev_card(self, dev_card):
        card = self.dev_cards.remove(dev_card)
        if dev_card == DEV_CARDS.KNIGHT:
            self._knights_played += 1

    def can_buy_road(self):
        return self.are_cards_in_hand([(RESOURCE_CARDS.WOOD, 1), (RESOURCE_CARDS.BRICK, 1)])

    def add_road(self):
        self._roads += 1

    def can_buy_settlement(self):
        return self.are_cards_in_hand([(RESOURCE_CARDS.WHEAT, 1), (RESOURCE_CARDS.SHEEP, 1), (RESOURCE_CARDS.WOOD, 1), (RESOURCE_CARDS.BRICK, 1)])

    def add_settlement(self):
        self._settlements += 1

    def can_buy_city(self):
        return self.are_cards_in_hand([(RESOURCE_CARDS.WHEAT, 2), (RESOURCE_CARDS.ORE, 3)])

    def add_city(self):
        self._settlements -= 1
        self._cities += 1

    def clone_player(self):
        return Player(self._name, self._identifier, self._color)

    def __repr__(self):
        return f'{self._name} ({self._color})'