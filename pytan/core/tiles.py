
from enum import Enum
from collections import namedtuple
from pytan.core.cards import ResourceCards

class TileTypes(Enum):
    WHEAT = 'WHEAT'
    WOOD = 'WOOD'
    SHEEP = 'SHEEP'
    ORE = 'ORE'
    BRICK = 'BRICK'
    DESERT = 'DESERT'

TILE_COUNTS = {
    TileTypes.WHEAT: 4,
    TileTypes.WOOD: 4,
    TileTypes.SHEEP: 4,
    TileTypes.ORE: 3,
    TileTypes.BRICK: 3,
    TileTypes.DESERT: 1
}

TILE_TYPES_TO_RESOURCE = {  
    TileTypes.WHEAT: ResourceCards.WHEAT,
    TileTypes.WOOD: ResourceCards.WOOD,
    TileTypes.SHEEP: ResourceCards.SHEEP,
    TileTypes.ORE: ResourceCards.ORE,
    TileTypes.BRICK: ResourceCards.BRICK,
    TileTypes.DESERT: None
}

PROB_COUNTS = {
    2: 1,
    3: 2,
    4: 2,
    5: 2,
    6: 2,
    8: 2,
    9: 2,
    10: 2,
    11: 2,
    12: 1
}

PROB_TO_PROD = {
    2: 1,
    3: 2,
    4: 3,
    5: 4,
    6: 5,
    7: 0,
    8: 5,
    9: 4,
    10: 3,
    11: 2,
    12: 1
}

CatanTile = namedtuple('CatanTile', ['coord', 'prob', 'tile_type', 'prod_points'])

'''
class CatanTile(object):
    def __init__(self, coord: int, prob: int, tile_type: TileTypes):
        self._coord = coord
        self._prob = prob 
        self._tile_type = tile_type
        self._prod_points = PROB_TO_PROD[prob]

    @property
    def coord(self) -> int:
        return self._coord

    @property
    def prob(self) -> int:
        return self._prob

    @property
    def prod_points(self) -> int:
        return self._prod_points

    @property
    def tile_type(self) -> TileTypes:
        return self._tile_type

    def __repr__(self):
        return f'<Tile Type: {self._tile_type} - Coord: {hex(self._coord)} - Prob: {self._prob}>'
'''