import click
import tkinter as tk
from pytan.gym.environments import CatanEnv
from pytan.gym.agents import Human, RandomAgent, GreedyAgent
from pytan.core.player import Player
from pytan.ui.guis import LeftSide, RightSide
from pytan.ui.state import CatanUIState, GameStates
from pytan.ui.board import BoardFrame
from pytan.log.logging import Logger
import threading
import time

@click.command()
@click.option('--players', '-p', default=4, help='Number of players')
@click.option('--bot', '-b', is_flag=True, help='Play bot game')
@click.option('--replay', default=None, type=str, help='Replay log file')
def main(players, bot, replay):
    logger = Logger(console_log=False)
    agents = [
        GreedyAgent(Player('P1', 0, 'red')),
        RandomAgent(Player('P2', 1, 'blue')),
        RandomAgent(Player('P3', 2, 'white')),
        RandomAgent(Player('P4', 3, 'orange'))
    ]
    env = CatanEnv(agents = agents, logger = logger)
    game = env.game

    #root = tk.Tk()
    #board = BoardFrame(root, game)
    #board.redraw()
    #board.pack()

    start = time.time()

    turns = []
    wins = [0,0,0,0]
    for i in range(100):
        game.start_game(randomize=True)
        while True:
            if game.state == GameStates.GAME_OVER or game.turn > 250:
                break
            actions = env.legal_actions
            action = env.current_player.choose_action(actions, game)
            env.step(action)
            #root.update()
        turns.append(game.turn)
        vp = [player.total_victory_points for player in game.players]
        winner = vp.index(max(vp))
        wins[winner] += 1
        print(f'\rGame: {i+1} - {vp} - turns: {game.turn}     ',end='')
    avg_t = sum(turns)//len(turns)

    lapse = round(time.time() - start, 2)

    print(f'\nWins: {wins} - avg turns: {avg_t} - took {lapse} seconds')