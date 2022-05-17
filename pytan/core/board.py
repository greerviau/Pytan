from pytan.core import hexmesh
from pytan.core.player import Player
from pytan.core.piece import PieceTypes, Piece
from pytan.core.cards import ResourceCards
from pytan.core.trading import PortTypes, Port, PORT_TYPE_COUNTS
from enum import Enum
import copy
import random

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

class CatanTile(object):
    def __init__(self, coord, prob, tile_type):
        self._coord = coord
        self._prob = prob 
        self._tile_type = tile_type
        self._prod_points = PROB_TO_PROD[prob]

    @property
    def coord(self):
        return self._coord

    @property
    def prob(self):
        return self._prob

    @property
    def prod_points(self):
        return self._prod_points

    @property
    def tile_type(self):
        return self._tile_type

    def __repr__(self):
        return f'<Tile Type: {self._tile_type} - Coord: {hex(self._coord)} - Prob: {self._prob}>'

class Board(hexmesh.HexMesh):
    def __init__(self):
        super().__init__(n_layers = 2)
        self.reset()
        
    def reset(self):
        self.setup_tiles()
        self.setup_ports()

    def setup_tiles(self):
        self._robber = None
        
        available_tiles = []
        available_probs = []

        for tile in TILE_COUNTS:
            for _ in range(TILE_COUNTS[tile]):
                available_tiles.append(tile)

        for prob in PROB_COUNTS:
            for _ in range(PROB_COUNTS[prob]):
                available_probs.append(prob)

        for coord in self._tiles:
            tile_choice = random.choice(available_tiles)
            available_tiles.remove(tile_choice)
            tile_type = tile_choice
            
            prob = 7
            if tile_type != TileTypes.DESERT:
                prob = random.choice(available_probs)
                available_probs.remove(prob)
            else:
                self._robber = Piece(coord, None, PieceTypes.ROBBER)

            self._tiles[coord] = CatanTile(coord, prob, tile_type)

    def setup_ports(self, rotate=0):
        self._ports = {}
        edge_tiles = list(self.edge_tiles.keys())
        for i in range(rotate):
            edge_tiles.append(edge_tiles.pop(0))

        available_ports = []
        for port_type in PORT_TYPE_COUNTS:
            for _ in range(PORT_TYPE_COUNTS[port_type]):
                available_ports.append(port_type)
        
        directions = ['NE', 'E', 'SE', 'SW', 'W', 'NW']
        dir_to_tile = hexmesh.direction_to_tile(edge_tiles[0], edge_tiles[1])
        i = directions.index(dir_to_tile) - 2
        j = 2
        for tile in edge_tiles:
            if j % 4 != 0:
                port_dir = directions[i]
                if (j+1) % 4 != 0:
                    i += 1
                    if i > len(directions) - 1:
                        i = 0
                edge = hexmesh.edge_in_direction(tile, port_dir)
                node1, node2 = tuple(self.edge_neighboring_nodes(edge).keys())
                port_type = random.choice(available_ports)
                available_ports.remove(port_type)
                self._ports[tile] = Port(node1, node2, tile, port_dir, port_type)

            j += 1

    def get_port_at(self, tile_coord: int, direction: str):
        for port in self._ports:
            if port.tile == tile_coord and port.direction == direction:
                return port
        port = Port(tile_coord, direction, PortTypes.NONE)
        self.ports.append(port)
        return port

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
    def ports(self):
        return self._ports

    @property
    def robber(self):
        return self._robber

    def legal_robber_placements(self):
        return [coord for coord, tile in self._tiles.items() if coord != self._robber.coord]

    def move_robber(self, coord: int):
        self._robber = Piece(coord, None, PieceTypes.ROBBER)

    def tiles_with_prob(self, prob: int):
        return {coord: tile for coord, tile in self._tiles.items() if type(tile) == CatanTile and tile.prob == prob}

    def settlements_on_tile(self, tile_coord: int):
        settlements = {}
        for node_coord in self.tile_neighboring_nodes(tile_coord):
            node = self._nodes[node_coord]
            if type(node) == Piece and node.piece_type == PieceTypes.SETTLEMENT:
                settlements[node_coord] = node
        return settlements
    
    def cities_on_tile(self, tile_coord: int):
        cities = {}
        for node_coord in self.tile_neighboring_nodes(tile_coord):
            node = self._nodes[node_coord]
            if type(node) == Piece and node.piece_type == PieceTypes.CITY:
                cities[node_coord] = node
        return cities
    
    def friendly_roads(self, player_id: int):
        return {coord: edge for coord, edge in self.occupied_edges.items() if type(edge) == Piece and edge.owner_id == player_id}

    def friendly_settlements(self, player_id: int):
        return {coord: node for coord, node in self.occupied_nodes.items() if type(node) == Piece and node.piece_type == PieceTypes.SETTLEMENT and node.owner_id == player_id}
 
    def friendly_cities(self, player_id: int):
        return {coord: node for coord, node in self.occupied_nodes.items() if type(node) == Piece and node.piece_type == PieceTypes.CITY and node.owner_id == player_id}

    def friendly_pieces(self, player_id: int) -> list[Piece]:
        pieces = []
        for edge in self.friendly_roads(player_id).values():
            pieces.append(edge)
        for node in self.friendly_settlements(player_id).values():
            pieces.append(edge)
        for node in self.friendly_cities(player_id).values():
            pieces.append(edge)
        return pieces

    def settlement_neighboring_settlement(self, node_coord: int):
        neighbor_nodes = self.node_neighboring_nodes(node_coord)
        for coord, node in neighbor_nodes.items():
            if type(node) == Piece:
                return True
        return False
            
    def settlement_neighboring_friendly_road(self, node_coord: int, player_id: int):
        neighbor_edges = self.node_neighboring_edges(node_coord)
        for coord, edge in neighbor_edges.items():
            if type(edge) == Piece and edge.owner_id == player_id:
                return True
        return False

    def road_neighboring_friendly_piece(self, edge_coord: int, player_id: int):
        neighbor_nodes = self.edge_neighboring_nodes(edge_coord)
        neighbor_edges = self.edge_neighboring_edges(edge_coord)
        for node, edge in zip(neighbor_nodes.values(), neighbor_edges.values()):
            if (type(node) == Piece and node.owner_id == player_id) or (type(edge) == Piece and edge.owner_id == player_id):
                return True
        return False

    def road_neighboring_enemy_settlement(self, edge_coord: int, player_id: int):
        for node in self.edge_neighboring_nodes(edge_coord).values():
            if type(node) == Piece and node.owner_id != player_id:
                return True
        return False

    def legal_road_placements(self, player_id: int):
        legal_road_placements = []
        for piece in self.friendly_pieces(player_id):
            edges = []
            if piece.piece_type == PieceTypes.ROAD:
                if self.road_neighboring_enemy_settlement(piece.coord, player_id):
                    continue
                edges = self.edge_neighboring_edges(piece.coord)
            else:
                edges = self.node_neighboring_edges(piece.coord)
            for coord, edge in edges.items():
                if edge == None:
                    legal_road_placements.append(coord)
        return legal_road_placements

    def legal_starting_settlement_placements(self, player_id: int):
        legal_settlement_placements = []
        for coord in self.empty_nodes:
            if not self.settlement_neighboring_settlement(coord):
                legal_settlement_placements.append(coord)
        return legal_settlement_placements
    
    def legal_settlement_placements(self, player_id: int):
        legal_settlement_placements = []
        for coord in self.empty_nodes:
            if not self.settlement_neighboring_settlement(coord) and self.settlement_neighboring_friendly_road(coord, player_id):
                legal_settlement_placements.append(coord)
        return legal_settlement_placements

    def legal_city_placements(self, player_id: int):
        legal_city_placements = []
        for coord, node in self.occupied_nodes.items():
            if type(node) == Piece and node.piece_type == PieceTypes.SETTLEMENT and node.owner_id == player_id:
                legal_city_placements.append(coord)
        return legal_city_placements

    def build_road(self, edge_coord: int, player: Player):
        edge = self._edges[edge_coord]
        if edge == None:
            road = Piece(edge_coord, player, PieceTypes.ROAD)
            self._edges[edge_coord] = road
            return road
        return None
        
    def build_settlement(self, node_coord: int, player: Player):
        node = self._nodes[node_coord]
        if node == None:
            settlement = Piece(node_coord, player, PieceTypes.SETTLEMENT)
            self._nodes[node_coord] = settlement
            return settlement
        return None
    
    def build_city(self, node_coord: int, player: Player):
        node = self._nodes[node_coord]
        if type(node) == Piece and node.piece_type == PieceTypes.SETTLEMENT:
            if node.owner_id == player.identifier:
                city = Piece(node_coord, player, PieceTypes.CITY)
                self._nodes[node_coord] = city
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

    print('Buy Road 0x66')
    board.build_road(0x66, 1)

    print('Buy Road 0x67')
    board.build_road(0x67, 1)

    print('Buy Road 0x68')
    board.build_road(0x68, 1)

    print('Buy Settlement 0x69')
    board.build_settlement(0x69, 1)

    print(board)
