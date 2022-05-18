import tkinter as tk
import tkutils
import math
import functools
from pytan.core.piece import Piece, PieceTypes
from pytan.core.state import GameStates
from pytan.core import hexmesh
from pytan.core.hexmesh import Directions
from pytan.core.cards import ResourceCards, DevCards

tk_status = {
    True: tk.NORMAL,
    False: tk.DISABLED,
    None: tk.DISABLED
}

class BoardFrame(tk.Frame):
    def __init__(self, master, game):
        super().__init__()
        self.master = master
        self.game = game
        self.game.add_observer(self)

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
        
        if self.game.state != GameStates.UNDEFINED:
            self._draw_ports(board, terrain_centers)    
        
        self._draw_pieces(board, terrain_centers)
        if self.game.state.is_building_road():
            self._draw_piece_shadows(PieceTypes.ROAD, board, terrain_centers)
        if self.game.state.is_building_settlement():
            self._draw_piece_shadows(PieceTypes.SETTLEMENT, board, terrain_centers)
        if self.game.state.is_building_city():
            self._draw_piece_shadows(PieceTypes.CITY, board, terrain_centers)
        if self.game.state.is_moving_robber():
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
        y -= 2
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
    def __init__(self, master, game):
        super().__init__()
        self.master = master
        self.game = game
        self.game.add_observer(self)
        
        player_label_frame = PlayerLabelFrame(self, game)
        dice_sides_frame = DiceSidesFrame(self, game)
        action_frame = ActionFrame(self, game)
        build_frame = BuildFrame(self, game, text='Build')

        player_label_frame.pack(pady=5, anchor='w')
        dice_sides_frame.pack(pady=5)
        action_frame.pack(pady=5)
        build_frame.pack(pady=5)

    def notify(self, observable):
        #TODO
        pass

class PlayerLabelFrame(tk.Frame):
    def __init__(self, master, game):
        super().__init__(master)

        self.master = master
        self.game = game
        self.game.add_observer(self)

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
                if n > 0:
                    s += ' '
                    if n > 1:
                        s += f'{n}x'
                    s += f'{card.value}'
            player_s.set(s)

    def notify(self, observable):
        self.set_player_labels()

class DiceSidesFrame(tk.Frame):
    def __init__(self, master, game):
        super().__init__(master)
        
        self.master = master
        self.game = game
        self.game.add_observer(self)

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
        self.roll_two_button.configure(state=tk_status[self.game.state.can_roll()])
        self.roll_three_button.configure(state=tk_status[self.game.state.can_roll()])
        self.roll_four_button.configure(state=tk_status[self.game.state.can_roll()])
        self.roll_five_button.configure(state=tk_status[self.game.state.can_roll()])
        self.roll_six_button.configure(state=tk_status[self.game.state.can_roll()])
        self.roll_seven_button.configure(state=tk_status[self.game.state.can_roll()])
        self.roll_eight_button.configure(state=tk_status[self.game.state.can_roll()])
        self.roll_nine_button.configure(state=tk_status[self.game.state.can_roll()])
        self.roll_ten_button.configure(state=tk_status[self.game.state.can_roll()])
        self.roll_eleven_button.configure(state=tk_status[self.game.state.can_roll()])
        self.roll_twelve_button.configure(state=tk_status[self.game.state.can_roll()])

    def on_roll(self, roll):
        self.game.roll(roll)
        self.set_states()

class ActionFrame(tk.Frame):
    def __init__(self, master, game):
        super().__init__(master)

        self.master = master
        self.game = game
        self.game.add_observer(self)

        self.roll_button = tk.Button(self, command=lambda:self.on_dice_roll(), text='Roll Dice')
        self.pass_turn_button = tk.Button(self, command=lambda:self.on_pass_turn(), text='Pass Turn')

        self.roll_button.grid(row=0, column=0)
        self.pass_turn_button.grid(row=0, column=1)

    def notify(self, observable):
        self.set_states()
    
    def set_states(self):
        self.roll_button.configure(state=tk_status[self.game.state.can_roll()])
        self.pass_turn_button.configure(state=tk_status[self.game.state.can_pass_turn()])
    
    def on_dice_roll(self):
        self.game.roll()
        self.set_states()

    def on_pass_turn(self):
        self.game.pass_turn()
        self.set_states()

class BuildFrame(tk.LabelFrame):
    def __init__(self, master, game, text=''):
        super().__init__(master, text=text)

        self.master = master
        self.game = game
        self.game.add_observer(self)

        self.build_road_button = tk.Button(self, command=lambda:self.on_build_road(), width=10, text='Road')
        self.build_settlement_button = tk.Button(self, command=lambda:self.on_build_settlement(), width=10, text='Settlement')
        self.upgrade_city_button = tk.Button(self, command=lambda:self.on_build_city(), width=10, text='City')
        self.buy_dev_card_button = tk.Button(self, command=lambda:self.on_buy_dev_card(), width=10, text='Dev Card')

        self.build_road_button.grid(row=0, column=0)
        self.build_settlement_button.grid(row=0, column=1)
        self.upgrade_city_button.grid(row=1, column=0)
        self.buy_dev_card_button.grid(row=1, column=1)

    def notify(self, observable):
        self.set_states()

    def set_states(self):
        self.build_road_button.configure(state=tk_status[self.game.state.can_build_road()])
        self.build_settlement_button.configure(state=tk_status[self.game.state.can_build_settlement()])
        self.upgrade_city_button.configure(state=tk_status[self.game.state.can_build_city()])
        self.buy_dev_card_button.configure(state=tk_status[self.game.state.can_buy_dev_card()])

    def on_build_road(self):
        self.game.start_building(PieceTypes.ROAD)
        self.set_states()

    def on_build_settlement(self):
        self.game.start_building(PieceTypes.SETTLEMENT)
        self.set_states()

    def on_build_city(self):
        self.game.start_building(PieceTypes.CITY)
        self.set_states()
    
    def on_buy_dev_card(self):
        self.game.buy_dev_card()
        self.set_states()