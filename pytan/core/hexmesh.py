from enum import Enum

class Directions(Enum):
    N = 'N'
    NE = 'NE'
    E = 'E'
    SE = 'SE'
    S = 'S'
    SW = 'SW'
    W = 'W'
    NW = 'NW'

TT_DIRS = {
    'NE': +0x02,
    'E': +0x22,
    'SE': +0x20,
    'SW': -0x02,
    'W': -0x22,
    'NW': -0x20
}

TN_DIRS= {
    'N': +0x01,
    'NE': +0x12,
    'SE': +0x21,
    'S': +0x10,
    'SW': -0x01,
    'NW': -0x10
}

TE_DIRS = {
    'NE': +0x01,
    'E': +0x11,
    'SE': +0x10,
    'SW': -0x01,
    'W': -0x11,
    'NW': -0x10
}

NN_DIRS = {
    'N': -0x0f,
    'NE': +0x11,
    'SE': +0x11,
    'S': +0x0f,
    'SW': -0x11,
    'NW': -0x11
}

NT_DIRS = {
    'N': -0x10,
    'NE': +0x01,
    'SE': +0x10,
    'S': -0x01,
    'SW': -0x12,
    'NW': -0x21
}

NE_DIRS = {
    'N': -0x10,
    'NE': +0x00,
    'SE': +0x00,
    'S': -0x01,
    'SW': -0x11,
    'NW': -0x11
}

EE_DIRS = {
    'NE': +0x01,
    'E': +0x11,
    'SE': +0x10,
    'SW': -0x01,
    'W': -0x11,
    'NW': -0x10
}

ET_DIRS = {
    'NE': +0x01,
    'E': +0x11,
    'SE': +0x10,
    'SW': -0x01,
    'W': -0x11,
    'NW': -0x10
}

EN_DIRS = {
    'N': +0x01,
    'NE': +0x11,
    'SE': +0x11,
    'S': +0x10,
    'SW': +0x00,
    'NW': +0x00
}

def direction_to_tile(tile_1_coord: int, tile_2_coord: int) -> Directions:
    offset = tile_2_coord - tile_1_coord
    for key, value in TT_DIRS.items():
        if value == offset:
            return Directions(key)
    return None

def tile_to_node_direction(tile_coord: int, node_coord: int) -> Directions:
    offset = node_coord - tile_coord
    for key, value in TN_DIRS.items():
        if value == offset:
            return Directions(key)
    return None

def tile_to_edge_direction(tile_coord: int, edge_coord: int) -> Directions:
    offset = edge_coord - tile_coord
    for key, value in TE_DIRS.items():
        if value == offset:
            return Directions(key)
    return None

def node_in_direction(tile_coord: int, direction: Directions) -> int:
    return tile_coord + TN_DIRS[direction.value]

def edge_in_direction(tile_coord: int, direction: Directions) -> int:
    return tile_coord + TE_DIRS[direction.value]

def hex_digits(coord: int) -> tuple[int, int]:
    h = hex(coord).replace('0x', '')
    d1 = int(h[0], 16)
    d2 = 0
    try:
        d2 = int(h[1], 16)
    except IndexError:
        d2 = d1
        d1 = 0
    return d1, d2

def tile_neighboring_tiles(tile_coord: int) -> list[int]:
    tiles = []
    for d in TT_DIRS.values():
        tiles.append(tile_coord + d)
    return tiles

def tile_neighboring_nodes(tile_coord: int) -> list[int]:
    nodes = []
    for d in TN_DIRS.values():
        nodes.append(tile_coord + d)
    return nodes

def tile_neighboring_edges(tile_coord: int) -> list[int]:
    edges = []
    for d in TE_DIRS.values():
        edges.append(tile_coord + d)
    return edges
    
class HexMesh(object):
    def __init__(self, n_layers: int = 0):
        #Init
        self._n_layers = n_layers
        self._init_tiles()
        self.init_nodes()
        self.init_edges()

    def _init_tiles(self):
        self._tiles = {}

        next_tile = 0x11
        for n in range(self._n_layers, 0, -1):
            self._tiles[next_tile] = None
            for d in TT_DIRS.values():
                r = n
                if d == TT_DIRS['NW']:
                    r -= 1
                for i in range(r):
                    next_tile += d
                    self._tiles[next_tile] = None
            next_tile += TT_DIRS['NE']
        self._tiles[next_tile] = None

        self._tiles = dict(reversed(list(self._tiles.items())))

        self._n_tiles = len(self._tiles)

    def init_nodes(self):
        self._nodes = {}
        for tile in self._tiles:
            nodes = tile_neighboring_nodes(tile)
            for node in nodes:
                self._nodes[node] = None

    def init_edges(self):
        self._edges = {}
        for tile in self._tiles:
            edges = tile_neighboring_edges(tile)
            for edge in edges:
                self._edges[edge] = None
    @property
    def tile_matrix_coords(self):
        return self._tile_matrix_coords
        
    @property
    def n_layers(self) -> int:
        return self._n_layers

    @property
    def tiles(self) -> dict[int, None]:
        return self._tiles
    
    @property
    def nodes(self) -> dict[int, None]:
        return self._nodes
    
    @property
    def edges(self) -> dict[int, None]:
        return self._edges
    
    @property
    def empty_nodes(self) -> list[int]:
        return [coord for coord, node in self._nodes.items() if node is None]

    @property
    def empty_edges(self) -> list[int]:
        return [coord for coord, edge in self._edges.items() if edge is None]

    @property
    def occupied_nodes(self) -> dict[int, None]:
        return {coord: node for coord, node in self._nodes.items() if node is not None}

    @property
    def occupied_edges(self) -> dict[int, None]:
        return {coord: edge for coord, edge in self._edges.items() if edge is not None}

    @property
    def edge_tiles(self) -> dict[int, None]:
        n = self._n_layers * 6
        return {k: self._tiles[k] for k in list(reversed(list(self._tiles.keys())[-n:]))}

    def tile_neighboring_tiles(self, tile_coord: int) -> list[int]:
        return tile_neighboring_tiles(tile_coord)

    def tile_neighboring_nodes(self, tile_coord: int) -> list[int]:
        return tile_neighboring_nodes(tile_coord)

    def tile_neighboring_edges(self, tile_coord: int) -> list[int]:
        return tile_neighboring_edges(tile_coord)

    def node_neighboring_tiles(self, node_coord: int) -> dict[int, None]:
        tiles = []
        d1, d2 = hex_digits(node_coord)
        if d2 % 2 == 0:
            tiles.append(node_coord + NT_DIRS['NE'])
            tiles.append(node_coord + NT_DIRS['S'])
            tiles.append(node_coord + NT_DIRS['NW'])
        else:
            tiles.append(node_coord + NT_DIRS['N'])
            tiles.append(node_coord + NT_DIRS['SE'])
            tiles.append(node_coord + NT_DIRS['SW'])

        return self.confirm_tiles_exist(tiles)

    def node_neighboring_nodes(self, node_coord: int) -> dict[int, None]:
        nodes = []
        d1, d2 = hex_digits(node_coord)
        if d2 % 2 == 0:
            nodes.append(node_coord + NN_DIRS['N'])
            nodes.append(node_coord + NN_DIRS['SE'])
            nodes.append(node_coord + NN_DIRS['SW'])
        else:
            nodes.append(node_coord + NN_DIRS['NE'])
            nodes.append(node_coord + NN_DIRS['S'])
            nodes.append(node_coord + NN_DIRS['NW'])

        return self.confirm_nodes_exist(nodes)

    def node_neighboring_edges(self, node_coord: int) -> dict[int, None]:
        edges = []
        d1, d2 = hex_digits(node_coord)
        if d2 % 2 == 0:
            edges.append(node_coord + NE_DIRS['N'])
            edges.append(node_coord + NE_DIRS['SE'])
            edges.append(node_coord + NE_DIRS['SW'])
        else:
            edges.append(node_coord + NE_DIRS['NE'])
            edges.append(node_coord + NE_DIRS['S'])
            edges.append(node_coord + NE_DIRS['NW'])

        return self.confirm_edges_exist(edges)

    def edge_neighboring_tiles(self, edge_coord: int) -> dict[int, None]:
        tiles = []
        d1, d2 = hex_digits(edge_coord)
        if d1 % 2 == 0 and d2 % 2 == 0:
            tiles.append(edge_coord + ET_DIRS['E'])
            tiles.append(edge_coord + ET_DIRS['W'])
        elif d1 % 2 == 0:
            tiles.append(edge_coord + ET_DIRS['SE'])
            tiles.append(edge_coord + ET_DIRS['NW'])
        else:
            tiles.append(edge_coord + ET_DIRS['NE'])
            tiles.append(edge_coord + ET_DIRS['SW'])

        return self.confirm_tiles_exist(tiles)

    def edge_neighboring_nodes(self, edge_coord: int) -> dict[int, None]:
        nodes = []
        d1, d2 = hex_digits(edge_coord)
        if d1 % 2 == 0 and d2 % 2 == 0:
            nodes.append(edge_coord + EN_DIRS['N'])
            nodes.append(edge_coord + EN_DIRS['S'])
        elif d1 % 2 == 0:
            nodes.append(edge_coord + EN_DIRS['NE'])
            nodes.append(edge_coord + EN_DIRS['SW'])
        else:
            nodes.append(edge_coord + EN_DIRS['SE'])
            nodes.append(edge_coord + EN_DIRS['NW'])

        return self.confirm_nodes_exist(nodes)
    
    def edge_neighboring_edges(self, edge_coord: int) -> dict[int, None]:
        edges = []
        d1, d2 = hex_digits(edge_coord)
        if d1 % 2 == 0 and d2 % 2 == 0:
            edges.append(edge_coord + EE_DIRS['NE'])
            edges.append(edge_coord + EE_DIRS['SE'])
            edges.append(edge_coord + EE_DIRS['SW'])
            edges.append(edge_coord + EE_DIRS['NW'])
        elif d1 % 2 == 0:
            edges.append(edge_coord + EE_DIRS['NE'])
            edges.append(edge_coord + EE_DIRS['E'])
            edges.append(edge_coord + EE_DIRS['SW'])
            edges.append(edge_coord + EE_DIRS['W'])
        else:
            edges.append(edge_coord + EE_DIRS['E'])
            edges.append(edge_coord + EE_DIRS['SE'])
            edges.append(edge_coord + EE_DIRS['W'])
            edges.append(edge_coord + EE_DIRS['NW'])
        return self.confirm_edges_exist(edges)

    def nearest_tile_to_node(self, node_coord: int) -> int:
        tiles = self.node_neighboring_tiles(node_coord)
        tile_coords = list(tiles.keys())
        return list(self.confirm_tiles_exist(tile_coords).keys())[0] 

    def nearest_tile_to_edge(self, edge_coord: int) -> int:
        tiles = self.edge_neighboring_tiles(edge_coord)
        tile_coords = list(tiles.keys())
        return list(self.confirm_tiles_exist(tile_coords).keys())[0] 

    def confirm_tiles_exist(self, tiles: list[int]) -> dict[int, None]:
        return {tile: self._tiles[tile] for tile in tiles if tile in self._tiles}

    def confirm_nodes_exist(self, nodes: list[int]) -> dict[int, None]:
        return {node: self._nodes[node] for node in nodes if node in self._nodes}

    def confirm_edges_exist(self, edges: list[int]) -> dict[int, None]:
        return {edge: self._edges[edge] for edge in edges if edge in self._edges}

    def __repr__(self):
        s = f'Mesh - N_Tiles: {self._n_tiles} - N_Layers: {self._n_layers}\n'
        for i, (coord, tile) in enumerate(self._tiles.items()):
            s += f'Tile {i+1} - {coord}:{tile}\n'
        return s