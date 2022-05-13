from enum import Enum

class RESOURCE_CARDS(Enum):
    WHEAT = 'WHEAT'
    WOOD = 'WOOD'
    SHEEP = 'SHEEP'
    ORE = 'ORE'
    BRICK = 'BRICK'

RESOURCE_CARD_COUNTS = {
    'WHEAT': 15,
    'WOOD': 15,
    'SHEEP': 15,
    'ORE': 15,
    'BRICK': 15
}

class DEV_CARDS(Enum):
    VP = 'VP'
    KNIGHT = 'KNIGHT'
    MONOPOLY = 'MONOPOLY'
    ROADBUILD = 'ROADBUILD'
    PLENTY = 'PLENTY'

DEV_CARD_COUNTS = {
    'VP': 5,
    'KNIGHT': 5,
    'MONOPOLY': 5,
    'ROADBUILD': 5,
    'PLENTY': 5
}

ROAD = [(RESOURCE_CARDS.WOOD, 1), (RESOURCE_CARDS.BRICK, 1)]
SETTLEMENT = [(RESOURCE_CARDS.WHEAT, 1), (RESOURCE_CARDS.SHEEP, 1), (RESOURCE_CARDS.WOOD, 1), (RESOURCE_CARDS.BRICK, 1)]
CITY = [(RESOURCE_CARDS.WHEAT, 2), (RESOURCE_CARDS.ORE, 3)]
DEV_CARD = [(RESOURCE_CARDS.WHEAT, 1), (RESOURCE_CARDS.ORE, 1), (RESOURCE_CARDS.SHEEP, 1)]
