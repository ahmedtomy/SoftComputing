from abc import ABC, abstractmethod


class Chromosome(ABC):
    """Blueprint for creating candidate solutions and populations."""

    @abstractmethod
    def create_genes(self):
        """Generate and return a new list of genes."""
        pass

    @abstractmethod
    def create_candidate(self):
        """Wrap newly generated genes into a CandidateSolution object."""
        pass

    @abstractmethod
    def create_population(self, n):
        """Create a list of n candidate solutions."""
        pass


class Selection(ABC):
    """Blueprint for parent selection strategies."""

    @abstractmethod
    def select(self, population, n, config):
        """Select n parent solutions from the population."""
        pass


class Crossover(ABC):
    """Blueprint for recombining two parents into two children."""

    @abstractmethod
    def crossover(self, parent1, parent2):
        """Combine genes of two parents to produce two offspring."""
        pass


class Mutation(ABC):
    """Blueprint for introducing random variations into a solution."""

    @abstractmethod
    def mutate(self, solution, mutation_rate):
        """Apply random mutations to a solution and return the modified copy."""
        pass


class Replacement(ABC):
    """Blueprint for forming the next generation from parents and offspring."""

    @abstractmethod
    def replace(self, parents, offspring, config):
        """Choose survivors for the next generation from parents and offspring."""
        pass


class InfeasibilityHandler(ABC):
    """Blueprint for evaluating solutions and handling constraint violations."""

    @abstractmethod
    def evaluate(self, solution, problem, config):
        """Evaluate a solution and handle constraints, returning None if rejected."""
        pass