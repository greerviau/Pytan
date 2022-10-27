import click

@click.command()
@click.option('--players', '-p', default=4, help='Number of players')
@click.option('--bot', '-p', default=4, help='Number of players')
def main():
    print('Main')