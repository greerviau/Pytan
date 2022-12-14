from pytan.ui.board import BoardFrame
from pytan.ui.controls import GameControlsFrame, PlayerLabelFrame, LogFrame, ReplayControl
from pytan.ui.state import CatanUIState, UIStates
import tkinter as tk

class LeftSide(tk.Frame):
    def __init__(self, master, game, ui_state):
        tk.Frame.__init__(self, master)

        player_label_frame = PlayerLabelFrame(self, game, ui_state)
        board_frame = BoardFrame(self, game, ui_state)
        player_label_frame.pack(pady=5, padx=5, anchor=tk.NW)
        board_frame.pack()

        board_frame.redraw()

class RightSide(tk.Frame):
    def __init__(self, master, game, ui_state):
        tk.Frame.__init__(self, master)

        self.game = game

        controls_frame = GameControlsFrame(self, game, ui_state)
        log_frame = LogFrame(self, game, ui_state, height=12)
        controls_frame.pack(pady=10, fill=tk.X, side=tk.TOP)
        log_frame.pack(side=tk.BOTTOM, fill=tk.X)

        game.start_game()

class ReplayGUI(tk.Frame):
    def __init__(self, master, replay):
        tk.Frame.__init__(self, master)

        game = replay.game

        ui_state = CatanUIState(game)
        ui_state.set_state(UIStates.INGAME)

        player_label_frame = PlayerLabelFrame(self, game, ui_state)
        self.replay_frame = ReplayControl(self, replay)
        board_frame = BoardFrame(self, game, ui_state, interact=False)
        log_frame = LogFrame(self, game, ui_state, height=46)

        player_label_frame.grid(row=0, column=0, sticky=tk.NW)
        self.replay_frame.grid(row=0, column=1)
        board_frame.grid(row=1, column=0)
        log_frame.grid(row=1, column=1)

        board_frame.redraw()