# Pytan
A Python implementation of Settlers of Catan

## Installation
```
pip install git+https://github.com/greerviau/Pytan.git
```

If developing use

```
git clone https://github.com/greerviau/Pytan.git && cd Pytan
pip install -e .
```

## Usage
### CLI
#### Arguments
```
-hp : Human Player {name}           | eg. -hp Bill
-b  : Bot {agent} (random, greedy)  | eg -b greedy
-s  : Simulate {n} (n games)        | eg -s 10
-r  : Replay {file} (.catan format) | eg -r test_log.catan
```
#### CLI Examples
Simulate 100 games between a 4 bot agents, 3 random and 1 greedy
```
pytan -b random -b random -b random -b greedy -s 100
```
Play a game with 1 human against 3 greedy agents
```
pytan -hp Bill -b greedy -b greedy -b greedy
```
Play a bot only game with 2 greedy agents and replay it 
```
pytan -b greedy -b greedy
```
Replay a specific log file
```
pytan -r test_log.catan
```
### Core Game
```python
from pytan.core.game import Game
from pytan.core.cards import ResourceCards as RC

catan = Game()
# or specity players
from pytan.core.player import Player
players = [
    # name, color, id (must be unique)
    Player('jim', 'blue', 0),
    Player('gary', 'green', 1),
    Player('zach', 'red', 2),
    Player('robert', 'orange', 3)
]
catan = Game(players=players)
catan.start_game()
catan.build_settlement(0x67)
catan.build_road(0x67)
...
catan.roll()
catan.pass_turn()
...
# Build City
catan.build_city(0x67)
...
# Roll 7, discard and move robber
catan.roll(7)
catan.discard([(RC.WHEAT,2), (RC.WOOD,1), (RC.ORE,3)])
catan.move_robber(0x11)
catan.steal(1) # player id
...
# Trading
catan.offer_trade([(RC.WHEAT, 1)], [(RC.WOOD, 1)], [0,1,3]) # params(offer, want, player_ids)
# player (0) turn, accept/decline trade?
catan.decline_trade()
# player (1) turn, accept/decline trade?
catan.accept_trade()
# player (3) turn, accept/decline trade?
catan.accept_trade()
# player (2) turn, trade with player (1) or player (3)?
catan.confirm_trade(1)
# player (2) traded 1 WHEAT to player(1) for 1 WOOD

# Trade with the Bank
# offer amount can be adjusted if player is on a port
catan.offer_trade([(RC.WHEAT, 4)], [(RC.WOOD, 1)], []) # leave player_ids empty
# player (2) traded 3 WHEAT to the Bank for 1 WOOD
...
# Dev Cards
catan.buy_dev_card()
catan.play_knight()
catan.play_monopoly(RC.WHEAT)
catan.play_year_plenty(RC.WOOD, RC.BRICK)
catan.play_road_builder()
...
catan.end_game(log=True)
```

### Bot Environment
```python
from pytan.core.player import Player
from pytan.ai.agents import RandomAgent, GreedyAgent
from pytan.ai.env CatanEnv

players = [
    RandomAgent(Player('Random1', 0, 'red')),
    RandomAgent(Player('Random2', 1, 'blue')),
    RandomAgent(Player('Random3', 2, 'white')),
    GreedyAgent(Player('Greedy', 3, 'orange'))
]

env = CatanEnv(players)

while True:
    current_player_id = env.game.current_player.id
    agent = env.agents[current_player_id]
    if agent.bot:
        action = agent.choose_action(env)
        env.step(action)
```

### UI
```
python3 ./pytan/ui/tests/play_game.py
```

Or write custom gui elements

```python
import tkinter as tk
from pytan.core.game import Game
from pytan.ui.board import BoardFrame
from pytan.ui.controls import GameControlsFrame
from pytan.ui.state import CatanUIState


class CatanGUI(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        game = Game()
        ui_state = CatanUIState(game)

        board_frame = BoardFrame(self, game, ui_state)
        controls_frame = GameControlsFrame(self, game, ui_state)

        board_frame.grid(row=0, column=0, sticky=tk.NSEW)
        controls_frame.grid(row=0, column=1, sticky=tk.NW)

        board_frame.redraw()

        game.start_game()

if __name__ == '__main__':
        
    app = tk.Tk()
    gui = CatanGUI(app)
    gui.pack()
    app.mainloop()
```

## TODO
- [x] Seperate Game States and UI States
- [x] Complete Core Gameplay Logic
- [x] Complete State Management
- [x] Complete GUI
- [x] Build Replay System
- [ ] Build GYM Environment for RL
- [x] Fix replay (currently broken)
## References
Shoutout to [rosshamish](https://github.com/rosshamish) for building some very usefull Catan projects that I referenced to help build this project. None of these were utilized directly because some features were out of date (and I wanted to build it myself anyway), but they were super helpful in understanding some of the underlying logic in building Catan.

* HexMesh implementation based on [rosshamish/hexgrid](https://github.com/rosshamish/hexgrid)
* Catan gameplay logic referenced from [rosshamish/catan-py](https://github.com/rosshamish/catan-py)
* GUI elements inspired and referenced from [rosshamish/catan-spectator](https://github.com/rosshamish/catan-spectator)

