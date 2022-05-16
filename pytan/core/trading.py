from enum import Enum
from pytan.core.cards import ResourceCards

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

class Port(object):
    def __init__(self, coord_1, coord_2, tile, direction, port_type):
        self._coord_1 = coord_1
        self._coord_2 = coord_2
        self._tile = tile
        self._direction = direction
        self._port_type = port_type
        self._exchange = 2
        if self._port_type == PortTypes.ANY:
            self._exchange = 3

    @property
    def coord_1(self):
        return self._coord_1
    
    @property
    def coord_2(self):
        return self._coord_2
    
    @property
    def tile(self):
        return self._tile

    @property
    def direction(self):
        return self._direction

    @property
    def port_type(self):
        return self._port_type

    @property
    def exchange(self):
        return self._exchange

    def can_exchange(self, resource_cards: list[ResourceCards]):
        required_card = PORT_TO_RESOURCE[self._port_type] if self._port_type != PortTypes.ANY else resource_cards[0]
        return len(resource_cards) >= self._exchange and resource_cards.count(required_card) == len(resource_cards)

    def node_is_on_port(self, node_coord: int):
        return node_coord == self._coord_1 or node_coord == self._coord_2
    
    def __repr__(self):
        return f'<Port Type: {self._port_type} - Coords: {hex(self._coord_1)}:{hex(self._coord_2)} - Tile: {self._tile}>'
