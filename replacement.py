"""Population-survival strategies used by :class:`GeneticAlgorithm`."""

from .interfaces import Replacement
class BaseReplacement(Replacement):
    
    def sort_best_first(self, population, mode):
        ranked = sorted(population, key=lambda sol: sol.fitness, reverse=(mode == "max"))
        return sorted(ranked, key=lambda sol: sol.feasible, reverse=True)

class ElitistReplacement(BaseReplacement):
    """Keep the best parents, then fill the population with the best survivors.

    ``config.elitism_count`` parents are guaranteed to survive.  The remaining
    places are chosen from all non-elite parents and all offspring, so this
    strategy never discards a good solution simply because crossover was poor.
    """

    def replace(self, parents, offspring, config):
        ranked_parents = self.sort_best_first(parents, config.mode)
        elites = [solution.copy() for solution in ranked_parents[:config.elitism_count]]
        pool = ranked_parents[config.elitism_count:] + list(offspring)
        survivors = self.sort_best_first(pool, config.mode)
        needed = config.population_size - len(elites)
        return elites + [solution.copy() for solution in survivors[:needed]]


class GenerationalReplacement(BaseReplacement):
    """Replace the old generation with offspring only.

    The GA engine creates exactly ``population_size`` offspring.  The fallback
    makes this strategy safe if it is called directly with too few offspring.
    """

    def replace(self, parents, offspring, config):
        ranked_offspring = self.sort_best_first(offspring, config.mode)
        if len(ranked_offspring) >= config.population_size:
            return [solution.copy() for solution in ranked_offspring[:config.population_size]]

        ranked_parents = self.sort_best_first(parents, config.mode)
        needed = config.population_size - len(ranked_offspring)
        return [solution.copy() for solution in ranked_offspring + ranked_parents[:needed]]


# A familiar name for teams that call the second strategy "full generational".
FullGenerationalReplacement = GenerationalReplacement
