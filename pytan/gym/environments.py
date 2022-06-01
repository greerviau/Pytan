from pytan.core.game import Game
from pytan.core.cards import ResourceCards
from pytan.core.state import GameStates
from pytan.core.trading import PortTypes
from pytan.gym.agents import BotAgent, RandomAgent, GreedyAgent
import random

class CatanEnv(Game):
    def __init__(self, players, logger):
        super().__init__(players=players, logger=logger)

    def get_valid_actions(self):
        actions = []
        actions.extend(self.get_valid_trades())
        if not any(actions):
            actions.extend(self.get_valid_build_actions())
        if self.state.can_roll():
            actions.append(('roll', [random.choice([2,3,4,5,6,8,9,10,11,12])]))
        if self.state.can_pass_turn() and not any(actions):
            actions.append(('pass_turn', []))
        return actions

    def get_valid_build_actions(self):
        actions = []
        if self.state.can_build_road() or self.state == GameStates.STARTING_ROAD:
            for coord in self.legal_road_placements():
                actions.append(('build_road', [coord]))
        if self.state.can_build_settlement() or self.state == GameStates.STARTING_SETTLEMENT:
            for coord in self.legal_settlement_placements():
                actions.append(('build_settlement', [coord]))
        if self.state.can_build_city():
            for coord in self.legal_city_placements():
                actions.append(('build_city', [coord]))
        return actions

    def get_valid_trades(self):
        trades = []
        if self.state.can_trade():
            for g_card in ResourceCards:
                e = 4
                if self._board.is_player_on_port(self.current_turn_player.id, PortTypes(g_card.value)):
                    e = 2
                elif self._board.is_player_on_port(self.current_turn_player.id, PortTypes.ANY):
                    e = 3
                n = self.current_turn_player.count_resource_cards(g_card)
                if n >= e:
                    for w_card in [c for c in ResourceCards if c != g_card]:
                        trades.append(('offer_trade', [[(g_card, e)], [(w_card, 1)], []]))
        return trades

    def step(self):
        actions = self.get_valid_actions()
        if self.current_turn_player.agent and type(self.current_turn_player.agent) in [RandomAgent, GreedyAgent]:
            function, args = self.current_turn_player.agent.choose_action(actions, self)
            getattr(self, function)(*args)

if __name__ == '__main__':
    from pytan.log.logging import Logger
    from pytan.core.player import Player
    from pytan.ui.board import BoardFrame
    import tkinter as tk
    logger = Logger(console_log=False)
    players = [
        Player('P1', 0, 'red', GreedyAgent()),
        Player('P2', 1, 'blue', RandomAgent()),
        Player('P3', 2, 'white', RandomAgent()),
        Player('P4', 3, 'orange', RandomAgent())
    ]
    game = CatanEnv(players, logger)
    game.start_game()
    
    root = tk.Tk()
    board = BoardFrame(root, game, interact=False)
    board.redraw()
    board.pack()
    
    turns = []
    wins = [0,0,0,0]
    for i in range(100):
        game.start_game(randomize=True)
        for j in range(1000):
            if game.state == GameStates.GAME_OVER:
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

        