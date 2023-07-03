import tkinter as tk
from pytan.core.game import Game
from pytan.ui.guis import BoardAndPlayerLabel, ControlsAndLog
from pytan.ui.state import CatanUIState

if __name__ == '__main__':
    game = Game()
    ui_state = CatanUIState(game)
        
    app = tk.Tk()
    left_side = BoardAndPlayerLabel(app, game, ui_state)
    right_side = ControlsAndLog(app, game, ui_state)
    left_side.pack(side=tk.LEFT)
    right_side.pack(side=tk.RIGHT, fill=tk.Y)

    app.mainloop()
    