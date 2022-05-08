from pytan.core.cards import RESOURCE_CARDS, DEV_CARDS

class Player(object):
    def __init__(self, name, identifier, color):
        # Init
        self._name = name
        self._id = identifier
        self._color = color
        self._resource_cards = []
        self._dev_cards = []
        self._roads = []
        self._settlements = []
        self._cities = []

        self._vps = 0
        self._knights_played = 0

    @property
    def name(self):
        return self._name

    @property
    def identifier(self):
        return self._id

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
        return 12 - len(self._roads)

    @property
    def settlements(self):
        return self._settlements

    @property
    def settlements_left(self):
        return 5 - len(self._settlements)

    @property
    def cities(self):
        return self._cities

    @property
    def cities_left(self):
        return 4 - len(self._cities)

    @property
    def victory_points(self):
        return self._vps

    @property
    def knights_played(self):
        return self._knights_played

    @staticmethod
    def clone_player(player):
        return Player(player.name, player.identifier, player.color)

    def collect_resource_card(self, card_key):
        self._resource_cards.append(RESOURCE_CARDS[card_key])

    def remove_resource_card(self, card_key):
        self._resource_cards.remove(RESOURCE_CARDS[card_key])

    def cards_in_hand(self, cards_needed):
        for card, num in cards_needed:
            if self._resource_cards.count(card) < num:
                return False
        return True

    def can_buy_dev_card(self):
        return self.cards_in_hand([(RESOURCE_CARDS[0], 1), (RESOURCE_CARDS[2], 1), (RESOURCE_CARDS[3], 1)])

    def collect_dev_card(self, dev_card_key):
        if self.can_buy_dev_card():
            self.remove_resource_card(0)
            self.remove_resource_card(2)
            self.remove_resource_card(3)
            self._dev_cards.append(DEV_CARDS[dev_card_key])

    def remove_dev_card(self, dev_card_key):
        card = self.dev_cards.remove(dev_card_key)
        if DEV_CARDS[dev_card_key] == 'KNIGHT':
            self._knights_played += 1

    def can_buy_road(self):
        return self.cards_in_hand([(RESOURCE_CARDS[1], 1), (RESOURCE_CARDS[4], 1)])

    def build_road(self, road):
        self._roads.append(road)

    def can_buy_settlement(self):
        return self.cards_in_hand([(RESOURCE_CARDS[0], 1), (RESOURCE_CARDS[1], 1), (RESOURCE_CARDS[2], 1), (RESOURCE_CARDS[4], 1)])

    def build_settlement(self, settlement):
        self._settlements.append(settlement)

    def can_buy_city(self):
        return self.cards_in_hand([(RESOURCE_CARDS[0], 2), (RESOURCE_CARDS[3], 3)])

    def upgrade_to_city(self, settlement, city):
        self._settlements.remove(settlement)
        self._cities.append(city)

    def __repr__(self):
        return f'{self._name} ({self._color})'