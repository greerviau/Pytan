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

