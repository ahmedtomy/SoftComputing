from .interfaces import Crossover
import random
class MultiPointCrossover(Crossover):
    """Recombines two parents by cutting chromosomes at multiple points and alternating segments."""

    def __init__(self, num_points=2):
        """Configure the number of crossover cut points."""
        self.num_points = num_points

    def crossover(self, parent1, parent2):
        """Perform multi-point crossover between parent1 and parent2 to produce two children."""
        gene_count = len(parent1.genes)
        cut_count = min(self.num_points, gene_count - 1)

        cut_points = sorted(random.sample(range(1, gene_count), cut_count))

        genes1 = []
        genes2 = []
        is_swapping = False

        for index in range(gene_count):
            if index in cut_points:
                is_swapping = not is_swapping

            if is_swapping:
                genes1.append(parent2.genes[index])
                genes2.append(parent1.genes[index])
            else:
                genes1.append(parent1.genes[index])
                genes2.append(parent2.genes[index])

        child1 = parent1.copy()
        child2 = parent2.copy()
        child1.genes = genes1
        child2.genes = genes2

        child1.reset()
        child2.reset()

        return child1, child2


class OrderCrossover(Crossover):
    """Order Crossover (OX1) for permutation representations like TSP or CVRP."""

    def crossover(self, parent1, parent2):
        """Generate two valid permutation offspring from two parent permutations."""
        child1 = self._make_child(parent1, parent2)
        child2 = self._make_child(parent2, parent1)
        return child1, child2

    def _make_child(self, keep_parent, fill_parent):
        """Create a child permutation preserving a slice from keep_parent and order from fill_parent."""
        gene_count = len(keep_parent.genes)

        cut_a = random.randint(0, gene_count - 1)
        cut_b = random.randint(0, gene_count - 1)
        start_index = min(cut_a, cut_b)
        end_index = max(cut_a, cut_b) + 1

        child_genes = [None] * gene_count

        copied_segment = []
        for index in range(start_index, end_index):
            gene = keep_parent.genes[index]
            child_genes[index] = gene
            copied_segment.append(gene)

        leftover_genes = []
        for gene in fill_parent.genes:
            if gene not in copied_segment:
                leftover_genes.append(gene)

        leftover_index = 0
        for index in range(gene_count):
            if child_genes[index] is None:
                child_genes[index] = leftover_genes[leftover_index]
                leftover_index += 1

        child = keep_parent.copy()
        child.genes = child_genes
        child.reset()

        return child