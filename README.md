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
from pytan.core.cards import ResourceCards as RC

catan = Game()
catan.start_game()
catan.build_settlement(0x67)
catan.build_road(0x67)
...
catan.pass_turn()
catan.roll()
...
catan.roll(7)
catan.discard([(RC.WHEAT,2), (RC.WOOD,1), (RC,ORE,3)])
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
```

## TODO
- [x] Seperate Game States and UI States
- [ ] Complete Core Gameplay Logic
- [x] Complete State Management
- [x] Complete GUI
- [ ] Build GYM Environment for RL

## References
Shoutout to [rosshamish](https://github.com/rosshamish) for building some very usefull Catan projects that I referenced to help build this project. None of these were utilized directly because some features were out of date (and I wanted to build it myself anyway), but they were super helpful in understanding some of the underlying logic in building Catan.

* HexMesh implementation based on [rosshamish/hexgrid](https://github.com/rosshamish/hexgrid)
* Catan gameplay logic referenced from [rosshamish/catan-py](https://github.com/rosshamish/catan-py)
* GUI elements inspired and referenced from [rosshamish/catan-spectator](https://github.com/rosshamish/catan-spectator)

