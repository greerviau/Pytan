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