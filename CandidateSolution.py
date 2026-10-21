import copy


class CandidateSolution:
    def __init__(self, genes):
        self.genes = genes          # list of genes
        self.fitness = None         # value used by the GA (after penalty)
        self.raw_fitness = None     # value from the problem (before penalty)
        self.feasible = True        # result of the feasibility check
        self.violation = 0          # how much the constraints are broken

    def copy(self):
        # full independent copy (genes and fitness values)
        return copy.deepcopy(self)

    def reset(self):
        # call after crossover/mutation: fitness must be recomputed
        self.fitness = None
        self.raw_fitness = None
        self.feasible = True
        self.violation = 0

    def is_better_than(self, other, mode="min"):
        if mode == "min":
            return self.fitness < other.fitness
        return self.fitness > other.fitness

    def __repr__(self):
        return "CandidateSolution(fitness=" + str(self.fitness) + ", genes=" + str(self.genes) + ")"