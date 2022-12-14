from pytan.core.player import Player
from pytan.core.state import GameStates
from pytan.gym.environments import CatanEnv
from pytan.gym.agents import GreedyAgent, RandomAgent
from pytan.ui.board import BoardFrame
from pytan.log.logging import Logger
import tkinter as tk

if __name__ == '__main__':
    logger = Logger(console_log=False)
    agents = [
        GreedyAgent(Player('P1', 0, 'red')),
        RandomAgent(Player('P2', 1, 'blue')),
        RandomAgent(Player('P3', 2, 'white')),
        RandomAgent(Player('P4', 3, 'orange'))
    ]
    game = CatanEnv(agents = agents, logger=False)
    game.start_game()

    root = tk.Tk()
    board = BoardFrame(root, game)
    board.redraw()
    board.pack()

    turns = []
    wins = [0,0,0,0]
    for i in range(100):
        game.start_game(randomize=True)
        while True:
            if game.state == GameStates.GAME_OVER or game.turn > 250:
                break
            game.step()
            root.update()
        turns.append(game.turn)
        vp = [player.total_victory_points for player in game.players]
        winner = vp.index(max(vp))
        wins[winner] += 1
        print(f'\rGame: {i+1} - {vp} - turns: {game.turn}     ',end='')
    avg_t = sum(turns)//len(turns)
    print(f'\nWins: {wins} - avg turns: {avg_t}')