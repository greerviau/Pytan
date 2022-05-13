# Pytan
A python implementation of settlers of Catan

## Installation
```
git clone https://github.com/greerviau/Pytan.git
python3 -m pip install -e ./Pytan
```

## Usage
### Core Game
```python
from pytan.core.game import Game

catan_game = Game()
catan_game.start_game()
catan_game.build_settlement(0x67)
catan_game.build_road(0x67)

catan_game.pass_turn()
catan_game.roll() # catan_game.roll(6)

catan_game.end_game(log=True)
```

### UI
```
python3 ./pytan/ui/guis.py
```

OR

```python
from pytan.ui.guis import CatanGUI

gui = CatanGUI()
gui.mainloop()
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
