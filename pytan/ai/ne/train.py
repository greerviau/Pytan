import numpy as np
import uuid
import time
import random
import threading
from pytan.core.player import Player
from pytan.ai.agents.evolutionagent import EvolutionAgent
from pytan.log.logging import Logger
from pytan.ai.env import CatanEnv

class Ecosystem():
    def __init__(self, original_f, scoring_function, population_size=100, holdout='sqrt', mating=True):
        """
        original_f must be a function to produce Organisms, used for the original population
        scoring_function must be a function which accepts an Organism as input and returns a float
        """
        self.population_size = population_size
        self.population = [original_f() for _ in range(population_size)]
        self.scoring_function = scoring_function
        if holdout == 'sqrt':
            self.holdout = max(1, int(np.sqrt(population_size)))
        elif holdout == 'log':
            self.holdout = max(1, int(np.log(population_size)))
        elif holdout > 0 and holdout < 1:
            self.holdout = max(1, int(holdout * population_size))
        else:
            self.holdout = max(1, int(holdout))
        self.mating = True
        self.reward_sum = 0
        self.rewards = []

    def find_best(self):
        return self.population[np.argsort(self.rewards)[-1]].clone()

    def select_parent(self):
        rand = random.random() * self.reward_sum
        sum = 0
        for i, r in enumerate(self.rewards):
            sum += r
            if sum > rand:
                return self.population[i]
        return self.population[0]

    def generation(self, keep_best=True):
        self.rewards = []
        n = self.population_size // 4
        for i in range(n):
            print(f"\rBatch: {i+1}/{n}", end='')
            self.rewards.extend(self.scoring_function(self.population[i*4:(i+1)*4]))
        self.reward_sum = sum(self.rewards)
        avg_reward = np.mean(self.rewards)
        min_reward = np.min(self.rewards)
        max_reward = np.max(self.rewards)
        print(f"\nreward sum: {self.reward_sum:.2f} avg reward: {avg_reward:.2f} min reward: {min_reward:.2f} max reward: {max_reward:.2f}")
        new_population = []
        for i in range(self.population_size-1):
            child = self.select_parent().crossover(self.select_parent())
            child.mutate()
            new_population.append(child)
        if keep_best:
            best = self.find_best()
            new_population.append(best) # Ensure best organism survives
        assert len(new_population) == self.population_size
        self.population = new_population

def main():

    # The function to create the initial population
    organism_creator = lambda : EvolutionAgent(Player('Player', uuid.uuid1().int, 'red'), [17, 16, 1], output='linear')

    def simulate_and_evaluate(agents):
        env = CatanEnv(agents=agents, logger=Logger(log_file=None, console_log=False))
        scores = []
        turns = []
        game = env.game
        n = 10
        for _ in range(n):
            game.start_game(randomize=True)
            while True:
                if game.is_over:
                    scores.append([game.get_player_by_id(agents[j].player.id).total_victory_points for j in range(len(agents))])
                    turns.append(game.turn)
                    break
                action = env.current_player.choose_action(env)
                env.step(action)
        #print(scores)
        #print(turns)
        return list(np.sum(np.divide(scores, np.array(turns)[:, None]), axis=0))

    # Create the scoring function and build the ecosystem
    scoring_function = lambda agents : simulate_and_evaluate(agents)
    ecosystem = Ecosystem(organism_creator, scoring_function, population_size=100, holdout=0.1, mating=True)
                        
    # Run 20 generations
    generations = 20
    for i in range(generations):
        print(f"Generation: {i}")
        ecosystem.generation()
        if (i+1) % 5 == 0:
            print("Finding best")
            best = ecosystem.find_best()
            print("Saving model")
            best.save_model(f'organism_gen_{i}.npy')

if __name__ == '__main__':
    main()