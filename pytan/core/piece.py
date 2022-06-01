from enum import Enum
from collections import namedtuple

class PieceTypes(Enum):
    ROAD = 0
    SETTLEMENT = 1
    CITY = 2
    ROBBER = 3

Piece = namedtuple('Piece', ['coord', 'owner_id', 'owner_name', 'color', 'piece_type'])

'''
class Piece(object):
    def __init__(self, coord: int, owner_id: int, owner_name: str, color: str, piece_type: PieceTypes):
        self._coord = coord
        self._owner_id = owner_id
        self._owner_name = owner_name
        self._color = color
        self._piece_type = piece_type

    @property
    def coord(self) -> int:
        return self._coord

    @property
    def owner_id(self) -> int:
        return self._owner.id

    @property
    def owner_name(self) -> str:
        return self._owner_name

    @property
    def color(self) -> str:
        return self._color

    @property
    def piece_type(self) -> PieceTypes:
        return self._piece_type

    def get_props(self) -> dict:
        return {
            'coord': self._coord,
            'owner_id': self._owner_id,
            'owner_name': self._owner_name,
            'color': self._color,
            'piece_type': self._piece_type
        }

    @staticmethod
    def create_from_props(props: dict) -> pytan.core.piece.Piece:
        return Piece(props['coord'], props['owner_id'], props['owner_name'], props['color'], props['piece_type'])

    def __repr__(self):
        return f'<Piece Type: {self._piece_type}  - Coord: {hex(self._coord)} - Owner: {self._owner_name}({self._color})>'
'''