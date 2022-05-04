import tkinter as tk
from constants import *

root = tk.Tk()
root.title('Catan')
root.geometry('900x600')

board_canvas = tk.Canvas(root, height=600, width=600, bg=HEX_COLORS['black'])
controls_frame = tk.Frame(root, height=600, width=300, bg=HEX_COLORS['white'])

# layout all of the main containers
root.grid_columnconfigure(0, weight=2)
root.grid_columnconfigure(1, weight=1)

board_canvas.grid(row=0, column=0, sticky='w')
controls_frame.grid(row=0, column=1, sticky='e')

roll_button = tk.Button(controls_frame, text='Roll Dice')
#actions = LabelFrame(controls_frame, text='Actions', bg='white')

roll_button.pack()
#actions.pack()


while 1:
    try:
        root.update()
    except (KeyboardInterrupt, TclError):
        exit()