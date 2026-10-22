import random
from interfaces import Crossover


class MultiPointCrossover(Crossover):
    def __init__(self, num_points=2):
        self.num_points = num_points

    def crossover(self, parent1, parent2):
        n = len(parent1.genes)
        k = min(self.num_points, n - 1)
        points = sorted(random.sample(range(1, n), k))

        genes1 = []
        genes2 = []
        swapping = False

        for i in range(n):
            if i in points:           # we reached a cut, so flip the mode
                swapping = not swapping

            if swapping:
                genes1.append(parent2.genes[i])
                genes2.append(parent1.genes[i])
            else:
                genes1.append(parent1.genes[i])
                genes2.append(parent2.genes[i])

        child1 = parent1.copy()
        child2 = parent2.copy()
        child1.genes = genes1
        child2.genes = genes2

        child1.reset()
        child2.reset()
        return child1, child2



        
class OrderCrossover(Crossover):

    def crossover(self, parent1, parent2):
        child1 = self._make_child(parent1, parent2)
        child2 = self._make_child(parent2, parent1)
        return child1, child2

    def _make_child(self, keep_parent, fill_parent):
        n = len(keep_parent.genes)

        # Step 1: pick a random piece of keep_parent and copy it
        a = random.randint(0, n - 1)
        b = random.randint(0, n - 1)
        start = min(a, b)
        end = max(a, b) + 1          # end is not included

        child_genes = [None] * n     # empty spots
        for i in range(start, end):
            child_genes[i] = keep_parent.genes[i]

        # Step 2: take fill_parent's genes in order, skipping the ones we already have
        leftovers = []
        for gene in fill_parent.genes:
            if gene not in child_genes[start:end]:
                leftovers.append(gene)

        # Step 3: put the leftovers into the empty spots, left to right
        j = 0
        for i in range(n):
            if child_genes[i] is None:
                child_genes[i] = leftovers[j]
                j += 1

        child = keep_parent.copy()
        child.genes = child_genes
        child.reset()
        return child