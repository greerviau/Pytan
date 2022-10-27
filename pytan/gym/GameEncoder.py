import numpy as np 
import math
import matplotlib.pyplot as plt
from pytan.core import hexmesh
from pytan.core.hexmesh import Directions
from pytan.core.game import Game
from pytan.core.board import Board

TILE_DIRECTION_TO_COORD_OFFSET = {
    Directions.NE: (-2, 2),
    Directions.E: (0, 4),
    Directions.SE: (2, 2),
    Directions.SW: (2, -2),
    Directions.W: (0, -4),
    Directions.NW: (-2, -2),
}

NODE_DIRECTION_TO_COORD_OFFSET = {
    Directions.N: (-1, 0),
    Directions.NE: (-1, 2),
    Directions.SE: (1, 2),
    Directions.S: (1, 0),
    Directions.SW: (1, -2),
    Directions.NW: (-1, -2)
}

EDGE_DIRECTION_TO_COORD_OFFSET = {
    Directions.NE: (-1, 1),
    Directions.E: (0, 2),
    Directions.SE: (1, 1),
    Directions.SW: (1, -1),
    Directions.W: (0, -2),
    Directions.NW: (-1, -1)
}

g_game = None
shape = (0,0)
tile_matrix_coords = {}
node_matrix_coords = {}
edge_matrix_coords = {}
tile_matrix = None
node_matrix = None
edge_matrix = None

def calculate_tile_matrix_shape(layers: int) -> tuple[int, int]:
    w = 5 + (8 * layers)
    h = 3 + (4 * layers)
    return h, w

def calculate_tile_matrix_coords(board: Board):
    tmc = {}
    h, w = calculate_tile_matrix_shape(board.n_layers)
    last_tile = 0x00
    for tile in board.tiles:
        if last_tile == 0x00:
            tmc[tile] = (h // 2, w //2)
        else:
            direction = hexmesh.direction_to_tile(last_tile, tile)
            last_coord = tmc[last_tile]
            offset = TILE_DIRECTION_TO_COORD_OFFSET[direction]
            tmc[tile] = tuple(map(lambda i, j: i + j, last_coord, offset))
        last_tile = tile
    return tmc

def init_coords(board: Board):
    global tile_matrix_coords, node_matrix_coords, edge_matrix_coords
    tile_matrix_coords = calculate_tile_matrix_coords(board)
    for t_coord, m_coord in tile_matrix_coords.items():
        for node in hexmesh.tile_neighboring_nodes(t_coord):
            direction = hexmesh.tile_to_node_direction(t_coord, node)
            offset = NODE_DIRECTION_TO_COORD_OFFSET[direction]
            node_matrix_coords[node] = tuple(map(lambda i, j: i + j, m_coord, offset))
        for edge in hexmesh.tile_neighboring_edges(t_coord):
            direction = hexmesh.tile_to_edge_direction(t_coord, edge)
            offset = EDGE_DIRECTION_TO_COORD_OFFSET[direction]
            edge_matrix_coords[edge] = tuple(map(lambda i, j: i + j, m_coord, offset))
        
def init_encoder(game: Game):
    global g_game, tile_matrix, node_matrix, edge_matrix, shape, tile_matrix_coords
    g_game = game
    shape = calculate_tile_matrix_shape(game.board.n_layers)
    init_coords(game.board)
    tile_matrix = np.zeros(shape)
    for t_coord, m_coord in tile_matrix_coords.items():
        tile = game.board.tiles[t_coord]
        v = round(tile.prob / 12, 2)
        tile_matrix[m_coord] = v
        tile_matrix[(m_coord[0], m_coord[1]-1)] = v
        tile_matrix[(m_coord[0], m_coord[1]+1)] = v
    tile_matrix = np.expand_dims(tile_matrix, axis=0)
    print(tile_matrix.shape)
    n_players = len(game.players)
    node_matrix = np.zeros((n_players, *shape))
    print(node_matrix.shape)
    edge_matrix = np.zeros((n_players, *shape))

def encoding() -> np.ndarray:
    return np.concatenate([tile_matrix, node_matrix, edge_matrix], axis=0)
    
def visualize_tiles():
    fig, ax = plt.subplots()
    ax.matshow(np.squeeze(tile_matrix, axis=0), cmap='ocean')

    plt.show()