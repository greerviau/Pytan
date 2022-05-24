from pytan.log.logging import Logger, LOG_CODES
from pytan.core.game import Game
from pytan.core.cards import ResourceCards
from pytan.core.player import Player
import os
import copy

class Replay(object):
    def __init__(self, log_file: str):
        assert os.path.exists(log_file)
        assert log_file.split('.')[-1] == 'catan'

        file = open(log_file, 'r')
        self._log_list = file.readlines()
        self._log_idx = -1
        
        self._game = Game(logger=Logger(raw_log=False))

        self._game_states = []

    @property
    def game(self):
        return self._game

    def _store_state(self):
        self._game_states.append(copy.deepcopy(self._game))

    def _parse_params(self, params_str):
        params_str_list = params_str.split(',')
        params = []
        for p_s in params_str_list:
            try:
                params.append(int(p_s))
                continue
            except ValueError:
                pass
            try:
                params.append(int(p_s, 16))
                continue
            except ValueError:
                pass
            try:
                params.append(float(p_s))
                continue
            except ValueError:
                pass
            try:
                params.append(p_s)
                continue
            except ValueError:
                pass
            if p_s.find('-') > 0:
                p_s_list = p_s.split('-')
                if p_s_list[0].isnumeric():
                    params.append([int(e) for e in p_s_list])
                else:
                    p_list = []
                    for e in p_s_list:
                        if e.find(':') > 0:
                            t = []
                            comps = e.split(':')
                            for c in comps:
                                if c.isnumeric():
                                    t.append(int(c))
                                elif c in [i.value for i in ResourceCards]:
                                    t.append(ResourceCards(c))
                            p_list.append(tuple(t))
                    params.append(p_list)
        return params

    def get_log(self, idx):
        log = self._log_list[idx]
        log = log.replace('\n','')
        log = log.strip()
        function = log
        params = []
        if log.find('=') > 0:
            function, params_str = log.split('=')
            params = self._parse_params(params_str)
            if function == 'add_player':
                params = [Player(*params)]

        return function, params

    def start(self):
        if len(self._game_states) == 0:
            while 1:
                function, params = self.get_log(0)
                self._log_list.pop(0)
                getattr(self._game, function)(*params)
                if function == 'start_game':
                    break
            self._store_state()
        else:
            print('The replay already started')

    def step_forward(self):
        if len(self._game_states) > 0:
            self._log_idx += 1
            if len(self._game_states) - 1 <= self._log_idx:
                function, params = self.get_log(self._log_idx)
                getattr(self._game, function)(*params)
                self._store_state()
            else:
                self._game = self._game_states[self._log_idx+1]
        else:
            print('Start the replay first')

    def step_backward(self):
        if len(self._game_states) > 0:
            if self._log_idx > 0:
                self._game = self._game_states[self._log_idx]
                self._log_idx -= 1
        else:
            print('Start the replay first')

if __name__ == '__main__':
    replay = Replay('./test_logs/test.catan')
    replay.start()
    replay.step_forward()
    replay.step_forward()
    replay.step_backward()
    replay.step_forward()