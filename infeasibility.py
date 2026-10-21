
from .interfaces import InfeasibilityHandler


class DefaultInfeasibilityHandler(InfeasibilityHandler):

    def evaluate(self, solution, problem, config):
        solution = solution.copy()

        # Check feasibility
        solution.feasible = problem.is_feasible(solution.genes)

        # Apply repair if requested
        if not solution.feasible and config.infeasible_strategy == "repair":
            solution.genes = problem.repair(solution.genes)
            solution.reset()
            solution.feasible = problem.is_feasible(solution.genes)

        # Reject infeasible solutions
        if not solution.feasible:
            if config.infeasible_strategy in ("repair", "reject"):
                return None

        # Calculate raw fitness and constraint violation
        solution.raw_fitness = problem.evaluate(solution.genes)
        solution.violation = problem.violation(solution.genes)

        if solution.violation < 0:
            raise ValueError("Violation must be non-negative")

        # Calculate final fitness
        solution.fitness = solution.raw_fitness

        if not solution.feasible:
            penalty = config.penalty_weight * solution.violation

            if config.mode == "min":
                solution.fitness += penalty
            else:
                solution.fitness -= penalty

        return solution
