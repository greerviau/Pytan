from pytan.core.hexmesh import Directions
from pytan.core.tiles import TileTypes
from pytan.core.cards import ResourceCards
from enum import Enum
from collections import namedtuple

class PortTypes(Enum):
    WHEAT = 'WHEAT'
    WOOD = 'WOOD'
    SHEEP = 'SHEEP'
    ORE = 'ORE'
    BRICK = 'BRICK'
    ANY = '3:1'
    NONE = None

PORT_TO_RESOURCE = {
    PortTypes.WHEAT: ResourceCards.WHEAT,
    PortTypes.WOOD: ResourceCards.WOOD,
    PortTypes.SHEEP: ResourceCards.SHEEP,
    PortTypes.ORE: ResourceCards.ORE,
    PortTypes.BRICK: ResourceCards.BRICK
}

PORT_TYPE_COUNTS = {
    PortTypes.WHEAT: 1,
    PortTypes.WOOD: 1,
    PortTypes.SHEEP: 1,
    PortTypes.ORE: 1,
    PortTypes.BRICK: 1,
    PortTypes.ANY: 4
}

Port = namedtuple('Port', ['coord_1', 'coord_2', 'tile', 'direction', 'port_type'])

def create_port(coord_1: int, coord_2: int, tile: TileTypes, direction: Directions, port_type: PortTypes):
    return Port(coord_1, coord_2, tile, direction, port_type)