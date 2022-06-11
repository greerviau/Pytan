from enum import Enum
from collections import namedtuple

class PieceTypes(Enum):
    ROAD = 0
    SETTLEMENT = 1
    CITY = 2
    ROBBER = 3

Piece = namedtuple('Piece', ['coord', 'owner_id', 'owner_name', 'color', 'piece_type'])

def place_piece(coord: int, owner_id: int, owner_name: str, color: str, piece_type: PieceTypes):
    return Piece(coord, owner_id, owner_name, color, piece_type)