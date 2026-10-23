import unittest

from SoftComputing.CreateGenes import IntegerChromosome
from SoftComputing.CandidateSolution import CandidateSolution
from SoftComputing.config import GAConfig
from SoftComputing.cvrpFitness import (
    build_cvrp_problem,
    format_cvrp_solution,
    route_distance,
    total_distance,
)
from SoftComputing.infeasibility import DefaultInfeasibilityHandler
from SoftComputing.cvrpTools import decode


class CVRPFitnessTests(unittest.TestCase):
    coordinates = [(0, 0), (3, 0), (6, 0), (0, 4)]
    demands = [0, 3, 2, 2]
    capacity = 4
    vehicles = 2

    def test_distance_includes_each_return_to_depot_and_empty_routes(self):
        self.assertEqual(route_distance([1, 2], self.coordinates), 12)
        self.assertEqual(route_distance([3], self.coordinates), 8)
        self.assertEqual(route_distance([], self.coordinates), 0)
        self.assertAlmostEqual(
            total_distance([1, 2, 3], self.coordinates, self.demands, 5, 2),
            20,
        )
        self.assertAlmostEqual(
            total_distance([1, 2, 3], self.coordinates, self.demands, 4, 2),
            6 + 6 + (52 ** 0.5) + 4,
        )

    def test_problem_connects_permutation_and_constraint_handlers(self):
        problem = build_cvrp_problem(
            self.coordinates, self.demands, self.capacity, self.vehicles
        )
        chromosome = IntegerChromosome(3, 1, 3, is_permutation=True)
        self.assertEqual(sorted(chromosome.create_genes()), [1, 2, 3])
        self.assertTrue(problem.is_feasible([1, 3, 2]))
        self.assertFalse(problem.is_feasible([2, 1, 3]))
        self.assertEqual(problem.violation([2, 1, 3]), 1)
        self.assertEqual(problem.violation([1, 1, 3]), 2)

        handler = DefaultInfeasibilityHandler()
        candidate = CandidateSolution([2, 1, 3])
        evaluated = handler.evaluate(
            candidate, problem, GAConfig(mode="min", penalty_weight=100)
        )
        self.assertFalse(evaluated.feasible)
        self.assertEqual(evaluated.fitness, evaluated.raw_fitness + 100)
        duplicate = handler.evaluate(
            CandidateSolution([1, 1, 3]),
            problem,
            GAConfig(mode="min", penalty_weight=100),
        )
        self.assertFalse(duplicate.feasible)
        self.assertEqual(duplicate.fitness, duplicate.raw_fitness + 200)
        self.assertIsNone(
            handler.evaluate(
                candidate, problem, GAConfig(mode="min", infeasible_strategy="reject")
            )
        )
        repaired = handler.evaluate(
            candidate, problem, GAConfig(mode="min", infeasible_strategy="repair")
        )
        self.assertTrue(repaired.feasible)
        self.assertEqual(sorted(repaired.genes), [1, 2, 3])
        self.assertEqual(repaired.fitness, repaired.raw_fitness)

    def test_output_format(self):
        text = format_cvrp_solution(
            [1, 3, 2], self.coordinates, self.demands, self.capacity, self.vehicles
        )
        self.assertEqual(
            text,
            f"Objective: {6 + 4 + 52 ** 0.5 + 6:.2f}\n"
            "Route for vehicle 0:\n"
            " 0 Load(0) -> 1 Load(0) -> 0 Load(3)\n"
            "Distance of the route: 6.00m\n"
            "Load of the route: 3\n\n"
            "Route for vehicle 1:\n"
            " 0 Load(0) -> 3 Load(0) -> 2 Load(2) -> 0 Load(4)\n"
            f"Distance of the route: {4 + 52 ** 0.5 + 6:.2f}m\n"
            "Load of the route: 4\n\n"
            f"Total distance of all routes: {6 + 4 + 52 ** 0.5 + 6:.2f}m\n"
            "Total load of all routes: 7",
        )
        unused_vehicle = format_cvrp_solution(
            [1, 3, 2], self.coordinates, self.demands, self.capacity, 3
        )
        self.assertNotIn("Route for vehicle 2:", unused_vehicle)
        self.assertIn(
            "Feasible: False",
            format_cvrp_solution(
                [2, 1, 3], self.coordinates, self.demands, self.capacity, self.vehicles
            ),
        )

    def test_instance_and_gene_validation(self):
        with self.assertRaises(ValueError):
            build_cvrp_problem(self.coordinates[:-1], self.demands, 4, 2)
        with self.assertRaises(ValueError):
            build_cvrp_problem(self.coordinates, self.demands, 0, 2)
        with self.assertRaises(ValueError):
            build_cvrp_problem(self.coordinates, self.demands, 4, 0)
        with self.assertRaises(ValueError):
            total_distance([0, 1, 2], self.coordinates, self.demands, 4, 2)
        with self.assertRaises(ValueError):
            build_cvrp_problem(None, self.demands, 4, 2, distance_matrix=[[0]])


class GoogleCVRPExampleTests(unittest.TestCase):
    distance_matrix = [
        [0, 548, 776, 696, 582, 274, 502, 194, 308, 194, 536, 502, 388, 354, 468, 776, 662],
        [548, 0, 684, 308, 194, 502, 730, 354, 696, 742, 1084, 594, 480, 674, 1016, 868, 1210],
        [776, 684, 0, 992, 878, 502, 274, 810, 468, 742, 400, 1278, 1164, 1130, 788, 1552, 754],
        [696, 308, 992, 0, 114, 650, 878, 502, 844, 890, 1232, 514, 628, 822, 1164, 560, 1358],
        [582, 194, 878, 114, 0, 536, 764, 388, 730, 776, 1118, 400, 514, 708, 1050, 674, 1244],
        [274, 502, 502, 650, 536, 0, 228, 308, 194, 240, 582, 776, 662, 628, 514, 1050, 708],
        [502, 730, 274, 878, 764, 228, 0, 536, 194, 468, 354, 1004, 890, 856, 514, 1278, 480],
        [194, 354, 810, 502, 388, 308, 536, 0, 342, 388, 730, 468, 354, 320, 662, 742, 856],
        [308, 696, 468, 844, 730, 194, 194, 342, 0, 274, 388, 810, 696, 662, 320, 1084, 514],
        [194, 742, 742, 890, 776, 240, 468, 388, 274, 0, 342, 536, 422, 388, 274, 810, 468],
        [536, 1084, 400, 1232, 1118, 582, 354, 730, 388, 342, 0, 878, 764, 730, 388, 1152, 354],
        [502, 594, 1278, 514, 400, 776, 1004, 468, 810, 536, 878, 0, 114, 308, 650, 274, 844],
        [388, 480, 1164, 628, 514, 662, 890, 354, 696, 422, 764, 114, 0, 194, 536, 388, 730],
        [354, 674, 1130, 822, 708, 628, 856, 320, 662, 388, 730, 308, 194, 0, 342, 422, 536],
        [468, 1016, 788, 1164, 1050, 514, 514, 662, 320, 274, 388, 650, 536, 342, 0, 764, 194],
        [776, 868, 1552, 560, 674, 1050, 1278, 742, 1084, 810, 1152, 274, 388, 422, 764, 0, 798],
        [662, 1210, 754, 1358, 1244, 708, 480, 856, 514, 468, 354, 844, 730, 536, 194, 798, 0],
    ]
    demands = [0, 1, 1, 2, 4, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8]
    routes = [[4, 3, 1, 7], [14, 16, 10, 9], [12, 11, 15, 13], [8, 2, 6, 5]]
    capacity = 15

    def test_published_instance_route_costs_loads_and_output(self):
        genes = [customer for route in self.routes for customer in route]
        routes, loads = decode(genes, self.demands, self.capacity, 4)
        self.assertEqual(routes, self.routes)
        self.assertEqual(loads, [15, 15, 15, 15])
        self.assertEqual(sorted(genes), list(range(1, 17)))
        self.assertEqual(
            [route_distance(route, None, distance_matrix=self.distance_matrix) for route in routes],
            [1552] * 4,
        )
        problem = build_cvrp_problem(
            None, self.demands, self.capacity, 4, distance_matrix=self.distance_matrix
        )
        self.assertTrue(problem.is_feasible(genes))
        self.assertEqual(problem.violation(genes), 0)
        self.assertEqual(problem.evaluate(genes), 6208)
        solution = DefaultInfeasibilityHandler().evaluate(
            CandidateSolution(genes), problem, GAConfig(mode="min")
        )
        self.assertEqual(solution.fitness, 6208)
        output = format_cvrp_solution(
            genes, None, self.demands, self.capacity, 4,
            distance_matrix=self.distance_matrix,
        )
        self.assertTrue(output.startswith("Objective: 6208\nRoute for vehicle 0:\n"))
        self.assertIn(
            " 0 Load(0) -> 4 Load(0) -> 3 Load(4) -> "
            "1 Load(6) -> 7 Load(7) -> 0 Load(15)\n"
            "Distance of the route: 1552m\nLoad of the route: 15",
            output,
        )
        self.assertIn("Route for vehicle 3:\n", output)
        self.assertEqual(output.count("Distance of the route: 1552m"), 4)
        self.assertTrue(output.endswith(
            "Total distance of all routes: 6208m\nTotal load of all routes: 60"
        ))


if __name__ == "__main__":
    unittest.main()
