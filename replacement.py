"""Population-survival strategies used by GeneticAlgorithm."""

from .interfaces import Replacement


def _get_fitness(solution):
    """Return the fitness value of a solution for sorting."""
    return solution.fitness


def _get_feasibility(solution):
    """Return the feasibility boolean flag of a solution for sorting."""
    return solution.feasible


class BaseReplacement(Replacement):
    """Base class providing stable two-stage sorting: feasibility first, then fitness."""

    def sort_best_first(self, population, mode):
        """Sort solutions so feasible solutions come first, ordered by best fitness."""
        # Step 1: Sort by fitness (lowest first for "min", highest first for "max")
        is_reverse = (mode == "max")
        ranked_by_fitness = sorted(population, key=_get_fitness, reverse=is_reverse)

        # Step 2: Stably sort by feasibility so True (feasible) comes before False (infeasible).
        # We keep this two-pass sorting approach because Python's Timsort is stable:
        # it partitions feasible and infeasible solutions while provably preserving
        # the exact fitness ranking established in Step 1 within each group.
        return sorted(ranked_by_fitness, key=_get_feasibility, reverse=True)


class ElitistReplacement(BaseReplacement):
    """Keep the best parents, then fill the population with the best survivors."""

    def replace(self, parents, offspring, config):
        """Preserve elite parents, then fill remaining population spots from all other candidates."""
        ranked_parents = self.sort_best_first(parents, config.mode)

        # Copy the guaranteed elite parents directly into the new population
        elites = []
        for index in range(config.elitism_count):
            parent = ranked_parents[index]
            elites.append(parent.copy())

        # Form a survivor pool from remaining non-elite parents and all offspring
        survivor_pool = []
        for index in range(config.elitism_count, len(ranked_parents)):
            parent = ranked_parents[index]
            survivor_pool.append(parent)

        for child in offspring:
            survivor_pool.append(child)

        # Rank the pool and select the best individuals to complete the population
        ranked_survivors = self.sort_best_first(survivor_pool, config.mode)
        needed = config.population_size - len(elites)

        next_generation = []
        for elite in elites:
            next_generation.append(elite)

        for index in range(needed):
            survivor = ranked_survivors[index]
            next_generation.append(survivor.copy())

        return next_generation


class GenerationalReplacement(BaseReplacement):
    """Replace the old generation with offspring only, falling back to parents if needed."""

    def replace(self, parents, offspring, config):
        """Form the next generation from offspring, using best parents only if offspring are scarce."""
        ranked_offspring = self.sort_best_first(offspring, config.mode)

        # Normal case: we have enough offspring to fill the population
        if len(ranked_offspring) >= config.population_size:
            next_generation = []
            for index in range(config.population_size):
                child = ranked_offspring[index]
                next_generation.append(child.copy())
            return next_generation

        # Fallback case: fill any deficit with the highest-ranked parents
        ranked_parents = self.sort_best_first(parents, config.mode)
        needed = config.population_size - len(ranked_offspring)

        next_generation = []
        for child in ranked_offspring:
            next_generation.append(child.copy())

        for index in range(needed):
            parent = ranked_parents[index]
            next_generation.append(parent.copy())

        return next_generation


# Alias for teams that refer to GenerationalReplacement as FullGenerationalReplacement.
FullGenerationalReplacement = GenerationalReplacement