import click
import tkinter as tk
from pytan.gym.environments import CatanEnv
from pytan.gym.agents import Human, RandomAgent, GreedyAgent
from pytan.core.game import Game
from pytan.core.player import Player
from pytan.ui.guis import LeftSide, RightSide, ReplayGUI
from pytan.ui.state import CatanUIState, GameStates
from pytan.ui.board import BoardFrame
from pytan.log.replay import Replay
from pytan.log.logging import Logger
import threading
import time
import os

bot_types = {
    'random': RandomAgent,
    'greedy': GreedyAgent
}

colors = ['red', 'white', 'blue', 'orange']

@click.command()
@click.option('--human', '-h', multiple=True, type=str, help='Human player to add by name')
@click.option('--bot', '-b', multiple=True, type=click.Choice(list(bot_types.keys())), help='Select the bot algorithm to add')
@click.option('--replay_file', '-rf', default=None, type=str, help='Replay log file')
@click.option('--simulate', '-s', type=int, help='Number of games to simulate')
def main(human, bot, replay_file, simulate):
    n_players = len(human) + len(bot)
    if n_players < 2:
        raise RuntimeError('Need atleast 2 players')
    elif n_players > 4:
        raise RuntimeError('Maximum 4 players')

    bot_game = any(bot)
    human_game = any(human)
    human_only_game = human_game and not bot_game
    
    if replay_file and (bot_game or human_game or simulate):
        raise RuntimeError('Cannot play replay and run game at the same time')

    if human_game and simulate:
        raise RuntimeError('Cannot simulate for human games')

    if replay_file:
        if not os.path.exists(replay_file):
            raise RuntimeError('Replay log file does not exist')
        if replay_file.split('.')[-1] != 'catan':
            raise RuntimeError('Use a valid .catan log file')

        replay = Replay(replay_file)
        app = tk.Tk()
        replaygui = ReplayGUI(app, replay)
        replaygui.pack()
        app.mainloop()
    else:
        
        if human_game:
            print('Humans: ', human)
        if bot_game:
            print('Bots: ', bot)

        if human_only_game:
            players = [Player(h, i, colors[i]) for i, h in enumerate(human)]
            game = Game(players=players, logger=Logger(console_log=False))
        else:
            agents = []
            i = 0
            for h in human:
                agents.append(Human(Player(h, i, colors[i])))
                i += 1
            for b in bot:
                agents.append(bot_types[b](Player(b, i, colors[i])))
                i += 1

            env = CatanEnv(agents=agents, logger=Logger(console_log=False))
            game = env.game

        if not simulate:
        
            def bot_loop():
                while True:
                    current_player_id = env.game.current_player.id
                    agent = env.agents[current_player_id]
                    if agent.bot:
                        action = agent.choose_action(env.legal_actions, env.game.get_state())
                        env.step(action)
                    time.sleep(0.5)
            
            ui_state = CatanUIState(game)
                
            app = tk.Tk()
            left_side = LeftSide(app, game, ui_state)
            right_side = RightSide(app, game, ui_state)
            left_side.pack(side=tk.LEFT)
            right_side.pack(side=tk.RIGHT, fill=tk.Y)

            if not human_only_game:
                bot_thread = threading.Thread(target=bot_loop, daemon=True)
                bot_thread.start()

            app.mainloop()
        else:
            start = time.time()
            turns = []
            wins = [0,0,0,0]
            for i in range(simulate):
                game.start_game(randomize=True)
                while True:
                    if game.state == GameStates.GAME_OVER or game.turn > 250:
                        break
                    actions = env.legal_actions
                    action = env.current_player.choose_action(actions, game.get_state())
                    env.step(action)
                turns.append(game.turn)
                vp = [player.total_victory_points for player in game.players]
                winner = vp.index(max(vp))
                wins[winner] += 1
                print(f'\rGame: {i+1} - {vp} - turns: {game.turn}     ',end='')
            avg_t = sum(turns)//len(turns)

            lapse = round(time.time() - start, 2)
            print(f'\nWins: {wins} - avg turns: {avg_t} - took {lapse} seconds')