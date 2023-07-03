import click
import tkinter as tk
import threading
import time
import os

from pytan.gym.environments import CatanEnv
from pytan.gym.agents import Human, RandomAgent, GreedyAgent
from pytan.core.game import Game
from pytan.core.player import Player
from pytan.ui.guis import BoardAndPlayerLabel, ControlsAndLog, ReplayGUI
from pytan.ui.state import CatanUIState, GameStates
from pytan.log.replay import Replay
from pytan.log.logging import Logger

bot_types = {
    'random': RandomAgent,
    'greedy': GreedyAgent
}

colors = ['red', 'white', 'blue', 'orange']

def help_menu():
    print('Hi')

def play_replay_file(replay_file):
    if not os.path.exists(replay_file):
        raise RuntimeError('Replay log file does not exist')
    if replay_file.split('.')[-1] != 'catan':
        raise RuntimeError('Use a valid .catan log file')

    replay = Replay(replay_file)
    app = tk.Tk()
    replaygui = ReplayGUI(app, replay)
    replaygui.pack()
    app.mainloop()

def setup_catan_env(human_player, bot, log):
    agents = []
    i = 0
    for h in human_player:
        agents.append(Human(Player(h, i, colors[i])))
        i += 1
    for b in bot:
        agents.append(bot_types[b](Player(b, i, colors[i])))
        i += 1

    env = CatanEnv(agents=agents, logger=Logger(log_file=(log if log else None), console_log=False))
    return env

def run_human_game(env, human_only_game):
    game = env.game
    
    ui_state = CatanUIState(game)
        
    app = tk.Tk()
    left_side = BoardAndPlayerLabel(app, game, ui_state)
    right_side = ControlsAndLog(app, game, ui_state)
    left_side.pack(side=tk.LEFT)
    right_side.pack(side=tk.RIGHT, fill=tk.Y)

    def bot_loop():
        current_player_id = env.game.current_player.id
        agent = env.agents[current_player_id]
        if agent.bot:
            action = agent.choose_action(env)
            env.step(action)
        app.after(500, bot_loop)

    game.start_game()

    if not human_only_game:
        bot_loop()
    app.mainloop()

def simulate_game(env):
    game = env.game
    game.start_game(randomize=True)
    while True:
        if game.state == GameStates.GAME_OVER:
            break
        action = env.current_player.choose_action(env)
        env.step(action)

def simulate_n_games(env, n_games):
    game = env.game
    start = time.time()
    turns = []
    wins = [0 for i in range(game.n_players)]
    for i in range(n_games):
        simulate_game(env)
        turns.append(game.turn)
        vp = [player.total_victory_points for player in game.players]
        winner = vp.index(max(vp))
        wins[winner] += 1
        print(f'\rGame: {i+1} - {vp} - turns: {game.turn}     ',end='')
    avg_t = sum(turns)//len(turns)

    lapse = round(time.time() - start, 2)
    print(f'\n\nWins: {wins}')
    print(f'avg turns: {avg_t}')
    print(f'took {lapse} seconds')

@click.command()
@click.option('--human_player', '-hp', multiple=True, type=str, help='Human player to add by name')
@click.option('--bot', '-b', multiple=True, type=click.Choice(list(bot_types.keys())), help='Select the bot algorithm to add')
@click.option('--replay_file', '-r', default=None, type=str, help='Replay log file')
@click.option('--simulate', '-s', type=int, help='Number of games to simulate')
@click.option('--log', '-l', type=str, help='Output log file')
@click.option('--help', '-h', is_flag=True, help='Help menu')
def main(human_player, bot, replay_file, simulate, log, help):
    if help:
        help_menu()
        return
    n_players = len(human_player) + len(bot)
    bot_game = any(bot)
    human_game = any(human_player)
    human_only_game = human_game and not bot_game

    if log and '.catan' not in log:
        raise RuntimeError('Log file must be .catan format')
    
    if simulate and log:
        raise RuntimeError('Cannot log simulated games')
    
    if replay_file and (bot_game or human_game or simulate):
        raise RuntimeError('Cannot play replay and run game at the same time')

    if human_game and simulate:
        raise RuntimeError('Cannot simulate for human_player games')

    if replay_file:
        play_replay_file(replay_file)
    else:
        if n_players < 2:
            raise RuntimeError('Need atleast 2 players')
        elif n_players > 4:
            raise RuntimeError('Maximum 4 players')
        
        if human_game:
            print('Humans: ', human_player)
        if bot_game:
            print('Bots: ', bot)

        env = setup_catan_env(human_player, bot, log)

        if not simulate:
            if human_game:
                run_human_game(env, human_only_game)
            else:
                simulate_game(env)
                print(f'Logs saved to {env.game.logger.log_file_path}')
                env.game.logger.save_raw_log_file()
                play_replay_file(env.game.logger.log_file_path)
        else:
            simulate_n_games(env, simulate)