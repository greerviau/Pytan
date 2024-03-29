import tkinter as tk
from pytan.ai.env import CatanEnv
from pytan.ai.agents import Human, RandomAgent, GreedyAgent
from pytan.core.player import Player
from pytan.ui.guis import BoardAndPlayerLabel, ControlsAndLog
from pytan.ui.state import CatanUIState
import threading
import time

if __name__ == '__main__':

    players = [
        Human(Player('Hooman', 0, 'red')),
        GreedyAgent(Player('Greed', 1, 'blue')),
        GreedyAgent(Player('Greed', 2, 'white')),
        RandomAgent(Player('Randotron', 3, 'orange'))
    ]

    env = CatanEnv(players)
    ui_state = CatanUIState(env.game)

    app = tk.Tk()
    left_side = BoardAndPlayerLabel(app, env.game, ui_state)
    right_side = ControlsAndLog(app, env.game, ui_state)
    left_side.pack(side=tk.LEFT)
    right_side.pack(side=tk.RIGHT, fill=tk.Y)
    
    def bot_loop():
        while True:
            current_player_id = env.game.current_player.id
            agent = env.agents[current_player_id]
            if agent.bot:
                action = agent.choose_action(env)
                env.step(action)
            app.after(500, bot_loop)
    bot_loop()

    app.mainloop()