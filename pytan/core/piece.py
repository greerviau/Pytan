from pytan.core.player import Player
from enum import Enum

class PieceTypes(Enum):
    ROAD = 0
    SETTLEMENT = 1
    CITY = 2
    ROBBER = 3

class Piece(object):
    def __init__(self, coord: int, owner: Player, piece_type: PieceTypes):
        self._coord = coord
        self._owner = owner
        self._piece_type = piece_type

    @property
    def coord(self) -> int:
        return self._coord
    
    @property
    def owner(self) -> Player:
        return self._owner

    @property
    def owner_id(self) -> int:
        return self._owner.identifier

    @property
    def piece_type(self) -> PieceTypes:
        return self._piece_type

    def __repr__(self):
        return f'<Piece Type: {self._piece_type}  - Coord: {hex(self._coord)} - Owner: {self._owner}>'
