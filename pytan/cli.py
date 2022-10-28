import click
from pytan.ui.tests import bot_game, play_game, replay

@click.command()
@click.option('--players', '-p', default=4, help='Number of players')
@click.option('--bot', '-b', is_flag=True, help='Play bot game')
@click.option('--replay', default=None, type=str, 'Replay file')
def main(players, bot, replay):

    