from .interfaces import InfeasibilityHandler


class DefaultInfeasibilityHandler(InfeasibilityHandler):
    """Standard handler that implements penalty, repair, or rejection for constraints."""

    def evaluate(self, solution, problem, config):
        """Evaluate a candidate solution and handle constraint violations according to config."""
        evaluated_solution = solution.copy()

        is_feasible = problem.is_feasible(evaluated_solution.genes)
        evaluated_solution.feasible = is_feasible

        if not evaluated_solution.feasible:
            if config.infeasible_strategy == "repair":
                evaluated_solution.genes = problem.repair(evaluated_solution.genes)
                evaluated_solution.reset()
                evaluated_solution.feasible = problem.is_feasible(evaluated_solution.genes)

        if not evaluated_solution.feasible:
            if config.infeasible_strategy == "repair" or config.infeasible_strategy == "reject":
                return None

        evaluated_solution.raw_fitness = problem.evaluate(evaluated_solution.genes)
        evaluated_solution.violation = problem.violation(evaluated_solution.genes)

        if evaluated_solution.violation < 0:
            raise ValueError("Violation must be non-negative")

        evaluated_solution.fitness = evaluated_solution.raw_fitness

        if not evaluated_solution.feasible:
            penalty_amount = config.penalty_weight * evaluated_solution.violation
            if config.mode == "min":
                evaluated_solution.fitness += penalty_amount
            else:
                evaluated_solution.fitness -= penalty_amount

        return evaluated_solution