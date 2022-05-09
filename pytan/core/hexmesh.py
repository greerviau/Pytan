from enum import Enum
from collections import Counter
import numpy as np
import copy

class TTDirs(Enum):
    NORTHEAST = +0x02
    EAST = +0x22
    SOUTHEAST = +0x20
    SOUTHWEST = -0x02
    WEST = -0x22
    NORTHWEST = -0x20

class TEDirs(Enum):
    NORTHEAST = +0x01
    EAST = +0x11
    SOUTHEAST = +0x10
    SOUTHWEST = -0x01
    WEST = -0x11
    NORTHWEST = -0x10

class TNDirs(Enum):
    NORTH = +0x01
    NORTHEAST = +0x12
    SOUTHEAST = +0x21
    SOUTH = +0x10
    SOUTHWEST = -0x01
    NORTHWEST = -0x10

class NNDirs(Enum):
    NORTH = -0x0f
    NORTHEAST = +0x11
    SOUTHEAST = +0x11
    SOUTH = +0x0f
    SOUTHWEST = -0x11
    NORTHWEST = -0x11

class NTDirs(Enum):
    NORTH = -0x10
    NORTHEAST = +0x01
    SOUTHEAST = +0x10
    SOUTH = -0x01
    SOUTHWEST = -0x12
    NORTHWEST = -0x21

class NEDirs(Enum):
    NORTH = -0x10
    NORTHEAST = +0x00
    SOUTHEAST = +0x00
    SOUTH = -0x01
    SOUTHWEST = -0x11
    NORTHWEST = -0x11

class EEDirs(Enum):
    NORTHEAST = +0x01
    EAST = +0x11
    SOUTHEAST = +0x10
    SOUTHWEST = -0x01
    WEST = -0x11
    NORTHWEST = -0x10

class ETDirs(Enum):
    NORTHEAST = +0x01
    EAST = +0x11
    SOUTHEAST = +0x10
    SOUTHWEST = -0x01
    WEST = -0x11
    NORTHWEST = -0x10

class ENDirs(Enum):
    NORTH = +0x01
    NORTHEAST = +0x11
    SOUTHEAST = +0x11
    SOUTH = +0x10
    SOUTHWEST = +0x00
    NORTHWEST = +0x00

class HexObject(object):
    def __init__(self, hex_code, direction, data):
        self._hex_code = hex_code
        self._direction = direction
        self._data = data

    @property
    def hex_code(self):
        return self._hex_code

    @property
    def direction(self):
        return self._direction

    @property
    def data(self):
        return self._data

    @direction.setter
    def direction(self, d):
        self._direction = d

    @data.setter
    def data(self, d):
        self._data = d

    @staticmethod
    def get_unique_hex_map(hex_objs):
        u = {}
        for h in hex_objs:
            if h.hex_code not in u:
                h_copy = copy.copy(h)
                h_copy.direction = None
                u[h.hex_code] = h_copy
        return u

    def __repr__(self):
        return f'Hex: {hex(self._hex_code)}  \tDirection: {self._direction}  \tData: {str(self._data)}\n'

class Node(HexObject):
    def __init__(self, hex_code, direction, data = None):
        #Init
        super().__init__(hex_code, direction, data)

        self._node_node_directions = []
        self._node_edge_directions = []
        self._node_tile_directions = []

        if direction == TNDirs.NORTH or direction == TNDirs.SOUTHEAST or direction == TNDirs.SOUTHWEST:
            self._node_node_directions = [ NNDirs.NORTH, NNDirs.SOUTHEAST, NNDirs.SOUTHWEST ]
            self._node_edge_directions = [ NEDirs.NORTH, NEDirs.SOUTHEAST, NEDirs.SOUTHWEST ]
            self._node_tile_directions = [ NTDirs.NORTHEAST, NTDirs.SOUTH, NTDirs.NORTHWEST ]
        elif direction == TNDirs.NORTHEAST or direction == TNDirs.NORTHWEST or direction == TNDirs.SOUTH:
            self._node_node_directions = [ NNDirs.NORTHEAST, NNDirs.NORTHWEST, NNDirs.SOUTH ]
            self._node_edge_directions = [ NEDirs.NORTHEAST, NEDirs.NORTHWEST, NEDirs.SOUTH ]
            self._node_tile_directions = [ NTDirs.NORTH, NTDirs.SOUTHEAST, NTDirs.SOUTHWEST ]

    @property
    def neighboring_nodes(self):
        return [n.value + self._hex_code for n in self._node_node_directions]

    @property
    def neighboring_edges(self):
        return [e.value + self._hex_code for e in self._node_edge_directions]

    @property
    def neighboring_tiles(self):
        return [t.value + self._hex_code for t in self._node_tile_directions]

class Edge(HexObject):
    def __init__(self, hex_code, direction, data = None):
        #Init
        super().__init__(hex_code, direction, data)
        
        self._edge_edge_directions = []
        self._edge_node_directions = []
        self._edge_tile_directions = []

        if direction == TEDirs.NORTHEAST or direction == TEDirs.SOUTHWEST:
            self._edge_edge_directions = [ EEDirs.EAST, EEDirs.SOUTHEAST, EEDirs.WEST, EEDirs.NORTHWEST ]
            self._edge_node_directions = [ ENDirs.SOUTHEAST, ENDirs.NORTHWEST ]
            self._edge_tile_directions = [ ENDirs.NORTHEAST, ENDirs.SOUTHWEST ]
        elif direction == TEDirs.EAST or direction == TEDirs.WEST:
            self._edge_edge_directions = [ EEDirs.NORTHEAST, EEDirs.SOUTHEAST, EEDirs.SOUTHWEST, EEDirs.NORTHWEST ]
            self._edge_node_directions = [ ENDirs.NORTH, ENDirs.SOUTH ]
            self._edge_tile_directions = [ ETDirs.EAST, ETDirs.WEST ]
        elif direction == TEDirs.NORTHWEST or direction == TEDirs.SOUTHEAST:
            self._edge_edge_directions = [ EEDirs.NORTHEAST, EEDirs.EAST, EEDirs.SOUTHWEST, EEDirs.WEST ]
            self._edge_node_directions = [ ENDirs.NORTHEAST, ENDirs.SOUTHWEST ]
            self._edge_tile_directions = [ ETDirs.SOUTHEAST, ETDirs.NORTHWEST ]

    @property
    def neighboring_nodes(self):
        return [n.value + self._hex_code for n in self._edge_node_directions]

    @property
    def neighboring_edges(self):
        return [e.value + self._hex_code for e in self._edge_edge_directions]

    @property
    def neighboring_tiles(self):
        return [t.value + self._hex_code for t in self._edge_tile_directions]

class Tile(HexObject):
    def __init__(self, hex_code, data = None):
        #Init
        super().__init__(hex_code, None, data)
        self._nodes = []
        self._edges = []
        for d in TNDirs:
            self._nodes.append(Node(self._hex_code + d.value, d))
        
        for d in TEDirs:
            self._edges.append(Edge(self._hex_code + d.value, d))

    @property
    def nodes(self):
        return self._nodes

    @property
    def edges(self):
        return self._edges

    @property
    def neighboring_tiles(self):
        return [d.value + self._hex_code for d in TTDirs]

    @property
    def neighboring_nodes(self):
        return [n.hex_code for n in self._nodes]

    @property
    def get_edges(self):
        return [e.hex_code for e in self._edges]
    
    def __repr__(self):
        s = f'Hex: {hex(self._hex_code)} - Data: {self._data}\n'
        s += 'Nodes:\n'
        for i, n in enumerate(self._nodes):
            s += f'\t{n}'
        s += 'Edges:\n'
        for i, e in enumerate(self._edges):
            s += f'\t{e}'
        return s

    
class HexMesh(object):
    def __init__(self, n_layers=0):
        #Init
        self._n_layers = n_layers
        self._tiles = {}

        next_tile = 0x11
        for n in range(n_layers, 0, -1):
            self._tiles[next_tile] = Tile(next_tile)
            for d in TTDirs:
                r = n
                if d == TTDirs.NORTHWEST:
                    r -= 1
                for i in range(r):
                    next_tile += d.value
                    self._tiles[next_tile] = Tile(next_tile)
            next_tile += TTDirs.NORTHEAST.value
        self._tiles[next_tile] = Tile(next_tile)

        self._tiles = dict(reversed(list(self._tiles.items())))

        self._n_tiles = len(self._tiles)

        nodes = []
        edges = []
        for tile in self._tiles.values():
            nodes.extend(tile.nodes)
            edges.extend(tile.edges)

        self._nodes = HexObject.get_unique_hex_map(nodes)
        self._edges = HexObject.get_unique_hex_map(edges)

    @property
    def tiles(self):
        return self._tiles
    
    @property
    def nodes(self):
        return self._nodes
    
    @property
    def edges(self):
        return self._edges

    @property
    def n_tiles(self):
        return self._n_tiles

    @property
    def n_layers(self):
        return self._n_layers

    def get_tile(self, hex_code):
        return self._tiles[hex_code]

    def get_node(self, hex_code):
        return self._nodes[hex_code]

    def get_edge(self, hex_code):
        return self._edges[hex_code]

    def try_get_value(self, hmap, key):
        try:
            return hmap[key]
        except KeyError:
            pass

    '''
    TILE HELPER FUNCTIONS
    '''

    # TILES NEIGHBORING TILES
    def get_neighboring_tiles_from_tile(self, hex_code):
        tile = self._tiles[hex_code]
        return self.get_neighboring_tiles(tile.hex_code)

    def get_neighboring_tiles(self, tile: Tile):
        return [self.try_get_value(self._tiles, t) for t in tile.neigboring_tiles if self.try_get_value(self._tiles, t)]

    # TILES NEIGHBORING NODES
    def get_neighboring_nodes_from_tile(self, hex_code):
        tile = self._tiles[hex_code]
        return self.get_neighboring_nodes(tile.hex_code)

    def get_neighboring_nodes(self, tile: Tile):
        return [self.try_get_value(self._nodes, n) for n in tile.neighboring_nodes if self.try_get_value(self._nodes, n)]

    # TILES NEIGHBORING EDGES
    def get_neighboring_edges_from_tile(self, hex_code):
        tile = self._tiles[hex_code]
        return self.get_neighboring_edges(tile)

    def get_neighboring_edges(self, tile: Tile):
        return [self.try_get_value(self._edges, e) for e in tile.neighboring_edges if self.try_get_value(self._edges, e)]

    '''
    NODE HELPER FUNCTIONS
    '''

    # NODES NEIGHBORING TILES
    def get_neighboring_tiles_from_node(self, hex_code):
        node = self._nodes[hex_code]
        return self.get_neighboring_tiles(node)

    def get_neighboring_tiles(self, node: Node):
        return [self.try_get_value(self._tiles, t) for t in node.neighboring_tiles if self.try_get_value(self._tiles, t)]

    # NODES NEIGHBORING NODES
    def get_neighboring_nodes_from_node(self, hex_code):
        node = self._nodes[hex_code]
        return self.get_neighboring_nodes(node)

    def get_neighboring_nodes(self, node: Node):
        return [self.try_get_value(self._nodes, n) for n in node.neighboring_nodes if self.try_get_value(self._nodes, n)]

    # NODES NEIGHBORING EDGES
    def get_neighboring_edges_from_node(self, hex_code):
        node = self._nodes[hex_code]
        return self.get_neighboring_edges(node)

    def get_neighboring_edges(self, node: Node):
        return [self.try_get_value(self._edges, e) for e in node.neighboring_edges if self.try_get_value(self._edges, e)]

    '''
    EDGE HELPER FUNCTIONS
    '''

    # EDGES NEIGHBORING TILES
    def get_neighboring_tiles_from_edge(self, hex_code):
        edge = self._edges[hex_code]
        return self.get_neighboring_tiles_from_edge(edge)

    def get_neighboring_tiles(self, edge: Edge):
        return [self.try_get_value(self._tiles, t) for t in edge.neighboring_tiles if self.try_get_value(self._tiles, t)]

    # EDGES NEIGHBORING NODES
    def get_neighboring_nodes_from_edge(self, hex_code):
        edge = self._edges[hex_code]
        return self.get_neighboring_nodes_from_edge(edge) 

    def get_neighboring_nodes(self, edge: Edge):
        return [self.try_get_value(self._nodes, n) for n in edge.neighboring_nodes if self.try_get_value(self._nodes, n)]

    # EDGES NEIGHBORING EDGES
    def get_neighboring_edges_from_edge(self, hex_code):
        edge = self._edges[hex_code]
        return self.get_neighboring_edges_from_edge(edge)

    def get_neighboring_edges(self, edge: Edge):
        return [self.try_get_value(self._edges, e) for e in edge.neighboring_edges if self.try_get_value(self._edges, e)]

    '''
    END HELPER FUNCTIONS
    '''

    def __repr__(self):
        s = f'Mesh - N_Tiles: {self._n_tiles} - N_Layers: {self._n_layers}\n'
        for i, tile in enumerate(self._tiles.values()):
            s += f'Tile {i+1} - {tile}\n'
        return s

if __name__ == '__main__':
    mesh = HexMesh(n_layers = 3)
    #print(f'{len(mesh.edges)} Edges')
    #print(mesh.edges.values())
    #tile = mesh.get_tile(0x57)
    #print(tile)
    node = mesh.get_node(0x67)
    print(node)
    print(node.neighboring_edges)
    print(mesh.get_neighboring_edges(node))
    #edge = mesh.get_edge(0x07)
    #print(edge)
    #print(mesh.get_neighboring_edges(edge))