import tkinter as tk
from pytan.core.game import Game
from pytan.ui.frames import BoardFrame, GameControlsFrame
from pytan.ui.state import CatanUIState


class CatanGUI(tk.Frame):
    def __init__(self):
        super().__init__()

        game = Game()
        ui_state = CatanUIState(game)

        board_frame = BoardFrame(self, game, ui_state)
        controls_frame = GameControlsFrame(self, game, ui_state)

        board_frame.grid(row=0, column=0, sticky=tk.NSEW)
        controls_frame.grid(row=0, column=1, sticky=tk.NW)

        board_frame.redraw()

        game.start_game()

if __name__ == '__main__':
        
    app = CatanGUI()
    app.mainloop()