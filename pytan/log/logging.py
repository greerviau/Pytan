import os
from datetime import datetime
from pytan.core.player import Player
from pytan.core.cards import ResourceCards, DevCards

LOG_CODES = {
    'set_seed': '{}={}',
    'reset': '{}',
    'clear_players': '{}',
    'add_player': '{}={},{},{}',
    'set_starting_player': '{}={}',
    'start_game': '{}',
    'end_game' : '{}',
    'roll': '{}={}',
    'pass_turn': '{}',
    'build_road': '{}={}',
    'build_settlement': '{}={}',
    'build_city': '{}={}',
    'buy_dev_card': '{}={}',
    'move_robber': '{}={}',
    'steal': '{}={}',
    'discard': '{}={}',
    'offer_trade': '{}={},{},{}',
    'accept_trade': '{}',
    'decline_trade': '{}',
    'confirm_trade': '{}={}',
    'play_knight': '{}',
    'play_monopoly': '{}={}',
    'play_road_builder': '{}',
    'play_year_plenty': '{}={},{}'
}

class Logger(object):
    def __init__(self, log_path: str = './game_logs/', console_log: bool = False, raw_log: bool = True):
        self.console_log = console_log
        self.raw_log = raw_log

        self.reset()

        self._log_path = log_path

    def reset(self):
        self._all_logs = []
        self._raw_logs = []
        self._start = datetime.now()

    @property
    def start(self):
        return self._start

    def log(self, text: str, end: str = '\n'):
        self._all_logs.append(text)
        if self.console_log:
            print(text, end=end)

    def log_action(self, function: str, *params: tuple):
        if self.raw_log and function in LOG_CODES.keys():
            str_params = []
            for param in params:
                if type(param) == list:
                    l = []
                    for p in param:
                        s = ''
                        if type(p) == tuple:
                            for e in p:
                                if type(e) == ResourceCards:
                                    s += e.value
                                elif type(e) == int:
                                    s += str(e)
                                if e != p[-1]:
                                    s += ':'
                        elif type(p) == int:
                            s += str(p)
                        l.append(s)
                    l_s = '-'.join(l)
                    str_params.append(f'[{l_s}]')
                elif type(param) == Player:
                    str_params.append(param.name)
                    str_params.append(param.id)
                    str_params.append(param.color)
                elif type(param) in [ResourceCards, DevCards]:
                    str_params.append(param.value)
                elif type(param) in [int, float, bool, str]:
                    str_params.append(str(param))
            formatter = LOG_CODES[function]
            action_log = formatter.format(function, *str_params)
            self._raw_logs.append(action_log)

    def log_dump(self):
        return '\n'.join(self._all_logs)

    def raw_dump(self):
        return '\n'.join(self._raw_logs)

    def save_raw_log_file(self, filename: str = ''):
        if not filename:
            filename = f'{self._start}.catan'
            filename = filename.replace(' ', '-')
        if not os.path.exists(self._log_path):
            os.makedirs(self._log_path)

        log_filename = os.path.join(self._log_path, filename)
        log_file = open(log_filename, 'w')

        log_file.write(self.raw_dump())
        
        log_file.close()
        log_file = None
        
    def save_log_file(self, filename: str = ''):
        if not filename:
            filename = f'{self._start}.log'
            filename = filename.replace(' ', '-')
        if not os.path.exists(self._log_path):
            os.makedirs(self._log_path)

        log_filename = os.path.join(self._log_path, filename)
        log_file = open(log_filename, 'w')

        log_file.write(self.log_dump())
        
        log_file.close()
        log_file = None

    def get_state(self) -> dict:
        return {
            'console_log': self.console_log,
            'raw_log': self.raw_log,
            'log_path': self._log_path,
            'all_logs': self._all_logs.copy(),
            'raw_logs': self._raw_logs.copy(),
            'start': self._start
        }

    def restore(self, state: dict):
        self.console_log = state['console_log']
        self.raw_log = state['raw_log']
        self.log_path = state['log_path']
        self._all_logs = state['all_logs'].copy()
        self._raw_logs = state['raw_logs'].copy()
        self._start = state['start']

    @staticmethod
    def create_from_state(state: dict) -> 'Logger':
        logger = Logger()
        logger.restore(state)
        return logger