import random
from .BaseClasses import BaseChromosome

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