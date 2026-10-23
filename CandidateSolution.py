import copy


class CandidateSolution:
    """Represents a single individual in the genetic algorithm population."""

    def __init__(self, genes):
        """Initialize a candidate solution with its genes and default metadata."""
        self.genes = genes          #[] of the solution
        self.fitness = None         # final fitness + penalty
        self.raw_fitness = None     # original fitness
        self.feasible = True        # True if all problem constraints are satisfied
        self.violation = 0          # numerical measure of how much constraints are broken

    def copy(self):
        return copy.deepcopy(self)

    def reset(self):
        self.fitness = None
        self.raw_fitness = None
        self.feasible = True
        self.violation = 0

    def is_better_than(self, other, mode="min"):
        if self.feasible != other.feasible:
            return self.feasible

        if mode == "min":
            return self.fitness < other.fitness
        else:
            return self.fitness > other.fitness

    def __repr__(self):
        """Return a readable string representation for debugging and printing."""
        return "CandidateSolution(fitness=" + str(self.fitness) + ", genes=" + str(self.genes) + ")"