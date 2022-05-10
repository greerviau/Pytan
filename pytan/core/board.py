from pytan.core.hexmesh import HexMesh
from enum import Enum
import copy
import random

class TILE_TYPES(Enum):
    WHEAT = 'WHEAT'
    WOOD = 'WOOD'
    SHEEP = 'SHEEP'
    ORE = 'ORE'
    BRUCK = 'BRICK'
    DESERT = 'DESERT'

TILE_COUNTS = {
    'WHEAT': 4,
    'WOOD': 4,
    'SHEEP': 4,
    'ORE': 3,
    'BRICK': 3,
    'DESERT': 1
}

PROB_COUNTS = {
    2: 1,
    3: 2,
    4: 2,
    5: 2,
    6: 2,
    7: 2,
    8: 2,
    9: 2,
    10: 2,
    11: 2,
    12: 1
}

class CatanTile(object):
    def __init__(self, coord, prob, tile_type):
        self._coord = coord
        self._prob = prob 
        self._tile_type = tile_type

    @property
    def coord(self):
        return self._coord

    @property
    def prob(self):
        return self._prob

    @property
    def tile_type(self):
        return self._tile_type

    def __repr__(self):
        return f'<Tile Type: {self._tile_type} - Coord: {hex(self._coord)} - Prob: {self._prob}>'

class Port(object):
    def __init__(self, coord_1, coord_2, tile, direction, port_type):
        self._coord_1 = coord_1
        self._coord_2 = coord_2
        self._tile = tile
        self._direction = direction
        self._port_type = port_type

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
    def port_type(self):
        return self._port_type
    
    def __repr__(self):
        return f'<Port Type: {self._port_type} - Coords: {hex(self._coord_1)}:{hex(self._coord_2)} - Tile: {self._tile}>'

class PieceTypes(Enum):
    ROAD = 0
    SETTLEMENT = 1
    CITY = 2
    ROBBER = 3

class Piece(object):
    def __init__(self, coord, owner, piece_type):
        self._coord = coord
        self._owner = owner
        self._piece_type = piece_type

    @property
    def coord(self):
        return self._coord
    
    @property
    def owner(self):
        return self._owner

    @property
    def piece_type(self):
        return self._piece_type

    def __repr__(self):
        return f'<Piece Type: {self._piece_type}  - Coord: {hex(self._coord)} - Owner: {self._owner}>'

class Board(HexMesh):
    def __init__(self, n_layers=2):
        super().__init__(n_layers = n_layers)
        self.reset()
        
    def reset(self):
        # Init board state
        available_tiles = []
        available_probs = []

        for tile_type in TILE_TYPES:
            tile_id = tile_type.value
            for _ in range(TILE_COUNTS[tile_id]):
                available_tiles.append(tile_type)

        for prob in PROB_COUNTS:
            for _ in range(PROB_COUNTS[prob]):
                available_probs.append(prob)

        for coord in self._tiles:
            tile_choice = random.choice(available_tiles)
            available_tiles.remove(tile_choice)
            tile_type = tile_choice
            
            prob = random.choice(available_probs)
            available_probs.remove(prob)

            self._tiles[coord] = CatanTile(coord, prob, tile_type)

    @property
    def roads(self):
        return {coord: edge for coord, edge in self._edges.items() if type(edge) == Piece and edge.piece_type == PieceTypes.ROAD}

    @property
    def settlements(self):
        return {coord: node for coord, node in self._nodes.items() if type(node) == Piece and node.piece_type == PieceTypes.SETTLEMENT}

    @property
    def cities(self):
        return {coord: node for coord, node in self._nodes.items() if type(node) == Piece and node.piece_type == PieceTypes.CITY}

    @property
    def empty_nodes(self):
        return [coord for coord, node in self._nodes.items() if node is None]

    def find_tiles_with_prob(self, prob):
        return {coord: tile for coord, tile in self._tiles.items() if type(tile) == CatanTile and tile.prob == prob}

    def find_settlements_on_tile(self, coord):
        settlements = {}
        for node_coord in self.tile_neighboring_nodes(coord):
            node = self._nodes[node_coord]
            if type(node) == Piece and node.piece_type == PieceTypes.SETTLEMENT:
                settlements[node_coord] = node
        return settlements

    def find_player_settlements(self, player_id):
        return {coord: node for coord, node in self._nodes.items() if type(node) == Piece and node.owner == player_id}

    def find_legal_road_placements(self, player_id):
        legal_road_placements = []
        for coord, edge in self._edges.items():
            if edge == None:
                legal = False
                for c, e in self.edge_neighboring_edges(coord).items():
                    if type(e) == Piece and e.owner == player_id:
                        legal = True
                        break
                for c, n in self.edge_neighboring_nodes(coord).items():
                    if type(n) == Piece and n.owner == player_id:
                        legal = True
                        break
                if legal:
                    legal_road_placements.append(coord)
        return legal_road_placements
    
    def find_legal_settlement_placements(self, player_id):
        legal_settlement_placements = []
        for coord, node in self._nodes.items():
            if node == None:
                neighbor_settlements = 0
                legal = False
                for c, e in self.node_neighboring_edges(coord).items():
                    if type(e) == Piece and e.owner == player_id:
                        legal = True
                        for _, n in self.edge_neighboring_nodes(c).items():
                            if type(n) == Piece and n.piece_type == PieceTypes.SETTLEMENT:
                                neighbor_settlements += 1
                if legal and neighbor_settlements == 0:
                    legal_settlement_placements.append(coord)
        return legal_settlement_placements

    def build_road(self, coord, player_id):
        edge = self._edges[coord]
        if edge == None:
            road = Piece(coord, player_id, PieceTypes.ROAD)
            self._edges[coord] = road
            return road
        return None
        
    def build_settlement(self, coord, player_id):
        node = self._nodes[coord]
        if node == None:
            settlement = Piece(coord, player_id, PieceTypes.SETTLEMENT)
            self._nodes[coord] = settlement
            return settlement
        return None
    
    def upgrade_to_city(self, coord, player_id):
        node = self._nodes[coord]
        if type(node) == Piece and node.piece_type == PieceTypes.SETTLEMENT:
            if node.owner == player_id:
                city = Piece(coord, player_id, PieceTypes.CITY)
                self._nodes[coord] = city
                return city
        return None

    def __repr__(self):
        s = 'Board\n\n'
        s += 'Tiles:\n'
        for tile in self._tiles.values():
            if tile is not None:
                s += f'{tile}\n'

        player_roads = {}
        player_settlements = {}
        player_cities = {}

        for edge in self._edges.values():
            if type(edge) == Piece:
                o_id = edge.owner
                if o_id not in player_roads:
                    player_roads[o_id] = []
                player_roads[o_id].append(edge)

        for node in self._nodes.values():
            if type(node) == Piece and node.piece_type == PieceTypes.SETTLEMENT:
                o_id = node.owner
                if o_id not in player_settlements:
                    player_settlements[o_id] = []
                player_settlements[o_id].append(node)

        for node in self._nodes.values():
            if type(node) == Piece and node.piece_type == PieceTypes.CITY:
                o_id = node.data.owner
                if o_id not in player_settlements:
                    player_cities[o_id] = []
                player_cities[o_id].append(node)

        s += '\nRoads:\n'
        for player in player_roads:
            for road in player_roads[player]:
                s += f'{road}\n'

        s += '\nSettlements:\n'
        for player in player_settlements:
            for settlement in player_settlements[player]:
                s += f'{settlement}\n'
        
        s += '\nCities:\n'
        for player in player_cities:
            for city in player_cities[player]:
                s += f'{city}\n'
        
        return s

if __name__ == '__main__':
    board = Board()
    print(board)
    print('Buy Settlement 0x76')
    board.build_settlement(0x76, 1)
    #print('Legal Roads')
    #print(board.find_legal_road_placements(1))
    #print('Legal Settlements')
    #print(board.find_legal_settlement_placements(1))

    print('Buy Road 0x66')
    board.build_road(0x66, 1)
    #print('Legal Roads')
    #print(board.find_legal_road_placements(1))
    #print('Legal Settlements')
    #print(board.find_legal_settlement_placements(1))

    print('Buy Road 0x67')
    board.build_road(0x67, 1)
    #print('Legal Roads')
    #print(board.find_legal_road_placements(1))
    #print('Legal Settlements')
    #print(board.find_legal_settlement_placements(1))

    print('Buy Road 0x68')
    board.build_road(0x68, 1)
    #print('Legal Roads')
    #print(board.find_legal_road_placements(1))
    #print('Legal Settlements')
    #print(board.find_legal_settlement_placements(1))

    print('Buy Settlement 0x69')
    board.build_settlement(0x69, 1)
    #print('Legal Roads')
    #print(board.find_legal_road_placements(1))
    #print('Legal Settlements')
    #print(board.find_legal_settlement_placements(1))

    print(board)
