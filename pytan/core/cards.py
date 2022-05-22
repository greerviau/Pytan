from enum import Enum

class ResourceCards(Enum):
    WHEAT = 'WHEAT'
    WOOD = 'WOOD'
    SHEEP = 'SHEEP'
    ORE = 'ORE'
    BRICK = 'BRICK'

RESOURCE_CARD_COUNTS = {
    ResourceCards.WHEAT: 19,
    ResourceCards.WOOD: 19,
    ResourceCards.SHEEP: 19,
    ResourceCards.ORE: 19,
    ResourceCards.BRICK: 19
}

class DevCards(Enum):
    VICTORY_POINT = 'VICTORY_POINT'
    KNIGHT = 'KNIGHT'
    MONOPOLY = 'MONOPOLY'
    ROADBUILDER = 'ROADBUILDER'
    YEAR_PLENTY = 'YEAR_PLENTY'

DEV_CARD_COUNTS = {
    DevCards.VICTORY_POINT: 5,
    DevCards.KNIGHT: 14,
    DevCards.MONOPOLY: 2,
    DevCards.ROADBUILDER: 2,
    DevCards.YEAR_PLENTY: 2
}

ROAD = [(ResourceCards.WOOD, 1), (ResourceCards.BRICK, 1)]
SETTLEMENT = [(ResourceCards.WHEAT, 1), (ResourceCards.SHEEP, 1), (ResourceCards.WOOD, 1), (ResourceCards.BRICK, 1)]
CITY = [(ResourceCards.WHEAT, 2), (ResourceCards.ORE, 3)]
DEV_CARD = [(ResourceCards.WHEAT, 1), (ResourceCards.ORE, 1), (ResourceCards.SHEEP, 1)]
