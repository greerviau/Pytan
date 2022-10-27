from pytan.core import hexmesh
from pytan.core.piece import PieceTypes, Piece, place_piece
from pytan.core.ports import PortTypes, Port, PORT_TYPE_COUNTS
from pytan.core.tiles import *
from pytan.core.player import Player
import random
import copy

class Board(hexmesh.HexMesh):
    def __init__(self, seed: float = random.random()):
        super().__init__(n_layers = 2)
        self._prng = random.Random()
        self.set_seed(seed)
        self.reset()
        
    def reset(self):
        self.init_nodes()
        self.init_edges()

    def set_seed(self, seed: int):
        self._seed = seed
        self._prng.seed(self._seed)
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
            tile_choice = self._prng.choice(available_tiles)
            available_tiles.remove(tile_choice)
            tile_type = tile_choice
            
            prob = 7
            if tile_type != TileTypes.DESERT:
                prob = self._prng.choice(available_probs)
                available_probs.remove(prob)
            else:
                self._robber = place_piece(coord, -1, '', 'black', PieceTypes.ROBBER)

            self._tiles[coord] = CatanTile(coord, prob, tile_type, PROB_TO_PROD[prob])

    def setup_ports(self, rotate: int = 0):
        self._ports = {}
        edge_tiles = list(self.edge_tiles.keys())
        for i in range(rotate):
            edge_tiles.append(edge_tiles.pop(0))

        available_ports = []
        for port_type in PORT_TYPE_COUNTS:
            for _ in range(PORT_TYPE_COUNTS[port_type]):
                available_ports.append(port_type)

        directions = [hexmesh.Directions.NE, hexmesh.Directions.E, hexmesh.Directions.SE, hexmesh.Directions.SW, hexmesh.Directions.W, hexmesh.Directions.NW]
        
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
                port_type = self._prng.choice(available_ports)
                available_ports.remove(port_type)
                self._ports[tile] = Port(node1, node2, tile, port_dir, port_type)

            j += 1

    @property
    def roads(self) -> dict[int, Piece]:
        return {coord: edge for coord, edge in self._edges.items() if type(edge) == Piece and edge.piece_type == PieceTypes.ROAD}

    @property
    def settlements(self) -> dict[int, Piece]:
        return {coord: node for coord, node in self._nodes.items() if type(node) == Piece and node.piece_type == PieceTypes.SETTLEMENT}

    @property
    def cities(self) -> dict[int, Piece]:
        return {coord: node for coord, node in self._nodes.items() if type(node) == Piece and node.piece_type == PieceTypes.CITY}

    @property
    def ports(self) -> dict[int, Port]:
        return self._ports

    @property
    def robber(self) -> Piece:
        return self._robber

    def is_player_on_port(self, player_id: int, port_type: PortTypes) -> bool:
        for port in self._ports.values():
            if port.port_type == port_type:
                p1 = self._nodes[port.coord_1]
                p2 = self._nodes[port.coord_2]
                if (type(p1) == Piece and p1.owner_id == player_id) or (type(p2) == Piece  and p2.owner_id == player_id):
                    return True
        return False

    def is_player_on_tile(self, tile_coord: int, player_id: int) -> bool:
        for node_coord in self.tile_neighboring_nodes(tile_coord):
            node = self._nodes[node_coord]
            if type(node) == Piece:
                if player_id == node.owner_id:
                    return True
        return False

    def legal_robber_placements(self) -> list[int]:
        return [coord for coord, tile in self._tiles.items() if coord != self._robber.coord]

    def move_robber(self, coord: int):
        self._robber = place_piece(coord, -1, '', 'black', PieceTypes.ROBBER)

    def tiles_with_prob(self, prob: int) -> dict[int, CatanTile]:
        return {coord: tile for coord, tile in self._tiles.items() if type(tile) == CatanTile and tile.prob == prob}

    def players_on_tile(self, tile_coord: int) -> list[int]:
        player_ids = set()
        for node_coord in self.tile_neighboring_nodes(tile_coord):
            node = self._nodes[node_coord]
            if type(node) == Piece:
                player_ids.add(node.owner_id)
        return list(player_ids)

    def settlements_on_tile(self, tile_coord: int) -> dict[int, Piece]:
        settlements = {}
        for node_coord in self.tile_neighboring_nodes(tile_coord):
            node = self._nodes[node_coord]
            if type(node) == Piece and node.piece_type == PieceTypes.SETTLEMENT:
                settlements[node_coord] = node
        return settlements
    
    def cities_on_tile(self, tile_coord: int) -> dict[int, Piece]:
        cities = {}
        for node_coord in self.tile_neighboring_nodes(tile_coord):
            node = self._nodes[node_coord]
            if type(node) == Piece and node.piece_type == PieceTypes.CITY:
                cities[node_coord] = node
        return cities
    
    def friendly_roads(self, player_id: int) -> dict[int, Piece]:
        return {coord: edge for coord, edge in self.occupied_edges.items() if type(edge) == Piece and edge.owner_id == player_id}

    def friendly_settlements(self, player_id: int) -> dict[int, Piece]:
        return {coord: node for coord, node in self.occupied_nodes.items() if type(node) == Piece and node.piece_type == PieceTypes.SETTLEMENT and node.owner_id == player_id}
 
    def friendly_cities(self, player_id: int) -> dict[int, Piece]:
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

    def settlement_neighboring_settlement(self, node_coord: int) -> bool:
        neighbor_nodes = self.node_neighboring_nodes(node_coord)
        for coord, node in neighbor_nodes.items():
            if type(node) == Piece:
                return True
        return False
            
    def settlement_neighboring_friendly_road(self, node_coord: int, player_id: int) -> bool:
        neighbor_edges = self.node_neighboring_edges(node_coord)
        for coord, edge in neighbor_edges.items():
            if type(edge) == Piece and edge.owner_id == player_id:
                return True
        return False

    def road_neighboring_friendly_piece(self, edge_coord: int, player_id: int) -> bool:
        neighbor_nodes = self.edge_neighboring_nodes(edge_coord)
        neighbor_edges = self.edge_neighboring_edges(edge_coord)
        for node, edge in zip(neighbor_nodes.values(), neighbor_edges.values()):
            if (type(node) == Piece and node.owner_id == player_id) or (type(edge) == Piece and edge.owner_id == player_id):
                return True
        return False

    def road_neighboring_enemy_settlement(self, edge_coord: int, player_id: int) -> bool:
        for node in self.edge_neighboring_nodes(edge_coord).values():
            if type(node) == Piece and node.owner_id != player_id:
                return True
        return False

    def legal_road_placements(self, player_id: int) -> list[int]:
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

    def legal_starting_settlement_placements(self, player_id: int) -> list[int]:
        legal_settlement_placements = []
        for coord in self.empty_nodes:
            if not self.settlement_neighboring_settlement(coord):
                legal_settlement_placements.append(coord)
        return legal_settlement_placements
    
    def legal_settlement_placements(self, player_id: int) -> list[int]:
        legal_settlement_placements = []
        for coord in self.empty_nodes:
            if not self.settlement_neighboring_settlement(coord) and self.settlement_neighboring_friendly_road(coord, player_id):
                legal_settlement_placements.append(coord)
        return legal_settlement_placements

    def legal_city_placements(self, player_id: int) -> list[int]:
        legal_city_placements = []
        for coord, node in self.occupied_nodes.items():
            if type(node) == Piece and node.piece_type == PieceTypes.SETTLEMENT and node.owner_id == player_id:
                legal_city_placements.append(coord)
        return legal_city_placements

    def build_road(self, edge_coord: int, player: Player) -> bool:
        edge = self._edges[edge_coord]
        if not edge:
            self._edges[edge_coord] = place_piece(edge_coord, player.id, player.name, player.color, PieceTypes.ROAD)
            return True
        return False
        
    def build_settlement(self, node_coord: int, player: Player) -> bool:
        node = self._nodes[node_coord]
        if not node:
            self._nodes[node_coord] = place_piece(node_coord, player.id, player.name, player.color, PieceTypes.SETTLEMENT)
            return True
        return False
    
    def build_city(self, node_coord: int, player: Player) -> bool:
        node = self._nodes[node_coord]
        if type(node) == Piece and node.piece_type == PieceTypes.SETTLEMENT:
            if node.owner_id == player.id:
                self._nodes[node_coord] = place_piece(node_coord, player.id, player.name, player.color, PieceTypes.CITY)
                return True
        return False

    def _neighboring_friendly_roads(self, road_coord: int, player_id: int) -> list[int]:
        return [coord for coord, road in self.edge_neighboring_edges(road_coord).items() if type(road) == Piece and road.owner_id == player_id]

    def find_longest_road_chain(self, player_id: int) -> int:
        roads = list(self.friendly_roads(player_id).keys())
        longest_chain = 0
        explored = set()
        while roads:
            chain_length = [1]
            self._explore_road(roads[0], player_id, explored, chain_length)
            if chain_length[0] > longest_chain:
                longest_chain = chain_length[0]
            roads = [r for r in roads if r not in explored]
        return longest_chain

    def _explore_road(self, road_coord: int, player_id: int, explored: set, chain_length: list[int], parent_neighbors=[]):
        explored.add(road_coord)
        neighbors = self._neighboring_friendly_roads(road_coord, player_id)
        if chain_length[0] == 1:
            parent_neighbors = neighbors.copy()
        elif chain_length[0] == 2 and [n for n in parent_neighbors if n not in neighbors and road_coord != n]:
            chain_length[0] += 1
        else:
            parent_neighbors = []
        neighbors = [n for n in neighbors if n not in explored]
        explored.update(neighbors)
        if neighbors:
            chain_length[0] += 1
            for neighbor in neighbors:
                self._explore_road(neighbor, player_id, explored, chain_length, parent_neighbors=parent_neighbors)    

    def get_state(self) -> dict:
        return {
            'tiles': self._tiles.copy(),
            'nodes': self._nodes.copy(),
            'edges': self._edges.copy(),
            'ports': self._ports.copy(),
            'n_tiles': self._n_tiles,
            'n_layers': self._n_layers,
            'robber': copy.copy(self._robber),
            'seed': self._seed,
        }

    def restore(self, state: dict):
        self._tiles = state['tiles'].copy()
        self._nodes = state['nodes'].copy()
        self._edges = state['edges'].copy()
        self._ports = state['ports'].copy()
        self._n_tiles = state['n_tiles']
        self._n_layers = state['n_layers']
        self._robber = copy.copy(state['robber'])
        self._seed = state['seed']

    @staticmethod
    def create_from_state(state: dict) -> 'Board':
        board = Board()
        board.restore(state)
        return board

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
                o_id = edge.owner_id
                if o_id not in player_roads:
                    player_roads[o_id] = []
                player_roads[o_id].append(edge)

        for node in self._nodes.values():
            if type(node) == Piece and node.piece_type == PieceTypes.SETTLEMENT:
                o_id = node.owner_id
                if o_id not in player_settlements:
                    player_settlements[o_id] = []
                player_settlements[o_id].append(node)

        for node in self._nodes.values():
            if type(node) == Piece and node.piece_type == PieceTypes.CITY:
                o_id = node.owner_id
                if o_id not in player_settlements:
                    player_cities[o_id] = []
                player_cities[o_id].append(node)

        s += '\nRoads:\n'
        for p_id in player_roads:
            for road in player_roads[p_id]:
                s += f'{road}\n'

        s += '\nSettlements:\n'
        for p_id in player_settlements:
            for settlement in player_settlements[p_id]:
                s += f'{settlement}\n'
        
        s += '\nCities:\n'
        for p_id in player_cities:
            for city in player_cities[p_id]:
                s += f'{city}\n'
        
        return s
