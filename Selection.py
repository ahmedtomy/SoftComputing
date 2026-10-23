from .interfaces import Selection
import random
class TournamentSelection(Selection):
    """Selects parents by running tournaments among randomly sampled individuals."""

    def __init__(self, tournament_size=None):
        """Optionally override tournament size; otherwise config.tournament_size is used."""
        self.tournament_size = tournament_size

    def select(self, population, n, config):
        """Select n parents by holding k-way tournaments among contenders."""
        if not population:
            raise ValueError("Population cannot be empty.")

        # Determine tournament size from override or configuration
        if self.tournament_size is not None:
            k = self.tournament_size
        else:
            k = config.tournament_size

        # Tournament size cannot exceed the population size
        if k > len(population):
            k = len(population)

        selected_parents = []



class RouletteWheelSelection(Selection):
    """Selects parents proportionally to their fitness using roulette wheel sampling."""

    def select(self, population, n, config):
        """Select n parents using fitness-proportionate probability distribution."""
        if not population:
            raise ValueError("Population cannot be empty.")

        epsilon = 1e-8

        # Prefer feasible individuals; fall back to all if none are feasible
        feasible_candidates = []
        for solution in population:
            if solution.feasible:
                feasible_candidates.append(solution)

        if len(feasible_candidates) > 0:
            candidates = feasible_candidates
        else:
            candidates = population

        # Extract fitness values for candidates
        fitnesses = []
        for solution in candidates:
            fitnesses.append(solution.fitness)

        # Convert fitness values into positive selection weights
        weights = []
        if config.mode == "max":
            min_fitness = min(fitnesses)
            if min_fitness <= 0:
                shift = abs(min_fitness) + epsilon
                for fitness_value in fitnesses:
                    weights.append(fitness_value + shift)
            else:
                for fitness_value in fitnesses:
                    weights.append(fitness_value)
        else:
            max_fitness = max(fitnesses)
            for fitness_value in fitnesses:
                weight = (max_fitness - fitness_value) + epsilon
                weights.append(weight)

        # Sample n candidates with probabilities proportional to weights
        chosen_candidates = random.choices(candidates, weights=weights, k=n)

        selected_solutions = []
        for solution in chosen_candidates:
            selected_solutions.append(solution.copy())

        return selected_solutions