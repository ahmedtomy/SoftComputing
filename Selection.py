import random

from .interfaces import Selection


class TournamentSelection(Selection):
    def __init__(self, tournament_size=None):
        self.tournament_size = tournament_size

    def select(self, population, n, config):
        if not population:
            raise ValueError("Population cannot be empty.")

        k = self.tournament_size if self.tournament_size is not None else config.tournament_size
        k = min(k, len(population))

        selected_parents = []

        for _ in range(n):
            contenders = random.sample(population, k)

            winner = contenders[0]
            for contender in contenders[1:]:
                if contender.is_better_than(winner, config.mode):
                    winner = contender

            selected_parents.append(winner.copy())

        return selected_parents


class RouletteWheelSelection(Selection):
    def select(self, population, n, config):
        if not population:
            raise ValueError("Population cannot be empty.")

        epsilon = 1e-8

        candidates = [sol for sol in population if sol.feasible]
        if not candidates:
            candidates = population

        fitnesses = [sol.fitness for sol in candidates]

        if config.mode == "max":
            min_fit = min(fitnesses)
            if min_fit <= 0:
                shift = abs(min_fit) + epsilon
                weights = [f + shift for f in fitnesses]
            else:
                weights = [f for f in fitnesses]
        else:
            max_fit = max(fitnesses)
            weights = [(max_fit - f) + epsilon for f in fitnesses]

        total_weight = sum(weights)
        return [sol.copy() for sol in random.choices(candidates, weights=weights, k=n)]