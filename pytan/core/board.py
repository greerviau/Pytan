from pytan.core import hexmesh
import copy
import random

TILE_TYPE_TO_ID = {
    'WHEAT': 0,
    'WOOD': 1,
    'SHEEP': 2,
    'ORE': 3,
    'BRICK': 4,
    'DESERT': 5
}

TILE_ID_TO_TYPE = {
    0: 'WHEAT',
    1: 'WOOD',
    2: 'SHEEP',
    3: 'ORE',
    4: 'BRICK',
    5: 'DESERT'
}

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
    12:1
}

class CatanTile(hexmesh.Tile):
    def __init__(self, hex_code, prob, _type, identifier):
        super().__init__(hex_code, None)
        self._prob = prob 
        self._type = _type
        self._id = identifier

    @property
    def prob(self):
        return self._prob

    @property
    def tile_type(self):
        return self._type

    @property
    def identifier(self):
        return self._id

    def __repr__(self):
        return f'{self._type} - {self._prob}'

class Port(object):
    def __init__(self, node1, node2, tile, direction, port_type):
        self._node1 = node1
        self._node2 = node2
        self._tile = tile
        self._direction = direction
        self._port_type = port_type

    @property
    def node1(self):
        return self._node1
    
    @property
    def node2(self):
        return self._node2
    
    @property
    def tile(self):
        return self._tile

    @property
    def port_type(self):
        return self._port_type

class Buildable(object):
    def __init__(self, owner, coord):
        self._owner = owner
        self._coord = coord

    @property
    def owner(self):
        return self._owner

    @property
    def owner_id(self):
        return self._owner.identifier

    @property
    def coord(self):
        return self._coord

    def __repr__(self):
        return f'Owner: {self._owner} - Coord: {hex(self._coord)}'

class Road(Buildable):
    def __init__(self, player_id, coord):
        super().__init__(player_id, coord)

    def __repr__(self):
        return f'Road - Owner: {self._owner} - Coord: {hex(self._coord)}'

class Settlement(Buildable):
    def __init__(self, player_id, coord):
        super().__init__(player_id, coord)
        self._vp = 1

    def __repr__(self):
        return f'Settlement - Owner: {self._owner} - Coord: {hex(self._coord)}' 

class City(Buildable):
    def __init__(self, player_id, coord):
        super().__init__(player_id, coord)
        self._vp = 2

    def __repr__(self):
        return f'City - Owner: {self._owner} - Coord: {hex(self._coord)}' 

class Board(object):
    def __init__(self):
        self.reset()
        
    def reset(self):
        self._hex_mesh = hexmesh.HexMesh(n_layers=2)

        # Init board state
        available_tiles = []
        available_probs = []

        for tile_type in TILE_TYPE_TO_ID:
            tile_id = TILE_TYPE_TO_ID[tile_type]
            for _ in range(TILE_COUNTS[tile_type]):
                available_tiles.append((tile_id, tile_type))

        for prob in PROB_COUNTS:
            for _ in range(PROB_COUNTS[prob]):
                available_probs.append(prob)

        for tile_code in self._hex_mesh.tiles:
            tile_choice = random.choice(available_tiles)
            available_tiles.remove(tile_choice)
            tile_id, tile_type = tile_choice
            
            prob = random.choice(available_probs)
            available_probs.remove(prob)

            self._hex_mesh.tiles[tile_code] = CatanTile(tile_code, prob, tile_type, tile_id)

    @property
    def tiles(self):
        return self._hex_mesh.tiles

    @property
    def nodes(self):
        return self._hex_mesh.nodes

    @property
    def edges(self):
        return self._hex_mesh.edges

    @property
    def roads(self):
        return [edge for edge in self._hex_mesh.edges.values() if type(edge.data) == Road]

    @property
    def settlements(self):
        return [node for node in self._hex_mesh.nodes.values() if type(node.data) == Settlement]

    @property
    def cities(self):
        return [node for node in self._hex_mesh.nodes.values() if type(node.data) == City]

    def find_tiles_with_prob(self, prob):
        tiles = []
        for tile in self._hex_mesh.tiles.values():
            if type(tile.data) == CatanTile:
                if tile.data.prob == prob:
                    tiles.append(tile)
        return tiles

    def find_empty_nodes(self):
        return [node for node in self._hex_mesh.nodes.values() if node.data == None]

    def find_settlements_on_tile(self, tile):
        settlements = []
        for node in self._hex_mesh.get_neighboring_nodes(tile):
            if type(node.data) == Settlement:
                settlements.append(node)
        return settlements

    def find_settlement_nodes(self, player_id):
        settlements = []
        for node in self._hex_mesh.nodes.values():
            data = node.data
            if type(data) == Settlement:
                if data.owner_id == player_id:
                    settlements.append(node)
        return settlements

    def find_legal_road_placements(self, player_id):
        legal_road_placements = []
        for edge in self._hex_mesh.edges.values():
            if edge.data == None:
                legal = False
                for e in self._hex_mesh.get_neighboring_edges(edge):
                    if type(e.data) == Road:
                        if e.data.owner_id == player_id:
                            legal = True
                            break
                for n in self._hex_mesh.get_neighboring_nodes(edge):
                    if type(n.data) == Settlement:
                        if n.data.owner_id == player_id:
                            legal = True
                            break
                if legal:
                    legal_road_placements.append(edge)
        return legal_road_placements
    
    def find_legal_settlement_placements(self, player_id):
        legal_settlement_placements = []
        for node in self._hex_mesh.nodes.values():
            if node.data == None:
                neighbor_settlements = 0
                legal = False
                for e1 in self._hex_mesh.get_neighboring_edges(node):
                    if type(e1.data) == Road:
                        if e1.data.owner_id == player_id:
                            legal = True
                            for n in self._hex_mesh.get_neighboring_nodes(e1):
                                if type(n.data) == Settlement:
                                    neighbor_settlements += 1
                if legal and neighbor_settlements == 0:
                    legal_settlement_placements.append(copy.copy(node))
        return legal_settlement_placements

    def build_road(self, coord, player):
        edge = self._hex_mesh.get_edge(coord)
        if edge.data == None:
            road = Road(player, coord)
            player.build_road(road)
            edge.data = road
            return road
        return None
        
    def build_settlement(self, coord, player):
        node = self._hex_mesh.get_node(coord)
        if node.data == None:
            settlement = Settlement(player, coord)
            player.build_settlement(settlement)
            node.data = settlement
            return settlement
        return None
    
    def upgrade_to_city(self, coord, player):
        node = self._hex_mesh.get_node(coord)
        if node.data != None and type(node.data) == Settlement:
            if node.data.player_id == player_id:
                city = City(player, coord)
                player.upgrade_to_city(node.data, city)
                node.data = city
                return city
        return None

    def __repr__(self):
        s = 'Board\n\n'
        s += 'Tiles:\n'
        for tile in self._hex_mesh.tiles.values():
            if type(tile.data) == CatanTile:
                s += f'Coord: {hex(tile.hex_code)} - {tile.data}\n'

        player_roads = {}
        player_settlements = {}
        player_cities = {}

        for edge in self._hex_mesh.edges.values():
            if type(edge.data) == Road:
                o_id = edge.data.owner_id
                if o_id not in player_roads:
                    player_roads[o_id] = []
                player_roads[o_id].append(edge.data)

        for node in self._hex_mesh.nodes.values():
            if type(node.data) == Settlement:
                o_id = node.data.owner_id
                if o_id not in player_settlements:
                    player_settlements[o_id] = []
                player_settlements[o_id].append(node.data)

        for node in self._hex_mesh.nodes.values():
            if type(node.data) == City:
                o_id = node.data.owner_id
                if o_id not in player_settlements:
                    player_cities[o_id] = []
                player_cities[o_id].append(node.data)

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
    print('Legal Roads')
    print(board.find_legal_road_placements(1))
    print('Legal Settlements')
    print(board.find_legal_settlement_placements(1))

    print('Buy Road 0x66')
    board.build_road(0x66, 1)
    print('Legal Roads')
    print(board.find_legal_road_placements(1))
    print('Legal Settlements')
    print(board.find_legal_settlement_placements(1))

    print('Buy Road 0x67')
    board.build_road(0x67, 1)
    print('Legal Roads')
    print(board.find_legal_road_placements(1))
    print('Legal Settlements')
    print(board.find_legal_settlement_placements(1))

    print('Buy Road 0x68')
    board.build_road(0x68, 1)
    print('Legal Roads')
    print(board.find_legal_road_placements(1))
    print('Legal Settlements')
    print(board.find_legal_settlement_placements(1))

    print('Buy Settlement 0x69')
    board.build_settlement(0x69, 1)
    print('Legal Roads')
    print(board.find_legal_road_placements(1))
    print('Legal Settlements')
    print(board.find_legal_settlement_placements(1))

    print(board)
