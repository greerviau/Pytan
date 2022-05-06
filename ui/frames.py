import tkinter as tk

class BoardFrame(tk.Frame):
    def __init__(self, master, game, *args, **kwargs):
        super(BoardFrame, self).__init__()
        self.master = master
        self.game = game

        self._board = game.board

        
        self._board_canvas = tk.Canvas(root, height=600, width=600, bg='Royal Blue')
        self._board_canvas.pack(expand=tk.YES, fill=tk.BOTH)

    def notify(self, observable):
        self.redraw()

    def draw(self, board):
        # TODO

class GameControlsFrame(tk.Frame):
    def __init__(self, master, game, *args, **kwargs):
        super(ControlsFrame, self).__init__()
        self.master = master
        self.game = game

        roll_button = tk.Button(self, text='Roll Dice')
        build_frame = tk.LabelFrame(self, text='Build', bg='white')

        roll_button.pack(pady=20)
        build_frame.pack()

        build_road_button = tk.Button(build_frame, width=15, text='Road')
        build_settlement_button = tk.Button(build_frame, width=15, text='Settlement')
        upgrade_city_button = tk.Button(build_frame, width=15, text='City')
        build_dev_card_button = tk.Button(build_frame, width=15, text='Dev Card')

        build_road_button.grid(row=0, column=0)
        build_settlement_button.grid(row=0, column=1)
        upgrade_city_button.grid(row=1, column=0)
        build_dev_card_button.grid(row=1, column=1)