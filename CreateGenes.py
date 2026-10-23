import random
from .interfaces import Chromosome
from .CandidateSolution import CandidateSolution


class BaseChromosome(Chromosome):
    """Shared base class providing candidate and population creation for chromosome types."""

    def __init__(self, length):
        """Initialize the chromosome length."""
        self.length = length

    def create_candidate(self):
        """Generate a single candidate solution using the subclass gene generator."""
        genes = self.create_genes()
        return CandidateSolution(genes)

    def create_population(self, n):
        """Create a list of n candidate solutions using explicit loop construction."""
        population = []
        for _ in range(n):
            candidate = self.create_candidate()
            population.append(candidate)
        return population


class BinaryChromosome(BaseChromosome):
    """Chromosome that represents solutions as lists of binary bits (0 or 1)."""

    def __init__(self, length):
        """Initialize a binary chromosome of given length."""
        super().__init__(length)

    def create_genes(self):
        """Generate a random list of bits (0 or 1) of specified length."""
        genes = []
        for _ in range(self.length):
            bit = random.randint(0, 1)
            genes.append(bit)
        return genes


class IntegerChromosome(BaseChromosome):
    """Chromosome representing solutions as integer values or full permutations."""

    def __init__(self, length, min_val, max_val, is_permutation=False):
        """Configure bounds and whether chromosomes form a unique permutation."""
        super().__init__(length)
        self.min_val = min_val
        self.max_val = max_val
        self.is_permutation = is_permutation

    def create_genes(self):
        """Generate either a random permutation or a list of random integers within bounds."""
        if self.is_permutation:
            genes = []
            for value in range(self.min_val, self.max_val + 1):
                genes.append(value)
            random.shuffle(genes)
            return genes
        else:
            genes = []
            for _ in range(self.length):
                value = random.randint(self.min_val, self.max_val)
                genes.append(value)
            return genes


class FloatingChromosome(BaseChromosome):
    """Chromosome that represents solutions as continuous real-valued numbers."""

    def __init__(self, length, min_val, max_val):
        """Configure length and range for continuous genes."""
        super().__init__(length)
        self.min_val = min_val
        self.max_val = max_val

    def create_genes(self):
        """Generate a list of random floating-point numbers between min_val and max_val."""
        genes = []
        for _ in range(self.length):
            gene_value = random.uniform(self.min_val, self.max_val)
            genes.append(gene_value)
        return genes
