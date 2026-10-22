import random
from interfaces import Mutation

class BitFlipMutation(Mutation):

    def mutate(self, solution, mutation_rate):
        mutant = solution.copy()

        for i in range(len(mutant.genes)):
            if random.random() < mutation_rate:   
                if mutant.genes[i] == 0:
                    mutant.genes[i] = 1
                else:
                    mutant.genes[i] = 0

        mutant.reset()
        return mutant


class UniformMutation(Mutation):

    def __init__(self, low=0.0, high=1.0):
        self.low = low
        self.high = high

    def mutate(self, solution, mutation_rate):
        mutant = solution.copy()

        for i in range(len(mutant.genes)):
            if random.random() < mutation_rate:   
                mutant.genes[i] = random.uniform(self.low, self.high)

        mutant.reset()
        return mutant

class SwapMutation(Mutation):

    def mutate(self, solution, mutation_rate):
        mutant = solution.copy()
        n = len(mutant.genes)

        for i in range(n):
            if random.random() < mutation_rate:   
                j = random.randint(0, n - 1)      
                temp = mutant.genes[i]
                mutant.genes[i] = mutant.genes[j]
                mutant.genes[j] = temp

        mutant.reset()
        return mutant