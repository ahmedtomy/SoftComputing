import copy


class CandidateSolution:
    """Represents a single individual in the genetic algorithm population."""

    def __init__(self, genes):
        """Initialize a candidate solution with its genes and default metadata."""
        self.genes = genes          # list of genes representing the solution
        self.fitness = None         # final fitness used by the GA (includes penalty)
        self.raw_fitness = None     # original fitness from the problem (without penalty)
        self.feasible = True        # True if all problem constraints are satisfied
        self.violation = 0          # numerical measure of how much constraints are broken

    def copy(self):
        """Create and return an independent deep copy of this solution."""
        return copy.deepcopy(self)

    def reset(self):
        """Reset fitness and constraint values when genes change after crossover or mutation."""
        self.fitness = None
        self.raw_fitness = None
        self.feasible = True
        self.violation = 0

    def is_better_than(self, other, mode="min"):
        """Compare this solution to another based on feasibility and optimization mode."""
        # A feasible solution is always preferred over an infeasible one
        if self.feasible != other.feasible:
            return self.feasible

        # When both are equally feasible or infeasible, compare numerical fitness
        if mode == "min":
            return self.fitness < other.fitness
        else:
            return self.fitness > other.fitness

    def __repr__(self):
        """Return a readable string representation for debugging and printing."""
        return "CandidateSolution(fitness=" + str(self.fitness) + ", genes=" + str(self.genes) + ")"
