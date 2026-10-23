import unittest

from ..CreateGenes import BinaryChromosome
from ..GAengine import GeneticAlgorithm
from ..Problem import Problem
from ..Selection import TournamentSelection
from ..config import GAConfig
from ..crossover import MultiPointCrossover
from ..mutation import BitFlipMutation
from ..replacement import ElitistReplacement


class GeneticAlgorithmTests(unittest.TestCase):
    def run_algorithm(self):
        config = GAConfig(
            population_size=10,
            generations=5,
            tournament_size=3,
            early_stop_patience=None,
            seed=42,
        )
        problem = Problem(
            fitness_fn=sum,
            feasibility_fn=lambda genes: True,
        )
        algorithm = GeneticAlgorithm(
            config=config,
            problem=problem,
            chromosome=BinaryChromosome(8),
            selection=TournamentSelection(),
            crossover=MultiPointCrossover(),
            mutation=BitFlipMutation(),
            replacement=ElitistReplacement(),
        )
        return algorithm.run()

    def test_run_evolves_population_and_records_history(self):
        best, history = self.run_algorithm()

        self.assertTrue(best.feasible)
        self.assertEqual(best.fitness, sum(best.genes))
        self.assertEqual(len(best.genes), 8)
        self.assertEqual(len(history["best_fitness"]), 6)
        self.assertEqual(len(history["average_fitness"]), 6)
        self.assertEqual(history["best_fitness"][-1], best.fitness)
        self.assertTrue(
            all(
                current <= previous
                for previous, current in zip(
                    history["best_fitness"],
                    history["best_fitness"][1:],
                )
            )
        )

    def test_seeded_run_is_repeatable(self):
        first_best, first_history = self.run_algorithm()
        second_best, second_history = self.run_algorithm()

        self.assertEqual(first_best.genes, second_best.genes)
        self.assertEqual(first_best.fitness, second_best.fitness)
        self.assertEqual(first_history, second_history)


if __name__ == "__main__":
    unittest.main()
