import tkinter as tk
from pytan.core.game import Game
from pytan.ui.board import BoardFrame
from pytan.ui.controls import GameControlsFrame, PlayerLabelFrame, LogFrame
from pytan.ui.state import CatanUIState

class Section1(tk.Frame):
    def __init__(self, master, game, ui_state):
        tk.Frame.__init__(self, master)

        player_label_frame = PlayerLabelFrame(self, game, ui_state)
        board_frame = BoardFrame(self, game, ui_state)
        player_label_frame.pack(anchor=tk.NW)
        board_frame.pack()

        board_frame.redraw()

class Section2(tk.Frame):
    def __init__(self, master, game, ui_state):
        tk.Frame.__init__(self, master)

        controls_frame = GameControlsFrame(self, game, ui_state)
        log_frame = LogFrame(self, game, ui_state)
        controls_frame.pack(pady=10, fill=tk.X, side=tk.TOP)
        log_frame.pack(side=tk.BOTTOM, fill=tk.X)

        game.start_game()

if __name__ == '__main__':

    game = Game()
    ui_state = CatanUIState(game)
        
    app = tk.Tk()
    section_1 = Section1(app, game, ui_state)
    section_2 = Section2(app, game, ui_state)
    section_1.pack(side=tk.LEFT)
    section_2.pack(side=tk.RIGHT, fill=tk.Y)

    app.mainloop()