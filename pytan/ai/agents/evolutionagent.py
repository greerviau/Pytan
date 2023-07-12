import numpy as np
import copy
import random
from pytan.core.player import Player
from pytan.core.game import Game
from . import BotAgent
import uuid
import math

class EvolutionAgent(BotAgent):

    def __init__(self, player: Player, dimensions=[17, 16, 1], use_bias=True, output='linear'):
        super().__init__(player)
        self.layers = []
        self.dimensions = dimensions
        self.use_bias = use_bias
        self.output = self._activation(output)
        for i in range(len(dimensions)-1):
            shape = (dimensions[i+1], dimensions[i])
            std = np.sqrt(2 / sum(shape))
            layer = np.random.normal(0, std, shape)
            self.layers.append(layer)

    def choose_action(self, env: 'CatanEnv'):
        actions = env.legal_actions
        if len(actions) == 0:
            raise RuntimeError('No actions')

        #print(game.get_state())

        game = Game.create_from_state(env.game.get_state())

        scores = []
        for function, args in actions:
            getattr(game, function)(*args)
            scores.append(self.score(env.get_state_vector()))
            game.undo()
        m = max(scores)
        c = scores.count(m)
        if c > 1:
            i = random.choice([i for i, s in enumerate(scores) if s == m])
        else:
            i = scores.index(m)
        action = actions[i]
        return action

    def score(self, X):
        X = np.array(X)
        #print(X)
        y = self.predict(X)
        return y[0]
    
    def save_model(self, file_path):
        assert '.npy' in file_path
        model = np.array(self.layers, dtype=object)
        np.save(file_path, model)

    def load_model(self, file_path):
        assert '.npy' in file_path
        self.layers = list(np.load(file_path, allow_pickle=True))

    def _activation(self, output):
        if output == 'softmax':
            return lambda X : np.exp(X) / np.sum(np.exp(X), axis=1).reshape(-1, 1)
        if output == 'sigmoid':
            return lambda X : (1 / (1 + np.exp(-X)))
        if output == 'linear':
            return lambda X : X

    def predict(self, X):
        #if not X.ndim == 2:
        #    raise ValueError(f'Input has {X.ndim} dimensions, expected 2')
        #if not X.shape[1] == self.layers[0].shape[0]:
        #    raise ValueError(f'Input has {X.shape[1]} features, expected {self.layers[0].shape[0]}')
        for index, layer in enumerate(self.layers):
            X = layer.dot(X)
            if index == len(self.layers) - 1:
                X = self.output(X) # output activation
            else:
                X = np.clip(X, 0, np.inf)  # ReLU
        
        return X
    
    def clone(self):
        clone = EvolutionAgent(Player('Player', uuid.uuid1().int, "red"), self.dimensions, self.use_bias)
        clone.layers = self.layers.copy()
        clone.output = self.output
        return clone

    def mutate(self, mr=0.05):
        for l in range(len(self.layers)):
            for i in range(self.layers[l].shape[0]):
                for j in range(self.layers[l].shape[1]):
                    r = random.random()
                    if r < mr:
                        self.layers[l][i][j] += np.random.normal() / 5
                    if self.layers[l][i][j] > 1:
                        self.layers[l][i][j] = 1
                    if self.layers[l][i][j] < -1:
                        self.layers[l][i][j] = -1

    def crossover(self, partner):
        if not len(self.layers) == len(partner.layers):
            raise ValueError('Both parents must have same number of layers')
        if not all(self.layers[x].shape == partner.layers[x].shape for x in range(len(self.layers))):
            raise ValueError('Both parents must have same shape')

        child = self.clone()
        for l, layer in enumerate(child.layers):
            randC = math.floor(random.random()*layer.shape[0])
            randR = math.floor(random.random()*layer.shape[1])
            for i in range(layer.shape[0]):
                for j in range(layer.shape[1]):
                    if i > randR or (i == randR and j <= randC):
                        continue
                    else:
                        child.layers[l][i][j] = partner.layers[l][i][j]
        return child