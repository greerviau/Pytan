import tkinter as tk
from pytan.log.replay import Replay
from pytan.ui.board import BoardFrame
from pytan.ui.controls import PlayerLabelFrame, LogFrame, ReplayControl
from pytan.ui.state import CatanUIState, UIStates
import time
import threading


class ReplayGUI(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.replay = Replay('../../log/test_logs/bot_game_1.catan')
        game = self.replay.game
        ui_state = CatanUIState(game)
        ui_state.set_state(UIStates.INGAME)

        player_label_frame = PlayerLabelFrame(self, game, ui_state)
        self.replay_frame = ReplayControl(self, self.replay)
        board_frame = BoardFrame(self, game, ui_state, interact=False)
        log_frame = LogFrame(self, game, ui_state, height=46)

        player_label_frame.grid(row=0, column=0, sticky=tk.NW)
        self.replay_frame.grid(row=0, column=1)
        board_frame.grid(row=1, column=0)
        log_frame.grid(row=1, column=1)

        board_frame.redraw()

if __name__ == '__main__':
        
    app = tk.Tk()
    catangui = ReplayGUI(app)
    catangui.pack()
    app.mainloop()