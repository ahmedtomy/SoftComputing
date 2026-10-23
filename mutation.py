import random
from .interfaces import Mutation


class BitFlipMutation(Mutation):
    """Mutates binary chromosomes by flipping each bit with probability mutation_rate."""

    def mutate(self, solution, mutation_rate):
        """Iterate over bits, flipping 0 to 1 and 1 to 0 based on mutation probability."""
        mutant = solution.copy()
        gene_count = len(mutant.genes)

        for gene_index in range(gene_count):
            roll = random.random()
            if roll < mutation_rate:
                current_bit = mutant.genes[gene_index]
                if current_bit == 0:
                    mutant.genes[gene_index] = 1
                else:
                    mutant.genes[gene_index] = 0

        mutant.reset()
        return mutant


class UniformMutation(Mutation):
    """Mutates real-valued chromosomes by drawing new values uniformly within [low, high]."""

    def __init__(self, low=0.0, high=1.0):
        """Configure the lower and upper bounds for new random floating-point values."""
        self.low = low
        self.high = high

    def mutate(self, solution, mutation_rate):
        """Iterate over real genes, replacing them with a random uniform value based on mutation probability."""
        mutant = solution.copy()
        gene_count = len(mutant.genes)

        for gene_index in range(gene_count):
            roll = random.random()
            if roll < mutation_rate:
                new_value = random.uniform(self.low, self.high)
                mutant.genes[gene_index] = new_value

        mutant.reset()
        return mutant


class SwapMutation(Mutation):
    """Mutates permutation chromosomes by swapping pairs of genes."""

    def mutate(self, solution, mutation_rate):
        """Iterate over genes, swapping with a random gene position when mutation triggers."""
        mutant = solution.copy()
        gene_count = len(mutant.genes)

        for gene_index in range(gene_count):
            roll = random.random()
            if roll < mutation_rate:
                swap_index = random.randint(0, gene_count - 1)
                temp = mutant.genes[gene_index]
                mutant.genes[gene_index] = mutant.genes[swap_index]
                mutant.genes[swap_index] = temp

        mutant.reset()
        return mutant
