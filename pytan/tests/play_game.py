import tkinter as tk
from pytan.core.game import Game
from pytan.ui.board import BoardFrame
from pytan.ui.controls import GameControlsFrame, PlayerLabelFrame, LogFrame
from pytan.ui.state import CatanUIState

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

def main():
    game = Game()
    ui_state = CatanUIState(game)
        
    app = tk.Tk()
    left_side = LeftSide(app, game, ui_state)
    right_side = RightSide(app, game, ui_state)
    left_side.pack(side=tk.LEFT)
    right_side.pack(side=tk.RIGHT, fill=tk.Y)

    app.mainloop()
    