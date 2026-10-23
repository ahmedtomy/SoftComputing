import random
from .interfaces import Chromosome
from .CandidateSolution import CandidateSolution
class BaseChromosome(Chromosome):
    """Shared code for Binary, Integer and Floating chromosomes.
    Children only need to write create_genes()."""

    def __init__(self, length):
        self.length = length

    def create_candidate(self):
        return CandidateSolution(self.create_genes())

    def create_population(self, n):
        return [self.create_candidate() for _ in range(n)]

class BinaryChromosome(BaseChromosome):
    def __init__(self, length):
        super().__init__(length)
    def create_genes(self):
        return [random.randint(0, 1) for _ in range(self.length)]



class IntegerChromosome(BaseChromosome):
    def __init__(self, length, min_val, max_val, is_permutation=False):
        super().__init__(length)
        self.min_val = min_val
        self.max_val = max_val
        self.is_permutation = is_permutation

    def create_genes(self):
        if self.is_permutation:
            genes = list(range(self.min_val, self.max_val + 1))
            random.shuffle(genes)
            return genes
        else:
            return [random.randint(self.min_val, self.max_val) for _ in range(self.length)]


class FloatingChromosome(BaseChromosome):
    def __init__(self, length, min_val, max_val):
        super().__init__(length)
        self.min_val = min_val
        self.max_val = max_val
    def create_genes(self):
        return [random.uniform(self.min_val, self.max_val) for _ in range(self.length)]