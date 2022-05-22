import tkinter as tk
import tkutils
import math
import functools
from pytan.core import hexmesh
from pytan.core.hexmesh import Directions
from pytan.core.game import Game
from pytan.core.piece import Piece, PieceTypes
from pytan.core.cards import ResourceCards, DevCards
from pytan.core.state import GameStates
from pytan.core.trading import PortTypes
from pytan.ui.state import CatanUIState, UIStates

tk_status = {
    True: tk.NORMAL,
    False: tk.DISABLED,
    None: tk.DISABLED
}

class BoardFrame(tk.Frame):
    def __init__(self, master: tk.Frame, game: Game, ui_state: CatanUIState):
        super().__init__()
        self.master = master
        self.game = game
        self.game.add_observer(self)

        self.ui_state = ui_state

        self._board = game.board

        
        self._board_canvas = tk.Canvas(self, height=600, width=600, bg='#24AAFA')
        self._board_canvas.pack(expand=tk.YES, fill=tk.BOTH)

        self._center_to_edge = math.cos(math.radians(30)) * self._tile_radius

    def piece_click(self, piece_type, event):
        tags = self._board_canvas.gettags(event.widget.find_closest(event.x, event.y))
        # avoid processing tile clicks
        tag = None
        for t in tags:
            if 'tile' not in t:
                tag = t
                break
        if tag is not None:
            self.ui_state.set_state(UIStates.INGAME)
            if piece_type == PieceTypes.ROAD:
                self.game.build_road(self._coord_from_road_tag(tag))
            elif piece_type == PieceTypes.SETTLEMENT:
                self.game.build_settlement(self._coord_from_settlement_tag(tag))
            elif piece_type == PieceTypes.CITY:
                self.game.build_city(self._coord_from_city_tag(tag))
            elif piece_type == PieceTypes.ROBBER:
                self.game.move_robber(self._coord_from_robber_tag(tag))
            self.redraw()

    def notify(self, observable):
        self.redraw()

    def draw(self, board):
        terrain_centers = self._draw_terrain(board)
        
        self._draw_numbers(board, terrain_centers)
        
        if self.ui_state != UIStates.SETUP:
            self._draw_ports(board, terrain_centers)    
        
        self._draw_pieces(board, terrain_centers)
        if self.ui_state.is_building_road():
            self._draw_piece_shadows(PieceTypes.ROAD, board, terrain_centers)
        if self.ui_state.is_building_settlement():
            self._draw_piece_shadows(PieceTypes.SETTLEMENT, board, terrain_centers)
        if self.ui_state.is_building_city():
            self._draw_piece_shadows(PieceTypes.CITY, board, terrain_centers)
        if self.ui_state.is_moving_robber():
            self._draw_piece_shadows(PieceTypes.ROBBER, board, terrain_centers) 

    def redraw(self):
        self._board_canvas.delete(tk.ALL)
        self.draw(self._board)

    def _draw_terrain(self, board):
        centers = {}
        last = None
        for tile_id in board.tiles:
            if not last:
                centers[tile_id] = self._board_center
                last = tile_id
                continue

            # Calculate the center of this tile as an offset from the center of
            # the neighboring tile in the given direction.
            ref_center = centers[last]
            direction = hexmesh.direction_to_tile(last, tile_id)
            theta = self._tile_angle_order.index(direction) * 60
            radius = 2 * self._center_to_edge + self._tile_padding
            dx = radius * math.cos(math.radians(theta))
            dy = radius * math.sin(math.radians(theta))
            centers[tile_id] = (ref_center[0] + dx, ref_center[1] + dy)
            last = tile_id

        for tile_id, (x, y) in centers.items():
            tile = board.tiles[tile_id]
            self._draw_tile(x, y, tile.tile_type, tile)

        return dict(centers)

    def _draw_tile(self, x, y, terrain, tile):
        self._draw_hexagon(self._tile_radius, offset=(x, y), fill=self._colors[terrain.value], tags=self._tile_tag(tile))

    def _draw_hexagon(self, radius, offset=(0, 0), rotate=30, fill='black', tags=None):
        points = self._hex_points(radius, offset, rotate)
        self._board_canvas.create_polygon(*points, fill=fill, outline='black', tags=tags)

    def _draw_numbers(self, board, terrain_centers):
        for tile_id, (x, y) in terrain_centers.items():
            tile = board.tiles[tile_id]
            if tile.prob != 7:
                self._draw_number(x, y, tile.prob, tile)

    def _draw_number(self, x, y, number, tile):
        color = 'red' if number in (6, 8) else 'black'
        self._board_canvas.create_oval(tkutils.circle_bbox(24, (x, y)), fill='white', outline='black', tags=self._tile_tag(tile))
        self._board_canvas.create_text(x, y-3, text=str(number), font=self._hex_font, fill=color, tags=self._tile_tag(tile))
        prod = tile.prod_points
        p_w = (prod*3) + ((prod-1)*2)
        p_x = x - (p_w/2)
        p_y = y+10
        for _ in range(prod):
            self._board_canvas.create_oval(tkutils.circle_bbox(2, (p_x, p_y)), fill='black', tags=self._tile_tag(tile))
            p_x += 5

    def _draw_ports(self, board, terrain_centers, ports=None, ghost=False):
        if ports is None:
            ports = board.ports
        port_centers = []
        for port in ports.values():
            tile_x, tile_y = terrain_centers[port.tile]
            theta = self._tile_angle_order.index(port.direction) * 60
            radius = 2 * self._center_to_edge + self._tile_padding
            dx = radius * math.cos(math.radians(theta))
            dy = radius * math.sin(math.radians(theta))
            port_centers.append((tile_x + dx, tile_y + dy, theta))

        port_centers = self._fixup_port_centers(port_centers)
        for (x, y, angle), port in zip(port_centers, ports.values()):
            self._draw_port(x, y, angle, port, ghost=ghost)

    def _draw_port(self, x, y, angle, port, ghost=False):
        opts = self._port_tkinter_opts(port, ghost=ghost)
        points = [x, y]
        for adjust in (-30, 30):
            x1 = x + math.cos(math.radians(angle + adjust)) * self._tile_radius
            y1 = y + math.sin(math.radians(angle + adjust)) * self._tile_radius
            points.extend([x1, y1])
        self._board_canvas.create_polygon(*points, **opts)
        self._board_canvas.create_text(x, y, text=port.port_type.value, fill='black', font=self._hex_font)
        #self._board_canvas.tag_bind(self._port_tag(port), '<ButtonPress-1>', functools.partial(self.port_click, port))

    def _draw_pieces(self, board, terrain_centers):
        roads, settlements, cities, robber = self._get_pieces(board)

        for road in roads:
            self._draw_piece(road.coord, road, terrain_centers)

        for settlement in settlements:
            self._draw_piece(settlement.coord, settlement, terrain_centers)

        for city in cities:
            self._draw_piece(city.coord, city, terrain_centers)

        self._draw_piece(robber.coord, robber, terrain_centers)

    def _draw_piece_shadows(self, piece_type, board, terrain_centers):
        piece = Piece(0x00, self.game.current_player, piece_type)
        if piece_type == PieceTypes.ROAD:
            edges = self.game.legal_road_placements()
            for edge in edges:
                self._draw_piece(edge, piece, terrain_centers, ghost=True)
        elif piece_type == PieceTypes.SETTLEMENT:
            nodes = self.game.legal_settlement_placements()
            for node in nodes:
                self._draw_piece(node, piece, terrain_centers, ghost=True)
        elif piece_type == PieceTypes.CITY:
            nodes = self.game.legal_city_placements()
            for node in nodes:
                self._draw_piece(node, piece, terrain_centers, ghost=True)
        elif piece_type == PieceTypes.ROBBER:
            tiles = self._board.legal_robber_placements()
            for coord in tiles:
                self._draw_piece(coord, piece, terrain_centers, ghost=True)

    def _draw_piece(self, coord, piece, terrain_centers, ghost=False):
        x, y, angle = self._get_piece_center(coord, piece, terrain_centers)
        tag = None
        if piece.piece_type == PieceTypes.ROAD:
            self._draw_road(x, y, coord, piece, angle=angle, ghost=ghost)
            tag = self._road_tag(coord)
        elif piece.piece_type == PieceTypes.SETTLEMENT:
            self._draw_settlement(x, y, coord, piece, ghost=ghost)
            tag = self._settlement_tag(coord)
        elif piece.piece_type == PieceTypes.CITY:
            self._draw_city(x, y, coord, piece, ghost=ghost)
            tag = self._city_tag(coord)
        elif piece.piece_type == PieceTypes.ROBBER:
            self._draw_robber(x, y, coord, piece, ghost=ghost)
            tag = self._robber_tag(coord)

        if ghost:
            self._board_canvas.tag_bind(tag, '<ButtonPress-1>', func=functools.partial(self.piece_click, piece.piece_type))
        else:
            self._board_canvas.tag_unbind(tag, '<ButtonPress-1>')

    def _piece_tkinter_opts(self, coord, piece, **kwargs):
        opts = dict()
        tag_funcs = {
            PieceTypes.ROAD: self._road_tag,
            PieceTypes.SETTLEMENT: self._settlement_tag,
            PieceTypes.CITY: self._city_tag,
            PieceTypes.ROBBER: self._robber_tag,
        }
        color = 'black'
        try:
            color = piece.owner.color
        except:
            pass

        opts['tags'] = tag_funcs[piece.piece_type](coord)
        if 'ghost' in kwargs and kwargs['ghost'] == True:
            opts['fill'] = '' # transparent
            opts['activefill'] = color
            opts['outline'] = color
            if piece.piece_type == PieceTypes.ROBBER:
                opts['outline'] = 'black'
                opts['activefill'] = 'gray'
        else:
            opts['fill'] = color
            opts['outline'] = 'black'
        del kwargs['ghost']
        opts.update(kwargs)
        return opts

    def _port_tkinter_opts(self, port, **kwargs):
        opts = dict()
        color = self._colors[port.port_type.value]
        next_color = self._colors[port.port_type.value]

        ghost = 'ghost' in kwargs and kwargs['ghost'] == True

        opts['tags'] = self._port_tag(port)
        opts['outline'] = 'black'
        opts['fill'] = color
        if ghost:
            opts['activefill'] = next_color

        del kwargs['ghost']
        opts.update(kwargs)
        return opts

    def _draw_road(self, x, y, coord, piece, angle, ghost=False):
        opts = self._piece_tkinter_opts(coord, piece, ghost=ghost)
        length = self._tile_radius * 0.8
        height = length // 4
        points = [x - length/2, y - height/2] # left top
        points += [x + length/2, y - height/2] # right top
        points += [x + length/2, y + height/2] # right bottom
        points += [x - length/2, y + height/2] # left bottom
        points = tkutils.rotate_2poly(angle, points, (x, y))
        self._board_canvas.create_polygon(*points, **opts)

    def _draw_settlement(self, x, y, coord, piece, ghost=False):
        opts = self._piece_tkinter_opts(coord, piece, ghost=ghost)
        width = 26
        height = 30
        points = [x - width/2, y - height/6] # left top
        points += [x, y - height/2 - 2] # middle point
        points += [x + width/2, y - height/6] # right top
        points += [x + width/2, y + height/2] # right bottom
        points += [x - width/2, y + height/2] # left bottom
        self._board_canvas.create_polygon(*points, **opts)

    def _draw_city(self, x, y, coord, piece, ghost=False):
        opts = self._piece_tkinter_opts(coord, piece, ghost=ghost)
        y -= 5
        width = 40
        height = 40
        points = [x - width/2, y - height/4] # left top
        points += [x - width/4, y - height/2] # point
        points += [x, y - height/4] # middle top
        points += [x, y] # middle
        points += [x + width/2, y] # right middle
        points += [x + width/2, y + height/2] # right bottom
        points += [x - width/2, y + height/2] # left bottom
        self._board_canvas.create_polygon(*points, **opts)

    def _draw_robber(self, x, y, coord, piece, ghost=False):
        opts = self._piece_tkinter_opts(coord, piece, ghost=ghost)
        radius = 10
        self._board_canvas.create_oval(x-radius, y-radius, x+radius, y+radius, **opts)

    def _get_pieces(self, board):
        roads = self._board.roads.values()
        settlements = self._board.settlements.values()
        cities = self._board.cities.values()
        robber = self._board.robber
        return roads, settlements, cities, robber

    def _get_piece_center(self, piece_coord, piece, terrain_centers):
        if piece.piece_type == PieceTypes.ROAD:
            # these pieces are on edges
            tile_coord = self._board.nearest_tile_to_edge(piece_coord)
            direction = hexmesh.tile_to_edge_direction(tile_coord, piece_coord)
            terrain_x, terrain_y = terrain_centers[tile_coord]
            angle = 60*self._edge_angle_order.index(direction)
            dx = math.cos(math.radians(angle)) * self.distance_tile_to_edge()
            dy = math.sin(math.radians(angle)) * self.distance_tile_to_edge()
            return terrain_x + dx, terrain_y + dy, angle + 90
        elif piece.piece_type in [PieceTypes.SETTLEMENT, PieceTypes.CITY]:
            # these pieces are on nodes
            tile_coord = self._board.nearest_tile_to_node(piece_coord)
            direction = hexmesh.tile_to_node_direction(tile_coord, piece_coord)
            terrain_x, terrain_y = terrain_centers[tile_coord]
            angle = 30 + 60*self._node_angle_order.index(direction)
            dx = math.cos(math.radians(angle)) * self._tile_radius
            dy = math.sin(math.radians(angle)) * self._tile_radius
            return terrain_x + dx, terrain_y + dy, 0
        elif piece.piece_type == PieceTypes.ROBBER:
            terrain_x, terrain_y = terrain_centers[piece_coord]
            return terrain_x, terrain_y, 0

    def _fixup_offset(self):
        offx, offy = self._board_center
        radius = 4 * self._center_to_edge + 2 * self._tile_padding
        offx += radius * math.cos(math.radians(240))
        offy += radius * math.sin(math.radians(240))
        return (offx, offy)

    def _fixup_terrain_centers(self, centers):
        offx, offy = self._fixup_offset()
        return dict((tile_id, (x + offx, y + offy)) for tile_id, (x, y) in centers.items())

    def _fixup_port_centers(self, port_centers):
        return [(x, y, angle + 180) for x, y, angle in port_centers]

    def _hex_points(self, radius, offset, rotate):
        offx, offy = offset
        points = []
        for theta in (60 * n for n in range(6)):
            x = (math.cos(math.radians(theta + rotate)) * radius) + offx
            y = (math.sin(math.radians(theta + rotate)) * radius) + offy
            points += [x, y]
        return points

    def distance_tile_to_edge(self):
        return self._tile_radius * math.cos(math.radians(30)) + 1/2*self._tile_padding

    def _tile_tag(self, tile):
        return f'tile_{hex(tile.coord)}'

    def _road_tag(self, coord):
        return f'road_{hex(coord)}'

    def _settlement_tag(self, coord):
        return f'settlement_{hex(coord)}'

    def _city_tag(self, coord):
        return f'city_{hex(coord)}'

    def _robber_tag(self, coord):
        return f'robber_{hex(coord)}'

    def _port_tag(self, port):
        return f'port_{hex(port.tile)}'

    def _tile_id_from_tag(self, tag):
        return int(tag[len('tile_0x'):], 16)

    def _coord_from_road_tag(self, tag):
        return int(tag[len('road_0x'):], 16)

    def _coord_from_settlement_tag(self, tag):
        return int(tag[len('settlement_0x'):], 16)

    def _coord_from_city_tag(self, tag):
        return int(tag[len('city_0x'):], 16)

    def _coord_from_robber_tag(self, tag):
        return int(tag[len('robber_0x'):], 16)

    _tile_radius  = 50
    _tile_padding = 0
    _board_center = (300, 300)
    _tile_angle_order = (Directions.E, Directions.SE, Directions.SW, Directions.W, Directions.NW, Directions.NE) # 0 + 60*index
    _edge_angle_order = (Directions.E, Directions.SE, Directions.SW, Directions.W, Directions.NW, Directions.NE) # 0 + 60*index
    _node_angle_order = (Directions.SE, Directions.S, Directions.SW, Directions.NW, Directions.N, Directions.NE) # 30 + 60*index
    _hex_font = (('Helvetica'), 18)
    _colors = {
        'WOOD': '#3AA123',
        'BRICK': '#E06C05',
        'WHEAT': '#FFE32D',
        'SHEEP': '#A8FF31',
        'ORE': '#8A8A8A',
        'DESERT': '#DBB135',
        '3:1': 'white',
        'NONE': '', # transparent
    }

class GameControlsFrame(tk.Frame):
    def __init__(self, master: tk.Frame, game: Game, ui_state: CatanUIState):
        super().__init__()
        self.master = master
        self.game = game
        self.game.add_observer(self)
        self.ui_state = ui_state

        ui_state.set_state(UIStates.INGAME)
        
        player_label_frame = PlayerLabelFrame(self, game, ui_state)
        dice_sides_frame = DiceSidesFrame(self, game, ui_state)
        action_frame = ActionFrame(self, game, ui_state)
        build_frame = BuildFrame(self, game, ui_state)
        dev_card_frame = DevCardFrame(self, game, ui_state)
        self.trade_button = tk.Button(self, command=self.on_trade, width=20, text='Trade')

        self.discard_frame = DiscardFrame(self, self.game, ui_state)
        self.steal_frame = StealFrame(self, self.game, ui_state)
        self.trade_frame = TradingFrame(self, self.game, ui_state)
        self.accept_trade_frame = AcceptTradeFrame(self, self.game, ui_state)
        self.confirm_trade_frame = ConfirmTradeFrame(self, self.game, ui_state)

        player_label_frame.pack(pady=5, anchor='w')
        dice_sides_frame.pack(pady=5)
        action_frame.pack(pady=5)
        build_frame.pack(pady=5)
        dev_card_frame.pack(pady=5)
        self.trade_button.pack(pady=5)

    def notify(self, observable):
        if self.game.state == GameStates.DISCARDING:
            self.discard_frame = DiscardFrame(self, self.game, self.ui_state)
            self.discard_frame.pack(pady=5)
        elif self.game.state == GameStates.STEALING:
            self.steal_frame = StealFrame(self, self.game, self.ui_state)
            self.steal_frame.pack(pady=5)
        elif self.game.state == GameStates.ACCEPTING_TRADE:
            self.accept_trade_frame = AcceptTradeFrame(self, self.game, self.ui_state)
            self.accept_trade_frame.pack(pady=5)
        elif self.game.state == GameStates.CONFIRMING_TRADE:
            self.confirm_trade_frame = ConfirmTradeFrame(self, self.game, self.ui_state)
            self.confirm_trade_frame.pack(pady=5)
        else:
            self.clear_discard()
            self.steal_frame.pack_forget()
            self.clear_accept_trade()
            self.confirm_trade_frame.pack_forget()
        
        self.set_states()

    def set_states(self):
        self.trade_button.configure(state=tk_status[self.ui_state.can_trade()])

    def on_trade(self):
        self.ui_state.set_state(UIStates.CREATING_TRADE)
        self.trade_frame = TradingFrame(self, self.game, self.ui_state)
        self.trade_frame.pack(pady=5)
        self.set_states()

    def clear_trade(self):
        self.trade_frame.pack_forget()
        self.set_states()

    def clear_accept_trade(self):
        self.accept_trade_frame.pack_forget()
        self.set_states()

    def clear_discard(self):
        self.discard_frame.pack_forget()
        self.set_states()

class PlayerLabelFrame(tk.Frame):
    def __init__(self, master: tk.Frame, game: Game, ui_state: CatanUIState):
        super().__init__(master)

        self.master = master
        self.game = game
        self.game.add_observer(self)
        self.ui_state = ui_state

        self._players = [tk.StringVar() for _ in self.game.players]
        self._cur_player = self.game.current_player
        
        self.player_labels = [tk.Label(self, textvariable=player) for player in self._players]
        for pl in self.player_labels:
            pl.pack(anchor='w')
        
        self.set_player_labels()

    def set_player_labels(self):
        self._cur_player = self.game.current_player
        for pl, player_s, player in zip(self.player_labels, self._players, self.game.players):
            s = ''
            if player.identifier == self._cur_player.identifier:
                pl.config(fg='red')
            else:
                pl.config(fg='white')
            s += str(player)
            s += f' - {player.victory_points}'
            if player.victory_points != player.total_victory_points:
                s += f'({player.total_victory_points})'
            s += ' | '
            for card in ResourceCards:
                n = player.count_resource_cards(card)
                if n > 0:
                    s += ' '
                    abrv = card.value[:2]
                    if n > 1:
                        s += f'{n}x'
                    s += f'{abrv}'
            if any(player.dev_cards):
                s += ' |'
            for card in DevCards:
                n = player.count_dev_cards(card)
                abrv = card.value[:2]
                if card.value.find('_') > 0:
                    parts = card.value.split('_')
                    abrv = parts[0][0] + parts[1][0]
                if n > 0:
                    s += ' '
                    if n > 1:
                        s += f'{n}x'
                    s += f'{abrv}'
            player_s.set(s)

    def notify(self, observable):
        self.set_player_labels()

class DiceSidesFrame(tk.Frame):
    def __init__(self, master: tk.Frame, game: Game, ui_state: CatanUIState):
        super().__init__(master)
        
        self.master = master
        self.game = game
        self.game.add_observer(self)
        self.ui_state = ui_state

        self.roll_two_button = tk.Button(self, command=lambda:self.on_roll(2), text='2')
        self.roll_three_button = tk.Button(self, command=lambda:self.on_roll(3), text='3')
        self.roll_four_button = tk.Button(self, command=lambda:self.on_roll(4), text='4')
        self.roll_five_button = tk.Button(self, command=lambda:self.on_roll(5), text='5')
        self.roll_six_button = tk.Button(self, command=lambda:self.on_roll(6), text='6')
        self.roll_seven_button = tk.Button(self, command=lambda:self.on_roll(7), text='7')
        self.roll_eight_button = tk.Button(self, command=lambda:self.on_roll(8), text='8')
        self.roll_nine_button = tk.Button(self, command=lambda:self.on_roll(9), text='9')
        self.roll_ten_button = tk.Button(self, command=lambda:self.on_roll(10), text='10')
        self.roll_eleven_button = tk.Button(self, command=lambda:self.on_roll(11), text='11')
        self.roll_twelve_button = tk.Button(self, command=lambda:self.on_roll(12), text='12')

        self.roll_two_button.grid(row=0,column=0)
        self.roll_three_button.grid(row=0,column=1)
        self.roll_four_button.grid(row=0,column=2)
        self.roll_five_button.grid(row=0,column=3)
        self.roll_six_button.grid(row=0,column=4)
        self.roll_seven_button.grid(row=0,column=5)
        self.roll_eight_button.grid(row=1,column=0)
        self.roll_nine_button.grid(row=1,column=1)
        self.roll_ten_button.grid(row=1,column=2)
        self.roll_eleven_button.grid(row=1,column=3)
        self.roll_twelve_button.grid(row=1,column=4)

    def notify(self, observable):
        self.set_states()

    def set_states(self):
        self.roll_two_button.configure(state=tk_status[self.ui_state.can_roll()])
        self.roll_three_button.configure(state=tk_status[self.ui_state.can_roll()])
        self.roll_four_button.configure(state=tk_status[self.ui_state.can_roll()])
        self.roll_five_button.configure(state=tk_status[self.ui_state.can_roll()])
        self.roll_six_button.configure(state=tk_status[self.ui_state.can_roll()])
        self.roll_seven_button.configure(state=tk_status[self.ui_state.can_roll()])
        self.roll_eight_button.configure(state=tk_status[self.ui_state.can_roll()])
        self.roll_nine_button.configure(state=tk_status[self.ui_state.can_roll()])
        self.roll_ten_button.configure(state=tk_status[self.ui_state.can_roll()])
        self.roll_eleven_button.configure(state=tk_status[self.ui_state.can_roll()])
        self.roll_twelve_button.configure(state=tk_status[self.ui_state.can_roll()])

    def on_roll(self, roll):
        self.game.roll(roll)
        self.set_states()

class ActionFrame(tk.Frame):
    def __init__(self, master: tk.Frame, game: Game, ui_state: CatanUIState):
        super().__init__(master)

        self.master = master
        self.game = game
        self.game.add_observer(self)
        self.ui_state = ui_state

        self.roll_button = tk.Button(self, command=self.on_dice_roll, text='Roll Dice')
        self.pass_turn_button = tk.Button(self, command=self.on_pass_turn, text='Pass Turn')
        self.cancel_button = tk.Button(self, command=self.on_cancel, text='Cancel')

        self.roll_button.grid(row=0, column=0)
        self.pass_turn_button.grid(row=0, column=1)
        self.cancel_button.grid(row=0, column=2)

    def notify(self, observable):
        self.set_states()
    
    def set_states(self):
        self.roll_button.configure(state=tk_status[self.ui_state.can_roll()])
        self.pass_turn_button.configure(state=tk_status[self.ui_state.can_pass_turn()])
        self.cancel_button.configure(state=tk_status[self.ui_state.can_cancel()])
    
    def on_dice_roll(self):
        self.game.roll()
        self.set_states()

    def on_pass_turn(self):
        self.ui_state.set_state(UIStates.INGAME)
        self.game.pass_turn()
        self.set_states()

    def on_cancel(self):
        self.ui_state.set_state(UIStates.INGAME)
        self.game.notify()
        self.set_states()

class BuildFrame(tk.LabelFrame):
    def __init__(self, master: tk.Frame, game: Game, ui_state: CatanUIState):
        super().__init__(master, text='Build')

        self.master = master
        self.game = game
        self.game.add_observer(self)
        self.ui_state = ui_state

        self.build_road_button = tk.Button(self, command=self.on_build_road, width=10, text='Road')
        self.build_settlement_button = tk.Button(self, command=self.on_build_settlement, width=10, text='Settlement')
        self.upgrade_city_button = tk.Button(self, command=self.on_build_city, width=10, text='City')
        self.buy_dev_card_button = tk.Button(self, command=self.on_buy_dev_card, width=10, text='Dev Card')

        self.build_road_button.grid(row=0, column=0)
        self.build_settlement_button.grid(row=0, column=1)
        self.upgrade_city_button.grid(row=1, column=0)
        self.buy_dev_card_button.grid(row=1, column=1)

    def notify(self, observable):
        self.set_states()

    def set_states(self):
        self.build_road_button.configure(state=tk_status[self.ui_state.can_build_road()])
        self.build_settlement_button.configure(state=tk_status[self.ui_state.can_build_settlement()])
        self.upgrade_city_button.configure(state=tk_status[self.ui_state.can_build_city()])
        self.buy_dev_card_button.configure(state=tk_status[self.ui_state.can_buy_dev_card()])

    def on_build_road(self):
        self.ui_state.set_state(UIStates.BUILDING_ROAD)
        self.game.notify()
        self.set_states()

    def on_build_settlement(self):
        self.ui_state.set_state(UIStates.BUILDING_SETTLEMENT)
        self.game.notify()
        self.set_states()

    def on_build_city(self):
        self.ui_state.set_state(UIStates.BUILDING_CITY)
        self.game.notify()
        self.set_states()
    
    def on_buy_dev_card(self):
        self.game.buy_dev_card()
        self.set_states()

class DevCardFrame(tk.Frame):
    def __init__(self, master: tk.Frame, game: Game, ui_state: CatanUIState):
        super().__init__(master)

        self.master = master
        self.game = game
        self.game.add_observer(self)
        self.ui_state = ui_state

        self.button_frame = tk.LabelFrame(self, text='Play Dev Card')
        self.button_frame.pack()

        self.knight_button = tk.Button(self.button_frame, command=self.on_knight, width=10, text='Knight')
        self.monopoly_button = tk.Button(self.button_frame, command=self.on_monopoly, width=10, text='Monopoly')
        self.road_builder_button = tk.Button(self.button_frame, command=self.on_road_builder, width=10, text='Road Builder')
        self.plenty_button = tk.Button(self.button_frame, command=self.on_plenty, width=10, text='Year Plenty')

        self.knight_button.grid(row=0, column=0)
        self.monopoly_button.grid(row=0, column=1)
        self.road_builder_button.grid(row=1, column=0)
        self.plenty_button.grid(row=1, column=1)

        self.monopoly_frame = MonopolyFrame(self, game, ui_state)

        self.plenty_frame = YearPlentyFrame(self, game, ui_state)

    def notify(self, observable):
        self.set_states()

    def set_states(self):
        self.knight_button.configure(state=tk_status[self.ui_state.can_play_knight()])
        self.monopoly_button.configure(state=tk_status[self.ui_state.can_play_monopoly()])
        self.road_builder_button.configure(state=tk_status[self.ui_state.can_play_road_builder()])
        self.plenty_button.configure(state=tk_status[self.ui_state.can_play_year_plenty()])

    def on_knight(self):
        self.game.play_knight()
        self.set_states()

    def on_monopoly(self):
        self.monopoly_frame = MonopolyFrame(self, self.game, self.ui_state)
        self.ui_state.set_state(UIStates.MONOPOLY)
        self.monopoly_frame.pack(pady=5)
        self.set_states()

    def on_road_builder(self):
        self.game.play_road_builder()
        self.set_states()

    def on_plenty(self):
        self.plenty_frame = YearPlentyFrame(self, self.game, self.ui_state)
        self.ui_state.set_state(UIStates.YEAR_PLENTY)
        self.plenty_frame.pack(pady=5)
        self.set_states()

    def clear_monopoly(self):
        self.ui_state.set_state(UIStates.INGAME)
        self.monopoly_frame.pack_forget()
        self.set_states()

    def clear_year_plenty(self):
        self.ui_state.set_state(UIStates.INGAME)
        self.plenty_frame.pack_forget()
        self.set_states()

class MonopolyFrame(tk.LabelFrame):
    def __init__(self, master: tk.Frame, game: Game, ui_state: CatanUIState):
        super().__init__(master, text='Monopoly')
        self.master = master
        self.game = game
        self.ui_state = ui_state

        self._resource = None
        
        self.wheat_bool = tk.BooleanVar()
        self.wood_bool = tk.BooleanVar()
        self.sheep_bool = tk.BooleanVar()
        self.brick_bool = tk.BooleanVar()
        self.ore_bool = tk.BooleanVar()

        self.wheat_button = tk.Checkbutton(self, variable=self.wheat_bool, command=self.on_wheat, text='Wheat')
        self.wood_button = tk.Checkbutton(self, variable=self.wood_bool, command=self.on_wood, text='Wood')
        self.sheep_button = tk.Checkbutton(self, variable=self.sheep_bool, command=self.on_sheep, text='Sheep')
        self.brick_button = tk.Checkbutton(self, variable=self.brick_bool, command=self.on_brick, text='Brick')
        self.ore_button = tk.Checkbutton(self, variable=self.ore_bool, command=self.on_ore, text='Ore')
        self.confirm_button = tk.Button(self, command=self.on_confirm, text='Confirm')

        self.wheat_button.grid(row=0, column=0)
        self.wood_button.grid(row=0, column=1)
        self.sheep_button.grid(row=0, column=2)
        self.brick_button.grid(row=1, column=0)
        self.ore_button.grid(row=1, column=1)
        self.confirm_button.grid(row=2, column=0)

    def on_wheat(self):
        self._resource = ResourceCards.WHEAT
        self.wood_bool.set(False)
        self.sheep_bool.set(False)
        self.brick_bool.set(False)
        self.ore_bool.set(False)

    def on_wood(self):
        self._resource = ResourceCards.WOOD
        self.wheat_bool.set(False)
        self.sheep_bool.set(False)
        self.brick_bool.set(False)
        self.ore_bool.set(False)

    def on_sheep(self):
        self._resource = ResourceCards.SHEEP
        self.wheat_bool.set(False)
        self.wood_bool.set(False)
        self.brick_bool.set(False)
        self.ore_bool.set(False)

    def on_brick(self):
        self._resource = ResourceCards.BRICK
        self.wheat_bool.set(False)
        self.wood_bool.set(False)
        self.sheep_bool.set(False)
        self.ore_bool.set(False)

    def on_ore(self):
        self._resource = ResourceCards.ORE
        self.wheat_bool.set(False)
        self.wood_bool.set(False)
        self.sheep_bool.set(False)
        self.brick_bool.set(False)

    def on_confirm(self):
        self.master.clear_monopoly()
        self.game.play_monopoly(self._resource)

class YearPlentyFrame(tk.LabelFrame):
    def __init__(self, master: tk.Frame, game: Game, ui_state: CatanUIState):
        super().__init__(master, text='Year Plenty')
        self.master = master
        self.game = game
        self.ui_state = ui_state

        self._resource_1 = None
        self._resource_2 = None

        self.choice_frame = tk.Frame(self)
        self.choice_frame.pack()

        self.choice_1_wheat_bool = tk.BooleanVar()
        self.choice_1_wood_bool = tk.BooleanVar()
        self.choice_1_sheep_bool = tk.BooleanVar()
        self.choice_1_brick_bool = tk.BooleanVar()
        self.choice_1_ore_bool = tk.BooleanVar()

        self.choice_1_label = tk.Label(self, text='Card 1')
        self.choice_1_wheat_button = tk.Checkbutton(self.choice_frame, variable=self.choice_1_wheat_bool, command=lambda:self.on_wheat(1), text='Wheat')
        self.choice_1_wood_button = tk.Checkbutton(self.choice_frame, variable=self.choice_1_wood_bool, command=lambda:self.on_wood(1), text='Wood')
        self.choice_1_sheep_button = tk.Checkbutton(self.choice_frame, variable=self.choice_1_sheep_bool, command=lambda:self.on_sheep(1), text='Sheep')
        self.choice_1_brick_button = tk.Checkbutton(self.choice_frame, variable=self.choice_1_brick_bool, command=lambda:self.on_brick(1), text='Brick')
        self.choice_1_ore_button = tk.Checkbutton(self.choice_frame, variable=self.choice_1_ore_bool, command=lambda:self.on_ore(1), text='Ore')
        
        self.choice_1_wheat_button.grid(row=0, column=0)
        self.choice_1_wood_button.grid(row=0, column=1)
        self.choice_1_sheep_button.grid(row=0, column=2)
        self.choice_1_brick_button.grid(row=0, column=3)
        self.choice_1_ore_button.grid(row=0, column=4)

        self.choice_2_wheat_bool = tk.BooleanVar()
        self.choice_2_wood_bool = tk.BooleanVar()
        self.choice_2_sheep_bool = tk.BooleanVar()
        self.choice_2_brick_bool = tk.BooleanVar()
        self.choice_2_ore_bool = tk.BooleanVar()

        self.choice_2_label = tk.Label(self, text='Card 2')
        self.choice_2_wheat_button = tk.Checkbutton(self.choice_frame, variable=self.choice_2_wheat_bool, command=lambda:self.on_wheat(2), text='Wheat')
        self.choice_2_wood_button = tk.Checkbutton(self.choice_frame, variable=self.choice_2_wood_bool, command=lambda:self.on_wood(2), text='Wood')
        self.choice_2_sheep_button = tk.Checkbutton(self.choice_frame, variable=self.choice_2_sheep_bool, command=lambda:self.on_sheep(2), text='Sheep')
        self.choice_2_brick_button = tk.Checkbutton(self.choice_frame, variable=self.choice_2_brick_bool, command=lambda:self.on_brick(2), text='Brick')
        self.choice_2_ore_button = tk.Checkbutton(self.choice_frame, variable=self.choice_2_ore_bool, command=lambda:self.on_ore(2), text='Ore')
        
        self.choice_2_wheat_button.grid(row=0, column=0)
        self.choice_2_wood_button.grid(row=0, column=2)
        self.choice_2_sheep_button.grid(row=0, column=2)
        self.choice_2_brick_button.grid(row=0, column=3)
        self.choice_2_ore_button.grid(row=0, column=4)
        
        self.confirm_button = tk.Button(self, command=self.on_confirm, text='Confirm')
        self.confirm_button.pack()

    def set_states(self):
        if self._resource_1:
            if ResourceCards.WHEAT != self._resource_1:
                self.choice_1_wheat_button.configure(state='disabled')
            if ResourceCards.WOOD != self._resource_1:
                self.choice_1_wood_button.configure(state='disabled')
            if ResourceCards.SHEEP != self._resource_1:
                self.choice_1_sheep_button.configure(state='disabled')
            if ResourceCards.BRICK != self._resource_1:
                self.choice_1_brick_button.configure(state='disabled')
            if ResourceCards.ORE != self._resource_1:
                self.ore_button.configure(state='disabled')
        else:
            self.choice_1_wood_button.configure(state='enabled')
            self.choice_1_wheat_button.configure(state='enabled')
            self.choice_1_sheep_button.configure(state='enabled')
            self.choice_1_brick_button.configure(state='enabled')
            self.choice_1_ore_button.configure(state='enabled')

        if self._resource_2:
            if ResourceCards.WHEAT != self._resource_2:
                self.choice_2_wheat_button.configure(state='disabled')
            if ResourceCards.WOOD != self._resource_2:
                self.choice_2_wood_button.configure(state='disabled')
            if ResourceCards.SHEEP != self._resource_2:
                self.choice_2_sheep_button.configure(state='disabled')
            if ResourceCards.BRICK != self._resource_2:
                self.choice_2_brick_button.configure(state='disabled')
            if ResourceCards.ORE != self._resource_2:
                self.ore_button.configure(state='disabled')
        else:
            self.choice_2_wood_button.configure(state='enabled')
            self.choice_2_wheat_button.configure(state='enabled')
            self.choice_2_sheep_button.configure(state='enabled')
            self.choice_2_brick_button.configure(state='enabled')
            self.choice_2_ore_button.configure(state='enabled')
    
    def on_wheat(self, card_n: int):
        if card_n == 1 and self.choice_1_wheat_bool.get():
            self._resource_1 = ResourceCards.WHEAT
        elif card_n == 2 and self.choice_2_wheat_bool.get():
            self._resource_2 = ResourceCards.WHEAT
        elif card_n == 1:
            self._resource_1 = None
        elif card_n == 2:
            self._resource_2 = None
                
        self.set_states()

    def on_wood(self, card_n: int):
        if card_n == 1 and self.choice_1_wood_bool.get():
            self._resource_1 = ResourceCards.WOOD
        elif card_n == 2 and self.choice_2_wood_bool.get():
            self._resource_2 = ResourceCards.WOOD
        elif card_n == 1:
            self._resource_1 = None
        elif card_n == 2:
            self._resource_2 = None

    def on_sheep(self, card_n: int):
        if card_n == 1 and self.choice_1_sheep_bool.get():
            self._resource_1 = ResourceCards.SHEEP
        elif card_n == 2 and self.choice_2_sheep_bool.get():
            self._resource_2 = ResourceCards.SHEEP
        elif card_n == 1:
            self._resource_1 = None
        elif card_n == 2:
            self._resource_2 = None

    def on_brick(self, card_n: int):
        if card_n == 1 and self.choice_1_brick_bool.get():
            self._resource_1 = ResourceCards.BRICK
        elif card_n == 2 and self.choice_2_brick_bool.get():
            self._resource_2 = ResourceCards.BRICK
        elif card_n == 1:
            self._resource_1 = None
        elif card_n == 2:
            self._resource_2 = None

    def on_ore(self, card_n: int):
        if card_n == 1 and self.choice_1_ore_bool.get():
            self._resource_1 = ResourceCards.ORE
        elif card_n == 2 and self.choice_2_ore_bool.get():
            self._resource_2 = ResourceCards.ORE
        elif card_n == 1:
            self._resource_1 = None
        elif card_n == 2:
            self._resource_2 = None

    def on_confirm(self, card_n: int):
        self.master.clear_year_plenty()
        pickup_list = []
        pickup_list.append((self._resource_1, 1))
        pickup_list.append((self._resource_2, 1))

        self.game.play_year_plenty(pickup_list)

class DiscardFrame(tk.LabelFrame):
    def __init__(self, master: tk.Frame, game: Game, ui_state: CatanUIState):
        super().__init__(master, text='Discard')
        self.master = master
        self.game = game
        self.ui_state = ui_state

        cur_player = self.game.current_player

        self.entry_frame = tk.Frame(self)
        self.entry_frame.pack()
    
        self.wheat_label = tk.Label(self.entry_frame, text='Wheat')
        self.wheat_entry = tk.Spinbox(self.entry_frame, from_=0, to=cur_player.count_resource_cards(ResourceCards.WHEAT))

        self.wheat_label.grid(row=0, column=0)
        self.wheat_entry.grid(row=0, column=1)

        self.wood_label = tk.Label(self.entry_frame, text='Wood')
        self.wood_entry = tk.Spinbox(self.entry_frame, from_=0, to=cur_player.count_resource_cards(ResourceCards.WOOD))

        self.wood_label.grid(row=1, column=0)
        self.wood_entry.grid(row=1, column=1)

        self.sheep_label = tk.Label(self.entry_frame, text='Sheep')
        self.sheep_entry = tk.Spinbox(self.entry_frame, from_=0, to=cur_player.count_resource_cards(ResourceCards.SHEEP))

        self.sheep_label.grid(row=2, column=0)
        self.sheep_entry.grid(row=2, column=1)

        self.brick_label = tk.Label(self.entry_frame, text='Brick')
        self.brick_entry = tk.Spinbox(self.entry_frame, from_=0, to=cur_player.count_resource_cards(ResourceCards.BRICK))

        self.brick_label.grid(row=3, column=0)
        self.brick_entry.grid(row=3, column=1)

        self.ore_label = tk.Label(self.entry_frame, text='Ore')
        self.ore_entry = tk.Spinbox(self.entry_frame, from_=0, to=cur_player.count_resource_cards(ResourceCards.ORE))

        self.ore_label.grid(row=4, column=0)
        self.ore_entry.grid(row=4, column=1)

        self.confirm_button = tk.Button(self, command=self.on_confirm, text='Confirm')
        self.confirm_button.pack()

    def on_confirm(self):
        wheat = tkutils.try_parse_int(self.wheat_entry.get())
        wood = tkutils.try_parse_int(self.wood_entry.get())
        sheep = tkutils.try_parse_int(self.sheep_entry.get())
        brick = tkutils.try_parse_int(self.brick_entry.get())
        ore = tkutils.try_parse_int(self.ore_entry.get())

        discard_list = []
        if wheat > 0:
            discard_list.append((ResourceCards.WHEAT, wheat))
        if wood > 0:
            discard_list.append((ResourceCards.WOOD, wood))
        if sheep > 0:
            discard_list.append((ResourceCards.SHEEP, sheep))
        if brick > 0:
            discard_list.append((ResourceCards.BRICK, brick))
        if ore > 0:
            discard_list.append((ResourceCards.ORE, ore))

        self.master.clear_discard()
        self.game.discard(discard_list)

class StealFrame(tk.LabelFrame):
    def __init__(self, master: tk.Frame, game: Game, ui_state: CatanUIState):
        super().__init__(master, text='Pick a player to steal from')
        self.master = master
        self.game = game
        self.ui_state = ui_state

        players = self.game.players_to_steal_from
        for p in players:
            b = tk.Button(self, command=lambda I=p.identifier: self.on_button(I), width=10, text=str(p))
            b.pack()

    def on_button(self, player_id: int):
        self.game.steal(player_id)

class TradingFrame(tk.LabelFrame):
    def __init__(self, master: tk.Frame, game: Game, ui_state: CatanUIState):
        super().__init__(master, text='Offer Trade')
        self.master = master
        self.game = game
        self.ui_state = ui_state

        cur_player = self.game.current_player
        
        self.offer_frame = tk.Frame(self)
        self.offer_frame.pack()

        self.give_entry_frame = tk.LabelFrame(self.offer_frame, text='Give')
        self.give_entry_frame.grid(row=0, column=0)
    
        self.wheat_give_label = tk.Label(self.give_entry_frame, text='Wheat')
        self.wheat_give_entry = tk.Spinbox(self.give_entry_frame, command=self.on_value_change, width=5, from_=0, to=cur_player.count_resource_cards(ResourceCards.WHEAT))
        self.wheat_give_label.grid(row=0, column=0)
        self.wheat_give_entry.grid(row=0, column=1)

        self.wood_give_label = tk.Label(self.give_entry_frame, text='Wood')
        self.wood_give_entry = tk.Spinbox(self.give_entry_frame, command=self.on_value_change, width=5, from_=0, to=cur_player.count_resource_cards(ResourceCards.WOOD))
        self.wood_give_label.grid(row=1, column=0)
        self.wood_give_entry.grid(row=1, column=1)

        self.sheep_give_label = tk.Label(self.give_entry_frame, text='Sheep')
        self.sheep_give_entry = tk.Spinbox(self.give_entry_frame, command=self.on_value_change, width=5, from_=0, to=cur_player.count_resource_cards(ResourceCards.SHEEP))
        self.sheep_give_label.grid(row=2, column=0)
        self.sheep_give_entry.grid(row=2, column=1)

        self.brick_give_label = tk.Label(self.give_entry_frame, text='Brick')
        self.brick_give_entry = tk.Spinbox(self.give_entry_frame, command=self.on_value_change, width=5, from_=0, to=cur_player.count_resource_cards(ResourceCards.BRICK))
        self.brick_give_label.grid(row=3, column=0)
        self.brick_give_entry.grid(row=3, column=1)

        self.ore_give_label = tk.Label(self.give_entry_frame, text='Ore')
        self.ore_give_entry = tk.Spinbox(self.give_entry_frame, command=self.on_value_change, width=5, from_=0, to=cur_player.count_resource_cards(ResourceCards.ORE))
        self.ore_give_label.grid(row=4, column=0)
        self.ore_give_entry.grid(row=4, column=1)

        self.want_entry_frame = tk.LabelFrame(self.offer_frame, text='Recieve')
        self.want_entry_frame.grid(row=0, column=1)
    
        self.wheat_want_label = tk.Label(self.want_entry_frame, text='Wheat')
        self.wheat_want_entry = tk.Spinbox(self.want_entry_frame, command=self.on_value_change, width=5, from_=0, to=4)
        self.wheat_want_label.grid(row=0, column=0)
        self.wheat_want_entry.grid(row=0, column=1)

        self.wood_want_label = tk.Label(self.want_entry_frame, text='Wood')
        self.wood_want_entry = tk.Spinbox(self.want_entry_frame, command=self.on_value_change, width=5, from_=0, to=4)
        self.wood_want_label.grid(row=1, column=0)
        self.wood_want_entry.grid(row=1, column=1)

        self.sheep_want_label = tk.Label(self.want_entry_frame, text='Sheep')
        self.sheep_want_entry = tk.Spinbox(self.want_entry_frame, command=self.on_value_change, width=5, from_=0, to=4)
        self.sheep_want_label.grid(row=2, column=0)
        self.sheep_want_entry.grid(row=2, column=1)

        self.brick_want_label = tk.Label(self.want_entry_frame, text='Brick')
        self.brick_want_entry = tk.Spinbox(self.want_entry_frame, command=self.on_value_change, width=5, from_=0, to=4)
        self.brick_want_label.grid(row=3, column=0)
        self.brick_want_entry.grid(row=3, column=1)

        self.ore_want_label = tk.Label(self.want_entry_frame, text='Ore')
        self.ore_want_entry = tk.Spinbox(self.want_entry_frame, command=self.on_value_change, width=5, from_=0, to=4)
        self.ore_want_label.grid(row=4, column=0)
        self.ore_want_entry.grid(row=4, column=1)

        self.players_frame = tk.Frame(self)
        self.players_frame.pack()

        self.selected_players = []

        self.player_vars = {}
        i = 0
        for p in self.game.other_players:
            pid = p.identifier
            self.player_vars[pid] = tk.BooleanVar()
            self.player_vars[pid].set(True)
            self.selected_players.append(pid)
            b = tk.Checkbutton(self.players_frame, variable=self.player_vars[pid], command=lambda I=pid: self.on_player(I), width=10, text=str(p))
            b.grid(row=0, column=i)
            i += 1
        self.bank_var = tk.BooleanVar()
        self.bank_button = tk.Checkbutton(self.players_frame, variable=self.bank_var, state='disabled', text='Bank')
        self.bank_button.grid(row=0,column=i)

        self.confirm_frame = tk.Frame(self)
        self.confirm_frame.pack()

        self.confirm_button = tk.Button(self.confirm_frame, command=self.on_confirm, text='Confirm')
        self.confirm_button.grid(row=0, column=0)

        self.cancel_button = tk.Button(self.confirm_frame, command=self.on_cancel, text='Cancel')
        self.cancel_button.grid(row=0, column=1)
    
    def get_give_values(self):
        give_wheat = tkutils.try_parse_int(self.wheat_give_entry.get())
        give_wood = tkutils.try_parse_int(self.wood_give_entry.get())
        give_sheep = tkutils.try_parse_int(self.sheep_give_entry.get())
        give_brick = tkutils.try_parse_int(self.brick_give_entry.get())
        give_ore = tkutils.try_parse_int(self.ore_give_entry.get())
        return give_wheat, give_wood, give_sheep, give_brick, give_ore

    def get_want_values(self):
        want_wheat = tkutils.try_parse_int(self.wheat_want_entry.get())
        want_wood = tkutils.try_parse_int(self.wood_want_entry.get())
        want_sheep = tkutils.try_parse_int(self.sheep_want_entry.get())
        want_brick = tkutils.try_parse_int(self.brick_want_entry.get())
        want_ore = tkutils.try_parse_int(self.ore_want_entry.get())
        return want_wheat, want_wood, want_sheep, want_brick, want_ore

    def on_value_change(self):
        give = self.get_give_values()
        want = self.get_want_values()
        order = ['WHEAT', 'WOOD', 'SHEEP', 'BRICK', 'ORE']
        non_zero_give = [g for g in give if g != 0]
        non_zero_want = [w for w in want if w != 0]
        if len(non_zero_give) == 1 and len(non_zero_want) == 1:
            if non_zero_give[0] == 4 and non_zero_want[0] == 1:
                for pvar in self.player_vars.values():
                    pvar.set(False)
                self.bank_var.set(True)
                self.selected_players = []
                return
            port = PortTypes(order[give.index(non_zero_give[0])])
            if non_zero_give[0] == 2 and non_zero_want[0] == 1:
                if self.game.board.is_player_on_port(self.game.current_player.identifier, port):
                    for pvar in self.player_vars.values():
                        pvar.set(False)
                    self.bank_var.set(True)
                    self.selected_players = []
                    return
        if self.bank_var.get():
            self.selected_players = []
            for pid, pvar in self.player_vars.items():
                pvar.set(True)
                self.selected_players.append(pid)
            self.bank_var.set(False)
    
    def on_player(self, player_id: int):
        if self.player_vars[player_id]:
            self.selected_players.append(player_id)
        else:
            try:
                self.selected_players.remove(player_id)
            except:
                pass

    def on_confirm(self):
        # GIVE LIST
        give_wheat, give_wood, give_sheep, give_brick, give_ore = self.get_give_values()

        give_list = []
        if give_wheat > 0:
            give_list.append((ResourceCards.WHEAT, give_wheat))
        if give_wood > 0:
            give_list.append((ResourceCards.WOOD, give_wood))
        if give_sheep > 0:
            give_list.append((ResourceCards.SHEEP, give_sheep))
        if give_brick > 0:
            give_list.append((ResourceCards.BRICK, give_brick))
        if give_ore > 0:
            give_list.append((ResourceCards.ORE, give_ore))

        # WANT LIST
        want_wheat, want_wood, want_sheep, want_brick, want_ore = self.get_want_values()

        want_list = []
        if want_wheat > 0:
            want_list.append((ResourceCards.WHEAT, want_wheat))
        if want_wood > 0:
            want_list.append((ResourceCards.WOOD, want_wood))
        if want_sheep > 0:
            want_list.append((ResourceCards.SHEEP, want_sheep))
        if want_brick > 0:
            want_list.append((ResourceCards.BRICK, want_brick))
        if want_ore > 0:
            want_list.append((ResourceCards.ORE, want_ore))
            
        self.ui_state.set_state(UIStates.INGAME)
        self.master.clear_trade()
        self.game.offer_trade(give_list, want_list, self.selected_players)

    def on_cancel(self):
        self.ui_state.set_state(UIStates.INGAME)
        self.master.clear_trade()

class AcceptTradeFrame(tk.LabelFrame):
    def __init__(self, master: tk.Frame, game: Game, ui_state: CatanUIState):
        super().__init__(master, text='Accept or Decline Trade')
        self.master = master
        self.game = game
        self.ui_state = ui_state

        self.accept_button = tk.Button(self, command=self.on_accept, width=10, text='Accept')
        self.decline_button = tk.Button(self, command=self.on_decline, width=10, text='Decline')
        self.accept_button.grid(row=0, column=0)
        self.decline_button.grid(row=0, column=1)

    def on_accept(self):
        self.master.clear_accept_trade()
        self.game.accept_trade()

    def on_decline(self):
        self.master.clear_accept_trade()
        self.game.decline_trade()
    
class ConfirmTradeFrame(tk.LabelFrame):
    def __init__(self, master: tk.Frame, game: Game, ui_state: CatanUIState):
        super().__init__(master, text='Choose player to trade with')
        self.master = master
        self.game = game
        self.ui_state = ui_state

        players = self.game.players_accepted_trade
        for p in players:
            b = tk.Button(self, command=lambda I=p.identifier: self.on_button(I), width=10, text=str(p))
            b.pack()

    def on_button(self, player_id: int):
        self.game.confirm_trade(player_id)