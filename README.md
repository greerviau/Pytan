# Pytan
A Python implementation of Settlers of Catan

## Installation
```
git clone https://github.com/greerviau/Pytan.git
python3 -m pip install -e ./Pytan
```

## Usage
### Core Game
```python
from pytan.core.game import Game

catan = Game()
catan.start_game()
catan.build_settlement(0x67)
catan.build_road(0x67)
...
catan.pass_turn()
catan.roll() # catan_game.roll(6)
...
catan.roll(7)
catan.discard([('WHEAT',2), ('WOOD',1), ('ORE',3)])
catan.move_robber(0x11)
catan.steal(1) # player id
...
catan.end_game(log=True)
```

### UI
```
python3 ./pytan/ui/gui.py
```

Or write custom gui elements

```python
import tkinter as tk
from pytan.core.game import Game
from pytan.ui.frames import BoardFrame, GameControlsFrame


class CatanGUI(tk.Frame):
    def __init__(self):
        super().__init__()

        game = Game()

        board_frame = BoardFrame(self, game)
        controls_frame = GameControlsFrame(self, game)

        board_frame.grid(row=0, column=0, sticky=tk.NSEW)
        controls_frame.grid(row=0, column=1, sticky=tk.NW)

        board_frame.redraw()

        game.start_game()

if __name__ == '__main__':
        
    app = CatanGUI()
    app.mainloop()
```

## TODO
* Complete Core Gameplay Logic
* Complete State Management
* Complete GUI
* Build GYM Environment for RL

## References
Shoutout to [rosshamish](https://github.com/rosshamish) for building some very usefull Catan projects that I referenced to help build this project. None of these were utilized directly because some features were out of date (and I wanted to build it myself anyway), but they were super helpful in understanding some of the underlying logic in building Catan.

* HexMesh implementation based on [rosshamish/hexgrid](https://github.com/rosshamish/hexgrid)
* Catan gameplay logic referenced from [rosshamish/catan-py](https://github.com/rosshamish/catan-py)
* GUI elements inspired and referenced from [rosshamish/catan-spectator](https://github.com/rosshamish/catan-spectator)

