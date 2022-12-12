from pytan.ui.guis import ReplayGUI
from pytan.log.replay import Replay
import tkinter as tk
import sys

if __name__ == '__main__':
    
    log_file = sys.argv[1]
    replay = Replay(log_file)
    app = tk.Tk()
    replaygui = ReplayGUI(app, replay.game)
    replaygui.pack()
    app.mainloop()