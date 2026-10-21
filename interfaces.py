
from abc import ABC, abstractmethod


class Chromosome(ABC):
    @abstractmethod
    def create_genes(self):
        pass

    @abstractmethod
    def create_candidate(self):
        pass

    @abstractmethod
    def create_population(self, n):
        pass


class Selection(ABC):
    @abstractmethod
    def select(self, population, n, config):
        pass


class Crossover(ABC):
    @abstractmethod
    def crossover(self, parent1, parent2):
        pass


class Mutation(ABC):
    @abstractmethod
    def mutate(self, solution, mutation_rate):
        pass


class Replacement(ABC):
    @abstractmethod
    def replace(self, parents, offspring, config):
        pass


class InfeasibilityHandler(ABC):
    @abstractmethod
    def evaluate(self, solution, problem, config):
        """
        Evaluate a solution and handle constraint violations.

        Return an evaluated CandidateSolution,
        or None if the solution must be rejected.
        """
        pass