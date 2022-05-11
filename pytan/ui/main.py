import tkinter as tk
from constants import *
from pytan.core.board import Board
from pytan.core.game import Game
from frames import BoardFrame, GameControlsFrame


class CatanGUI(tk.Frame):
    def __init__(self, options=None, *args, **kwargs):
        super(CatanGUI, self).__init__()

        self.game = Game()
        self.game.start_game()
        self.game.build_starting_settlement(0x67)
        self.game.build_starting_road(0x67)
        print(self.game.board)

        self._board_frame = BoardFrame(self, self.game)
        self._controls_frame = GameControlsFrame(self, self.game)

        self._board_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self._controls_frame.grid(row=0, column=1, sticky=tk.NW)

        self._board_frame.redraw()

if __name__ == '__main__':
        
    app = CatanGUI()
    app.mainloop()