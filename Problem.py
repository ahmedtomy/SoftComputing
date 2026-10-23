class Problem:
    """Defines an optimization problem by bundling fitness, feasibility, violation, and repair functions."""

    def __init__(self, fitness_fn, feasibility_fn, violation_fn=None, repair_fn=None):
        """Store the functions defining problem evaluation and constraint handling."""
        self.fitness_fn = fitness_fn          # function mapping genes to a numeric cost or reward
        self.feasibility_fn = feasibility_fn  # function returning True if constraints are satisfied
        self.violation_fn = violation_fn      # optional function returning degree of violation
        self.repair_fn = repair_fn            # optional function transforming genes into a feasible form

    def evaluate(self, genes):
        """Compute and return the objective fitness value for given genes."""
        return self.fitness_fn(genes)

    def is_feasible(self, genes):
        """Return True if given genes satisfy all problem constraints."""
        return self.feasibility_fn(genes)

    def violation(self, genes):
        """Compute how much the constraints are violated (0 if feasible)."""
        if self.violation_fn is not None:
            return self.violation_fn(genes)

        # Default fallback: 0 violation if feasible, 1 if infeasible
        if self.is_feasible(genes):
            return 0
        return 1

    def repair(self, genes):
        """Attempt to fix an infeasible chromosome using the problem-specific repair function."""
        if self.repair_fn is not None:
            return self.repair_fn(genes)
        return genes
