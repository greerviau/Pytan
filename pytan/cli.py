import click
from pytan.tests import bot_game, play_game, replay, sim_game

@click.command()
@click.option('--players', '-p', default=4, help='Number of players')
@click.option('--bot', '-b', is_flag=True, help='Play bot game')
@click.option('--replay', default=None, type=str, help='Replay log file')
def main(players, bot, replay):
    pass