from pytan.log.logging import Logger, LOG_CODES
from pytan.core.game import Game
from pytan.core.cards import ResourceCards, DevCards
from pytan.core.player import Player
import os

class Replay(object):
    def __init__(self, log_file: str, console_log: bool = False):
        assert os.path.exists(log_file)
        assert log_file.split('.')[-1] == 'catan'

        file = open(log_file, 'r')
        self._log_list = file.readlines()
        self._log_idx = -1

        self.replay_started = False
        
        self._game = Game(logger=Logger(raw_log=False, console_log=console_log))

    @property
    def game(self) -> Game:
        return self._game
    
    @property
    def has_next(self) -> bool:
        return self._log_idx < len(self._log_list) - 1 or self._game.can_redo

    @property
    def has_last(self) -> bool:
        return self._log_idx > 0 and self._game.can_undo

    def _parse_params(self, params_str: str) -> list[None]:
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
            if p_s in [i.value for i in ResourceCards]:
                params.append(ResourceCards(p_s))
                continue
            elif p_s in [i.value for i in DevCards]:
                params.append(DevCards(p_s))
                continue
            elif p_s.find('[') > -1:
                param = []

                p_s_list = p_s.strip().strip('][').split('-')
                
                if p_s_list[0].isnumeric():
                    param = [int(e) for e in p_s_list]
                elif p_s_list[0]:
                    for e in p_s_list:
                        if e.find(':') > -1:
                            t = []
                            comps = e.split(':')
                            for c in comps:
                                if c.isnumeric():
                                    t.append(int(c))
                                elif c in [i.value for i in ResourceCards]:
                                    t.append(ResourceCards(c))
                            param.append(tuple(t))
                params.append(param)
            else:
                params.append(p_s)
        return params

    def get_action(self, idx: int) -> tuple[str, list[None]]:
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
        if not self.replay_started:
            while 1:
                function, params = self.get_action(0)
                self._log_list.pop(0)
                getattr(self._game, function)(*params)
                if function == 'start_game':
                    break
            self.replay_started = True
        else:
            print('The replay already started')

    def step_forward(self):
        if self.replay_started:
            if self.has_next:
                if self._game.can_redo:
                    self._game.redo()
                else:
                    self._log_idx += 1
                    function, params = self.get_action(self._log_idx)
                    getattr(self._game, function)(*params)
            else:
                print('Reached the end')
        else:
            print('Start the replay first')

    def step_backward(self):
        if self.replay_started:
            if self.has_last:
                self._game.undo()
            else:
                print('At the begining')
        else:
            print('Start the replay first')

if __name__ == '__main__':
    replay = Replay('./test_logs/test_1.catan', console_log=True)
    replay.start()
    while replay.has_next:
        replay.step_forward()