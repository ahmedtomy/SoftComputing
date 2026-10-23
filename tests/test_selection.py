import unittest

from ..CandidateSolution import CandidateSolution
from ..Selection import TournamentSelection
from ..config import GAConfig


class TournamentSelectionTests(unittest.TestCase):
    def make_solution(self, genes, fitness, feasible=True):
        solution = CandidateSolution(genes)
        solution.fitness = fitness
        solution.feasible = feasible
        return solution

    def test_selects_best_candidate_for_minimization(self):
        population = [
            self.make_solution([1], 5),
            self.make_solution([2], 10),
            self.make_solution([3], -100, feasible=False),
        ]
        config = GAConfig(population_size=3, tournament_size=3, mode="min")

        parents = TournamentSelection().select(population, 2, config)

        self.assertEqual(len(parents), 2)
        self.assertEqual([parent.genes for parent in parents], [[1], [1]])
        self.assertIsNot(parents[0], population[0])
        self.assertIsNot(parents[0], parents[1])

    def test_selects_best_candidate_for_maximization(self):
        population = [
            self.make_solution([1], 5),
            self.make_solution([2], 10),
            self.make_solution([3], 2),
        ]
        config = GAConfig(population_size=3, tournament_size=3, mode="max")

        parents = TournamentSelection().select(population, 2, config)

        self.assertEqual([parent.genes for parent in parents], [[2], [2]])


if __name__ == "__main__":
    unittest.main()
