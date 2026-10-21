class Problem:
    """The user gives the GA a fitness function and a feasibility function.
    violation_fn and repair_fn are optional."""

    def __init__(self, fitness_fn, feasibility_fn, violation_fn=None, repair_fn=None):
        self.fitness_fn = fitness_fn          # genes -> number (e.g. total distance)
        self.feasibility_fn = feasibility_fn  # genes -> True / False
        self.violation_fn = violation_fn      # genes -> how much constraints are broken
        self.repair_fn = repair_fn            # genes -> repaired genes

    def evaluate(self, genes):
        return self.fitness_fn(genes)

    def is_feasible(self, genes):
        return self.feasibility_fn(genes)

    def violation(self, genes):
        if self.violation_fn is not None:
            return self.violation_fn(genes)
        if self.is_feasible(genes):
            return 0
        return 1

    def repair(self, genes):
        if self.repair_fn is not None:
            return self.repair_fn(genes)
        return genes