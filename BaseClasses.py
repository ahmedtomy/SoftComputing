"""BASE CLASSES: partly finished classes that hold code shared by their children.
They implement an interface but still leave some methods for the concrete class."""
from .interfaces import Chromosome, Replacement
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


class BaseReplacement(Replacement):
    """Shared code for the replacement methods.
    Children only need to write replace()."""

    def sort_best_first(self, population, mode):
        # best solution first (lowest fitness if "min", highest if "max")
        return sorted(population, key=lambda sol: sol.fitness, reverse=(mode == "max"))

    