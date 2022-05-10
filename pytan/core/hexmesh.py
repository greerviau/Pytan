from enum import Enum
from collections import Counter
import numpy as np
import copy

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
    'N': -0x01,
    'NE': -0x11,
    'SE': -0x11,
    'S': +0x10,
    'SW': +0x00,
    'NW': +0x00
}

def direction_to_tile(offset):
    for key, value in TT_DIRS.items():
        if value == offset:
            return key
    return None

def tile_to_node_direction(offset):
    for key, value in TN_DIRS.items():
        if value == offset:
            return key
    return None

def tile_to_edge_direction(offset):
    for key, value in TE_DIRS.items():
        if value == offset:
            return key
    return None
    
class HexMesh(object):
    def __init__(self, n_layers=0):
        #Init
        self._n_layers = n_layers
        self._tiles = {}
        self._nodes = {}
        self._edges = {}

        next_tile = 0x11
        for n in range(n_layers, 0, -1):
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

        for tile in self._tiles:
            nodes = self.tile_neighboring_nodes(tile)
            for node in nodes:
                self._nodes[node] = None
            edges = self.tile_neighboring_edges(tile)
            for edge in edges:
                self._edges[edge] = None

    @property
    def tiles(self):
        return self._tiles
    
    @property
    def nodes(self):
        return self._nodes
    
    @property
    def edges(self):
        return self._edges

    def hex_digits(self, coord):
        h = hex(coord)
        d1 = int(h[2], 16)
        d2 = 0
        try:
            d2 = int(h[3], 16)
        except IndexError:
            d2 = d1
            d1 = 0
        return d1, d2
    
    def tile_neighboring_tiles(self, tile_coord):
        tile = []
        for d in TT_DIRS.values():
            tile.append(tile_coord + d)

    def tile_neighboring_nodes(self, tile_coord):
        nodes = []
        for d in TN_DIRS.values():
            nodes.append(tile_coord + d)

        return nodes

    def tile_neighboring_edges(self, tile_coord):
        edges = []
        for d in TE_DIRS.values():
            edges.append(tile_coord + d)

        return edges

    def node_neighboring_tiles(self, node_coord):
        tiles = []
        d1, d2 = self.hex_digits(node_coord)
        if d2 % 2 == 0:
            tiles.append(node_coord + NT_DIRS['NE'])
            tiles.append(node_coord + NT_DIRS['S'])
            tiles.append(node_coord + NT_DIRS['NW'])
        else:
            tiles.append(node_coord + NT_DIRS['N'])
            tiles.append(node_coord + NT_DIRS['SE'])
            tiles.append(node_coord + NT_DIRS['SW'])

        return self.confirm_tiles_exist(tiles)

    def node_neighboring_nodes(self, node_coord):
        nodes = []
        d1, d2 = self.hex_digits(node_coord)
        if d2 % 2 == 0:
            node.append(node_coord + NN_DIRS['N'])
            node.append(node_coord + NN_DIRS['SE'])
            node.append(node_coord + NN_DIRS['SW'])
        else:
            node.append(node_coord + NN_DIRS['NE'])
            node.append(node_coord + NN_DIRS['S'])
            node.append(node_coord + NN_DIRS['NW'])

        return self.confirm_nodes_exist(nodes)

    def node_neighboring_edges(self, node_coord):
        edges = []
        d1, d2 = self.hex_digits(node_coord)
        if d2 % 2 == 0:
            edges.append(node_coord + NE_DIRS['N'])
            edges.append(node_coord + NE_DIRS['SE'])
            edges.append(node_coord + NE_DIRS['SW'])
        else:
            edges.append(node_coord + NE_DIRS['NE'])
            edges.append(node_coord + NE_DIRS['S'])
            edges.append(node_coord + NE_DIRS['NW'])

        return self.confirm_edges_exist(edges)

    def edge_neighboring_tiles(self, edge_coord):
        tiles = []
        d1, d2 = self.hex_digits(edge_coord)
        if d1 % 2 == 0 and d2 % 2 == 0:
            tiles.append(edge_coord + ET_DIRS['E'])
            tiles.append(edge_coord + ET_DIRS['W'])
        if d1 % 2 == 0:
            tiles.append(edge_coord + ET_DIRS['SE'])
            tiles.append(edge_coord + ET_DIRS['NW'])
        else:
            tiles.append(edge_coord + ET_DIRS['NE'])
            tiles.append(edge_coord + ET_DIRS['SW'])

        return self.confirm_tiles_exist(tiles)

    def edge_neighboring_nodes(self, edge_coord):
        nodes = []
        d1, d2 = self.hex_digits(edge_coord)
        if d1 % 2 == 0 and d2 % 2 == 0:
            nodes.append(edge_coord + EN_DIRS['N'])
            nodes.append(edge_coord + EN_DIRS['S'])
        if d1 % 2 == 0:
            nodes.append(edge_coord + EN_DIRS['NE'])
            nodes.append(edge_coord + EN_DIRS['SW'])
        else:
            nodes.append(edge_coord + EN_DIRS['SE'])
            nodes.append(edge_coord + EN_DIRS['NW'])

        return self.confirm_nodes_exist(nodes)
    
    def edge_neighboring_edges(self, edge_coord):
        edges = []
        d1, d2 = self.hex_digits(edge_coord)
        if d1 % 2 == 0 and d2 % 2 == 0:
            edges.append(edge_coord + EE_DIRS['NE'])
            edges.append(edge_coord + EE_DIRS['SE'])
            edges.append(edge_coord + EE_DIRS['SW'])
            edges.append(edge_coord + EE_DIRS['NW'])
        if d1 % 2 == 0:
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

    def get_nearest_tile_to_node(self, node_coord):
        tiles = self.node_neighboring_tiles(node_coord)
        return list(tiles.keys())[0] 

    def get_nearest_tile_to_edge(self, edge_coord):
        tiles = self.edge_neighboring_tiles(edge_coord)
        return list(tiles.keys())[0] 

    def confirm_tiles_exist(self, tiles):
        return {tile: self.try_get_value(self._tiles, tile) for tile in tiles}

    def confirm_nodes_exist(self, nodes):
        return {node: self.try_get_value(self._nodes, node) for node in nodes}

    def confirm_edges_exist(self, edges):
        return {edge: self.try_get_value(self._edges, edge) for edge in edges}

    def try_get_value(self, hmap, key):
        try:
            return hmap[key]
        except KeyError:
            pass

    def __repr__(self):
        s = f'Mesh - N_Tiles: {self._n_tiles} - N_Layers: {self._n_layers}\n'
        for i, (coord, tile) in enumerate(self._tiles.items()):
            s += f'Tile {i+1} - {coord}:{tile}\n'
        return s